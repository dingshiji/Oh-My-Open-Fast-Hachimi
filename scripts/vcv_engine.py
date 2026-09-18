import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import sys,json
SR=44100;LEAD=.13;BEAT=1

def synth_chunks(model,mel,f0):
 import numpy as np,torch
 hop=512;step=1024;overlap=64;N=mel.shape[1];out=np.zeros(N*hop);weight=np.zeros(N*hop)
 for start in range(0,N,step):
  lo=max(0,start-overlap);hi=min(N,start+step+overlap)
  with torch.inference_mode():y=model.spec2wav_torch(torch.from_numpy(mel[:,lo:hi]).unsqueeze(0).cuda(),f0=torch.from_numpy(f0[lo:hi].astype(np.float32)).unsqueeze(0).cuda()).cpu().numpy()
  y=y[:(hi-lo)*hop];w=np.ones(len(y));edge=overlap*hop
  if lo>0:w[:edge]=np.linspace(0,1,edge)
  if hi<N:w[-edge:]=np.linspace(1,0,edge)
  out[lo*hop:lo*hop+len(y)]+=y*w;weight[lo*hop:lo*hop+len(y)]+=w
  print('VOCODER',hi,'/',N,flush=True)
 return out/np.maximum(weight,1e-8)

def render():
    import numpy as np,torch,soundfile as sf,time
    from scipy.interpolate import interp1d
    from scipy.signal import butter,sosfiltfilt
    neural=ROOT/'models';sys.path.insert(0,config()['hifisampler'])
    from util.nsf_hifigan import NsfHifiGAN
    from util.wav2mel import PitchAdjustableMelSpectrogram
    torch.set_num_threads(4);torch.manual_seed(734)
    parts=json.loads((WORK/'notes_lyrics.json').read_text(encoding='utf-8'));all_ph=json.loads((WORK/'phonemes.json').read_text(encoding='utf-8'))
    total=max(ns[-1]['end'] for ns in parts if ns)*BEAT+LEAD+1.20
    hop=512;sourcehop=128;frames=int(np.ceil(total*SR/hop));t=(np.arange(frames)+.5)*hop/SR-LEAD
    analyzer=PitchAdjustableMelSpectrogram(hop_length=sourcehop)
    model=NsfHifiGAN(next((neural/'pc_nsf_hifigan').rglob('model.ckpt')));model.to_device('cuda')
    source_pre={'は':.114,'じ':.110,'み':.125,'な':.115,'め':.120,'る':.070,'ど':.070,'あ':.035,'し':.125,'が':.070,'や':.080,'く':.080,'でぃ':.070,'ま':.125,'ぼ':.080,'ん':.090}
    for pi,(notes,phonemes) in enumerate(zip(parts,all_ph)):
        bank=['teio','manbo'][pi]
        if not notes:
            sf.write(OUT/(['A_teio_主旋律干声.wav','B_manbo_应答干声.wav'][pi]),np.zeros(round(total*SR)),SR,subtype='PCM_24');continue
        melmix=np.zeros((128,frames),np.float32);weights=np.zeros(frames,np.float32);cache={};lastgain=1.;records=[];segments=[]
        for i,p in enumerate(phonemes):
            r=p['record'];key=(r['folder'],r['wav']);path=ROOT/'assets/private/voicebanks'/bank/key[0]/key[1]
            if key not in cache:
                y,fs=sf.read(path,dtype='float32');assert fs==SR
                if y.ndim>1:y=y.mean(axis=1)
                with torch.inference_mode():m=analyzer(torch.from_numpy(y).unsqueeze(0).cuda()).squeeze(0).cpu().numpy()
                cache[key]=(y,np.log(np.maximum(m,1e-5)),(np.arange(m.shape[-1])+.5)*sourcehop/SR)
            y,source_mel,source_t=cache[key]
            off,cons,cut,pre,over=np.array(r['params'],float)/1000;vowel=off+pre;src_pre=min(pre,source_pre.get(p['kana'], .035 if p['token'] in 'aiueo' else .09));a=p['start']-p['pre_target']
            nxt=phonemes[i+1] if i+1<len(phonemes) else None;cross=.012;connected=nxt is not None and nxt['continuous']
            b=nxt['start']-nxt['pre_target']+cross if connected else p['end']+.035
            if nxt and not connected:b=min(b,nxt['start']-nxt['pre_target'])
            assert b>p['start']+.008,(pi,i,p,b)
            indices=np.where((t>=a)&(t<=b))[0];local=t[indices];assert len(indices)>0
            duration=max(.012,b-p['start']);attack=min(.052,duration*.45);src_attack=.070 if p['kana']!='ん' else .008
            src_end=(off-cut if cut<0 else len(y)/SR-cut)-.065
            if p['kana']=='ん':src_end=vowel+.050
            src_end=max(vowel+src_attack+.010,src_end)
            positions=np.interp(local,[a,p['start'],p['start']+attack,b],[vowel-src_pre,vowel,vowel+src_attack,src_end])
            mel=interp1d(source_t,source_mel,axis=1,bounds_error=False,fill_value='extrapolate')(positions)
            rms=float(np.sqrt(np.mean(y[round((vowel+.075)*SR):round((vowel+.20)*SR)]**2)+1e-9))
            gain=float(np.clip(.145/rms,.60,1.9)) if p['kana']!='ん' else lastgain*.82
            if p['kana']!='ん':lastgain=gain
            n=notes[p['note']];phase=n['start']%4
            accent=1.035 if phase<.01 else 1.015 if abs(phase-2)<.01 else .95
            if pi==0 and p['note']<19:accent=[1.03,.94,.98,1.00,.93,.99,1.02,.96,.97,1.00,.94,.96,1.03,.93,1.01,.96,1.03,.97,1.00][p['note']]
            if pi==1:accent*=1.04 if n['lyric']=='man' else .94
            mel+=np.log(gain*accent)
            w=np.ones(len(indices))
            if p['continuous']:w*=np.clip((local-a)/cross,0,1)
            if connected:w*=np.clip((b-local)/cross,0,1)
            melmix[:,indices]+=mel*w;weights[indices]+=w
            if not p['continuous']:segments.append([a,b])
            else:segments[-1][1]=b
            records.append(dict(note=p['note']+1,lyric=n['lyric'],alias=p['alias'],onset=p['start'],start=a,end=b,pre_ms=1000*p['pre_target'],source_pre_ms=1000*src_pre,gain=gain))
        active=weights>1e-5;melmix[:,active]/=weights[active];melmix[:,~active]=np.log(1e-5)
        pitch=np.full(frames,notes[0]['pitch'],float)
        for i,n in enumerate(notes):
            a=n['start']*BEAT;b=n['end']*BEAT;sel=(t>=a)&(t<b);pitch[sel]=n['pitch']
            # Keep pitch steady through rests and use the next note's pitch for
            # its consonant lead-in; legato transitions are just 12 ms long.
            if i:
                prev=notes[i-1];gap=(n['start']-prev['end'])*BEAT
                if gap>=.04:pitch[(t>=a-.10)&(t<a)]=n['pitch']
                else:
                    glide=.012;ix=(t>=a-glide)&(t<a);f=np.clip((t[ix]-a+glide)/glide,0,1);f=f*f*(3-2*f)
                    pitch[ix]=prev['pitch']+(n['pitch']-prev['pitch'])*f
            if pi==0 and b-a>.65:
                va=a+.42;v=(t>va)&(t<b);pitch[v]+=.11*np.minimum(1,(t[v]-va)/.18)*np.sin(2*np.pi*5.2*(t[v]-va))
            nxt=notes[i+1] if i+1<len(notes) else None
            pitch[(t>=b)&(t<(nxt['start']*BEAT-.10 if nxt else total))]=n['pitch']
        f0=440*2**((pitch-69)/12)
        np.savez_compressed(WORK/f'{bank}_features.npz',mel=melmix,f0=f0,time=t)
        print('FEATURES READY',bank,'phonemes',len(phonemes),'source_wavs',len(cache),'frames',frames,flush=True)
        started=time.time()
        with torch.inference_mode():result=synth_chunks(model,melmix,f0)
        result=result[:round(total*SR)]
        result=sosfiltfilt(butter(2,65,fs=SR,btype='highpass',output='sos'),result)
        ts=np.arange(len(result))/SR-LEAD;gate=np.zeros(len(result))
        for a,b in segments:
            lo=max(0,int((a+LEAD)*SR));hi=min(len(ts),int((b+LEAD)*SR)+1);tt=ts[lo:hi];env=np.clip((tt-a)/.014,0,1)*np.clip((b-tt)/.025,0,1);gate[lo:hi]=np.maximum(gate[lo:hi],env)
        result*=gate
        # Very gently relax the ends of longer sustained notes.
        for n in notes:
            a=n['start']*BEAT;b=n['end']*BEAT
            if b-a>.65:
                mask=(ts>=a+.30)&(ts<=b);result[mask]*=1-.09*np.clip((ts[mask]-a-.30)/max(.1,b-a-.30),0,1)
        result*=.88/max(np.max(np.abs(result)),1e-9)
        assert np.isfinite(result).all()
        dest=OUT/(['A_teio_主旋律干声.wav','B_manbo_应答干声.wav'][pi]);sf.write(dest,result,SR,subtype='PCM_24')
        (WORK/f'{bank}_render_record.json').write_text(json.dumps(dict(segments=segments,records=records),ensure_ascii=False,indent=2),encoding='utf-8')
        print('AUDIO READY',bank,'seconds',len(result)/SR,'synthesis_seconds',round(time.time()-started,2),'gpu_peak_GB',round(torch.cuda.max_memory_allocated()/1e9,2),flush=True)
        torch.cuda.empty_cache()
    (WORK/'render_meta.json').write_text(json.dumps(dict(sr=SR,lead=LEAD,duration=total,score_source=str(SOURCE),engine='PC-NSF-HiFiGAN 2025.02; same method as Origin 11',roles={'A':'teio','B':'manbo'},notes=[len(n) for n in parts],vibrato_cents=11),ensure_ascii=False,indent=2),encoding='utf-8')
