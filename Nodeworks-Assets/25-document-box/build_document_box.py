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

# Four upright ring binders, cobalt / white / white / cobalt.
materials['cobalt']=PBRMaterial(name='cobalt_binder_cover',baseColorFactor=[0,16,245,255],metallicFactor=.04,roughnessFactor=.38)
materials['white']=PBRMaterial(name='white_binder_cover',baseColorFactor=[236,242,255,255],metallicFactor=.02,roughnessFactor=.45)
materials['paper']=PBRMaterial(name='pale_document_pages',baseColorFactor=[218,227,245,255],metallicFactor=0.,roughnessFactor=.85)
materials['hole']=PBRMaterial(name='dark_finger_hole_interior',baseColorFactor=[3,8,28,255],metallicFactor=0.,roughnessFactor=.9)
materials['metal']=PBRMaterial(name='small_warm_label_plate',baseColorFactor=[112,104,91,255],metallicFactor=.50,roughnessFactor=.35)
for i,(x,h,mat) in enumerate([(.120,.310,'cobalt'),(.040,.318,'white'),(-.040,.326,'white'),(-.120,.334,'cobalt')]):
 name='binder_'+str(i+1)
 rounded(name+'_paper_block',.058,.201,h-.018,x=x,y=-.007,z=h/2,r=.003,b=.002,mat='paper')
 # Two thin stiff cover boards, with softly rounded outer corners.
 for sign,label in [(-1,'left'),(1,'right')]:
  cover=upright(name+'_'+label+'_cover',.226,h,.005,r=.008,b=.0015,mat=mat)
  cover.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2,[0,0,1]));cover.apply_translation([x+sign*.033,0,h/2])
 spine=upright(name+'_spine',.071,h,.016,x=x,y=.108,z=h/2,r=.007,b=.003,mat=mat)
 # Finger pull is a real recessed bore through the spine, backed by a dark interior.
 holes=[(.060,.0115)]
 if mat=='white':holes.append((h-.067,.009))
 cutters=[]
 for j,(z,r) in enumerate(holes):
  cutters.append(trimesh.creation.cylinder(radius=r,sections=28,segment=[[x,.091,z],[x,.129,z]]))
  rod(name+'_hole_interior_'+str(j),[x,.108,z],[x,.109,z],r*.98,'hole',sections=28)
 spine.merge_vertices();spine.fix_normals()
 result=trimesh.boolean.difference([spine]+cutters,engine='manifold')
 result.unmerge_vertices()
 scene.delete_geometry(name+'_spine');add(result,name+'_spine',mat)
 if mat=='cobalt':
  upright(name+'_small_spine_label',.018,.006,.0015,x=x,y=.117,z=h-.055,r=.0015,b=.0004,mat='metal')
 else:
  upright(name+'_label_line',.024,.002,.001,x=x,y=.117,z=h-.100,r=.0005,b=.0002,mat='paper')
 # White index tabs sit on the visible top edge of the outer blue binders.
 if mat=='cobalt':
  rounded(name+'_top_index_label',.024,.119,.0015,x=x,y=-.004,z=h-.006,r=.007,b=.0004,mat='white')
# A broad rectangular index label on the exposed outer face of the first binder.
label=upright('front_blue_binder_side_index',.061,.047,.0015,r=.003,b=.0004,mat='white')
label.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[0,0,1]));label.apply_translation([.1565,-.015,.185])
# Normalize glTF coordinates, Y-up, origin bottom-center.
rot=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);scene.apply_transform(rot)
for mesh in scene.geometry.values():_=mesh.vertex_normals
scene.metadata={'asset':'Nodeworks / 25 Document Box','status':'Reference-based reconstruction; not exact 1:1','units':'meter','up_axis':'Y','origin':'bottom-center','animation':False,'external_textures':False,'includes':'four binders'}
f=OUT/'25-nodeworks-document-box.glb';scene.export(str(f))
s=trimesh.load(f,force='scene');checks={}
for name in s.geometry:
 m=s.geometry[name].copy();m.merge_vertices();checks[name]=bool(m.is_watertight and m.is_winding_consistent)
report={'meshes':len(s.geometry),'triangles':sum(len(m.faces) for m in s.geometry.values()),'size_bytes':f.stat().st_size,'dimensions_m':s.extents.tolist(),'finite_vertices':all(np.isfinite(m.vertices).all() for m in s.geometry.values()),'valid_face_indices':all(m.faces.max()<len(m.vertices) for m in s.geometry.values()),'closed_and_consistent_meshes':checks,'external_textures':False,'animation':False}
assert report['finite_vertices'] and report['valid_face_indices'] and all(checks.values())
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
