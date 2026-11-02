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
 verts=[];faces=[];rings=[];n=320
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

def efficient_ring(name,outer_bounds,inner_bounds,ro,ri,depth,y=0,bevel=.006,mat='frame'):
 # Analytic concentric rounded rectangles: detail concentrated at curved corners.
 def contour(bounds,r,inset,inside=False):
  x0,z0,x1,z1=bounds
  if inside:x0-=inset;z0-=inset;x1+=inset;z1+=inset;r+=inset
  else:x0+=inset;z0+=inset;x1-=inset;z1-=inset;r-=inset
  result=[]
  for cx,cz,a in [(x1-r,z1-r,0),(x0+r,z1-r,90),(x0+r,z0+r,180),(x1-r,z0+r,270)]:
   for k in range(13):
    angle=math.radians(a+k*90/12);result.append([cx+r*math.cos(angle),cz+r*math.sin(angle)])
  return np.array(result[::-1] if inside else result)
 verts=[];faces=[];rings=[];n=52
 for inset,yy in [(bevel,-depth/2),(bevel*.293,-depth/2+bevel*.293),(0,-depth/2+bevel),(0,depth/2-bevel),(bevel*.293,depth/2-bevel*.293),(bevel,depth/2)]:
  loops=[contour(outer_bounds,ro,inset),contour(inner_bounds,ri,inset,True)];rings.append(loops)
  for arr in loops:verts.extend([[a,y+yy,c] for a,c in arr])
 stride=2*n
 for j in range(5):
  for k in range(2):
   for i in range(n):
    a=j*stride+k*n+i;c=j*stride+k*n+(i+1)%n;d=a+stride;e=c+stride
    faces.extend([[a,e,c],[a,d,e]])
 for idx,yy,flip in [(0,-depth/2,False),(-1,depth/2,True)]:
  pp=Polygon(rings[idx][0],holes=[rings[idx][1]])
  vv,ff=trimesh.creation.triangulate_polygon(pp,engine='triangle',triangle_args='pY');start=len(verts)
  verts.extend([[a,y+yy,c] for a,c in vv])
  faces.extend([[start+int(i) for i in (f[::-1] if flip else f)] for f in ff])
 return add(trimesh.Trimesh(verts,faces,process=False),name,mat)

# Matching dark graphite frame, softly blue transparent glass, and steel handles.
materials['frame']=PBRMaterial(name='graphite_powder_coated_frame',baseColorFactor=[15,20,31,255],metallicFactor=.32,roughnessFactor=.36)
materials['frame_edge']=PBRMaterial(name='graphite_edge_trim',baseColorFactor=[27,34,49,255],metallicFactor=.38,roughnessFactor=.31)
materials['rubber']=PBRMaterial(name='black_glazing_seal',baseColorFactor=[5,8,14,255],metallicFactor=0.,roughnessFactor=.78)
materials['glass']=PBRMaterial(name='pale_blue_transparent_glass',baseColorFactor=[90,161,230,68],metallicFactor=0.,roughnessFactor=.12,alphaMode='BLEND',doubleSided=True)
materials['handle']=PBRMaterial(name='satin_graphite_handle',baseColorFactor=[52,65,87,255],metallicFactor=.55,roughnessFactor=.32)
materials['reflection']=PBRMaterial(name='subtle_glass_reflection',baseColorFactor=[230,248,255,68],metallicFactor=0.,roughnessFactor=.2,alphaMode='BLEND',doubleSided=True)
# Main rectangular frame with a rounded outer perimeter and a true open center.
outer=round_rect(-.80,.0,.80,2.40,.071)
inner=round_rect(-.742,.058,.742,2.342,.026)
efficient_ring('outer_graphite_frame',[-.80,0,.80,2.40],[-.742,.058,.742,2.342],.071,.026,.092,bevel=.010,mat='frame')
# Slight rear edge adds a fine metallic seam to the reference's thick side profile.
rear_outer=round_rect(-.789,.011,.789,2.389,.062)
rear_inner=round_rect(-.749,.051,.749,2.349,.028)
efficient_ring('rear_perimeter_edge',[-.789,.011,.789,2.389],[-.749,.051,.749,2.349],.062,.028,.018,y=.047,bevel=.005,mat='frame_edge')
# A separate recessed glazing gasket seats each pane without covering its center.
seal_outer=round_rect(-.749,.051,.749,2.349,.028)
seal_inner=round_rect(-.727,.073,.727,2.327,.013)
efficient_ring('inner_glazing_seal',[-.749,.051,.749,2.349],[-.727,.073,.727,2.327],.028,.013,.018,y=-.004,bevel=.004,mat='rubber')
# Paired narrow meeting stiles produce the central joint seen in the reference.
upright('center_left_meeting_stile',.022,2.289,.055,x=-.014,y=-.007,z=1.20,r=.008,b=.006,mat='frame')
upright('center_right_meeting_stile',.022,2.289,.055,x=.014,y=-.007,z=1.20,r=.008,b=.006,mat='frame_edge')
upright('center_joint_gasket',.005,2.283,.011,x=0,y=-.037,z=1.20,r=.002,b=.001,mat='rubber')
# Real thin pane meshes. Alpha blend keeps the material portable between glTF viewers.
upright('left_transparent_glass',.702,2.246,.008,x=-.376,y=.006,z=1.20,r=.013,b=.002,mat='glass')
upright('right_transparent_glass',.702,2.246,.008,x=.376,y=.006,z=1.20,r=.013,b=.002,mat='glass')
# The two small central rectangular handles sit forward of the meeting stiles.
for x,label in [(-.042,'left'),(.042,'right')]:
 upright(label+'_handle_mount',.049,.285,.017,x=x,y=-.045,z=1.155,r=.012,b=.005,mat='rubber')
 upright(label+'_handle_body',.047,.259,.040,x=x,y=-.063,z=1.155,r=.011,b=.008,mat='handle')
 upright(label+'_handle_edge',.009,.223,.007,x=x-.010,y=-.086,z=1.155,r=.003,b=.002,mat='steel')
# Restrained front-surface reflection detail, as in the upper-left reference pane.
upright('left_glass_reflection_dash',.254,.013,.0014,x=-.438,y=-.0008,z=2.015,r=.005,b=.0004,mat='reflection')
upright('left_glass_reflection_glint',.010,1.95,.0012,x=-.695,y=-.0009,z=1.20,r=.004,b=.0003,mat='reflection')
# Small corner hardware kept on the inside rear edge, not added as large hinges.
for xx in [-.773,.773]:
 for zz in [.037,2.363]:
  rod('rear_corner_fastener_'+str(xx)+'_'+str(zz),[xx,.056,zz],[xx,.059,zz],.006,'handle')
# Export a static Y-up asset with consistent bottom-center coordinates.
rot=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);scene.apply_transform(rot)
shift=np.eye(4);shift[0,3]=-scene.bounds[:,0].mean();shift[1,3]=-scene.bounds[0,1];scene.apply_transform(shift)
for m in scene.geometry.values():_=m.vertex_normals
scene.metadata={'asset':'Nodeworks / 05 Glass Wall Left','status':'Reference-based reconstruction; not exact 1:1','units':'meter','up_axis':'Y','origin':'bottom-center','animation':False,'glass':'alpha-blended, no physical refraction'}
path=OUT/'05-nodeworks-glass-wall-left.glb';scene.export(str(path))
s=trimesh.load(path,force='scene')
frame=s.geometry['outer_graphite_frame'].copy();frame.merge_vertices()
report={'meshes':len(s.geometry),'triangles':sum(len(m.faces) for m in s.geometry.values()),'size_bytes':path.stat().st_size,'dimensions_m':s.extents.tolist(),'bounds':s.bounds.tolist(),'finite_vertices':all(np.isfinite(m.vertices).all() for m in s.geometry.values()),'valid_face_indices':all(m.faces.max()<len(m.vertices) for m in s.geometry.values()),'frame_watertight':bool(frame.is_watertight),'frame_consistent_winding':bool(frame.is_winding_consistent),'glass_alpha_mode':s.geometry['left_transparent_glass'].visual.material.alphaMode,'glass_rgba':s.geometry['left_transparent_glass'].visual.material.baseColorFactor.tolist()}
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
