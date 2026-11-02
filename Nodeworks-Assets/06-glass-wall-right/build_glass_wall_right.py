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

def rod(name,p1,p2,r,mat='steel'):
 return add(trimesh.creation.cylinder(radius=r,sections=12,segment=np.array([p1,p2])),name,mat)
def ball(name,p,r,mat='trim'):
 m=trimesh.creation.icosphere(subdivisions=2,radius=r);m.apply_translation(p);return add(m,name,mat)

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

# Same glass and graphite palette as Asset 05, with a white service cap.
materials['frame']=PBRMaterial(name='graphite_powder_coated_frame',baseColorFactor=[15,20,31,255],metallicFactor=.32,roughnessFactor=.36)
materials['frame_edge']=PBRMaterial(name='graphite_edge_trim',baseColorFactor=[27,34,49,255],metallicFactor=.38,roughnessFactor=.31)
materials['rubber']=PBRMaterial(name='black_glazing_seal',baseColorFactor=[5,8,14,255],metallicFactor=0.,roughnessFactor=.78)
materials['glass']=PBRMaterial(name='pale_blue_transparent_glass',baseColorFactor=[90,161,230,68],metallicFactor=0.,roughnessFactor=.12,alphaMode='BLEND',doubleSided=True)
materials['socket']=PBRMaterial(name='dark_cap_socket',baseColorFactor=[23,29,40,255],metallicFactor=.15,roughnessFactor=.48)
materials['reflection']=PBRMaterial(name='subtle_glass_edge_glint',baseColorFactor=[230,248,255,48],metallicFactor=0.,roughnessFactor=.2,alphaMode='BLEND',doubleSided=True)
# Real open perimeter, narrow dark glazing seal and fine rear edge.
efficient_ring('outer_graphite_frame',[-1.20,.023,1.20,2.40],[-1.14,.083,1.14,2.34],.030,.011,.094,bevel=.007,mat='frame')
efficient_ring('rear_perimeter_edge',[-1.189,.034,1.189,2.389],[-1.148,.075,1.148,2.348],.024,.012,.018,y=.048,bevel=.005,mat='frame_edge')
efficient_ring('inner_glazing_seal',[-1.147,.076,1.147,2.347],[-1.127,.096,1.127,2.327],.018,.007,.017,y=-.004,bevel=.003,mat='rubber')
# Two solid vertical mullions divide three fixed panes. Reference has no handles.
for xx,label in [(-.39,'left'),(.39,'right')]:
 upright(label+'_mullion',.048,2.275,.068,x=xx,y=-.001,z=1.2115,r=.009,b=.006,mat='frame')
 upright(label+'_mullion_front_edge',.014,2.249,.008,x=xx-.010,y=-.039,z=1.2115,r=.005,b=.002,mat='frame_edge')
 upright(label+'_mullion_left_seal',.009,2.245,.014,x=xx-.027,y=-.005,z=1.2115,r=.003,b=.002,mat='rubber')
 upright(label+'_mullion_right_seal',.009,2.245,.014,x=xx+.027,y=-.005,z=1.2115,r=.003,b=.002,mat='rubber')
for x,w,label in [(-.777,.696,'left'),(0,.716,'center'),(.777,.696,'right')]:
 upright(label+'_transparent_glass',w,2.225,.008,x=x,y=.007,z=1.2115,r=.007,b=.0016,mat='glass')
# Rounded bottom extrusion extends slightly beyond the main side posts.
rounded('bottom_graphite_rail',2.465,.163,.047,x=0,y=.002,z=.0235,r=.058,b=.010,mat='frame')
rounded('bottom_rear_edge_trim',2.437,.150,.015,x=0,y=.006,z=.049,r=.050,b=.005,mat='frame_edge')
# Rounded white top cap, dark gasket beneath it and two service hatch outlines.
rounded('top_cap_dark_gasket',2.485,.192,.036,x=0,y=.004,z=2.397,r=.082,b=.009,mat='frame')
rounded('top_white_cap',2.50,.215,.060,x=0,y=.002,z=2.442,r=.095,b=.013,mat='trim')
for x,label in [(-.430,'left'),(.430,'right')]:
 rounded(label+'_hatch_outline',.775,.150,.004,x=x,y=.005,z=2.473,r=.013,b=.0012,mat='recess')
 rounded(label+'_white_service_hatch',.754,.132,.006,x=x,y=.005,z=2.476,r=.010,b=.0017,mat='trim')
 # Thin lip runs along the rear edge, visible in the isometric reference.
 rounded(label+'_hatch_lip',.698,.013,.005,x=x,y=.065,z=2.481,r=.004,b=.0015,mat='shell')
for x,label in [(-1.077,'left'),(1.077,'right')]:
 rounded(label+'_cap_socket_recess',.108,.055,.004,x=x,y=.004,z=2.474,r=.017,b=.001,mat='recess')
 rounded(label+'_cap_socket_inner',.078,.030,.005,x=x,y=.004,z=2.477,r=.010,b=.0015,mat='socket')
# Restrained glass-edge reflections; no large graphic overlays.
for x,label in [(-1.103,'left'),(-.340,'center'),(.436,'right')]:
 upright(label+'_glass_edge_glint',.008,2.13,.0012,x=x,y=.0005,z=1.2115,r=.003,b=.0003,mat='reflection')
# Small rear corner fasteners remain discreet and separate from the main frame.
for xx in [-1.17,1.17]:
 for zz in [.051,2.37]:
  rod('rear_corner_fastener_'+str(xx)+'_'+str(zz),[xx,.057,zz],[xx,.061,zz],.0055,'steel')
# Match the coordinate system and floor origin of the previous components.
rot=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);scene.apply_transform(rot)
shift=np.eye(4);shift[0,3]=-scene.bounds[:,0].mean();shift[1,3]=-scene.bounds[0,1];scene.apply_transform(shift)
for m in scene.geometry.values():_=m.vertex_normals
scene.metadata={'asset':'Nodeworks / 06 Glass Wall Right','status':'Reference-based reconstruction; not exact 1:1','units':'meter','up_axis':'Y','origin':'bottom-center','animation':False,'glass':'alpha-blended, no physical refraction'}
path=OUT/'06-nodeworks-glass-wall-right.glb';scene.export(str(path))
s=trimesh.load(path,force='scene')
frame=s.geometry['outer_graphite_frame'].copy();frame.merge_vertices()
report={'meshes':len(s.geometry),'triangles':sum(len(m.faces) for m in s.geometry.values()),'size_bytes':path.stat().st_size,'dimensions_m':s.extents.tolist(),'bounds':s.bounds.tolist(),'finite_vertices':all(np.isfinite(m.vertices).all() for m in s.geometry.values()),'valid_face_indices':all(m.faces.max()<len(m.vertices) for m in s.geometry.values()),'frame_watertight':bool(frame.is_watertight),'frame_consistent_winding':bool(frame.is_winding_consistent),'glass_alpha_mode':s.geometry['center_transparent_glass'].visual.material.alphaMode,'glass_rgba':s.geometry['center_transparent_glass'].visual.material.baseColorFactor.tolist(),'glass_panes':3}
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
