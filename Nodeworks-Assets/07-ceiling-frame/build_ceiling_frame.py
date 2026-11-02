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
 verts=[];faces=[];n=256
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
  vv,ff=trimesh.creation.triangulate_polygon(Polygon(shapes[idx]),engine='triangle',triangle_args='pY');start=len(verts)
  verts.extend([[a,y+yy,c] for a,c in vv])
  for f in ff:faces.append([start+int(i) for i in (f[::-1] if flip else f)])
 mesh=trimesh.Trimesh(verts,faces,process=False)
 return add(mesh,name,mat)

def rod(name,p1,p2,r,mat='steel'):
 return add(trimesh.creation.cylinder(radius=r,sections=12,segment=np.array([p1,p2])),name,mat)
def ball(name,p,r,mat='trim'):
 m=trimesh.creation.icosphere(subdivisions=2,radius=r);m.apply_translation(p);return add(m,name,mat)

from shapely.geometry import box
materials['socket']=PBRMaterial(name='deep_mounting_socket',baseColorFactor=[3,5,9,255],metallicFactor=.10,roughnessFactor=.70)
materials['seam']=PBRMaterial(name='fine_joint_shadow',baseColorFactor=[114,125,146,255],metallicFactor=.06,roughnessFactor=.55)
# Source: Z-up. The ceiling frame is a short inverted-U crossbeam.
left_poly=round_outline([(-1.52,.015),(-1.52,.330),(-1.365,.563),(-1.270,.620),(-1.055,.620),(-1.055,.421),(-1.130,.410),(-1.200,.340),(-1.200,.015)],.065)
right_poly=round_outline([(1.055,.421),(1.130,.410),(1.200,.340),(1.200,.030),(1.520,.030),(1.520,.520),(1.465,.600),(1.370,.620),(1.055,.620)],.065)
left=facade('left_end_bracket',left_poly,.350,bevel=.018,mat='shell')
right=facade('right_end_bracket',right_poly,.350,bevel=.018,mat='shell')
rounded('central_crossbeam',2.104,.348,.198,x=0,y=0,z=.521,r=.025,b=.014,mat='trim')
# A shallow long-side seam and a slightly inset underside echo the panel split.
upright('front_crossbeam_joint',2.020,.010,.003,x=0,y=-.175,z=.451,r=.003,b=.0008,mat='seam')
rounded('underside_center_insert',1.99,.232,.009,x=0,y=.0,z=.420,r=.018,b=.003,mat='shell')
# Real subtractive sockets, rather than colored marks on the outer shell.
def rounded_slot_cutter(x,y,z,w,d,height):
 r=min(w,d)*.32;poly=box(-w/2+r,-d/2+r,w/2-r,d/2-r).buffer(r,quad_segs=8)
 m=trimesh.creation.extrude_polygon(poly,height=height,engine='triangle');m.apply_translation([x,y,z]);return m
left_top=rounded_slot_cutter(-1.245,0,.548,.094,.056,.11)
right_top=rounded_slot_cutter(1.300,0,.548,.094,.056,.11)
# Outer-left face has a rectangular service opening. Right-inner face has a round socket.
left_side=trimesh.creation.box(extents=[.12,.071,.054]);left_side.apply_translation([-1.501,-.008,.158])
right_side=trimesh.creation.cylinder(radius=.025,sections=24,segment=[[1.17,-.008,.208],[1.27,-.008,.208]])
for name,cutters in [('left_end_bracket',[left_top,left_side]),('right_end_bracket',[right_top,right_side])]:
 original=scene.geometry[name].copy();original.merge_vertices();original.fix_normals()
 assert original.is_watertight, name+' must be closed before socket cuts'
 cut=trimesh.boolean.difference([original,*cutters],engine='manifold')
 cut=trimesh.graph.smooth_shade(cut,angle=math.radians(35),facet_minarea=50)
 cut.visual=TextureVisuals(material=materials['shell']);_=cut.vertex_normals
 scene.geometry[name]=cut
# Dark socket floors and a narrow steel lining reinforce the recess depth.
for x,label in [(-1.245,'left'),(1.300,'right')]:
 rounded(label+'_mounting_socket_floor',.088,.050,.004,x=x,y=0,z=.605,r=.015,b=.001,mat='socket')
 rounded(label+'_mounting_socket_lining',.063,.025,.003,x=x,y=.001,z=.608,r=.007,b=.0008,mat='socket')
# Small dark floor behind the left exterior service hole.
service_floor=trimesh.creation.box(extents=[.003,.065,.048]);service_floor.apply_translation([-1.491,-.008,.158]);add(service_floor,'left_service_socket_floor','socket')
rod('right_inner_socket_floor',[1.221,-.008,.208],[1.224,-.008,.208],.024,'socket')
# Reference also shows a small upper recess on the left bevel.
slant=rounded('left_upper_service_recess',.066,.048,.006,r=.010,b=.0015,mat='socket')
rot_slant=trimesh.transformations.rotation_matrix(-math.radians(56),[0,1,0]);slant.apply_transform(rot_slant);slant.apply_translation([-1.432,-.004,.468])
# Discreet short joint lines between the three casing sections.
for x,label in [(-1.053,'left'),(1.053,'right')]:
 rounded(label+'_top_join',.004,.312,.002,x=x,y=0,z=.6208,r=.001,b=.0004,mat='seam')
# Export a compact static component. Position under ceiling in the assembled scene.
rot=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);scene.apply_transform(rot)
shift=np.eye(4);shift[0,3]=-scene.bounds[:,0].mean();shift[1,3]=-scene.bounds[0,1];scene.apply_transform(shift)
for m in scene.geometry.values():_=m.vertex_normals
scene.metadata={'asset':'Nodeworks / 07 Ceiling Frame','status':'Reference-based reconstruction; not exact 1:1','units':'meter','up_axis':'Y','origin':'bottom-center','animation':False}
path=OUT/'07-nodeworks-ceiling-frame.glb';scene.export(str(path))
s=trimesh.load(path,force='scene')
closed={}
for name in ['left_end_bracket','right_end_bracket']:
 m=s.geometry[name].copy();m.merge_vertices();closed[name]=bool(m.is_watertight and m.is_winding_consistent)
report={'meshes':len(s.geometry),'triangles':sum(len(m.faces) for m in s.geometry.values()),'size_bytes':path.stat().st_size,'dimensions_m':s.extents.tolist(),'bounds':s.bounds.tolist(),'finite_vertices':all(np.isfinite(m.vertices).all() for m in s.geometry.values()),'valid_face_indices':all(m.faces.max()<len(m.vertices) for m in s.geometry.values()),'brackets_closed_and_consistent':closed,'subtractive_mounting_sockets':4}
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
