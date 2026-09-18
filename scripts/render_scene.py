"""Self-contained Blender scene; generic demo singers, no private models/textures."""
from pathlib import Path
import bpy, sys, json, math, bisect
from mathutils import Vector

spec = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
job = json.loads(spec.read_text(encoding='utf-8-sig'))
base = spec.parent
out = (base / job['frames']).resolve()
out.mkdir(parents=True, exist_ok=True)
events = json.loads((base / job['mouth_events']).read_text(encoding='utf-8-sig'))
starts = [[p['start'] for p in part] for part in events]
bpy.ops.wm.read_factory_settings(use_empty=True)
s = bpy.context.scene
s.render.engine = 'BLENDER_EEVEE_NEXT'
s.render.resolution_x = job.get('width', 1920)
s.render.resolution_y = job.get('height', 1080)
s.render.resolution_percentage = 100
s.render.film_transparent = True
s.render.image_settings.file_format = 'PNG'
s.render.image_settings.color_mode = 'RGBA'
s.render.image_settings.compression = 5
s.eevee.taa_render_samples = job.get('samples', 16)
s.view_settings.view_transform = 'Standard'
s.world = bpy.data.worlds.new('World')
s.world.use_nodes = True
s.world.node_tree.nodes['Background'].inputs[0].default_value = (.8, .8, .8, 1)
s.world.node_tree.nodes['Background'].inputs[1].default_value = .6

def material(name, color):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = .7
    return m

skin = material('Cream', (.98, .76, .57))
dark = material('Features', (.065, .045, .07))
pink = material('Mouth', (.45, .045, .11))
white = material('Stage', (.92, .92, .97))
colors = [material('A blue', (.18, .45, .88)), material('B purple', (.63, .29, .72))]

def sphere(name, location, scale, mat, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, location=location)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    ob.data.materials.append(mat)
    if parent is not None:
        ob.parent = parent  # coordinates intentionally remain local to the root
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob

roots, mouths, arms = [], [], []
for i, x in enumerate([-1.35, 1.35]):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=1.0, depth=.14, location=(x, 0, .07))
    bpy.context.object.data.materials.append(white)
    root = bpy.data.objects.new(f'Generic singer {i}', None)
    s.collection.objects.link(root)
    root.location = (x, 0, .14)
    roots.append(root)
    sphere('Body', (0, 0, .72), (.40, .29, .49), colors[i], root)
    sphere('Head', (0, 0, 1.58), (.62, .38, .60), skin, root)
    for side in [-1, 1]:
        sphere('Foot', (side*.22, -.035, .12), (.17, .25, .12), colors[i], root)
        sphere('Eye', (side*.21, -.365, 1.68), (.060, .035, .085), dark, root)
    pair = [sphere('Arm', (side*.48, 0, .77), (.13, .16, .36), colors[i], root) for side in [-1, 1]]
    arms.append(pair)
    # Embedded front of head; no floating mouth planes or external UV contracts.
    mouths.append(sphere('Mouth', (0, -.369, 1.39), (.15, .026, .022), pink, root))
    bpy.ops.object.text_add(location=(x, -.85, -.26), rotation=(math.pi/2, 0, 0))
    label = bpy.context.object
    label.data.body = f'{"A" if i == 0 else "B"} - DEMO'
    label.data.align_x = 'CENTER'
    label.data.size = .19
    label.data.materials.append(dark)

bpy.ops.object.camera_add(location=(0, -10, 2.55))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, 0, 1.12))-camera.location).to_track_quat('-Z', 'Y').to_euler()
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 6.4
s.camera = camera
for position, energy, size in [((-3, -4, 6), 500, 5), ((4, -1, 4), 300, 4)]:
    bpy.ops.object.light_add(type='AREA', location=position)
    lamp = bpy.context.object
    lamp.data.energy, lamp.data.shape, lamp.data.size = energy, 'DISK', size
    lamp.rotation_euler = (Vector((0, 0, 1))-lamp.location).to_track_quat('-Z', 'Y').to_euler()

shapes = {'closed': (.15, .026, .018), 'a': (.15, .026, .14),
          'i': (.20, .026, .045), 'u': (.075, .026, .10),
          'e': (.17, .026, .085), 'o': (.10, .026, .12)}
fps = job.get('fps', 30)
for frame in range(math.ceil(job['duration']*fps)):
    t = frame/fps
    sway = math.sin(math.pi*(t-job.get('lead', .13))*job.get('bpm', 100)/60)
    for i, root in enumerate(roots):
        # Rotate about stage-top pivot so the soles never go below the platform.
        root.rotation_euler[1] = .06*sway
        root.location.z = .14 + abs(math.sin(.06*sway))*.4
        for side, arm in zip([-1, 1], arms[i]):
            arm.rotation_euler[1] = side*(.28 + .16*sway)
        j = bisect.bisect_right(starts[i], t)-1
        p = events[i][j] if j >= 0 else None
        vowel = p['vowel'] if p and t < p['end'] else 'closed'
        mouths[i].scale = shapes.get(vowel, shapes['closed'])
    s.render.filepath = str(out/f'{frame:06}.png')
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)
print('RENDER_COMPLETE: procedural demo singers', flush=True)
