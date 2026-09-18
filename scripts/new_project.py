import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import argparse,re
p=argparse.ArgumentParser();p.add_argument('name');a=p.parse_args();assert re.fullmatch(r'[\w-]+',a.name),'Use letters, digits, underscore, hyphen'
root=ROOT/'projects'/a.name
if root.exists():raise SystemExit('Project already exists; do not overwrite. Choose another name.')
root.mkdir(parents=True);(ROOT/'output'/a.name).mkdir(parents=True,exist_ok=True)
(root/'STATE.md').write_text('# '+a.name+'\n\nSource: pending\nSelected range: pending\nLatest user score: pending\nCurrent step: source inspection\nUpload authorization: none\nNext reviewable artifact: stems\n',encoding='utf8')
write(root/'task.json',dict(title=a.name,source='source.mp4',start=0,duration=None,roles={'A':'teio','B':'manbo'},background=None,subtitles='Chinese',upload_authorized=False));print(root)
