"""Extract / separate / mix. All timestamps in seconds; audio is processed locally."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import argparse
def extract(a):
 args=[tool('ffmpeg'),'-v','error','-y']
 if a.start:args+=['-ss',a.start]
 args+=['-i',a.input]
 if a.duration:args+=['-t',a.duration]
 run(args+['-vn','-ar','44100','-ac','2','-c:a','pcm_s24le',a.output])
def separate(a):
 import torch,numpy as np,soundfile as sf
 from demucs.pretrained import get_model
 from demucs.apply import apply_model
 torch.set_num_threads(4);torch.hub.set_dir(str(ROOT/'models/torch/hub'))
 m=get_model('htdemucs_6s').eval();out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
 with sf.SoundFile(a.input) as source:
  sr=source.samplerate;assert sr==44100 and source.channels==2,'Run extract first (44.1 kHz stereo)'
  n=len(source);files={s:sf.SoundFile(str(out/(s+'.wav')),'w',sr,2,subtype='FLOAT') for s in m.sources}
  try:
   step=90*sr;pad=2*sr
   for start in range(0,n,step):
    end=min(n,start+step);lo=max(0,start-pad);hi=min(n,end+pad);source.seek(lo);x=torch.from_numpy(source.read(hi-lo,dtype='float32').T);ref=x.mean(0);mean=ref.mean();std=ref.std().clamp(min=1e-6)
    with torch.inference_mode():z=apply_model(m,((x-mean)/std)[None],device=a.device,shifts=2,overlap=.25,progress=False)[0].cpu()*std+mean
    for i,s in enumerate(m.sources):files[s].write(z[i,:,start-lo:end-lo].numpy().T)
    print('SEPARATED',end/sr,'/',n/sr,flush=True)
  finally:
   for f in files.values():f.close()
 import numpy as np
 for names,name in [(['drums','bass','other','guitar','piano'],'instrumental'),(['other','guitar','piano'],'melody_instruments'),(['drums','bass'],'drums_bass')]:
  # Float WAV preserves reconstruction headroom, no per-stem clipping.
  y=sum(sf.read(out/(s+'.wav'),dtype='float32')[0] for s in names);sf.write(out/(name+'.wav'),y,sr,subtype='FLOAT')
 write(out/'separation.json',dict(model='htdemucs_6s',duration=n/sr,shifts=2,device=a.device))
def mix(a):
 import numpy as np,soundfile as sf
 spec=read(a.spec);base=Path(a.spec).resolve().parent;sr=44100;n=round(spec['duration']*sr);y=np.zeros((n,2),np.float32)
 for t in spec['tracks']:
  path=(base/t['file']).resolve();z,s=sf.read(path,dtype='float32',always_2d=True);assert s==sr
  if 'target_lufs' in t:z*=10**((t['target_lufs']-float(loudness(path)['input_i']))/20)
  z*=t.get('gain',1);z=z[round(t.get('trim_start',0)*sr):]
  if z.shape[1]==1:
   ang=(1+t.get('pan',0))*np.pi/4;z=z*np.array([np.cos(ang),np.sin(ang)])
  offset=round(t.get('offset',0)*sr);lo=max(0,offset);hi=min(n,offset+len(z))
  if hi>lo:y[lo:hi]+=z[lo-offset:hi-offset]
 peak=float(np.max(abs(y)));y*=min(1,.92/max(peak,1e-9));fade=spec.get('fade_out',1.8)
 if fade:y*=np.minimum(1,np.arange(n)[::-1]/sr/fade)[:,None]
 assert np.isfinite(y).all();sf.write(a.output,y,sr,subtype='PCM_24');write(str(a.output)+'.json',dict(duration=n/sr,peak=float(np.max(abs(y))),mix=spec))
if __name__=='__main__':
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
 e=sub.add_parser('extract');e.add_argument('input');e.add_argument('output');e.add_argument('--start',type=float,default=0);e.add_argument('--duration',type=float)
 e=sub.add_parser('separate');e.add_argument('input');e.add_argument('output');e.add_argument('--device',default='cuda')
 e=sub.add_parser('mix');e.add_argument('spec');e.add_argument('output');a=p.parse_args();globals()[a.command](a)
