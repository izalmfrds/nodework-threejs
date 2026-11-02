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

# Slightly tapered open white cup, with one broad and one thin cobalt band.
materials['white']=PBRMaterial(name='white_cup_body',baseColorFactor=[241,246,255,255],metallicFactor=.01,roughnessFactor=.37)
materials['cobalt']=PBRMaterial(name='cobalt_cup_bands',baseColorFactor=[0,17,255,255],metallicFactor=.04,roughnessFactor=.32)
materials['inside_blue']=PBRMaterial(name='dark_blue_top_inset',baseColorFactor=[0,13,103,255],metallicFactor=.02,roughnessFactor=.39)
def lathe(name,profile,mat):
 mesh=trimesh.creation.revolve(np.array(profile,float),sections=64)
 mesh.fix_normals();return add(mesh,name,mat)
# Closed wall section includes underside, exterior, inner lip and inner bottom.
profile=[(0,0),(.033,0),(.035,.001),(.036,.003),(.0365,.006),(.0447,.120),(.045,.125),(.044,.127),(.041,.127),(.0405,.124),(.0403,.120),(.0323,.010),(.031,.007),(0,.007),(0,0)]
lathe('tapered_white_cup_shell',profile,'white')
def outer_radius(z):return .0365+(z-.006)*(.0447-.0365)/(.120-.006)
for label,z0,z1 in [('wide_upper',.085,.108),('thin_lower',.026,.033)]:
 r0=outer_radius(z0);r1=outer_radius(z1)
 lathe(label+'_cobalt_band',[(r0-.0002,z0),(r0+.00025,z0),(r1+.00025,z1),(r1-.0002,z1),(r0-.0002,z0)],'cobalt')
# Rolled white rim has a softly rounded cross-section and visible inner opening.
angles=np.linspace(0,2*math.pi,17)
lathe('rolled_white_rim',[(.0445+.0040*math.cos(a),.125+.0040*math.sin(a)) for a in angles],'white')
# Blue recessed top surface follows the illustrated reference; no separate lid.
rod('recessed_blue_top_surface',[0,0,.115],[0,0,.116],.0400,'inside_blue',sections=64)
rot=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);scene.apply_transform(rot)
for mesh in scene.geometry.values():_=mesh.vertex_normals
scene.metadata={'asset':'Nodeworks / 26 Coffee Cup','status':'Reference-based reconstruction; not exact 1:1','units':'meter','up_axis':'Y','origin':'bottom-center','animation':False,'external_textures':False}
f=OUT/'26-nodeworks-coffee-cup.glb';scene.export(str(f))
s=trimesh.load(f,force='scene');checks={}
for name in s.geometry:
 m=s.geometry[name].copy();m.merge_vertices();checks[name]=bool(m.is_watertight and m.is_winding_consistent)
report={'meshes':len(s.geometry),'triangles':sum(len(m.faces) for m in s.geometry.values()),'size_bytes':f.stat().st_size,'dimensions_m':s.extents.tolist(),'finite_vertices':all(np.isfinite(m.vertices).all() for m in s.geometry.values()),'valid_face_indices':all(m.faces.max()<len(m.vertices) for m in s.geometry.values()),'closed_and_consistent_meshes':checks,'external_textures':False,'animation':False}
assert report['finite_vertices'] and report['valid_face_indices'] and all(checks.values())
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
