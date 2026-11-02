from pathlib import Path
import math,json
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial
from trimesh.visual import TextureVisuals
OUT=Path(__file__).parent
scene=trimesh.Scene()
materials={}
for name,col,rough,metal in [('shell','#e2e7f5',.32,.06),('panel','#d7ddec',.42,.02),('trim','#f2f5ff',.28,.04),('blue','#001aff',.25,.12),('gasket','#344053',.65,.05),('recess','#747f95',.48,.1),('steel','#a7b2c8',.3,.55)]:
 rgb=[int(col[i:i+2],16) for i in (1,3,5)]
 materials[name]=PBRMaterial(name=name,baseColorFactor=rgb+[255],metallicFactor=metal,roughnessFactor=rough,emissiveFactor=[0,.016,.12] if name=='blue' else [0,0,0])

def rounded(name,w,d,h,x=0,y=0,z=0,r=.05,b=.01,mat='shell'):
 # Z-up source, exported as glTF Y-up. Rounded plan corners and bevelled top/bottom.
 r=min(r,w/2-.0001,d/2-.0001); b=min(b,h*.48,r*.8)
 verts=[]; rings=[]; seg=7
 # offset of each ring from the largest outer contour
 for inset,zz in [(b,-h/2),(b*(1-math.sin(math.pi/6)),-h/2+b*(1-math.cos(math.pi/6))),(b*(1-math.sin(math.pi/3)),-h/2+b*(1-math.cos(math.pi/3))),(0,-h/2+b),(0,h/2-b),(b*(1-math.sin(math.pi/3)),h/2-b*(1-math.cos(math.pi/3))),(b*(1-math.sin(math.pi/6)),h/2-b*(1-math.cos(math.pi/6))),(b,h/2)]:
  ring=[]
  rr=r-inset
  for cx,cy,a in [(w/2-r,d/2-r,0),(-w/2+r,d/2-r,90),(-w/2+r,-d/2+r,180),(w/2-r,-d/2+r,270)]:
   for k in range(seg+1):
    angle=math.radians(a+90*k/seg)
    ring.append(len(verts));verts.append([cx+rr*math.cos(angle)+x,cy+rr*math.sin(angle)+y,zz+z])
  rings.append(ring)
 faces=[];n=len(rings[0])
 for j in range(len(rings)-1):
  for i in range(n):
   a,c=rings[j][i],rings[j][(i+1)%n];d1,e=rings[j+1][i],rings[j+1][(i+1)%n]
   faces.extend([[a,c,e],[a,e,d1]])
 # Separate cap vertices keep large planar surfaces flat.
 for ri,reverse in [(0,True),(-1,False)]:
  idx=[]
  for vi in rings[ri]:idx.append(len(verts));verts.append(verts[vi])
  center=len(verts);verts.append([x,y,z+(-h/2 if reverse else h/2)])
  for i in range(n):
   f=[center,idx[i],idx[(i+1)%n]];faces.append(f[::-1] if reverse else f)
 mesh=trimesh.Trimesh(vertices=verts,faces=faces,process=False)
 mesh.visual=TextureVisuals(material=materials[mat]);scene.add_geometry(mesh,node_name=name,geom_name=name)
 return mesh

def add(mesh,name,mat):
 mesh.visual=TextureVisuals(material=materials[mat]);scene.add_geometry(mesh,node_name=name,geom_name=name);return mesh

def rod(name,p1,p2,r,mat='steel',sections=24):
 return add(trimesh.creation.cylinder(radius=r,sections=sections,segment=np.array([p1,p2])),name,mat)

materials['blue_light']=PBRMaterial(name='cobalt_blue_light_housing',baseColorFactor=[0,16,255,255],metallicFactor=.08,roughnessFactor=.27,emissiveFactor=[0,.012,.12])
materials['diffuser']=PBRMaterial(name='cool_white_emissive_diffuser',baseColorFactor=[235,247,255,255],metallicFactor=0.,roughnessFactor=.34,emissiveFactor=[.65,.82,1.])
materials['rod_dark']=PBRMaterial(name='graphite_suspension_rods',baseColorFactor=[12,17,29,255],metallicFactor=.55,roughnessFactor=.28)
materials['rod_highlight']=PBRMaterial(name='satin_rod_edge',baseColorFactor=[61,74,96,255],metallicFactor=.65,roughnessFactor=.29)
materials['socket']=PBRMaterial(name='mounting_socket_interior',baseColorFactor=[3,5,9,255],metallicFactor=.10,roughnessFactor=.70)
# Layered capsule-like light body. End radii follow the soft isometric reference.
rounded('bottom_blue_edge',2.752,.532,.028,x=0,y=0,z=.014,r=.235,b=.007,mat='blue_light')
rounded('white_emissive_perimeter_diffuser',2.770,.548,.044,x=0,y=0,z=.050,r=.242,b=.009,mat='diffuser')
rounded('main_blue_light_housing',2.800,.560,.105,x=0,y=0,z=.1245,r=.248,b=.012,mat='blue_light')
rounded('white_top_cover',2.800,.560,.034,x=0,y=0,z=.194,r=.248,b=.010,mat='trim')
rounded('underside_white_diffuser',2.638,.432,.008,x=0,y=0,z=.004,r=.190,b=.002,mat='diffuser')
# Two dark vertical supports connect the light housing and the narrow ceiling bar.
for x,label in [(-1.025,'left'),(1.025,'right')]:
 rod(label+'_lower_socket',[x,0,.207],[x,0,.226],.042,'rod_dark')
 rod(label+'_suspension_rod',[x,0,.221],[x,0,.663],.026,'rod_dark')
 rod(label+'_rod_highlight',[x-.013,-.018,.235],[x-.013,-.018,.650],.006,'rod_highlight',sections=12)
 rod(label+'_upper_socket',[x,0,.647],[x,0,.665],.033,'rod_dark')
# White upper mount with two real recessed fixing slots.
mount=rounded('white_upper_mount',2.420,.144,.060,x=0,y=0,z=.691,r=.023,b=.010,mat='trim')
from shapely.geometry import box
cutters=[]
for x in [-1.025,1.025]:
 r=.009;poly=box(-.042+r,-.021+r,.042-r,.021-r).buffer(r,quad_segs=8)
 c=trimesh.creation.extrude_polygon(poly,height=.06,engine='triangle');c.apply_translation([x,0,.696]);cutters.append(c)
mount=mount.copy();mount.merge_vertices();mount.fix_normals();assert mount.is_watertight
cut=trimesh.boolean.difference([mount,*cutters],engine='manifold')
cut=trimesh.graph.smooth_shade(cut,angle=math.radians(35),facet_minarea=50)
cut.visual=TextureVisuals(material=materials['trim']);_=cut.vertex_normals;scene.geometry['white_upper_mount']=cut
for x,label in [(-1.025,'left'),(1.025,'right')]:
 rounded(label+'_upper_mount_socket_floor',.078,.035,.003,x=x,y=0,z=.707,r=.008,b=.0008,mat='socket')
# Source construction is Z-up; final output matches the prior Y-up components.
rot=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);scene.apply_transform(rot)
shift=np.eye(4);shift[0,3]=-scene.bounds[:,0].mean();shift[1,3]=-scene.bounds[0,1];scene.apply_transform(shift)
for m in scene.geometry.values():_=m.vertex_normals
scene.metadata={'asset':'Nodeworks / 08 Hanging Light','status':'Reference-based reconstruction; not exact 1:1','units':'meter','up_axis':'Y','origin':'bottom-center','animation':False,'light':'emissive material; no scene lights or bloom baked in'}
path=OUT/'08-nodeworks-hanging-light.glb';scene.export(str(path))
s=trimesh.load(path,force='scene')
mount=s.geometry['white_upper_mount'].copy();mount.merge_vertices()
report={'meshes':len(s.geometry),'triangles':sum(len(m.faces) for m in s.geometry.values()),'size_bytes':path.stat().st_size,'dimensions_m':s.extents.tolist(),'bounds':s.bounds.tolist(),'finite_vertices':all(np.isfinite(m.vertices).all() for m in s.geometry.values()),'valid_face_indices':all(m.faces.max()<len(m.vertices) for m in s.geometry.values()),'upper_mount_watertight':bool(mount.is_watertight),'upper_mount_consistent_winding':bool(mount.is_winding_consistent),'diffuser_emissive_factor':s.geometry['white_emissive_perimeter_diffuser'].visual.material.emissiveFactor.tolist(),'recessed_upper_fixing_slots':2}
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
