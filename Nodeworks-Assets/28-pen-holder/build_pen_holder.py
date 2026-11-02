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

# Open white square stationery holder with rounded edges and a real cavity.
materials['white']=PBRMaterial(name='white_pen_holder',baseColorFactor=[237,243,255,255],metallicFactor=.01,roughnessFactor=.43)
materials['cobalt']=PBRMaterial(name='cobalt_blue_stationery',baseColorFactor=[0,29,255,255],metallicFactor=.03,roughnessFactor=.40)
materials['cyan']=PBRMaterial(name='blue_pen_button',baseColorFactor=[0,99,244,255],metallicFactor=.03,roughnessFactor=.37)
materials['gray']=PBRMaterial(name='graphite_gray_stationery',baseColorFactor=[24,32,51,255],metallicFactor=.06,roughnessFactor=.48)
materials['metal']=PBRMaterial(name='small_metal_pen_tips',baseColorFactor=[111,130,159,255],metallicFactor=.65,roughnessFactor=.30)
outer=rounded('outer_holder',.078,.078,.099,z=.0495,r=.008,b=.0035,mat='white')
inner=rounded('cavity_cutter',.065,.065,.110,z=.062,r=.005,b=.0015,mat='white')
outer.merge_vertices();outer.fix_normals();inner.merge_vertices();inner.fix_normals()
container=trimesh.boolean.difference([outer,inner],engine='manifold')
container.unmerge_vertices()
scene.delete_geometry('outer_holder');scene.delete_geometry('cavity_cutter');add(container,'hollow_white_square_holder','white')
# Four pens stand in the cavity and fan out slightly, as in the reference.
def pen(label,p1,p2,r,mat,button_mat,clip=False):
 p1=np.array(p1,float);p2=np.array(p2,float);axis=p2-p1;axis/=np.linalg.norm(axis)
 rod(label+'_barrel',p1,p2,r,mat,sections=24)
 rod(label+'_top_collar',p2-axis*.006,p2+axis*.001,r*1.03,mat,sections=24)
 rod(label+'_click_button',p2+axis*.001,p2+axis*.005,r*.69,button_mat,sections=24)
 if clip:
  offset=np.array([0.,r*1.03,0.])
  rod(label+'_pocket_clip',p2-axis*.007+offset,p2-axis*.037+offset,r*.18,button_mat,sections=12)
pen('tall_blue_pen',[.009,.001,.015],[.018,.001,.151],.0067,'cobalt','cyan',True)
pen('short_blue_pen',[.019,.018,.014],[.033,.022,.128],.0059,'cobalt','cobalt')
pen('tall_gray_pen',[-.010,-.003,.014],[-.032,-.009,.153],.0061,'gray','metal',True)
pen('rear_gray_pen',[-.009,-.022,.014],[-.014,-.025,.126],.0053,'gray','gray')
rot=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);scene.apply_transform(rot)
for mesh in scene.geometry.values():_=mesh.vertex_normals
scene.metadata={'asset':'Nodeworks / 28 Pen Holder','status':'Reference-based reconstruction; not exact 1:1','units':'meter','up_axis':'Y','origin':'bottom-center','animation':False,'external_textures':False,'includes':['holder','four pens']}
f=OUT/'28-nodeworks-pen-holder.glb';scene.export(str(f))
s=trimesh.load(f,force='scene');checks={}
for name in s.geometry:
 m=s.geometry[name].copy();m.merge_vertices();checks[name]=bool(m.is_watertight and m.is_winding_consistent)
report={'meshes':len(s.geometry),'triangles':sum(len(m.faces) for m in s.geometry.values()),'size_bytes':f.stat().st_size,'dimensions_m':s.extents.tolist(),'finite_vertices':all(np.isfinite(m.vertices).all() for m in s.geometry.values()),'valid_face_indices':all(m.faces.max()<len(m.vertices) for m in s.geometry.values()),'closed_and_consistent_meshes':checks,'external_textures':False,'animation':False}
assert report['finite_vertices'] and report['valid_face_indices'] and all(checks.values())
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
