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
 verts=[];faces=[];n=192
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

from shapely.geometry import box

def round_rect(x0,z0,x1,z1,r):
 return orient(box(x0+r,z0+r,x1-r,z1-r).buffer(r,quad_segs=10),sign=1.)

def frame_panel(name,poly,depth,y=0,bevel=.018,mat='shell'):
 # Loft every boundary, including the inner opening, and cap the annular face.
 verts=[];faces=[];rings=[];n=192
 for inset,yy in [(bevel,-depth/2),(bevel*.293,-depth/2+bevel*.293),(0,-depth/2+bevel),(0,depth/2-bevel),(bevel*.293,depth/2-bevel*.293),(bevel,depth/2)]:
  pp=orient(poly.buffer(-inset),sign=1.)
  loops=[]
  for curve in [pp.exterior,*pp.interiors]:
   arr=np.array([curve.interpolate(t,normalized=True).coords[0] for t in np.arange(n)/n]);loops.append(arr)
  rings.append(loops)
  for arr in loops:verts.extend([[a,y+yy,c] for a,c in arr])
 count=len(rings[0]);stride=count*n
 for j in range(5):
  for k in range(count):
   for i in range(n):
    a=j*stride+k*n+i;c=j*stride+k*n+(i+1)%n;d=a+stride;e=c+stride
    faces.extend([[a,e,c],[a,d,e]])
 for idx,yy,flip in [(0,-depth/2,False),(-1,depth/2,True)]:
  pp=Polygon(rings[idx][0],holes=rings[idx][1:]);vv,ff=trimesh.creation.triangulate_polygon(pp,engine='triangle',triangle_args='pY');start=len(verts)
  verts.extend([[a,y+yy,c] for a,c in vv])
  for f in ff:faces.append([start+int(i) for i in (f[::-1] if flip else f)])
 return add(trimesh.Trimesh(verts,faces,process=False),name,mat)

# White facade with one large rounded opening. Inner opening is real geometry.
outer=round_rect(-.86,.035,.74,2.43,.095)
opening=round_rect(-.66,.32,.54,1.91,.155)
frame_panel('main_storage_frame',outer.difference(opening),.29,y=-.025,bevel=.021,mat='trim')
upright('recessed_back_wall',1.33,1.89,.060,x=-.06,y=.139,z=1.19,r=.09,b=.012,mat='panel')
# Horizontal shelf slabs seated inside the opening.
for name,z in [('lower_shelf',.88),('upper_shelf',1.44)]:
 rounded(name,1.235,.345,.058,x=-.06,y=-.025,z=z,r=.025,b=.011,mat='trim')
 upright(name+'_front_lip',1.19,.025,.018,x=-.06,y=-.205,z=z+.002,r=.009,b=.004,mat='shell')
rounded('bottom_niche_sill',1.10,.31,.035,x=-.06,y=-.025,z=.345,r=.06,b=.009,mat='trim')
# Architectural top cap and small inlaid service features.
rounded('crown_main_cap',1.69,.405,.092,x=-.015,y=.0,z=2.445,r=.055,b=.015,mat='trim')
rounded('top_recess_channel',.90,.064,.012,x=-.11,y=-.045,z=2.497,r=.018,b=.003,mat='recess')
rounded('top_channel_white_rail',.85,.033,.018,x=-.11,y=-.095,z=2.508,r=.012,b=.004,mat='trim')
rounded('top_dark_service_port',.14,.075,.013,x=.59,y=.028,z=2.497,r=.022,b=.004,mat='gasket')
rounded('top_left_service_port',.095,.057,.009,x=-.62,y=.050,z=2.496,r=.015,b=.003,mat='steel')
# Right exposed support rod and continuous blue channel, characteristic of the reference.
upright('right_blue_vertical_channel',.051,1.16,.012,x=.665,y=-.177,z=1.62,r=.012,b=.003,mat='blue')
upright('right_channel_border',.078,1.205,.011,x=.665,y=-.169,z=1.62,r=.018,b=.004,mat='recess')
# Ensure blue is in front of its recess.
scene.geometry['right_blue_vertical_channel'].apply_translation([0,-.006,0])
rounded('support_top_blue_socket',.195,.245,.105,x=.915,y=.020,z=2.362,r=.032,b=.015,mat='blue')
rounded('right_support_cap',.33,.37,.085,x=.90,y=.016,z=2.465,r=.026,b=.013,mat='trim')
rod('right_exposed_support_rod',[.935,.025,.17],[.935,.025,2.33],.036,'gasket')
rod('right_support_metal_highlight',[.918,-.008,.21],[.918,-.008,2.315],.011,'steel')
rounded('support_bottom_socket',.16,.18,.095,x=.935,y=.025,z=.145,r=.023,b=.011,mat='recess')
rounded('support_bottom_foot',.19,.205,.045,x=.935,y=.025,z=.083,r=.025,b=.009,mat='gasket')
upright('header_blue_indicator',.165,.044,.012,x=.54,y=-.183,z=2.285,r=.014,b=.003,mat='blue')
upright('header_indicator_white_cutout',.062,.012,.014,x=.52,y=-.192,z=2.292,r=.004,b=.002,mat='trim')

# Six individual storage boxes. Every box has a lid, inset handle and lid label.
def storage_box(name,x,z,w=.30,h=.28,color='blue'):
 y=-.052;depth=.275
 rounded(name+'_body',w,depth,h,x=x,y=y,z=z+h/2,r=.035,b=.012,mat=color)
 rounded(name+'_lid',w+.013,depth+.013,.040,x=x,y=y,z=z+h+.006,r=.022,b=.008,mat=color)
 # Shallow contrasting lid seam and recessed handle components.
 upright(name+'_handle_recess',.080,.050,.007,x=x,y=y-depth/2-.005,z=z+h*.54,r=.016,b=.002,mat='gasket' if color!='blue' else 'recess')
 upright(name+'_handle_insert',.047,.012,.009,x=x,y=y-depth/2-.010,z=z+h*.56,r=.004,b=.002,mat='trim' if color=='blue' else 'steel')
 rounded(name+'_lid_label',.088,.046,.004,x=x,y=y-.010,z=z+h+.028,r=.009,b=.001,mat='trim' if color=='blue' else 'panel')
 # Small side catch, visible when the camera is angled.
 upright(name+'_side_catch',.018,.035,.006,x=x+w/2-.017,y=y-depth/2-.009,z=z+h-.025,r=.004,b=.002,mat='trim' if color=='blue' else 'recess')
storage_box('upper_box_left',-.455,1.472,w=.31,h=.285)
storage_box('upper_box_center',-.055,1.472,w=.32,h=.268,color='trim')
storage_box('upper_box_right',.329,1.472,w=.255,h=.235)
storage_box('lower_box_left',-.489,.912,w=.18,h=.238)
storage_box('lower_box_center',-.183,.912,w=.32,h=.247,color='trim')
storage_box('lower_box_right',.332,.912,w=.255,h=.239)
# Base panel seam and mounting details.
upright('base_service_inset',.92,.057,.007,x=-.05,y=-.175,z=.165,r=.016,b=.002,mat='shell')
for x,k in [(-.73,1),(.61,2)]:
 rod('lower_frame_fastener_'+str(k),[x,-.173,.14],[x,-.183,.14],.012,'steel')
for x in [-.74,.62]:
 rounded('frame_foot_'+str(x),.18,.24,.024,x=x,y=.015,z=.024,r=.023,b=.006,mat='gasket')
# Consistent glTF coordinates and origin with Asset 02.
rot=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);scene.apply_transform(rot)
shift=np.eye(4);shift[0,3]=-scene.bounds[:,0].mean();shift[1,3]=-scene.bounds[0,1];scene.apply_transform(shift)
for m in scene.geometry.values():_=m.vertex_normals
scene.metadata={'asset':'Nodeworks / 03 Main Structure Right','status':'Reference-based reconstruction; not exact 1:1','units':'meter','up_axis':'Y','origin':'bottom-center','animation':False}
path=OUT/'03-nodeworks-main-structure-right.glb';scene.export(str(path))
s=trimesh.load(path,force='scene')
frame=s.geometry['main_storage_frame'].copy();frame.merge_vertices()
report={'meshes':len(s.geometry),'triangles':sum(len(m.faces) for m in s.geometry.values()),'size_bytes':path.stat().st_size,'dimensions_m':s.extents.tolist(),'bounds':s.bounds.tolist(),'finite_vertices':all(np.isfinite(m.vertices).all() for m in s.geometry.values()),'valid_face_indices':all(m.faces.max()<len(m.vertices) for m in s.geometry.values()),'main_frame_watertight':bool(frame.is_watertight),'main_frame_consistent_winding':bool(frame.is_winding_consistent)}
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
