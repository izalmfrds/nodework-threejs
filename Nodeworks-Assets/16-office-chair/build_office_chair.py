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

materials['seat_white']=PBRMaterial(name='soft_white_chair_cushions',baseColorFactor=[242,246,253,255],metallicFactor=0.,roughnessFactor=.75)
materials['frame_white']=PBRMaterial(name='white_chair_frame',baseColorFactor=[223,232,248,255],metallicFactor=.15,roughnessFactor=.38)
materials['chair_blue']=PBRMaterial(name='cobalt_blue_chair_trim',baseColorFactor=[0,17,255,255],metallicFactor=.04,roughnessFactor=.35)
materials['mechanism']=PBRMaterial(name='dark_chair_mechanism',baseColorFactor=[7,10,18,255],metallicFactor=.25,roughnessFactor=.47)
materials['tire']=PBRMaterial(name='black_caster_tires',baseColorFactor=[3,4,7,255],metallicFactor=.02,roughnessFactor=.64)
materials['hub_gray']=PBRMaterial(name='dark_caster_hub',baseColorFactor=[27,34,49,255],metallicFactor=.30,roughnessFactor=.42)

def fillet_path(points,r=.03):
 pts=[np.array(p,float) for p in points];out=[pts[0]]
 for i in range(1,len(pts)-1):
  a,p,b=pts[i-1],pts[i],pts[i+1];u=a-p;v=b-p;rr=min(r,np.linalg.norm(u)*.25,np.linalg.norm(v)*.25)
  start=p+u/np.linalg.norm(u)*rr;end=p+v/np.linalg.norm(v)*rr
  for t in np.linspace(0,1,8):out.append((1-t)**2*start+2*(1-t)*t*p+t*t*end)
 out.append(pts[-1]);return np.array(out)

def arm_tube(name,path,rx,ry,mat):
 path=np.array(path);verts=[];faces=[];n=12
 for i,p in enumerate(path):
  tangent=path[min(i+1,len(path)-1)]-path[max(i-1,0)];tangent/=np.linalg.norm(tangent)
  normal=np.array([1.,0,0]);side=np.cross(tangent,normal);side/=np.linalg.norm(side)
  for k in range(n):
   a=2*math.pi*k/n;verts.append(p+rx*math.cos(a)*normal+ry*math.sin(a)*side)
 for i in range(len(path)-1):
  for k in range(n):
   a=i*n+k;b=i*n+(k+1)%n;c=(i+1)*n+k;d=(i+1)*n+(k+1)%n;faces.extend([[a,b,d],[a,d,c]])
 for idx,reverse in [(0,True),(len(path)-1,False)]:
  center=len(verts);verts.append(path[idx]);offset=idx*n
  for k in range(n):
   f=[center,offset+k,offset+(k+1)%n];faces.append(f[::-1] if reverse else f)
 mesh=trimesh.Trimesh(verts,faces,process=True);mesh.fix_normals();return add(mesh,name,mat)

# Dark under-seat shell and softly rounded seat cushion.
rounded('dark_underseat_shell',.535,.502,.031,x=0,y=-.020,z=.4395,r=.082,b=.010,mat='mechanism')
soft_cushion('white_seat_cushion',.530,.500,.078,x=0,y=-.020,z=.494,e1=.30,e2=.28,mat='seat_white')
# Blue-edged reclining backrest with white padding on its front.
back=upright('blue_backrest_shell',.500,.493,.041,r=.073,b=.012,mat='chair_blue')
back_transform=trimesh.transformations.rotation_matrix(math.radians(-8),[1,0,0]);back_transform[:3,3]=[0,.264,.796];back.apply_transform(back_transform)
soft_cushion('white_backrest_cushion',.470,.076,.456,x=0,y=.231,z=.799,e1=.31,e2=.29,tilt_x=-8,mat='seat_white')
back_support=upright('blue_lower_back_support',.142,.158,.047,r=.023,b=.008,mat='chair_blue')
back_support.apply_transform(trimesh.transformations.rotation_matrix(math.radians(-9),[1,0,0]));back_support.apply_translation([0,.240,.535])
# Paired white U-shaped arm supports and hooked blue upper pads.
for x,label in [(-.309,'left'),(.309,'right')]:
 p=fillet_path([[x,.177,.674],[x,.177,.512],[x,.120,.478],[x,-.123,.478],[x,-.197,.516],[x,-.197,.664]],r=.040)
 arm_tube(label+'_white_arm_support',p,.014,.014,'frame_white')
 p=[[x,.210,.698],[x,-.170,.698]]
 for a in np.linspace(math.pi/2,math.pi,13)[1:]:p.append([x,-.170+.040*math.cos(a),.658+.040*math.sin(a)])
 p.append([x,-.210,.632]);arm_tube(label+'_blue_armrest_pad',p,.029,.020,'chair_blue')
# Height-adjustment column and the center of the five-point base.
rod('dark_underseat_mount',[0,0,.382],[0,0,.430],.062,'mechanism')
rod('dark_height_adjustment_sleeve',[0,0,.205],[0,0,.404],.034,'mechanism')
rod('lower_chrome_column',[0,0,.135],[0,0,.263],.025,'steel')
rod('white_base_center_hub',[0,0,.123],[0,0,.177],.064,'frame_white')
# Five radial white spokes and five twin-wheel caster assemblies.
for i in range(5):
 angle=math.radians(-90+72*i);radial=np.array([math.cos(angle),math.sin(angle),0]);tangent=np.array([-math.sin(angle),math.cos(angle),0])
 spoke=rounded('base_spoke_'+str(i+1),.278,.052,.037,r=.014,b=.008,mat='frame_white')
 t=trimesh.transformations.rotation_matrix(angle,[0,0,1])@trimesh.transformations.rotation_matrix(math.radians(9),[0,1,0]);t[:3,3]=radial*.168+np.array([0,0,.137]);spoke.apply_transform(t)
 center=radial*.305+np.array([0,0,.043]);stem_center=radial*.305
 rod('caster_'+str(i+1)+'_stem',stem_center+[0,0,.070],stem_center+[0,0,.127],.012,'mechanism',sections=16)
 fork=rounded('caster_'+str(i+1)+'_housing',.057,.041,.036,r=.010,b=.007,mat='mechanism')
 rz=trimesh.transformations.rotation_matrix(angle,[0,0,1]);rz[:3,3]=radial*.305+np.array([0,0,.070]);fork.apply_transform(rz)
 wheels=[];hubs=[]
 for sign in [-1,1]:
  wc=center+tangent*(sign*.017)
  wheels.append(trimesh.creation.cylinder(radius=.043,sections=24,segment=[wc-tangent*.010,wc+tangent*.010]))
  hc=center+tangent*(sign*.028)
  hubs.append(trimesh.creation.cylinder(radius=.019,sections=20,segment=[hc-tangent*.001,hc+tangent*.001]))
 tire_mesh=trimesh.util.concatenate(wheels);tire_mesh=trimesh.graph.smooth_shade(tire_mesh,angle=math.radians(35),facet_minarea=50);add(tire_mesh,'caster_'+str(i+1)+'_twin_wheels','tire')
 hub_mesh=trimesh.util.concatenate(hubs);hub_mesh=trimesh.graph.smooth_shade(hub_mesh,angle=math.radians(35),facet_minarea=50);add(hub_mesh,'caster_'+str(i+1)+'_hub_caps','hub_gray')
# Subtle side adjustment lever below the seat, without extra decorative parts.
rod('seat_adjustment_lever',[.10,-.005,.411],[.215,-.005,.411],.007,'mechanism',sections=12)
rounded('seat_adjustment_handle',.053,.027,.017,x=.224,y=-.005,z=.411,r=.009,b=.005,mat='mechanism')
# Export Y-up, meter units, and a bottom-center origin.
rot=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);scene.apply_transform(rot)
shift=np.eye(4);shift[0,3]=-scene.bounds[:,0].mean();shift[1,3]=-scene.bounds[0,1];scene.apply_transform(shift)
for mesh in scene.geometry.values():_=mesh.vertex_normals
scene.metadata={'asset':'Nodeworks / 16 Office Chair','status':'Reference-based reconstruction; not exact 1:1','units':'meter','up_axis':'Y','origin':'bottom-center','animation':False}
path=OUT/'16-nodeworks-office-chair.glb';scene.export(str(path))
s=trimesh.load(path,force='scene');checks={}
for name in ['white_seat_cushion','white_backrest_cushion','blue_backrest_shell','left_white_arm_support','left_blue_armrest_pad','base_spoke_1','caster_1_twin_wheels']:
 mesh=s.geometry[name].copy();mesh.merge_vertices();checks[name]=bool(mesh.is_watertight and mesh.is_winding_consistent)
report={'meshes':len(s.geometry),'triangles':sum(len(mesh.faces) for mesh in s.geometry.values()),'size_bytes':path.stat().st_size,'dimensions_m':s.extents.tolist(),'bounds':s.bounds.tolist(),'finite_vertices':all(np.isfinite(mesh.vertices).all() for mesh in s.geometry.values()),'valid_face_indices':all(mesh.faces.max()<len(mesh.vertices) for mesh in s.geometry.values()),'closed_and_consistent_meshes':checks,'base_spokes':5,'casters':5,'wheels':10,'external_textures':False}
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
