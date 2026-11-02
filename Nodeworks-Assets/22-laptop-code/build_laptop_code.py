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

def upright(name,w,h,depth,x=0,y=0,z=0,r=.04,b=.008,mat='shell'):
 mesh=rounded(name,w,h,depth,r=r,b=b,mat=mat)
 transform=np.array([[1,0,0,x],[0,0,-1,y],[0,1,0,z],[0,0,0,1]],dtype=float)
 mesh.apply_transform(transform)
 return mesh

def ellipsoid(name,center,radii,mat,sub=2,rotation=None):
 mesh=trimesh.creation.icosphere(subdivisions=sub,radius=1)
 mesh.apply_scale(radii)
 if rotation is not None:mesh.apply_transform(rotation)
 mesh.apply_translation(center);return add(mesh,name,mat)

# Laptop body, keyboard and screen: part of this complete reference component.
materials['eyes']=PBRMaterial(name='webcam',baseColorFactor=[1,2,5,255],metallicFactor=0.,roughnessFactor=.7)
materials['code_pink']=PBRMaterial(name='pink_status',baseColorFactor=[242,110,186,255],metallicFactor=0.,roughnessFactor=.6,emissiveFactor=[.16,.03,.08])
materials['laptop_shell']=PBRMaterial(name='graphite_laptop_shell',baseColorFactor=[62,75,105,255],metallicFactor=.20,roughnessFactor=.39)
materials['bezel']=PBRMaterial(name='dark_graphite_screen_frame',baseColorFactor=[9,14,25,255],metallicFactor=.12,roughnessFactor=.42)
materials['keyboard']=PBRMaterial(name='dark_laptop_keys',baseColorFactor=[5,8,14,255],metallicFactor=.03,roughnessFactor=.60)
materials['screen']=PBRMaterial(name='navy_code_screen',baseColorFactor=[2,12,38,255],metallicFactor=0.,roughnessFactor=.55,emissiveFactor=[.008,.025,.065])
materials['code_white']=PBRMaterial(name='pale_code_lines',baseColorFactor=[216,240,255,255],metallicFactor=0.,roughnessFactor=.65,emissiveFactor=[.10,.15,.20])
materials['code_cyan']=PBRMaterial(name='cyan_code_accent',baseColorFactor=[3,133,240,255],metallicFactor=0.,roughnessFactor=.55,emissiveFactor=[0,.12,.20])
rounded('laptop_base',.642,.430,.024,x=0,y=-.590,z=.830,r=.024,b=.006,mat='laptop_shell')
keys=[]
for row in range(5):
 for col in range(11):
  key=trimesh.creation.box(extents=[.040,.023,.003]);key.apply_translation([(col-5)*.049,-.731+row*.031,.844]);keys.append(key)
space=trimesh.creation.box(extents=[.245,.022,.003]);space.apply_translation([0,-.559,.844]);keys.append(space)
add(trimesh.util.concatenate(keys),'laptop_keyboard_keys','keyboard')
rounded('laptop_trackpad_border',.168,.078,.002,x=0,y=-.463,z=.843,r=.009,b=.0006,mat='gasket')
rounded('laptop_trackpad_face',.157,.067,.002,x=0,y=-.463,z=.844,r=.007,b=.0006,mat='laptop_shell')
rod('laptop_hinge',[-.292,-.795,.842],[.292,-.795,.842],.011,'laptop_shell',sections=24)
screen_before=set(scene.geometry)
upright('laptop_screen_frame',.642,.405,.024,x=0,y=-.795,z=1.047,r=.021,b=.006,mat='bezel')
upright('laptop_code_display',.592,.347,.003,x=0,y=-.781,z=1.047,r=.010,b=.0008,mat='screen')
# The small display uses geometric placeholder strokes, matching the visible code motif.
upright('code_header_accent',.174,.007,.0015,x=.169,y=-.778,z=1.201,r=.002,b=.0004,mat='code_cyan')
for i,(x,w) in enumerate([(-.161,.115),(-.109,.197),(-.091,.232),(-.126,.163),(-.095,.225),(-.139,.137),(-.109,.197)]):
 upright('code_line_'+str(i+1),w,.006,.0015,x=-x,y=-.778,z=1.168-i*.030,r=.002,b=.0004,mat='code_white')
upright('code_bottom_accent',.215,.009,.0015,x=.140,y=-.778,z=.943,r=.002,b=.0004,mat='code_cyan')
upright('code_status_line',.078,.006,.0015,x=-.196,y=-.778,z=.942,r=.002,b=.0004,mat='code_white')
upright('code_status_pink',.039,.006,.0015,x=-.133,y=-.778,z=.942,r=.002,b=.0004,mat='code_pink')
ellipsoid('laptop_webcam',[0,-.780,1.238],[.003,.0015,.003],'eyes',sub=1)
screen_tilt=trimesh.transformations.rotation_matrix(math.radians(12),[1,0,0],point=[0,-.795,.842])
for name in set(scene.geometry)-screen_before:scene.geometry[name].apply_transform(screen_tilt)

# Normalize to a compact 34 cm laptop in glTF Y-up coordinates.
for mesh in scene.geometry.values():
 mesh.apply_translation([0,.590,-.818]);mesh.apply_scale(.53)
rot=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);scene.apply_transform(rot)
shift=np.eye(4);shift[0,3]=-scene.bounds[:,0].mean();shift[1,3]=-scene.bounds[0,1];shift[2,3]=-scene.bounds[:,2].mean();scene.apply_transform(shift)
for mesh in scene.geometry.values():_=mesh.vertex_normals
scene.metadata={'asset':'Nodeworks / 22 Laptop Code','status':'Reference-based reconstruction; not exact 1:1','units':'meter','up_axis':'Y','origin':'bottom-center','animation':False,'external_textures':False}
f=OUT/'22-nodeworks-laptop-code.glb';scene.export(str(f))
s=trimesh.load(f,force='scene');checks={}
for name in ['laptop_base','laptop_screen_frame','laptop_trackpad_border']:
 m=s.geometry[name].copy();m.merge_vertices();checks[name]=bool(m.is_watertight and m.is_winding_consistent)
report={'meshes':len(s.geometry),'triangles':sum(len(m.faces) for m in s.geometry.values()),'size_bytes':f.stat().st_size,'dimensions_m':s.extents.tolist(),'finite_vertices':all(np.isfinite(m.vertices).all() for m in s.geometry.values()),'valid_face_indices':all(m.faces.max()<len(m.vertices) for m in s.geometry.values()),'closed_and_consistent_meshes':checks,'external_textures':False,'animation':False}
assert report['finite_vertices'] and report['valid_face_indices'] and all(checks.values())
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
