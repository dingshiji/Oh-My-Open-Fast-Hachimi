import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import importlib.util,argparse
def main():
 p=argparse.ArgumentParser();p.add_argument('--scope',choices=['all','video'],default='all');a=p.parse_args()
 failed=[]
 for n in (['ffmpeg','ffprobe','blender'] if a.scope=='video' else ['ffmpeg','ffprobe','blender','musescore']):
  p=tool(n);ok=Path(p).is_file() or shutil.which(p) is not None;print(n,'OK' if ok else 'MISSING',p)
  if not ok:failed.append(n)
 if a.scope=='video':
  if failed:raise SystemExit('Missing video tools: '+', '.join(failed))
  scene=ROOT/'assets/private/characters/duo_stage.blend'
  print('duo_stage.blend', 'OK' if scene.exists() else 'MISSING (real characters need a self-built scene; see docs/SCENE_CONTRACT.md)')
  print('Video OK: procedural demo scene; no private character assets required');return
 required=['assets/private/metadata/teio_oto.json','assets/private/metadata/manbo_oto.json','assets/private/voicebanks/teio','assets/private/voicebanks/manbo']
 for name in required:
  ok=(ROOT/name).exists();print(name,'OK' if ok else 'MISSING')
  if not ok:failed.append(name)
 for name in ['numpy','scipy','soundfile','music21','torch','demucs']:
  print('Python',name,'available' if importlib.util.find_spec(name) else 'not in this interpreter (CPU/GPU environments may be separate)')
 print('HifiSampler util:',(Path(config()['hifisampler'])/'util/nsf_hifigan.py').is_file())
 print('Vocoder model:',bool(list((ROOT/'models/pc_nsf_hifigan').rglob('model.ckpt'))))
 scene=ROOT/'assets/private/characters/duo_stage.blend'
 print('duo_stage.blend','OK' if scene.exists() else 'MISSING (procedural demo only; build your own for real characters, see docs/SCENE_CONTRACT.md)')
 if failed:raise SystemExit('Missing assets/tools: '+', '.join(failed))
if __name__=='__main__':main()
