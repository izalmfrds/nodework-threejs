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
 verts=[]; rings=[]; seg=6
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

from shapely.geometry import Polygon
from shapely.geometry.polygon import orient

# All construction below uses Z-up. The facade faces -Y.
def upright(name,w,h,depth,x=0,y=0,z=0,r=.04,b=.008,mat='shell'):
 mesh=rounded(name,w,h,depth,r=r,b=b,mat=mat)
 transform=np.array([[1,0,0,x],[0,0,-1,y],[0,1,0,z],[0,0,0,1]],dtype=float)
 mesh.apply_transform(transform)
 return mesh

def add(mesh,name,mat):
 mesh.visual=TextureVisuals(material=materials[mat]);scene.add_geometry(mesh,node_name=name,geom_name=name);return mesh

from shapely.geometry import LineString
materials['desk_white']=PBRMaterial(name='satin_white_desktop',baseColorFactor=[241,244,253,255],metallicFactor=.03,roughnessFactor=.40)
materials['cabinet_white']=PBRMaterial(name='white_cabinet_panels',baseColorFactor=[227,233,247,255],metallicFactor=.02,roughnessFactor=.49)
materials['accent_blue']=PBRMaterial(name='cobalt_blue_desk_accents',baseColorFactor=[0,17,255,255],metallicFactor=.05,roughnessFactor=.33)
materials['joint_gray']=PBRMaterial(name='subtle_cabinet_joints',baseColorFactor=[126,139,166,255],metallicFactor=.03,roughnessFactor=.58)
materials['foot_dark']=PBRMaterial(name='dark_recessed_plinth',baseColorFactor=[8,11,17,255],metallicFactor=0.,roughnessFactor=.80)

def face_shape(name,shape,depth,y,mat):
 mesh=trimesh.creation.extrude_polygon(shape,height=depth,engine='triangle')
 t=np.array([[1,0,0,0],[0,0,-1,y],[0,1,0,0],[0,0,0,1]],float);mesh.apply_transform(t)
 mesh=trimesh.graph.smooth_shade(mesh,angle=math.radians(35),facet_minarea=50)
 return add(mesh,name,mat)

# Two adjacent work surfaces with a real central seam.
for x,label in [(-.69,'left'),(.69,'right')]:
 rounded(label+'_white_desktop',1.360,1.620,.054,x=x,y=0,z=.771,r=.057,b=.013,mat='desk_white')
# Cabinet supports leave open knee spaces beneath the worktops.
rounded('left_rear_support_cabinet',.365,.625,.724,x=-1.157,y=.4675,z=.382,r=.034,b=.012,mat='cabinet_white')
rounded('front_center_support_cabinet',.830,.500,.724,x=-.025,y=-.545,z=.382,r=.042,b=.015,mat='cabinet_white')
rounded('right_drawer_pedestal',.425,1.440,.724,x=1.1425,y=0,z=.382,r=.035,b=.012,mat='cabinet_white')
for x,y,w,d,label in [(-1.157,.4675,.339,.595,'left_rear'),(-.025,-.545,.800,.470,'front_center'),(1.1425,0,.399,1.410,'right')]:
 rounded(label+'_recessed_floor_plinth',w,d,.020,x=x,y=y,z=.010,r=.018,b=.005,mat='foot_dark')
# A discreet high stretcher sits behind the left knee opening.
rounded('left_rear_underdesk_stretcher',.950,.060,.085,x=-.505,y=.728,z=.693,r=.016,b=.008,mat='panel')
# Three drawer fronts on the right-hand pedestal, with narrow gray recessed pulls.
for k,z in enumerate([.145,.382,.619],1):
 upright('right_drawer_'+str(k)+'_front',.374,.224,.013,x=1.1425,y=-.727,z=z,r=.015,b=.004,mat='desk_white')
 upright('right_drawer_'+str(k)+'_pull',.156,.012,.004,x=1.1425,y=-.735,z=z+.027,r=.004,b=.001,mat='joint_gray')
# Left desk: two blue cable slots inset into the front and rear of the work surface.
for y,label in [(-.674,'front'),(.674,'rear')]:
 rounded('left_'+label+'_cable_slot_seat',.678,.066,.003,x=-.736,y=y,z=.798,r=.020,b=.0008,mat='panel')
 rounded('left_'+label+'_blue_cable_slot',.638,.041,.005,x=-.736,y=y,z=.801,r=.016,b=.0012,mat='accent_blue')
# A short blue corner trim under the inner front edge of the right worktop.
plan=LineString([(.016,-.538),(.016,-.721),(.076,-.795),(.540,-.795)]).buffer(.017,cap_style='round',join_style='round')
edge=trimesh.creation.extrude_polygon(plan,height=.021,engine='triangle');edge.apply_translation([0,0,.730]);edge=trimesh.graph.smooth_shade(edge,angle=math.radians(35),facet_minarea=50);add(edge,'right_inner_corner_blue_trim','accent_blue')
# Curved cobalt channel on the front support cabinet, matching the visible motif.
curve=[(-.103,.025),(-.103,.354)]+[(.021+.124*math.cos(a),.354+.124*math.sin(a)) for a in np.linspace(math.pi,math.pi/2,21)]+[(.304,.478)]
channel=LineString(curve).buffer(.028,cap_style='flat',join_style='round')
face_shape('front_support_blue_channel',channel,.006,-.796,'accent_blue')
# Two quiet casing seams and small fixing heads at the left side of the support.
upright('front_support_left_panel_seam',.003,.633,.002,x=-.303,y=-.797,z=.386,r=.001,b=.0004,mat='panel')
for z,k in [(.643,1),(.563,2)]:
 head=trimesh.creation.cylinder(radius=.006,height=.003,sections=16)
 t=np.array([[1,0,0,-.358],[0,0,-1,-.799],[0,1,0,z],[0,0,0,1]],float);head.apply_transform(t);add(head,'front_support_fixing_'+str(k),'joint_gray')
# White divider along the center joint, perpendicular to the desktop width.
divider=upright('central_white_divider',1.058,.290,.070,z=0,r=.088,b=.013,mat='desk_white')
rot=trimesh.transformations.rotation_matrix(math.pi/2,[0,0,1]);divider.apply_transform(rot);divider.apply_translation([-.006,0,.943])
# Rear privacy panels: low white companion panel and blue-edged white panel.
upright('rear_low_white_divider',.474,.282,.055,x=.277,y=.130,z=.939,r=.068,b=.011,mat='desk_white')
upright('rear_blue_divider_outline',.731,.370,.064,x=.807,y=.130,z=.983,r=.067,b=.012,mat='accent_blue')
upright('rear_divider_white_front',.684,.331,.016,x=.816,y=.088,z=.979,r=.054,b=.005,mat='desk_white')
upright('rear_divider_white_back',.684,.331,.016,x=.816,y=.172,z=.979,r=.054,b=.005,mat='desk_white')
# Export using the same bottom-center origin and Y-up coordinate system.
rot=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);scene.apply_transform(rot)
shift=np.eye(4);shift[0,3]=-scene.bounds[:,0].mean();shift[1,3]=-scene.bounds[0,1];scene.apply_transform(shift)
for mesh in scene.geometry.values():_=mesh.vertex_normals
scene.metadata={'asset':'Nodeworks / 15 Office Desk Cluster','status':'Reference-based reconstruction; not exact 1:1','units':'meter','up_axis':'Y','origin':'bottom-center','animation':False}
path=OUT/'15-nodeworks-office-desk-cluster.glb';scene.export(str(path))
s=trimesh.load(path,force='scene');checks={}
for name in ['left_white_desktop','right_white_desktop','front_center_support_cabinet','right_drawer_pedestal','central_white_divider','rear_blue_divider_outline','front_support_blue_channel']:
 mesh=s.geometry[name].copy();mesh.merge_vertices();checks[name]=bool(mesh.is_watertight and mesh.is_winding_consistent)
report={'meshes':len(s.geometry),'triangles':sum(len(mesh.faces) for mesh in s.geometry.values()),'size_bytes':path.stat().st_size,'dimensions_m':s.extents.tolist(),'bounds':s.bounds.tolist(),'desktop_height_m':.798,'finite_vertices':all(np.isfinite(mesh.vertices).all() for mesh in s.geometry.values()),'valid_face_indices':all(mesh.faces.max()<len(mesh.vertices) for mesh in s.geometry.values()),'closed_and_consistent_meshes':checks,'work_surfaces':2,'drawer_fronts':3,'external_textures':False}
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
