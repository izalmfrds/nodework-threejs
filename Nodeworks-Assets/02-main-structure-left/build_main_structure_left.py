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
 verts=[]; rings=[]; seg=5
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

def round_outline(points,rad=.065):
 # Quadratic corner fillets retain the asymmetric architectural silhouette.
 result=[]
 for i,p in enumerate(points):
  p=np.array(p,dtype=float);prev=np.array(points[i-1]);nxt=np.array(points[(i+1)%len(points)])
  a=prev-p;c=nxt-p;radius=min(rad,np.linalg.norm(a)*.28,np.linalg.norm(c)*.28)
  a=p+a/np.linalg.norm(a)*radius;c=p+c/np.linalg.norm(c)*radius
  for t in np.linspace(0,1,7,endpoint=False):result.append((1-t)**2*a+2*(1-t)*t*p+t*t*c)
 return orient(Polygon(result),sign=1.)

def facade(name,poly,depth,y=0,bevel=.018,mat='shell'):
 # Bevelled contour loft; independent planar caps preserve crisp normals.
 verts=[];faces=[];n=360
 shapes=[]
 for offset,yy in [(bevel,-depth/2),(bevel*.293,-depth/2+bevel*.293),(0,-depth/2+bevel),(0,depth/2-bevel),(bevel*.293,depth/2-bevel*.293),(bevel,depth/2)]:
  boundary=orient(poly.buffer(-offset,join_style='round'),sign=1.).exterior
  arr=np.array([boundary.interpolate(t,normalized=True).coords[0] for t in np.arange(n)/n])
  shapes.append(arr)
  verts.extend([[a,y+yy,c] for a,c in arr])
 for j in range(5):
  for i in range(n):
   a=j*n+i;c=j*n+(i+1)%n;d=(j+1)*n+i;e=(j+1)*n+(i+1)%n
   faces.extend([[a,e,c],[a,d,e]])
 # Flat caps use triangulated inset shape. Exact seam matched with sampled loft.
 for idx,yy,flip in [(0,-depth/2,False),(-1,depth/2,True)]:
  vv,ff=trimesh.creation.triangulate_polygon(Polygon(shapes[idx]),engine='earcut');start=len(verts)
  verts.extend([[a,y+yy,c] for a,c in vv])
  for f in ff:faces.append([start+int(i) for i in (f[::-1] if flip else f)])
 mesh=trimesh.Trimesh(verts,faces,process=False)
 return add(mesh,name,mat)

def rod(name,p1,p2,r,mat='steel'):
 return add(trimesh.creation.cylinder(radius=r,sections=12,segment=np.array([p1,p2])),name,mat)
def ball(name,p,r,mat='trim'):
 m=trimesh.creation.icosphere(subdivisions=2,radius=r);m.apply_translation(p);return add(m,name,mat)

# Tall front facade with a genuinely open doorway and rounded internal shoulders.
poly=round_outline([(-.99,.035),(-.99,2.19),(-.90,2.32),(.40,2.32),(.50,2.40),(.57,2.40),(.57,.035),(.02,.035),(.02,1.36),(-.045,1.45),(-.60,1.45),(-.69,1.36),(-.69,.035)],.085)
facade('main_arch_facade',poly,.245,y=-.13,bevel=.022,mat='trim')
# Thin backing on the right-hand storage niche. The door area stays open.
upright('right_niche_back_panel',.61,2.13,.075,x=.82,y=.116,z=1.18,r=.055,b=.013,mat='panel')
upright('right_outer_upright',.105,2.22,.24,x=1.145,y=.025,z=1.17,r=.032,b=.012)
rounded('right_lower_sill',.66,.26,.115,x=.83,y=.0,z=.075,r=.035,b=.018)
rounded('right_middle_shelf',.65,.27,.067,x=.825,y=-.035,z=1.37,r=.025,b=.012,mat='trim')
rounded('right_top_shelf',.65,.255,.07,x=.825,y=-.015,z=2.20,r=.022,b=.012)
# Crown cap extends right, echoing the stepped futuristic header.
cap=round_outline([(.36,2.31),(.48,2.43),(.91,2.43),(.99,2.50),(1.21,2.50),(1.21,2.30),(1.10,2.23),(.60,2.23)],.06)
facade('stepped_crown_cap',cap,.32,y=-.016,bevel=.018,mat='trim')
blue=round_outline([(.48,2.278),(.94,2.278),(1.16,2.378),(1.208,2.378),(1.208,2.305),(1.105,2.235),(.56,2.235)],.028)
facade('crown_blue_edge_inlay',blue,.012,y=-.185,bevel=.003,mat='blue')
# Offset header channels visible on top, with clean blue inserts.
rounded('upper_rail_inset',1.18,.082,.012,x=-.27,y=-.11,z=2.333,r=.025,b=.003,mat='recess')
rounded('upper_rail_blue_line',1.12,.029,.013,x=-.27,y=-.135,z=2.341,r=.01,b=.003,mat='blue')
rounded('upper_raised_white_rail',1.03,.075,.030,x=-.27,y=-.065,z=2.347,r=.024,b=.008,mat='trim')
rounded('right_cap_service_recess',.22,.11,.012,x=1.065,y=-.02,z=2.507,r=.028,b=.003,mat='recess')
rounded('right_cap_service_insert',.12,.052,.013,x=1.065,y=-.02,z=2.514,r=.013,b=.003,mat='gasket')
# Dark vertical recessed track on left column.
upright('left_recess_track',.104,1.66,.016,x=-.845,y=-.260,z=.94,r=.032,b=.005,mat='gasket')
upright('left_track_inner_rail',.025,1.59,.012,x=-.852,y=-.271,z=.94,r=.009,b=.003,mat='steel')
upright('left_track_blue_segment',.027,.37,.015,x=-.852,y=-.279,z=.42,r=.009,b=.003,mat='blue')
upright('left_track_blue_clamp',.072,.074,.024,x=-.845,y=-.285,z=.60,r=.015,b=.005,mat='blue')
# Inset logo: raised cobalt badge with six white spokes and round nodes.
upright('nodeworks_badge',.262,.262,.025,x=-.58,y=-.270,z=1.92,r=.055,b=.007,mat='blue')
center=np.array([-.58,-.290,1.92])
for i in range(6):
 a=math.radians(90+i*60);end=center+np.array([math.cos(a)*.077,0,math.sin(a)*.077])
 rod('logo_spoke_'+str(i),center,end,.008,'trim');ball('logo_node_'+str(i),end,.014,'trim')
ball('logo_hub',center,.017,'trim')
# Tiny trophy/device inside right niche, matching the small blue shelf detail.
rounded('shelf_blue_plinth',.22,.10,.035,x=.66,y=-.06,z=1.425,r=.012,b=.006,mat='blue')
rod('shelf_device_stem',[.66,-.055,1.44],[.66,-.055,1.60],.014,'steel')
ball('shelf_device_center',[.66,-.055,1.62],.035,'trim')
for a in [45,135]:
 aa=math.radians(a);p=[.66+.075*math.cos(aa),-.055,1.62+.075*math.sin(aa)]
 rod('device_arm_'+str(a),[.66,-.055,1.62],p,.009,'steel');ball('device_tip_'+str(a),p,.014,'trim')
# Fasteners and discreet bottom feet are actual geometry.
for xx,zz,k in [(-.77,.12,1),(.105,.15,2),(.81,.16,3),(1.145,2.07,4)]:
 rod('fastener_'+str(k),[xx,(-.102 if k==4 else -.258),zz],[xx,(-.112 if k==4 else -.267),zz],.011,'steel')
for x in [-.845,.30,1.12]:
 rounded('bottom_contact_'+str(x),.13,.18,.018,x=x,y=.0,z=.018,r=.015,b=.005,mat='gasket')
rot=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);scene.apply_transform(rot)
shift=np.eye(4);shift[0,3]=-scene.bounds[:,0].mean();shift[1,3]=-scene.bounds[0,1];scene.apply_transform(shift)
# Evaluate normals before export so the GLB includes smooth, authored normals.
for m in scene.geometry.values():_=m.vertex_normals
scene.metadata={'asset':'Nodeworks / 02 Main Structure Left','status':'Reference-based reconstruction; not exact 1:1','units':'meter','up_axis':'Y','origin':'bottom-center','animation':False}
path=OUT/'02-nodeworks-main-structure-left.glb';scene.export(str(path))
s=trimesh.load(path,force='scene')
report={'meshes':len(s.geometry),'triangles':sum(len(m.faces) for m in s.geometry.values()),'size_bytes':path.stat().st_size,'dimensions_m':s.extents.tolist(),'bounds':s.bounds.tolist(),'finite_vertices':all(np.isfinite(m.vertices).all() for m in s.geometry.values()),'valid_face_indices':all(m.faces.max()<len(m.vertices) for m in s.geometry.values())}
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
