"""Optional Muscriptor upload. Explicit per-task consent required, recorded locally."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import argparse,base64
def main():
 p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('output');p.add_argument('--voice',action='store_true');p.add_argument('--consent',required=True,help='Path to task-specific JSON consent record');a=p.parse_args()
 consent=read(a.consent);src=Path(a.input).resolve();site='https://muscriptor.kyutai.org'
 import hashlib
 digest=hashlib.sha256(src.read_bytes()).hexdigest()
 assert consent.get('site')==site and consent.get('sha256')==digest and consent.get('user_approved') is True,'Consent must match exact file and destination'
 import requests
 session=requests.Session();proxy=config().get('proxy')
 if proxy:session.proxies={'http':proxy,'https':proxy}
 data={'detect_tempo':'false'}
 if a.voice:data['instruments']='voice'
 with src.open('rb') as f:
  response=session.post(site+'/transcribe',files={'file':(src.name,f,'audio/wav')},data=data,stream=True,timeout=(30,300));response.raise_for_status()
  for line in response.iter_lines():
   if line.startswith(b'data: '):
    event=json.loads(line[6:])
    if event.get('type')=='transcription_complete':Path(a.output).write_bytes(base64.b64decode(event['data']));return
 raise RuntimeError('No MIDI received; API may have changed. Inspect service before retrying.')
if __name__=='__main__':main()
