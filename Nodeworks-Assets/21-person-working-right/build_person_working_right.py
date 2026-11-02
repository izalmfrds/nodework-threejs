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

# Reuse the exported chair, retaining its real geometry and material definitions.
chair=trimesh.load(OUT/'16-nodeworks-office-chair.glb',force='scene')
to_z=trimesh.transformations.rotation_matrix(math.pi/2,[1,0,0])
for node in chair.graph.nodes_geometry:
 matrix,g=chair.graph[node];mesh=chair.geometry[g].copy();mesh.apply_transform(matrix);mesh.apply_transform(to_z)
 name='chair_'+node
 if node in ['left_blue_armrest_pad','right_blue_armrest_pad']:mesh.visual=TextureVisuals(material=materials['shirt'])
 scene.add_geometry(mesh,node_name=name,geom_name=name)
# A pale back cover leaves the blue perimeter visible from the reference's rear angle.
cover=upright('chair_white_rear_back_cover',.466,.454,.016,r=.062,b=.005,mat='shirt')
cover.apply_transform(trimesh.transformations.rotation_matrix(math.radians(-8),[1,0,0]));cover.apply_translation([0,.301,.796])
# Bent seated legs and light gray shoes resting at floor level.
for x,label in [(-.101,'left'),(.108,'right')]:
 sole=rounded(label+'_shoe_sole',.142,.242,.018,x=x,y=-.465,z=.012,r=.044,b=.006,mat='sole')
 soft_cushion(label+'_shoe_upper',.141,.238,.078,x=x,y=-.465,z=.061,e1=.34,e2=.36,mat='shoe')
 ellipsoid(label+'_ankle',[x,-.407,.123],[.048,.052,.033],'shoe')
 limb(label+'_seated_trouser_thigh',[[x,.012,.590],[x,-.165,.562],[x,-.349,.525]],[.082,.080,.074],'pants',n=28)
 ellipsoid(label+'_trouser_knee',[x,-.354,.507],[.074,.075,.079],'pants')
 limb(label+'_seated_trouser_shin',[[x,-.355,.505],[x,-.397,.335],[x,-.407,.145]],[.071,.065,.059],'pants',n=28)
soft_cushion('seated_trouser_pelvis',.300,.231,.146,x=0,y=.006,z=.583,e1=.40,e2=.55,mat='pants')
rounded('seated_dark_waist_belt',.306,.199,.031,x=0,y=.0,z=.604,r=.046,b=.006,mat='sole')
upright('small_belt_buckle',.043,.023,.005,x=.008,y=-.102,z=.604,r=.004,b=.001,mat='steel')
# Fitted long-sleeve shirt for the seated dashboard character.
torso_before=set(scene.geometry)
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
for name in set(scene.geometry)-torso_before:
 scene.geometry[name].vertices[:,0]*=.92
 scene.geometry[name].apply_translation([0,0,-.190])
# Long sleeves with elbows bent naturally toward the keyboard.
for label,sign in [('left',-1),('right',1)]:
 limb(label+'_upper_white_sleeve',[[sign*.165,.003,.915],[sign*.209,-.069,.862],[sign*.230,-.174,.806]],[.060,.054,.048],'shirt')
 ellipsoid(label+'_sleeve_elbow',[sign*.230,-.174,.806],[.049,.048,.050],'shirt')
 limb(label+'_typing_forearm_sleeve',[[sign*.230,-.174,.806],[sign*.200,-.321,.825],[sign*.153,-.470,.846]],[.047,.041,.032],'shirt')
 limb(label+'_shirt_cuff',[[sign*.156,-.462,.845],[sign*.150,-.484,.847]],[.033,.033],'trim')
 ellipsoid(label+'_typing_palm',[sign*.151,-.510,.852],[.032,.038,.018],'skin')
 for i in range(4):
  x=sign*.151+(i-1.5)*.012
  limb(label+'_typing_finger_'+str(i+1),[[x,-.527,.854],[x,-.552,.851],[x,-.574,.843]],[.0075,.007,.006],'skin',n=12)
 ellipsoid(label+'_typing_thumb',[sign*.124,-.512,.849],[.013,.023,.012],'skin')
# Stylized head and facial details, turned a little toward the presenting gesture.
head_names=set(scene.geometry)
head,_=soft_cushion('peach_head',.276,.245,.339,x=0,y=.002,z=1.387,e1=.67,e2=.74,mat='skin')
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
ellipsoid('open_presenting_smile',[.001,-.122,1.313],[.031,.005,.008],'mouth')
ellipsoid('small_white_smile_teeth',[.001,-.127,1.316],[.022,.002,.0025],'trim')
# Smooth swept hair, gathered into a low ponytail at the back of the head.
ellipsoid('hair_rear_mass',[0,.064,1.455],[.146,.083,.132],'hair',sub=3)
ellipsoid('hair_crown',[-.009,.015,1.563],[.146,.116,.071],'hair',sub=3)
ellipsoid('hair_left_temple',[-.125,.009,1.458],[.031,.078,.083],'hair',sub=3)
ellipsoid('hair_right_temple',[.126,.016,1.464],[.028,.071,.077],'hair',sub=3)
rotlock=trimesh.transformations.rotation_matrix(math.radians(-16),[0,1,0])
ellipsoid('hair_swept_front_lock',[.013,-.064,1.560],[.139,.078,.055],'hair',sub=3,rotation=rotlock)
hair_parts=[name for name in scene.geometry if name.startswith('hair_')]
hair_mesh=trimesh.boolean.union([scene.geometry[name].copy() for name in hair_parts],engine='manifold')
for name in hair_parts:scene.delete_geometry(name)
add(hair_mesh,'gathered_dark_hairstyle','hair')
# Rounded hanging ponytail with a soft outward curve, behind the head.
pony,_=soft_cushion('low_curved_ponytail',.151,.147,.288,x=.008,y=.229,z=1.389,e1=.70,e2=.83,mat='hair')
for v in pony.vertices:
 t=float(np.clip((1.505-v[2])/.245,0,1))
 v[1]+=.040*t*t
 v[0]+=.012*t
materials['hair_tie']=PBRMaterial(name='muted_brown_hair_tie',baseColorFactor=[70,25,17,255],metallicFactor=0.,roughnessFactor=.75)
rod('ponytail_hair_tie',[.006,.160,1.490],[.006,.190,1.490],.055,'hair_tie',sections=32)
# Rotate only head components around the neck, leaving the pose unchanged.
head_rotation=trimesh.transformations.rotation_matrix(math.radians(0),[0,0,1],point=[0,.008,1.25])
for name in set(scene.geometry)-head_names:scene.geometry[name].apply_transform(head_rotation)
# Lower the head with the seated torso and incline it slightly toward the screen.
head_bend=trimesh.transformations.rotation_matrix(math.radians(8),[1,0,0],point=[0,.008,1.045])
for name in set(scene.geometry)-head_names:
 scene.geometry[name].apply_translation([0,0,-.190]);scene.geometry[name].apply_transform(head_bend)
# Laptop body, keyboard and screen: part of this complete reference component.
materials['laptop_shell']=PBRMaterial(name='graphite_laptop_shell',baseColorFactor=[16,22,35,255],metallicFactor=.20,roughnessFactor=.39)
materials['keyboard']=PBRMaterial(name='dark_laptop_keys',baseColorFactor=[5,8,14,255],metallicFactor=.03,roughnessFactor=.60)
materials['screen']=PBRMaterial(name='white_dashboard_screen',baseColorFactor=[245,249,255,255],metallicFactor=0.,roughnessFactor=.55,emissiveFactor=[.12,.12,.12])
materials['code_white']=PBRMaterial(name='pale_code_lines',baseColorFactor=[216,240,255,255],metallicFactor=0.,roughnessFactor=.65,emissiveFactor=[.10,.15,.20])
materials['code_cyan']=PBRMaterial(name='cyan_code_accent',baseColorFactor=[3,133,240,255],metallicFactor=0.,roughnessFactor=.55,emissiveFactor=[0,.12,.20])
rounded('laptop_base',.642,.430,.024,x=0,y=-.590,z=.830,r=.024,b=.006,mat='laptop_shell')
keys=[]
for row in range(5):
 for col in range(11):
  key=trimesh.creation.box(extents=[.040,.023,.003]);key.apply_translation([(col-5)*.049,-.731+row*.031,.844]);keys.append(key)
space=trimesh.creation.box(extents=[.245,.022,.003]);space.apply_translation([0,-.559,.844]);keys.append(space)
add(trimesh.util.concatenate(keys),'laptop_keyboard_keys','keyboard')
rounded('laptop_trackpad_border',.168,.078,.002,x=0,y=-.463,z=.843,r=.009,b=.0006,mat='steel')
rounded('laptop_trackpad_face',.157,.067,.002,x=0,y=-.463,z=.844,r=.007,b=.0006,mat='laptop_shell')
rod('laptop_hinge',[-.292,-.795,.842],[.292,-.795,.842],.011,'laptop_shell',sections=24)
screen_before=set(scene.geometry)
upright('laptop_screen_frame',.642,.405,.024,x=0,y=-.795,z=1.047,r=.021,b=.006,mat='laptop_shell')
upright('laptop_dashboard_display',.592,.347,.003,x=0,y=-.781,z=1.047,r=.010,b=.0008,mat='screen')
# White dashboard with seven increasing cobalt bars and a rising trend line.
# Screen front faces +Y; reverse X ordering makes the chart rise left-to-right.
upright('dashboard_header',.153,.010,.0015,x=.190,y=-.778,z=1.194,r=.003,b=.0004,mat='badge')
upright('dashboard_subtitle',.092,.004,.0015,x=.220,y=-.778,z=1.177,r=.001,b=.0003,mat='steel')
for i in range(7):
 x=.236-i*.076;h=.038+i*.023
 upright('dashboard_bar_'+str(i+1),.049,h,.003,x=x,y=-.776,z=.923+h/2,r=.005,b=.0006,mat='badge')
# Fine baseline and chart grid, set slightly behind the bars.
for j in range(4):
 upright('dashboard_grid_'+str(j),.530,.0015,.001,x=0,y=-.778,z=.925+j*.063,r=.0005,b=.0002,mat='panel')
chart_points=[[.236-i*.076,-.772,.989+i*.025+(.009 if i%2==0 else -.003)] for i in range(7)]
for i in range(6):rod('dashboard_trend_'+str(i),chart_points[i],chart_points[i+1],.004,'code_cyan',sections=12)
for i,point in enumerate(chart_points):ellipsoid('dashboard_dot_'+str(i),point,[.006,.002,.006],'code_cyan',sub=1)
upright('dashboard_top_stat',.045,.029,.002,x=-.240,y=-.776,z=1.190,r=.004,b=.0004,mat='code_cyan')
ellipsoid('laptop_webcam',[0,-.780,1.238],[.003,.0015,.003],'eyes',sub=1)
screen_tilt=trimesh.transformations.rotation_matrix(math.radians(12),[1,0,0],point=[0,-.795,.842])
for name in set(scene.geometry)-screen_before:scene.geometry[name].apply_transform(screen_tilt)
# Consistent glTF coordinates; whole-assembly origin includes the screen projection.
rot=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);scene.apply_transform(rot)
shift=np.eye(4);shift[0,3]=-scene.bounds[:,0].mean();shift[1,3]=-scene.bounds[0,1];scene.apply_transform(shift)
for mesh in scene.geometry.values():_=mesh.vertex_normals
scene.metadata={'asset':'Nodeworks / 21 Person Working Right','status':'Reference-based stylized reconstruction; not exact 1:1','units':'meter','up_axis':'Y','origin':'bottom-center of complete assembly','animation':False,'rigged':False,'includes':['person','chair','laptop']}
file=OUT/'21-nodeworks-person-working-right.glb';scene.export(str(file))
s=trimesh.load(file,force='scene');checks={}
for name in ['peach_head','white_shirt_torso','left_seated_trouser_thigh','right_seated_trouser_shin','left_typing_palm','laptop_base','laptop_screen_frame','chair_outer_graphite_frame']:
 if name not in s.geometry:continue
 m=s.geometry[name].copy();m.merge_vertices();checks[name]=bool(m.is_watertight and m.is_winding_consistent)
report={'meshes':len(s.geometry),'triangles':sum(len(mesh.faces) for mesh in s.geometry.values()),'size_bytes':file.stat().st_size,'dimensions_m':s.extents.tolist(),'bounds':s.bounds.tolist(),'finite_vertices':all(np.isfinite(mesh.vertices).all() for mesh in s.geometry.values()),'valid_face_indices':all(mesh.faces.max()<len(mesh.vertices) for mesh in s.geometry.values()),'closed_and_consistent_meshes':checks,'pose':'static seated working pose','includes':['person','chair','laptop'],'rigged':False,'external_textures':False}
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
