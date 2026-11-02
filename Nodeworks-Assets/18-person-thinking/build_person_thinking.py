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

materials['skin']=PBRMaterial(name='warm_peach_skin',baseColorFactor=[214,133,85,255],metallicFactor=0.,roughnessFactor=.71)
materials['skin_detail']=PBRMaterial(name='warm_skin_detail',baseColorFactor=[162,83,47,255],metallicFactor=0.,roughnessFactor=.77)
materials['shirt']=PBRMaterial(name='white_button_down_shirt',baseColorFactor=[232,239,252,255],metallicFactor=0.,roughnessFactor=.78)
materials['pants']=PBRMaterial(name='charcoal_navy_trousers',baseColorFactor=[17,24,39,255],metallicFactor=0.,roughnessFactor=.83)
materials['hair']=PBRMaterial(name='dark_swept_hair',baseColorFactor=[5,8,16,255],metallicFactor=0.,roughnessFactor=.56)
materials['eyes']=PBRMaterial(name='dark_eyes_and_brows',baseColorFactor=[2,2,4,255],metallicFactor=0.,roughnessFactor=.65)
materials['mouth']=PBRMaterial(name='soft_smile',baseColorFactor=[89,32,16,255],metallicFactor=0.,roughnessFactor=.78)
materials['shoe']=PBRMaterial(name='light_gray_shoes',baseColorFactor=[183,196,219,255],metallicFactor=0.,roughnessFactor=.72)
materials['sole']=PBRMaterial(name='dark_shoe_soles_and_belt',baseColorFactor=[4,6,11,255],metallicFactor=0.,roughnessFactor=.82)
materials['badge']=PBRMaterial(name='small_cobalt_chest_badge',baseColorFactor=[0,18,255,255],metallicFactor=0.,roughnessFactor=.47)

def ellipsoid(name,center,radii,mat,sub=2,rotation=None):
 mesh=trimesh.creation.icosphere(subdivisions=sub,radius=1)
 mesh.apply_scale(radii)
 if rotation is not None:mesh.apply_transform(rotation)
 mesh.apply_translation(center);return add(mesh,name,mat)

def limb(name,points,radii,mat,n=20):
 points=np.array(points,float);radii=np.array(radii,float)
 if len(points)>2:
  from scipy.interpolate import PchipInterpolator
  distance=np.r_[0.,np.cumsum(np.linalg.norm(np.diff(points,axis=0),axis=1))]
  samples=np.linspace(0,distance[-1],max(10,len(points)*4))
  points=PchipInterpolator(distance,points,axis=0)(samples);radii=np.interp(samples,distance,radii)
 verts=[];faces=[]
 for i,(p,r) in enumerate(zip(points,radii)):
  tangent=points[min(i+1,len(points)-1)]-points[max(i-1,0)];tangent/=np.linalg.norm(tangent)
  ref=np.array([0.,1,0]) if abs(tangent[1])<.9 else np.array([1.,0,0])
  a=np.cross(tangent,ref);a/=np.linalg.norm(a);b=np.cross(tangent,a)
  for k in range(n):
   t=2*math.pi*k/n;verts.append(p+r*(math.cos(t)*a+math.sin(t)*b))
 for i in range(len(points)-1):
  for k in range(n):
   a=i*n+k;b=i*n+(k+1)%n;c=(i+1)*n+k;d=(i+1)*n+(k+1)%n;faces.extend([[a,b,d],[a,d,c]])
 for idx,flip in [(0,True),(len(points)-1,False)]:
  c=len(verts);verts.append(points[idx])
  for k in range(n):
   f=[c,idx*n+k,idx*n+(k+1)%n];faces.append(f[::-1] if flip else f)
 mesh=trimesh.Trimesh(verts,faces,process=True);mesh.fix_normals();return add(mesh,name,mat)

def body_loft(name,rings,mat,n=32):
 verts=[];faces=[]
 for z,x,y,rx,ry in rings:
  for k in range(n):
   a=2*math.pi*k/n;verts.append([x+rx*signed_power(math.cos(a),.65),y+ry*signed_power(math.sin(a),.65),z])
 for i in range(len(rings)-1):
  for k in range(n):
   a=i*n+k;b=i*n+(k+1)%n;c=(i+1)*n+k;d=(i+1)*n+(k+1)%n;faces.extend([[a,b,d],[a,d,c]])
 for idx,flip in [(0,True),(len(rings)-1,False)]:
  z,x,y,_,_=rings[idx];c=len(verts);verts.append([x,y,z])
  for k in range(n):
   f=[c,idx*n+k,idx*n+(k+1)%n];faces.append(f[::-1] if flip else f)
 mesh=trimesh.Trimesh(verts,faces,process=True);mesh.fix_normals();return add(mesh,name,mat)

# Light gray rounded shoes and dark thin soles, in a relaxed standing stance.
for x,label,angle in [(-.100,'left',5),(.112,'right',-5)]:
 sole=rounded(label+'_shoe_sole',.145,.245,.018,r=.045,b=.006,mat='sole')
 rz=trimesh.transformations.rotation_matrix(math.radians(angle),[0,0,1]);sole.apply_transform(rz);sole.apply_translation([x,-.047,.012])
 shoe,_=soft_cushion(label+'_shoe_upper',.143,.240,.078,x=0,y=0,z=0,e1=.34,e2=.36,mat='shoe');shoe.apply_transform(rz);shoe.apply_translation([x,-.047,.061])
 ellipsoid(label+'_ankle',[x,.012,.123],[.051,.055,.037],'shoe')
# Straight tapered trouser legs, with a small natural separation below the pelvis.
body_loft('left_trouser_leg',[(.139,-.100,0,.059,.065),(.20,-.099,0,.062,.068),(.39,-.094,.003,.068,.076),(.57,-.084,.006,.074,.080),(.785,-.078,0,.080,.089)],'pants')
body_loft('right_trouser_leg',[(.139,.112,.005,.059,.065),(.20,.109,.005,.062,.068),(.39,.100,.007,.068,.076),(.57,.085,.006,.074,.080),(.785,.078,0,.080,.089)],'pants')
body_loft('trouser_pelvis',[(.705,0,.018,.118,.066),(.750,0,.013,.150,.078),(.786,0,.004,.150,.089)],'pants')
rounded('dark_waist_belt',.306,.196,.032,x=0,y=0,z=.787,r=.046,b=.006,mat='sole')
upright('small_belt_buckle',.043,.023,.005,x=.008,y=-.101,z=.787,r=.004,b=.001,mat='steel')
# White fitted shirt, neck, collar flaps and quiet front buttons.
body_loft('white_shirt_torso',[(.794,0,0,.146,.089),(.824,0,0,.151,.093),(.94,0,.002,.161,.097),(1.065,0,.006,.179,.102),(1.125,0,.007,.181,.094),(1.163,0,.007,.129,.079)],'shirt')
rod('neck',[0,.008,1.135],[0,.008,1.253],.045,'skin',sections=32)
from shapely.geometry import Polygon
for side,label in [(-1,'left'),(1,'right')]:
 poly=Polygon([(side*.011,1.156),(side*.059,1.208),(side*.082,1.153),(side*.049,1.115)])
 mesh=trimesh.creation.extrude_polygon(poly,height=.009,engine='triangle');t=np.array([[1,0,0,0],[0,0,-1,-.082],[0,1,0,0],[0,0,0,1]],float);mesh.apply_transform(t);add(mesh,label+'_shirt_collar','shirt')
for z,k in [(1.087,1),(1.004,2),(.922,3),(.842,4)]:ellipsoid('shirt_button_'+str(k),[0,-.099,z],[.004,.003,.004],'trim',sub=1)
upright('blue_chest_badge',.031,.037,.004,x=.074,y=-.102,z=1.085,r=.006,b=.001,mat='badge')
ellipsoid('badge_white_mark',[.074,-.106,1.085],[.007,.0018,.008],'trim',sub=1)
# Left elbow bent outward, with a small hand resting against the waist.
limb('left_upper_shirt_sleeve',[[-.165,.003,1.105],[-.218,-.005,1.035],[-.284,-.015,.953]],[.060,.054,.049],'shirt')
ellipsoid('left_sleeve_elbow',[-.284,-.015,.953],[.050,.049,.052],'shirt')
limb('left_lower_shirt_sleeve',[[-.284,-.015,.953],[-.244,-.065,.909],[-.177,-.121,.858]],[.048,.044,.035],'shirt')
limb('left_white_cuff',[[-.184,-.115,.864],[-.166,-.130,.850]],[.036,.035],'trim')
ellipsoid('left_waist_hand',[-.142,-.145,.841],[.038,.025,.041],'skin')
for i in range(4):
 z=.858-i*.014
 limb('left_hand_finger_'+str(i+1),[[-.156,-.160,z],[-.127,-.171,z-.006],[-.109,-.157,z-.012]],[.009,.0085,.007],'skin',n=12)
ellipsoid('left_hand_thumb',[-.166,-.154,.865],[.016,.012,.024],'skin')
# Right elbow lowered and forearm lifted toward the chin.
limb('right_upper_shirt_sleeve',[[.165,.003,1.105],[.218,-.003,1.046],[.259,-.047,1.005]],[.060,.053,.048],'shirt')
ellipsoid('right_sleeve_elbow',[.259,-.047,1.005],[.049,.047,.051],'shirt')
limb('right_lifted_forearm_sleeve',[[.259,-.047,1.005],[.223,-.092,1.092],[.151,-.139,1.218]],[.047,.043,.033],'shirt')
limb('right_white_cuff',[[.156,-.136,1.209],[.141,-.146,1.231]],[.035,.033],'trim')
ellipsoid('right_thinking_hand',[.111,-.157,1.257],[.034,.024,.044],'skin')
for i in range(3):
 x=.085+i*.014
 limb('right_curled_finger_'+str(i+1),[[x,-.164,1.263],[x-.004,-.146,1.295],[x-.011,-.133,1.313-i*.005]],[.0095,.009,.0075],'skin',n=12)
limb('right_hand_thumb',[[.135,-.160,1.243],[.113,-.180,1.257],[.090,-.171,1.269]],[.012,.011,.009],'skin',n=12)
# Stylized head and facial details, turned a little toward the thinking hand.
head_names=set(scene.geometry)
head,_=soft_cushion('peach_head',.292,.250,.351,x=0,y=.002,z=1.387,e1=.67,e2=.74,mat='skin')
# A gently tapered lower jaw avoids a perfectly spherical head.
for v in head.vertices:
 if v[2]<1.36:v[0]*=(.86+.14*np.clip((v[2]-1.211)/.149,0,1))
for x,label in [(-.145,'left'),(.145,'right')]:
 ellipsoid(label+'_ear',[x,.005,1.378],[.027,.022,.041],'skin')
 ellipsoid(label+'_inner_ear',[x,-.014,1.378],[.014,.006,.025],'skin_detail')
for x,label in [(-.044,'left'),(.044,'right')]:
 ellipsoid(label+'_eye_white',[x,-.122,1.408],[.010,.003,.020],'trim')
 ellipsoid(label+'_eye',[x+.002,-.127,1.407],[.0085,.004,.017],'eyes')
 ellipsoid(label+'_eye_glint',[x,-.131,1.415],[.0024,.001,.003],'trim',sub=1)
 limb(label+'_eyebrow',[[x-.019,-.114,1.458],[x-.001,-.119,1.464],[x+.017,-.115,1.460]],[.0065,.007,.006],'hair',n=12)
ellipsoid('small_rounded_nose',[.004,-.139,1.361],[.020,.022,.016],'skin')
limb('gentle_smile',[[-.027,-.114,1.317],[-.010,-.123,1.308],[.010,-.123,1.307],[.029,-.114,1.315]],[.003,.0035,.0035,.0025],'mouth',n=10)
# Dark swept hair: rear mass, temples, crown and a broad swept front lock.
ellipsoid('hair_rear_mass',[0,.063,1.449],[.151,.080,.139],'hair',sub=3)
ellipsoid('hair_crown',[-.018,.017,1.565],[.152,.119,.075],'hair',sub=3)
ellipsoid('hair_left_temple',[-.128,-.005,1.460],[.034,.083,.092],'hair',sub=3)
ellipsoid('hair_right_temple',[.128,.005,1.474],[.029,.074,.073],'hair',sub=2)
rotlock=trimesh.transformations.rotation_matrix(math.radians(-10),[0,1,0])
ellipsoid('hair_swept_front_lock',[.024,-.062,1.572],[.137,.078,.047],'hair',sub=3,rotation=rotlock)
ellipsoid('hair_swept_tip',[.116,-.015,1.592],[.041,.060,.047],'hair',sub=2,rotation=rotlock)
# Join the overlapping hair masses into one continuous sculpted surface.
hair_parts=[name for name in scene.geometry if name.startswith('hair_')]
hair_mesh=trimesh.boolean.union([scene.geometry[name].copy() for name in hair_parts],engine='manifold')
for name in hair_parts:scene.delete_geometry(name)
add(hair_mesh,'swept_dark_hairstyle','hair')
# Rotate only head components around the neck, leaving the pose unchanged.
head_rotation=trimesh.transformations.rotation_matrix(math.radians(12),[0,0,1],point=[0,.008,1.25])
for name in set(scene.geometry)-head_names:scene.geometry[name].apply_transform(head_rotation)
# Y-up and bottom-center output. This is a posed mesh, without a skeleton.
rot=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);scene.apply_transform(rot)
shift=np.eye(4);shift[0,3]=-scene.bounds[:,0].mean();shift[1,3]=-scene.bounds[0,1];scene.apply_transform(shift)
for mesh in scene.geometry.values():_=mesh.vertex_normals
scene.metadata={'asset':'Nodeworks / 18 Person Thinking','status':'Reference-based stylized reconstruction; not exact 1:1','units':'meter','up_axis':'Y','origin':'bottom-center','animation':False,'rigged':False}
file=OUT/'18-nodeworks-person-thinking.glb';scene.export(str(file))
s=trimesh.load(file,force='scene');checks={}
for name in ['peach_head','white_shirt_torso','left_trouser_leg','right_trouser_leg','left_shoe_upper','right_shoe_upper','right_thinking_hand']:
 m=s.geometry[name].copy();m.merge_vertices();checks[name]=bool(m.is_watertight and m.is_winding_consistent)
report={'meshes':len(s.geometry),'triangles':sum(len(mesh.faces) for mesh in s.geometry.values()),'size_bytes':file.stat().st_size,'dimensions_m':s.extents.tolist(),'bounds':s.bounds.tolist(),'finite_vertices':all(np.isfinite(mesh.vertices).all() for mesh in s.geometry.values()),'valid_face_indices':all(mesh.faces.max()<len(mesh.vertices) for mesh in s.geometry.values()),'closed_and_consistent_meshes':checks,'pose':'static thinking pose','rigged':False,'external_textures':False}
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
