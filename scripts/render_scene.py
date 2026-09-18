"""Run with Blender: blender -b -t 4 --python scripts/render_scene.py -- job.json"""
from pathlib import Path
import bpy,sys,json,math,bisect
from mathutils import Quaternion
R=Path(__file__).resolve().parents[1];specfile=Path(sys.argv[sys.argv.index('--')+1]).resolve();job=json.loads(specfile.read_text(encoding='utf-8-sig'));base=specfile.parent
out=(base/job['frames']).resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'assets/private/characters/duo_stage.blend'))
s=bpy.context.scene;fps=job.get('fps',30);s.render.resolution_x=job.get('width',1920);s.render.resolution_y=job.get('height',1080);s.render.resolution_percentage=100;s.render.film_transparent=True;s.eevee.taa_render_samples=job.get('samples',16);s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.compression=5
rigs=[bpy.data.objects[x+' dance rig'] for x in ['teio','manbo']]
nts=[bpy.data.objects[n].data.materials[0].node_tree for n in ['teio_Object_172','manbo_mouth']];offs=[nt.nodes.get('Mouth tile offset') for nt in nts]
stretch=next(l.from_node for l in nts[0].links if l.to_node==offs[0] and l.to_socket==offs[0].inputs[0]);scale=next(l.from_node for l in nts[0].links if l.to_node==stretch and l.to_socket==stretch.inputs[0])
shapes=[((.25,0,0),(1,1,1)),((.5,0,0),(1,1,1)),((.5,.125,0),(1.05,1.15,1)),((.25,.125,0),(1.35,1.25,1)),((.5,0,0),(1.08,1.8,1)),((.25,.125,0),(1,1,1))]
events=json.loads((base/job['mouth_events']).read_text(encoding='utf8'));starts=[[p['start'] for p in ps] for ps in events]
def rotate(b,axis,angle):
 q=b.bone.matrix_local.to_quaternion();b.rotation_mode='QUATERNION';b.rotation_quaternion=q.inverted()@Quaternion(axis,angle)@q
for i in range(math.ceil(job['duration']*fps)):
 t=i/fps;phase=(t-job.get('lead',.13))*job.get('bpm',100)/60;angle=math.pi*phase;sway=math.cos(angle);pulse=math.cos(angle*2)
 for index,rig in enumerate(rigs):
  rig.location=(-1.35 if index==0 else 1.35,0,.012*(1-pulse));rig.rotation_euler=(0,.072*sway,.27*sway)
  for name,b in rig.pose.bones.items():
   b.location=(0,0,0);b.scale=(1,1,1);rotate(b,(0,0,1),0)
   if name=='head':rotate(b,(0,1,0),-.045*sway)
   elif name.startswith('arm'):
    side=1 if name.endswith('L') else -1;rotate(b,(0,1,0),side*(.88+.12*side*sway))
   elif name.startswith('fore'):
    side=1 if name.endswith('L') else -1;rotate(b,(0,0,1),side*(.60+.08*side*sway))
   elif name.startswith('leg'):rotate(b,(0,1,0),-.035*sway)
   elif name=='tail':rotate(b,(0,0,1),-.22*sway)
  j=bisect.bisect_right(starts[index],t)-1;p=events[index][j] if j>=0 else None;v=p['vowel'] if p and t<p['end'] else 'closed'
  if index==0:
   tile,st=shapes[{'a':1,'i':2,'u':3,'e':4,'o':5}.get(v,0)];offs[0].inputs[1].default_value=tile;scale.inputs[1].default_value=st
  else:offs[1].inputs[1].default_value={'a':(.5,0,0),'e':(.5,0,0),'i':(.5,0,0),'o':(.25,-.125,0),'u':(.25,-.125,0)}.get(v,(.25,0,0))
 dest=out/f'{i:06}.png';s.render.filepath=str(dest);bpy.context.view_layer.update();bpy.ops.render.render(write_still=True)
print('RENDER_COMPLETE',flush=True)
