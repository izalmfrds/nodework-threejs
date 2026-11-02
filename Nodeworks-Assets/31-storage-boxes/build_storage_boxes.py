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

# Two closed office storage boxes: larger cobalt box and smaller white box.
materials['white']=PBRMaterial(name='white_storage_box',baseColorFactor=[235,242,255,255],metallicFactor=.01,roughnessFactor=.45)
materials['cobalt']=PBRMaterial(name='cobalt_storage_box',baseColorFactor=[0,22,255,255],metallicFactor=.03,roughnessFactor=.40)
materials['seam']=PBRMaterial(name='dark_blue_lid_seams',baseColorFactor=[7,17,56,255],metallicFactor=0.,roughnessFactor=.7)
materials['handle']=PBRMaterial(name='dark_recessed_handle',baseColorFactor=[2,6,17,255],metallicFactor=.04,roughnessFactor=.72)
materials['label']=PBRMaterial(name='warm_gray_top_label',baseColorFactor=[133,131,143,255],metallicFactor=.05,roughnessFactor=.65)
for label,x,y,w,d,h,mat in [('blue',.090,-.026,.170,.207,.160,'cobalt'),('white',-.085,.025,.156,.170,.140,'white')]:
 rounded(label+'_box_body',w,d,h-.027,x=x,y=y,z=(h-.027)/2,r=.009,b=.004,mat=mat)
 rounded(label+'_lid_seam',w+.001,d+.001,.0025,x=x,y=y,z=h-.027,r=.009,b=.0008,mat='seam')
 rounded(label+'_overhanging_lid',w+.009,d+.009,.027,x=x,y=y,z=h-.0135,r=.010,b=.003,mat=mat)
 # Finger-pull motifs are inset dark panels on the exposed sides.
 upright(label+'_front_dark_pull',.030,.020,.0015,x=x,y=y+d/2+.0008,z=h-.047,r=.002,b=.0004,mat='handle')
 upright(label+'_front_index_label',.036,.021,.0015,x=x,y=y+d/2+.001,z=h-.073,r=.002,b=.0004,mat='white' if mat=='cobalt' else 'cobalt')
 side=upright(label+'_side_dark_pull',.026,.019,.0015,r=.002,b=.0004,mat='handle')
 side.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[0,0,1]));side.apply_translation([x+w/2+.0008,y+.022,h-.047])
 side_index=upright(label+'_side_index_label',.034,.019,.0015,r=.002,b=.0004,mat='white' if mat=='cobalt' else 'cobalt')
 side_index.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[0,0,1]));side_index.apply_translation([x+w/2+.001,y+.022,h-.073])
 if mat=='cobalt':
  rounded('blue_lid_white_label_border',.070,.029,.0012,x=x,y=y,z=h+.0006,r=.003,b=.0003,mat='white')
  rounded('blue_lid_gray_label_inset',.059,.019,.0013,x=x,y=y,z=h+.0013,r=.002,b=.0003,mat='label')
 else:
  rounded('white_lid_small_gray_mark',.020,.005,.0012,x=x,y=y,z=h+.0006,r=.0015,b=.0003,mat='label')
  upright('white_lid_front_blue_tab',.024,.007,.0012,x=x+.039,y=y+d/2+.005,z=h-.014,r=.002,b=.0003,mat='cobalt')
rot=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);scene.apply_transform(rot)
for mesh in scene.geometry.values():_=mesh.vertex_normals
scene.metadata={'asset':'Nodeworks / 31 Storage Boxes','status':'Reference-based reconstruction; not exact 1:1','units':'meter','up_axis':'Y','origin':'bottom-center of assembly','animation':False,'external_textures':False}
shift=np.eye(4);shift[0,3]=-scene.bounds[:,0].mean();shift[2,3]=-scene.bounds[:,2].mean();scene.apply_transform(shift)
f=OUT/'31-nodeworks-storage-boxes.glb';scene.export(str(f))
s=trimesh.load(f,force='scene');checks={}
for name in s.geometry:
 m=s.geometry[name].copy();m.merge_vertices();checks[name]=bool(m.is_watertight and m.is_winding_consistent)
report={'meshes':len(s.geometry),'triangles':sum(len(m.faces) for m in s.geometry.values()),'size_bytes':f.stat().st_size,'dimensions_m':s.extents.tolist(),'finite_vertices':all(np.isfinite(m.vertices).all() for m in s.geometry.values()),'valid_face_indices':all(m.faces.max()<len(m.vertices) for m in s.geometry.values()),'closed_and_consistent_meshes':checks,'external_textures':False,'animation':False}
assert report['finite_vertices'] and report['valid_face_indices'] and all(checks.values())
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
