import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import argparse,math
def mouths(a):
 parts=read(a.input);out=[]
 for ps in parts:
  events=[]
  for p in ps:
   start=p['start']+a.lead;end=p['end']+a.lead;tok=p['token'];v='closed' if tok=='n' else tok[-1]
   if tok.startswith(('m','b','p')):
    events.append(dict(start=start,end=min(end,start+.025),vowel='closed'));start+=.025
   if end>start:events.append(dict(start=start,end=end,vowel=v if v in 'aiueo' else 'closed'))
  out.append(events)
 write(a.output,out)
def captions(a):
 lines=read(a.input)
 def stamp(t):
  cs=round(t*100);return f'{cs//360000}:{cs//6000%60:02}:{cs//100%60:02}.{cs%100:02}'
 header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Microsoft YaHei,46,&H00FFFFFF,&H00FFFFFF,&H00352A3E,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,2,40,40,55,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
 rows=[]
 for l in lines:
  assert l['end']>l['start']>=0;txt=l['text'].replace('\n',r'\N').replace('{','').replace('}','');rows.append(f"Dialogue: 0,{stamp(l['start'])},{stamp(l['end'])},Default,,0,0,0,,{txt}")
 Path(a.output).write_text(header+'\n'.join(rows),encoding='utf-8-sig')
def validate_job(job, base):
 for name, default in [('duration',0),('fps',30),('width',1920),('height',1080),('bpm',100)]:
  value=job.get(name,default)
  if not isinstance(value,(int,float)) or not math.isfinite(value) or value<=0:
   raise ValueError(f'{name} must be finite and positive')
 for name in ['width','height']:
  value=job.get(name,1920 if name=='width' else 1080)
  if int(value)!=value or value%2:raise ValueError(f'{name} must be an even integer')
 for name in ['audio','mouth_events','background','subtitles']:
  if name in ['audio','mouth_events'] or job.get(name):
   if not (base/job[name]).is_file():raise FileNotFoundError(base/job[name])
 parts=read(base/job['mouth_events'])
 if len(parts)!=2:raise ValueError('mouth_events must contain two parts')
 for events in parts:
  end=0
  for e in events:
   a,b=e['start'],e['end']
   if not (math.isfinite(a) and math.isfinite(b) and a>=end and b>a):
    raise ValueError('Mouth events must be finite, ordered, and non-overlapping')
   if e['vowel'] not in ('a','i','u','e','o','closed'):raise ValueError('Unknown mouth vowel')
   end=b

def render(a):
 spec=Path(a.spec).resolve();job=read(spec);base=spec.parent
 validate_job(job, base)
 Path(a.output).resolve().parent.mkdir(parents=True,exist_ok=True)
 run([tool('blender'),'-b','--python-exit-code','1','-t','4','--python',ROOT/'scripts/render_scene.py','--',spec])
 frames=base/job['frames'];audio=base/job['audio'];dest=Path(a.output).resolve();w=job.get('width',1920);h=job.get('height',1080);fps=job.get('fps',30)
 # Solid color is generated at runtime; no inherited wallpaper or background asset.
 cmd=[tool('ffmpeg'),'-v','warning','-y','-framerate',fps,'-i',frames/'%06d.png']
 if job.get('background'):cmd+=['-loop','1','-framerate',fps,'-i',base/job['background']]
 else:cmd+=['-f','lavfi','-i',f"color=c={job.get('color','white')}:s={w}x{h}:r={fps}"]
 cmd+=['-i',audio];filt=f'[1:v]scale={w}:{h}[bg];[bg][0:v]overlay=shortest=1'
 if job.get('subtitles'):
  # Use a safe local basename in cwd, avoiding Windows drive/colon escaping.
  sub=base/job['subtitles'];local=base/'render_subtitles.ass'
  if sub.resolve()!=local.resolve():shutil.copyfile(sub,local)
  filt+=",ass=render_subtitles.ass"
 fade=job.get('fade_out',.8)
 if fade:filt+=f",fade=t=out:st={max(0,job['duration']-fade)}:d={fade}"
 filt+=',format=yuv420p[v]';cmd+=['-filter_complex',filt,'-map','[v]','-map','2:a','-c:v',job.get('encoder','libx264'),'-c:a','aac','-b:a','256k','-t',job['duration'],'-movflags','+faststart',dest];run(cmd,cwd=base)
 run([tool('ffmpeg'),'-v','error','-i',dest,'-f','null','-']);write(str(dest)+'.json',dict(decode='PASS',job=job))
if __name__=='__main__':
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
 for c in ['mouths','captions','render']:
  q=sub.add_parser(c);q.add_argument('spec' if c=='render' else 'input');q.add_argument('output')
  if c=='mouths':q.add_argument('--lead',type=float,default=.13)
 a=p.parse_args();globals()[a.command](a)
