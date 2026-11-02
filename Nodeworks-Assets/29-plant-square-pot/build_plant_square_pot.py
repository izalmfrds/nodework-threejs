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

# White squat square planter with a rosette of broad pointed green leaves.
materials['white']=PBRMaterial(name='white_square_planter',baseColorFactor=[237,243,255,255],metallicFactor=.01,roughnessFactor=.43)
materials['soil']=PBRMaterial(name='dark_potting_soil',baseColorFactor=[16,23,13,255],metallicFactor=0.,roughnessFactor=1.)
materials['cobalt']=PBRMaterial(name='cobalt_corner_badge',baseColorFactor=[0,28,255,255],metallicFactor=.06,roughnessFactor=.34)
materials['label']=PBRMaterial(name='small_gray_pot_label',baseColorFactor=[87,106,145,255],metallicFactor=.05,roughnessFactor=.6)
for i,color in enumerate([[31,118,6,255],[40,145,9,255],[23,94,4,255],[49,154,12,255]]):
 materials['leaf'+str(i)]=PBRMaterial(name='leaf_green_'+str(i),baseColorFactor=color,metallicFactor=0.,roughnessFactor=.63)
outer=rounded('pot_outer',.150,.150,.103,z=.0515,r=.010,b=.004,mat='white')
inner=rounded('pot_cavity',.128,.128,.120,z=.072,r=.006,b=.002,mat='white')
outer.merge_vertices();outer.fix_normals();inner.merge_vertices();inner.fix_normals()
pot=trimesh.boolean.difference([outer,inner],engine='manifold');pot.unmerge_vertices()
scene.delete_geometry('pot_outer');scene.delete_geometry('pot_cavity');add(pot,'hollow_white_square_pot','white')
rounded('recessed_soil',.126,.126,.008,z=.087,r=.005,b=.0015,mat='soil')
# Closed, thin sculpted leaves have a raised midrib and tapered pointed ends.
def leaf(name,angle,reach,rise,width,mat):
 angle=math.radians(angle);direction=np.array([math.cos(angle),math.sin(angle),0.]);side=np.array([-math.sin(angle),math.cos(angle),0.])
 verts=[[direction[0]*.006,direction[1]*.006,.087]];faces=[];rings=[];n=12
 for t in np.linspace(.045,.965,20):
  c=direction*(.006+reach*t**1.50);c[2]=.087+rise*(1-(1-t)**1.25)
  w=width*math.sin(math.pi*t)**1.05;thick=.0009*math.sin(math.pi*t)**.5
  ring=[]
  for j in range(n):
   a=2*math.pi*j/n;v=c+side*w*math.cos(a)
   v[2]+=.0045*math.sin(math.pi*t)*(1-math.cos(a)**2)+thick*math.sin(a)
   ring.append(len(verts));verts.append(v.tolist())
  rings.append(ring)
 for j in range(n):faces.append([0,rings[0][(j+1)%n],rings[0][j]])
 for low,high in zip(rings[:-1],rings[1:]):
  for j in range(n):
   k=(j+1)%n;faces.extend([[low[j],low[k],high[k]],[low[j],high[k],high[j]]])
 tip=direction*(.006+reach);tip[2]=.087+rise;idx=len(verts);verts.append(tip.tolist())
 for j in range(n):faces.append([rings[-1][j],rings[-1][(j+1)%n],idx])
 mesh=trimesh.Trimesh(vertices=verts,faces=faces,process=True);mesh.fix_normals();add(mesh,name,mat)
# Outer leaves spread wider; taller inner leaves form the upright crown.
for i,(a,r,h,w) in enumerate([(15,.132,.129,.024),(81,.119,.142,.026),(147,.130,.124,.026),(214,.126,.133,.024),(282,.125,.123,.025),(47,.074,.195,.024),(126,.067,.191,.026),(202,.069,.179,.023),(291,.061,.180,.023),(337,.040,.148,.025)]):
 leaf('pointed_green_leaf_'+str(i+1),a,r,h,w,'leaf'+str(i%4))
# Small front label and cobalt bumper at the visible bottom corner.
label=upright('small_gray_side_label',.024,.009,.0015,r=.0015,b=.0004,mat='label')
label.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[0,0,1]));label.apply_translation([.0755,.025,.078])
rounded('blue_corner_accent',.024,.024,.020,x=.067,y=.067,z=.010,r=.007,b=.004,mat='cobalt')
rot=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);scene.apply_transform(rot)
for mesh in scene.geometry.values():_=mesh.vertex_normals
scene.metadata={'asset':'Nodeworks / 29 Plant Square Pot','status':'Reference-based reconstruction; not exact 1:1','units':'meter','up_axis':'Y','origin':'bottom-center of pot','animation':False,'external_textures':False}
f=OUT/'29-nodeworks-plant-square-pot.glb';scene.export(str(f))
s=trimesh.load(f,force='scene');checks={}
for name in s.geometry:
 m=s.geometry[name].copy();m.merge_vertices();checks[name]=bool(m.is_watertight and m.is_winding_consistent)
report={'meshes':len(s.geometry),'triangles':sum(len(m.faces) for m in s.geometry.values()),'size_bytes':f.stat().st_size,'dimensions_m':s.extents.tolist(),'finite_vertices':all(np.isfinite(m.vertices).all() for m in s.geometry.values()),'valid_face_indices':all(m.faces.max()<len(m.vertices) for m in s.geometry.values()),'closed_and_consistent_meshes':checks,'external_textures':False,'animation':False}
assert report['finite_vertices'] and report['valid_face_indices'] and all(checks.values())
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
