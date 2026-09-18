# 自建角色场景契约：duo_stage.blend

**本仓库不提供 `assets/private/characters/duo_stage.blend`。**

`scripts/render_scene.py` 默认只生成程序化通用演示角色（球体），用于在没有私有素材时验证舞台、动作、嘴型和编码；**它不代表帝宝/曼波的外观**。要渲染真实角色，AI agent 必须自己构建 `duo_stage.blend`。本页给出原始素材、必须满足的对象/骨骼/材质节点契约，以及消费它的渲染器要求。

构建出的场景仍包含第三方模型，**不要提交或分发**（见 THIRD_PARTY.md）。

## 1. 原始素材

按 [assets/DOWNLOAD.txt](../assets/DOWNLOAD.txt) 取得后放到：

```
assets/private/characters/originals/
  tokai_teio_chibi.glb          # 帝宝：glTF，自带骨架，Blender 可直接 import
  manbo_source/
    skin1.max                   # 曼波：3ds Max 格式
    Texture2D/*.png             # 曼波贴图
```

- `tokai_teio_chibi.glb` 直接 `bpy.ops.import_scene.gltf`。它自带一个骨骼名很长的 armature（`_rootJoint`/`Hip_03`…）。
- `skin1.max` **Blender 不能导入**。必须先用 3ds Max 或转换工具导出为 FBX/GLB 再导入；曼波历史上有 UV/重复面问题，导入后要检查。

## 2. 场景必须包含的对象（名字区分大小写，渲染器按名引用）

| 名称 | 类型 | 说明 |
|---|---|---|
| `teio dance rig` | ARMATURE | 帝宝绑定骨架，位于原点附近，11 根骨骼见下 |
| `manbo dance rig` | ARMATURE | 曼波绑定骨架，同上 |
| `teio_Object_169` … `teio_Object_177` | MESH | 帝宝网格，父级 `teio dance rig`，加 Armature 修改器，保留顶点组 |
| `teio_Object_172` | MESH | 帝宝**嘴**（约 100 顶点，材质索引 0 为嘴材质） |
| `manbo_mesh` | MESH | 曼波网格，父级 `manbo dance rig`，Armature 修改器 |
| `manbo_mouth` | MESH | 曼波**嘴**（约 100 顶点，材质索引 0 为嘴材质） |
| `Camera` | CAMERA | 固定正面：`ORTHO`，`ortho_scale≈7.15`，`location=(0,-9,2.65)`，`rotation=(1.4165,0,0)` |
| `Key` / `Fill` | LIGHT | AREA + DISK 补光 |
| `Cream dance pedestal` / `Cream dance pedestal.001` | MESH | 脚下舞台圆台，位置 `(∓1.35, 0, -0.055)` |

骨骼名（两根 rig 相同，均为 11 根）：`root, head, armL, foreL, legL, footL, armR, foreR, legR, footR, tail`。
帝宝 glb 的原始骨骼名不同，需要重命名/重建为上述名字，否则渲染器的 `pose.bones` 驱动会找不到。

- 贴图必须打包进 blend（File → External Data → Pack Resources）。
- 不要放背景图；预览用纯色（默认白）。

## 3. 嘴型材质节点契约（最容易漏）

渲染器通过材质节点名驱动嘴型，必须精确命名：

- 帝宝嘴：`teio_Object_172`.data.materials[0].node_tree 中存在名为 **`Mouth tile offset`** 的节点；它的 `Vector` 输入（输入 0）由一个 Vector Math「拉伸」节点提供；该拉伸节点的输入 0 接 UV，输入 1 是缩放向量。渲染器设置：
  - `Mouth tile offset`.inputs[1] = tile 偏移
  - 拉伸节点.inputs[1] = 缩放向量
- 曼波嘴：`manbo_mouth`.data.materials[0].node_tree 中存在 **`Mouth tile offset`**，其输入 0 接 UV；渲染器设置 `Mouth tile offset`.inputs[1] = tile 偏移。

已验证的取值表：

| vowel | teio tile | teio scale | manbo tile |
|---|---|---|---|
| closed | (.25, 0, 0) | (1, 1, 1) | (.5, 0, 0) |
| a | (.5, 0, 0) | (1, 1, 1) | (.5, 0, 0) |
| i | (.5, .125, 0) | (1.05, 1.15, 1) | (.5, 0, 0) |
| u | (.25, .125, 0) | (1.35, 1.25, 1) | (.25, -.125, 0) |
| e | (.5, 0, 0) | (1.08, 1.8, 1) | (.5, 0, 0) |
| o | (.25, .125, 0) | (1, 1, 1) | (.25, -.125, 0) |

## 4. 消费方（渲染器）契约

当前 `scripts/render_scene.py` 是程序化版本，不会打开 `duo_stage.blend`。构建好场景后，需要一个「打开 blend 并按契约驱动」的渲染器。下面是历史已验证的实现（按当前仓库路径可直接用作 `scripts/render_scene_private.py`，再用 `video.py render` 的同一套 job JSON 调用）：

```python
"""Run with Blender: blender -b -t 4 --python scripts/render_scene_private.py -- job.json"""
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
```

要它可复现：把上面的 `render_scene_private.py` 作为独立文件，或者据此改写 `render_scene.py`，然后仍用 `python scripts/video.py render <job.json> <out.mp4>`（`video.py` 不关心用哪个 Blender 脚本，只负责调 Blender、叠加背景/字幕/音频）。

## 5. 验证清单

- 先生成一小段（3–10 秒）或单帧：脚落在圆台上、嘴随元音开合、嘴上方无黑线、贴图无丢失。
- 骨骼名与嘴型节点名必须与第 2、3 节一致，否则渲染器会 `KeyError`/找不到节点。
- `python scripts/doctor.py` 会提示 `duo_stage.blend` 缺失；这是提示，不阻止程序化视频测试。
- 不要把构建好的 blend 提交到 Git；它含第三方模型。
