from pathlib import Path
import os,json,subprocess,shutil
ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write(path,obj):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')
def config():
 p=ROOT/'config/local.json';return read(p if p.exists() else ROOT/'config/tools.example.json')
def tool(name):return config().get(name,name)
def run(args,**kwargs):return subprocess.run(list(map(str,args)),check=True,**kwargs)
def score_export(src,dest):
 exe=Path(tool('musescore'));env=os.environ.copy()
 for k in list(env):
  if k.upper().startswith(('QT_','QML')):env.pop(k)
 if os.name=='nt':env.update(QT_QPA_PLATFORM='windows',QT_QPA_PLATFORM_PLUGIN_PATH=str(exe.parent/'platforms'),QT_PLUGIN_PATH=str(exe.parent))
 run([exe,'-o',dest,src],env=env,cwd=exe.parent,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
def loudness(path):
 p=subprocess.run([tool('ffmpeg'),'-hide_banner','-i',str(path),'-af','loudnorm=I=-18:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,encoding='utf8',errors='replace',check=True)
 return json.loads(p.stderr[p.stderr.rfind('{'):p.stderr.rfind('}')+1])
