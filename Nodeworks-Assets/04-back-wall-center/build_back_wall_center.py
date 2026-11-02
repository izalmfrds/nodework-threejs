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
 verts=[]; rings=[]; seg=8
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
 verts=[];faces=[];rings=[];n=384
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

# Palette: dark gray inset, neutral housing. No blue is present on this asset.
materials['screen']=PBRMaterial(name='matte_charcoal_inset',baseColorFactor=[18,23,35,255],metallicFactor=.02,roughnessFactor=.68)
materials['seal']=PBRMaterial(name='dark_bezel_seal',baseColorFactor=[9,12,20,255],metallicFactor=.0,roughnessFactor=.72)
materials['ports']=PBRMaterial(name='service_port_interior',baseColorFactor=[43,51,67,255],metallicFactor=.2,roughnessFactor=.5)
# Continuous rounded housing. Slightly inset rear cover defines a casing seam.
upright('main_rounded_housing',2.80,1.86,.29,x=0,y=.0,z=.93,r=.155,b=.032,mat='shell')
upright('rear_cover',2.66,1.72,.025,x=0,y=.148,z=.93,r=.120,b=.009,mat='panel')
# Slightly darker seat under the raised white frame.
upright('bezel_shadow_seat',2.405,1.415,.035,x=.105,y=-.155,z=.833,r=.143,b=.012,mat='recess')
# White annular bezel; the face stays truly recessed inside its opening.
outer=round_rect(.105-2.38/2,.833-1.39/2,.105+2.38/2,.833+1.39/2,.132)
inner=round_rect(.105-2.24/2,.833-1.25/2,.105+2.24/2,.833+1.25/2,.103)
frame_panel('raised_white_bezel',outer.difference(inner),.067,y=-.204,bevel=.012,mat='trim')
upright('inner_dark_gasket',2.264,1.274,.018,x=.105,y=-.207,z=.833,r=.112,b=.005,mat='seal')
upright('matte_dark_center_panel',2.233,1.243,.024,x=.105,y=-.217,z=.833,r=.101,b=.007,mat='screen')
# Three-piece crown service cover with a narrow longitudinal slot.
rounded('crown_left_cover',.44,.235,.013,x=-1.135,y=.006,z=1.866,r=.027,b=.004,mat='trim')
rounded('crown_center_cover',1.78,.235,.013,x=0,y=.006,z=1.866,r=.026,b=.004,mat='trim')
rounded('crown_right_cover',.44,.235,.013,x=1.135,y=.006,z=1.866,r=.027,b=.004,mat='trim')
rounded('crown_longitudinal_slot',1.38,.020,.006,x=0,y=-.012,z=1.875,r=.006,b=.002,mat='ports')
rounded('crown_slot_inner_lip',1.19,.007,.007,x=0,y=-.012,z=1.879,r=.0025,b=.001,mat='steel')
for xx,k in [(-1.13,1),(1.13,2)]:
 rounded('crown_mount_socket_'+str(k),.103,.060,.007,x=xx,y=.013,z=1.875,r=.019,b=.002,mat='ports')
 rounded('crown_socket_inner_'+str(k),.058,.025,.008,x=xx,y=.013,z=1.880,r=.007,b=.002,mat='gasket')
# Small side-facing ports, modeled on the visible left edge of the reference.
def side_detail(name,depth,width,height,x,y,z,mat):
 # Use rounded XY prism and rotate its local Z direction to the X side.
 m=rounded(name,width,height,depth,r=min(.010,width*.22,height*.22),b=min(.002,depth*.25),mat=mat)
 # local X -> world Y, local Y -> world Z, local Z -> world X
 t=np.array([[0,0,1,x],[1,0,0,y],[0,1,0,z],[0,0,0,1]],float);m.apply_transform(t)
for z,k in [(1.48,1),(1.41,2),(.96,3),(.73,4),(.51,5)]:
 side_detail('left_service_recess_'+str(k),.007,.029,.041,-1.403,.012,z,'recess')
 side_detail('left_service_inner_'+str(k),.008,.012,.020,-1.408,.012,z,'ports')
# Two tiny face fasteners in the upper housing and discrete bottom contact pads.
for xx,k in [(-.27,1),(.27,2)]:
 rod('upper_face_fastener_'+str(k),[xx,-.146,1.68],[xx,-.151,1.68],.007,'steel')
for xx,k in [(-.98,1),(.98,2)]:
 rounded('bottom_contact_pad_'+str(k),.24,.16,.012,x=xx,y=.010,z=.006,r=.028,b=.004,mat='panel')
# Consistent Y-up and bottom-center origin, same as previous assets.
rot=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);scene.apply_transform(rot)
shift=np.eye(4);shift[0,3]=-scene.bounds[:,0].mean();shift[1,3]=-scene.bounds[0,1];scene.apply_transform(shift)
for m in scene.geometry.values():_=m.vertex_normals
scene.metadata={'asset':'Nodeworks / 04 Back Wall Center','status':'Reference-based reconstruction; not exact 1:1','units':'meter','up_axis':'Y','origin':'bottom-center','animation':False}
path=OUT/'04-nodeworks-back-wall-center.glb';scene.export(str(path))
s=trimesh.load(path,force='scene')
bezel=s.geometry['raised_white_bezel'].copy();bezel.merge_vertices()
report={'meshes':len(s.geometry),'triangles':sum(len(m.faces) for m in s.geometry.values()),'size_bytes':path.stat().st_size,'dimensions_m':s.extents.tolist(),'bounds':s.bounds.tolist(),'finite_vertices':all(np.isfinite(m.vertices).all() for m in s.geometry.values()),'valid_face_indices':all(m.faces.max()<len(m.vertices) for m in s.geometry.values()),'bezel_watertight':bool(bezel.is_watertight),'bezel_consistent_winding':bool(bezel.is_winding_consistent)}
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
