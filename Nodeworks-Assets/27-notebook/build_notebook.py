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

# Closed notebook with pale cover, dark lower cover and a cobalt elastic strap.
materials['white']=PBRMaterial(name='white_notebook_cover',baseColorFactor=[236,242,255,255],metallicFactor=.01,roughnessFactor=.46)
materials['paper']=PBRMaterial(name='pale_notebook_pages',baseColorFactor=[206,218,240,255],metallicFactor=0.,roughnessFactor=.85)
materials['page_line']=PBRMaterial(name='page_edge_seams',baseColorFactor=[121,137,166,255],metallicFactor=0.,roughnessFactor=.85)
materials['dark']=PBRMaterial(name='dark_navy_bottom_cover',baseColorFactor=[7,12,25,255],metallicFactor=.03,roughnessFactor=.53)
materials['cobalt']=PBRMaterial(name='cobalt_elastic_strap',baseColorFactor=[0,32,255,255],metallicFactor=0.,roughnessFactor=.56)
rounded('dark_bottom_cover',.216,.157,.004,x=0,y=0,z=.0045,r=.012,b=.0013,mat='dark')
rounded('pale_page_block',.209,.150,.015,x=0,y=0,z=.014,r=.009,b=.002,mat='paper')
# Fine stacked page edges are shallow inset lines on the exposed front edge.
for i,z in enumerate([.0105,.0140,.0175]):
 rounded('page_edge_line_'+str(i),.185,.00045,.00025,x=0,y=.07515,z=z,r=.00015,b=.00005,mat='page_line')
rounded('white_top_cover',.216,.157,.005,x=0,y=0,z=.023,r=.012,b=.0018,mat='white')
rounded('white_bound_spine',.212,.007,.020,x=0,y=-.075,z=.015,r=.003,b=.002,mat='white')
# Continuous rectangular loop: the elastic crosses top, both ends and underside.
from shapely.geometry import box
core=box(-.075,-.0075,.075,.0075)
outer=core.buffer(.0065,quad_segs=8);inner=core.buffer(.0040,quad_segs=8)
loop=trimesh.creation.extrude_polygon(outer.difference(inner),height=.014,engine='triangle')
transform=np.array([[0,0,1,-.073],[1,0,0,0],[0,1,0,.014],[0,0,0,1]],float)
loop.apply_transform(transform);loop.fix_normals();add(loop,'continuous_blue_elastic_band','cobalt')
rot=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);scene.apply_transform(rot)
for mesh in scene.geometry.values():_=mesh.vertex_normals
scene.metadata={'asset':'Nodeworks / 27 Notebook','status':'Reference-based reconstruction; not exact 1:1','units':'meter','up_axis':'Y','origin':'bottom-center','animation':False,'external_textures':False}
f=OUT/'27-nodeworks-notebook.glb';scene.export(str(f))
s=trimesh.load(f,force='scene');checks={}
for name in s.geometry:
 m=s.geometry[name].copy();m.merge_vertices();checks[name]=bool(m.is_watertight and m.is_winding_consistent)
report={'meshes':len(s.geometry),'triangles':sum(len(m.faces) for m in s.geometry.values()),'size_bytes':f.stat().st_size,'dimensions_m':s.extents.tolist(),'finite_vertices':all(np.isfinite(m.vertices).all() for m in s.geometry.values()),'valid_face_indices':all(m.faces.max()<len(m.vertices) for m in s.geometry.values()),'closed_and_consistent_meshes':checks,'external_textures':False,'animation':False}
assert report['finite_vertices'] and report['valid_face_indices'] and all(checks.values())
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
