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

materials['upholstery']=PBRMaterial(name='soft_white_upholstery',baseColorFactor=[236,240,249,255],metallicFactor=0.,roughnessFactor=.78)
materials['cushion_white']=PBRMaterial(name='white_seat_and_back_cushions',baseColorFactor=[245,247,253,255],metallicFactor=0.,roughnessFactor=.80)
materials['pillow_blue']=PBRMaterial(name='cobalt_blue_throw_pillow',baseColorFactor=[0,22,255,255],metallicFactor=0.,roughnessFactor=.76)
materials['piping_blue']=PBRMaterial(name='blue_pillow_edge_seam',baseColorFactor=[0,6,98,255],metallicFactor=0.,roughnessFactor=.82)
materials['wood']=PBRMaterial(name='dark_brown_wooden_feet',baseColorFactor=[37,18,7,255],metallicFactor=0.,roughnessFactor=.65)
materials['foot_pad']=PBRMaterial(name='black_foot_pads',baseColorFactor=[3,4,6,255],metallicFactor=0.,roughnessFactor=.83)

def signed_power(x,e):return np.sign(x)*np.abs(x)**e

def soft_cushion(name,w,d,h,x,y,z,e1=.30,e2=.30,tilt_x=0,tilt_y=0,mat='cushion_white'):
 # Low-resolution superellipsoid concentrates shape in rounded corners and soft bulges.
 verts=[];faces=[];nu=40;nv=20
 for j in range(nv+1):
  v=-math.pi/2+math.pi*j/nv
  cv=0. if j in (0,nv) else math.cos(v)
  for i in range(nu):
   u=2*math.pi*i/nu
   verts.append([w/2*signed_power(cv,e1)*signed_power(math.cos(u),e2),d/2*signed_power(cv,e1)*signed_power(math.sin(u),e2),h/2*signed_power(math.sin(v),e1)])
 for j in range(nv):
  for i in range(nu):
   a=j*nu+i;b=j*nu+(i+1)%nu;c=(j+1)*nu+i;dd=(j+1)*nu+(i+1)%nu
   faces.extend([[a,b,dd],[a,dd,c]])
 mesh=trimesh.Trimesh(verts,faces,process=True);mesh.update_faces(mesh.nondegenerate_faces());mesh.remove_unreferenced_vertices();mesh.fix_normals()
 t=trimesh.transformations.rotation_matrix(math.radians(tilt_y),[0,1,0])@trimesh.transformations.rotation_matrix(math.radians(tilt_x),[1,0,0]);t[:3,3]=[x,y,z];mesh.apply_transform(t)
 return add(mesh,name,mat),t

# Four short dark brown feet, including a discreet black contact pad.
for x,label in [(-.835,'left'),(.835,'right')]:
 for y,side in [(-.325,'front'),(.325,'rear')]:
  rounded(label+'_'+side+'_wooden_foot',.132,.132,.083,x=x,y=y,z=.0485,r=.018,b=.008,mat='wood')
  rounded(label+'_'+side+'_foot_pad',.130,.130,.012,x=x,y=y,z=.006,r=.017,b=.003,mat='foot_pad')
# Thick lower rail, back support and rectangular padded arms.
rounded('lower_upholstered_base',1.770,.788,.166,x=0,y=0,z=.205,r=.057,b=.030,mat='upholstery')
rounded('rear_upholstered_support',1.575,.158,.677,x=0,y=.313,z=.6365,r=.055,b=.041,mat='upholstery')
for x,label in [(-.883,'left'),(.883,'right')]:
 rounded(label+'_padded_armrest',.225,.880,.540,x=x,y=0,z=.407,r=.048,b=.038,mat='upholstery')
# Separate seat and back cushions preserve the central seams in the reference.
for x,label in [(-.389,'left'),(.389,'right')]:
 soft_cushion(label+'_seat_cushion',.762,.648,.163,x=x,y=-.038,z=.357,e1=.29,e2=.25)
 soft_cushion(label+'_back_cushion',.772,.177,.574,x=x,y=.249,z=.717,e1=.29,e2=.27,tilt_x=-8)
# One blue throw pillow on the right seat, lightly tilted and resting on the back.
pillow,transform=soft_cushion('blue_throw_pillow',.398,.131,.429,x=.418,y=.104,z=.631,e1=.38,e2=.34,tilt_x=-13,tilt_y=-6,mat='pillow_blue')
# A single thin blue seam mesh follows the pillow perimeter.
verts=[];faces=[];n=64;kmax=6;path=[]
for i in range(n):
 a=2*math.pi*i/n
 path.append(np.array([.195*signed_power(math.cos(a),.34),-.040,.211*signed_power(math.sin(a),.34)]))
for i,p in enumerate(path):
 tangent=path[(i+1)%n]-path[(i-1)%n];tangent/=np.linalg.norm(tangent)
 normal=np.array([0,-1,0]);side=np.cross(tangent,normal);side/=np.linalg.norm(side)
 for k in range(kmax):
  a=2*math.pi*k/kmax;verts.append(p+.0025*(math.cos(a)*normal+math.sin(a)*side))
for i in range(n):
 for k in range(kmax):
  a=i*kmax+k;b=i*kmax+(k+1)%kmax;c=((i+1)%n)*kmax+k;d=((i+1)%n)*kmax+(k+1)%kmax
  faces.extend([[a,b,d],[a,d,c]])
seam=trimesh.Trimesh(verts,faces,process=True);seam.fix_normals();seam.apply_transform(transform);add(seam,'blue_pillow_edge_seam','piping_blue')
# Y-up export with bottom-center origin, matching all prior components.
rot=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);scene.apply_transform(rot)
shift=np.eye(4);shift[0,3]=-scene.bounds[:,0].mean();shift[1,3]=-scene.bounds[0,1];scene.apply_transform(shift)
for mesh in scene.geometry.values():_=mesh.vertex_normals
scene.metadata={'asset':'Nodeworks / 13 Sofa','status':'Reference-based reconstruction; not exact 1:1','units':'meter','up_axis':'Y','origin':'bottom-center','animation':False}
path=OUT/'13-nodeworks-sofa.glb';scene.export(str(path))
s=trimesh.load(path,force='scene');checks={}
for name in ['lower_upholstered_base','left_padded_armrest','right_padded_armrest','left_seat_cushion','right_seat_cushion','left_back_cushion','right_back_cushion','blue_throw_pillow']:
 mesh=s.geometry[name].copy();mesh.merge_vertices();mesh.remove_unreferenced_vertices();checks[name]=bool(mesh.is_watertight and mesh.is_winding_consistent)
report={'meshes':len(s.geometry),'triangles':sum(len(mesh.faces) for mesh in s.geometry.values()),'size_bytes':path.stat().st_size,'dimensions_m':s.extents.tolist(),'bounds':s.bounds.tolist(),'finite_vertices':all(np.isfinite(mesh.vertices).all() for mesh in s.geometry.values()),'valid_face_indices':all(mesh.faces.max()<len(mesh.vertices) for mesh in s.geometry.values()),'closed_and_consistent_meshes':checks,'seat_cushions':2,'back_cushions':2,'throw_pillows':1,'external_textures':False}
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
