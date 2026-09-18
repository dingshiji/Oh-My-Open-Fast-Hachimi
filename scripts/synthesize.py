import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import json
KANA=dict(zip('a i u e o ka ki ku ke ko ga gi gu ge go sa shi su se so ta chi tsu te to da de do na ni nu ne no ha hi fu he ho ba bi bu be bo pa pi pu pe po ma mi mu me mo ya yu yo ra ri ru re ro wa ji sho ryo ti n'.split(), 'あ い う え お か き く け こ が ぎ ぐ げ ご さ し す せ そ た ち つ て と だ で ど な に ぬ ね の は ひ ふ へ ほ ば び ぶ べ ぼ ぱ ぴ ぷ ぺ ぽ ま み む め も や ゆ よ ら り る れ ろ わ じ しょ りょ てぃ ん'.split()))
KANA.update(di='でぃ',s='し')
SPLIT={'din':['di','n'],'don':['do','n'],'man':['ma','n'],'sen':['se','n'],'oi':['o','i'],'shii':['shi','i'],'ai':['a','i']}
PRE={'は':.095,'じ':.066,'み':.054,'な':.052,'め':.054,'る':.034,'ど':.042,'あ':.022,'し':.072,'が':.042,'や':.040,'く':.045,'でぃ':.042,'ま':.054,'ぼ':.041,'ん':.020}

KANA.update(ja='じゃ',ju='じゅ',jo='じょ',je='じぇ',cha='ちゃ',chu='ちゅ',cho='ちょ',che='ちぇ',sha='しゃ',shu='しゅ',she='しぇ',fo='ふぉ')
def configure():
 parts=json.loads((W/'notes_lyrics.json').read_text(encoding='utf8'));allunits=[]
 for pi,ns in enumerate(parts):
  bank=['teio','manbo'][pi];index={x['alias']:x for x in json.loads((ROOT/f'assets/private/metadata/{bank}_oto.json').read_text(encoding='utf8'))};units=[]
  for idx,n in enumerate(ns):
   ph=n['phonemes'];a=n['start'];b=n['end'];dur=b-a
   if dur<.09 and len(ph)>2:ph=[ph[0],ph[-1]]
   if len(ph)==1:bounds=[a,b]
   elif ph[-1]=='n':
    tail=min(.045,max(.012,dur*.18));remaining=dur-tail
    bounds=[a+remaining*j/(len(ph)-1) for j in range(len(ph))]+[b]
   else:bounds=[a+dur*j/len(ph) for j in range(len(ph)+1)]
   for j,tok in enumerate(ph):
    start,end=bounds[j:j+2];prev=units[-1] if units else None;continuous=prev is not None and start-prev['end']<.04
    prevlen=prev['end']-prev['start'] if continuous else .15
    kana=KANA[tok];pre=min(PRE.get(kana,.04),prevlen*.20,(end-start)*.30)
    units.append(dict(note=idx,start=start,end=end,pitch=n['pitch'],kana=kana,token=tok,pre_target=pre,continuous=continuous))
  vowel='-'
  for p in units:
   if not p['continuous']:vowel='-'
   suf='C5' if p['pitch']>=72 else 'G4' if p['pitch']>=63 else 'B3'
   candidates=[f'{vowel} {p["kana"]}{suf}',f'- {p["kana"]}{suf}',f'{p["kana"]}{suf}']
   alias=next((x for x in candidates if x in index),None)
   if alias is None and p['token']=='fo':
    p['kana']='ふ';p['token']='fu';alias=next(x for x in [f'{vowel} ふ{suf}',f'- ふ{suf}'] if x in index)
   assert alias,candidates
   p['alias']=alias;p['record']=index[alias];vowel='n' if p['token']=='n' else p['token'][-1]
  allunits.append(units);print('PHONEMES',bank,len(units),flush=True)
 (W/'phonemes.json').write_text(json.dumps(allunits,ensure_ascii=False,indent=2),encoding='utf8')
def main():
 import argparse,copy
 import vcv_engine as engine
 global W,O
 p=argparse.ArgumentParser();p.add_argument('notes');p.add_argument('output');a=p.parse_args()
 O=Path(a.output).resolve();O.mkdir(parents=True,exist_ok=True);W=O/'work';W.mkdir(exist_ok=True)
 parts=read(a.notes);assert len(parts)==2 and any(parts),'Need exactly two parts, at least one nonempty'
 for ns in parts:
  for n in ns:
   assert n['end']>n['start'] and 0<=n['pitch']<=127
   tok=n.get('lyric','a');n.setdefault('bar',1)
   if 'phonemes' not in n:
    if tok in SPLIT:n['phonemes']=SPLIT[tok]
    elif tok in KANA:n['phonemes']=[tok]
    elif tok.endswith('n') and tok[:-1] in KANA:n['phonemes']=[tok[:-1],'n']
    else:raise ValueError('Unsupported token '+tok+'; edit phonemes explicitly (Japanese romanization)')
  assert all(x['end']<=y['start']+.001 for x,y in zip(ns,ns[1:])),'Overlapping or unsorted notes'
 write(W/'notes_lyrics.json',parts);configure();engine.WORK=W;engine.OUT=O;engine.SOURCE=Path(a.notes).resolve();engine.render()
if __name__=='__main__':main()
