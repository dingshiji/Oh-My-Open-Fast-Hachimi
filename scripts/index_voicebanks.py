import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
def main():
 for bank in ['teio','manbo']:
  root=ROOT/'assets/private/voicebanks'/bank;records=[]
  for path in sorted(root.rglob('oto.ini')):
   raw=path.read_bytes()
   for enc in ['utf-8-sig','cp932','gb18030']:
    try:text=raw.decode(enc);break
    except UnicodeDecodeError:continue
   else:raise ValueError('Cannot decode '+str(path))
   for line in text.splitlines():
    if '=' not in line:continue
    wav,tail=line.split('=',1);values=tail.split(',')
    if len(values)!=6:continue
    alias=values[0] or Path(wav).stem
    for v in values[1:]:float(v)
    assert (path.parent/wav).exists()
    records.append(dict(folder=str(path.parent.relative_to(root)),wav=wav,alias=alias,params=values[1:]))
  assert records;write(ROOT/f'assets/private/metadata/{bank}_oto.json',records);print(bank,len(records))
if __name__=='__main__':main()
