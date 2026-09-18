"""MusicXML/MuseScore to canonical seconds-based two-part note events, or back."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import argparse
def extract(a):
 from music21 import converter,note,chord
 source=Path(a.input).resolve();xml=source
 if source.suffix.lower()=='.mscz':
  xml=Path(a.output).resolve().with_suffix('.musicxml');score_export(source,xml)
 score=converter.parse(str(xml));parts=[]
 if len(score.parts)!=2:raise ValueError('Expected exactly two monophonic parts: teio, manbo')
 # Merge explicit ties in seconds, including intermediate ties across barlines.
 for part in score.parts:
  ns=[];last_vowel='a';tie_open=False
  for row in part.flatten().secondsMap:
   n=row['element']
   if isinstance(n,chord.Chord):raise ValueError('Polyphonic chord: choose one sung pitch before synthesis')
   if not isinstance(n,note.Note):continue
   kind=n.tie.type if n.tie else None
   if kind in ('continue','stop'):
    if not ns or not tie_open or ns[-1]['pitch']!=n.pitch.midi or abs(ns[-1]['end']-row['offsetSeconds'])>.002:raise ValueError('Orphan/noncontiguous tie; inspect score')
    ns[-1]['end']=row['offsetSeconds']+row['durationSeconds'];tie_open=kind=='continue';continue
   token=n.lyric
   if token is None:token=last_vowel
   for char in reversed(token):
    if char in 'aiueo':last_vowel=char;break
   ns.append(dict(start=row['offsetSeconds'],end=row['offsetSeconds']+row['durationSeconds'],pitch=n.pitch.midi,lyric=token,bar=n.measureNumber or 1))
   tie_open=kind=='start'
  ns.sort(key=lambda n:n['start'])
  if any(x['end']>y['start']+.002 for x,y in zip(ns,ns[1:])):raise ValueError('Part has overlapping voices; resolve in score first')
  parts.append(ns)
 write(a.output,parts)
def build(a):
 from music21 import stream,note,meter,tempo,instrument,metadata
 import math
 parts=read(a.input);s=stream.Score();s.metadata=metadata.Metadata(title=a.title);beat=60/a.bpm
 bar_length=meter.TimeSignature(a.meter).barDuration.quarterLength
 total=math.ceil(max(n['end'] for ns in parts for n in ns)/beat/bar_length)*bar_length
 for pi,ns in enumerate(parts):
  p=stream.Part();p.partName=['teio','manbo'][pi];p.insert(0,instrument.Piano());p.insert(0,meter.TimeSignature(a.meter));p.insert(0,tempo.MetronomeMark(number=a.bpm));cursor=0
  for n in ns:
   start=round(n['start']/beat*8)/8;end=max(start+.125,round(n['end']/beat*8)/8);start=max(cursor,start)
   if end<=start:raise ValueError('Quantization collides with note; inspect rhythm manually')
   if start>cursor:p.insert(cursor,note.Rest(quarterLength=start-cursor))
   nn=note.Note(n['pitch'],quarterLength=end-start);nn.lyric=n.get('lyric');p.insert(start,nn);cursor=end
  if cursor<total:p.insert(cursor,note.Rest(quarterLength=total-cursor))
  p.makeMeasures(inPlace=True);p.makeTies(inPlace=True);s.insert(0,p)
 path=Path(a.output).resolve();xml=path.with_suffix('.musicxml');s.write('musicxml',fp=xml)
 if path.suffix=='.mscz':score_export(xml,path)
def export(a):score_export(Path(a.input).resolve(),Path(a.output).resolve())
if __name__=='__main__':
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
 for c in ['extract','build','export']:
  q=sub.add_parser(c);q.add_argument('input');q.add_argument('output')
  if c=='build':q.add_argument('--bpm',type=float,required=True);q.add_argument('--meter',default='4/4');q.add_argument('--title',default='双人哈基米')
 a=p.parse_args();globals()[a.command](a)
