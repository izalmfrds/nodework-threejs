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

materials['table_white']=PBRMaterial(name='satin_white_tabletop',baseColorFactor=[241,244,252,255],metallicFactor=.03,roughnessFactor=.37)
materials['base_dark']=PBRMaterial(name='dark_graphite_table_base',baseColorFactor=[12,17,29,255],metallicFactor=.24,roughnessFactor=.43)
materials['pad_dark']=PBRMaterial(name='black_floor_contact_pad',baseColorFactor=[3,4,7,255],metallicFactor=0.,roughnessFactor=.81)
materials['cube_blue']=PBRMaterial(name='cobalt_blue_table_cube',baseColorFactor=[0,16,255,255],metallicFactor=.04,roughnessFactor=.34)
materials['badge_gray']=PBRMaterial(name='small_gray_badge_center',baseColorFactor=[93,111,145,255],metallicFactor=.08,roughnessFactor=.55)

def disk(name,r,z0,z1,bevel,mat,sections=96):
 b=min(bevel,(z1-z0)*.45,r*.3)
 profile=[[0,z0],[r-b,z0],[r-.5*b,z0+.134*b],[r-.134*b,z0+.5*b],[r,z0+b],[r,z1-b],[r-.134*b,z1-.5*b],[r-.5*b,z1-.134*b],[r-b,z1],[0,z1]]
 mesh=trimesh.creation.revolve(np.array(profile),sections=sections)
 mesh=trimesh.graph.smooth_shade(mesh,angle=math.radians(40),facet_minarea=50)
 return add(mesh,name,mat)
# Low round coffee table with one pedestal and a smaller circular dark base.
disk('black_floor_contact_pad',.344,.0,.010,.003,'pad_dark',sections=80)
disk('dark_round_pedestal_base',.376,.009,.054,.010,'base_dark')
disk('central_dark_support',.055,.050,.375,.007,'base_dark',sections=48)
disk('blue_lower_support_collar',.062,.054,.111,.008,'cube_blue',sections=48)
disk('white_under_table_mount',.127,.343,.375,.008,'table_white',sections=64)
disk('white_circular_tabletop',.610,.365,.430,.014,'table_white',sections=128)
# The small blue cube in the reference remains a separate tabletop object.
rounded('blue_tabletop_cube',.205,.205,.115,x=0,y=0,z=.4875,r=.013,b=.008,mat='cube_blue')
# Small white hexagonal top emblem and a restrained gray center.
badge=trimesh.creation.cylinder(radius=.063,height=.0028,sections=6);badge.apply_translation([0,0,.5470]);add(badge,'cube_white_hexagonal_emblem','trim')
center=trimesh.creation.cylinder(radius=.016,height=.0015,sections=32);center.apply_translation([0,0,.5492]);add(center,'cube_emblem_gray_center','badge_gray')
# Same export coordinates and origin as all prior components.
rot=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);scene.apply_transform(rot)
shift=np.eye(4);shift[0,3]=-scene.bounds[:,0].mean();shift[1,3]=-scene.bounds[0,1];scene.apply_transform(shift)
for mesh in scene.geometry.values():_=mesh.vertex_normals
scene.metadata={'asset':'Nodeworks / 14 Round Table','status':'Reference-based reconstruction; not exact 1:1','units':'meter','up_axis':'Y','origin':'bottom-center','animation':False}
path=OUT/'14-nodeworks-round-table.glb';scene.export(str(path))
s=trimesh.load(path,force='scene');checks={}
for name,mesh in s.geometry.items():
 m=mesh.copy();m.merge_vertices();checks[name]=bool(m.is_watertight and m.is_winding_consistent)
report={'meshes':len(s.geometry),'triangles':sum(len(mesh.faces) for mesh in s.geometry.values()),'size_bytes':path.stat().st_size,'dimensions_m':s.extents.tolist(),'bounds':s.bounds.tolist(),'tabletop_height_m':.430,'tabletop_diameter_m':1.220,'finite_vertices':all(np.isfinite(mesh.vertices).all() for mesh in s.geometry.values()),'valid_face_indices':all(mesh.faces.max()<len(mesh.vertices) for mesh in s.geometry.values()),'closed_and_consistent_meshes':checks,'external_textures':False}
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
