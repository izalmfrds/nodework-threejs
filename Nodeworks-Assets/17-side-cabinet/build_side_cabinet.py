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
 verts=[]; rings=[]; seg=9
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

from shapely.geometry import LineString,box
materials['cabinet_white']=PBRMaterial(name='satin_white_side_cabinet',baseColorFactor=[235,241,252,255],metallicFactor=.03,roughnessFactor=.43)
materials['accent_blue']=PBRMaterial(name='cobalt_blue_cabinet_inlay',baseColorFactor=[0,17,255,255],metallicFactor=.04,roughnessFactor=.34)
materials['plinth_dark']=PBRMaterial(name='thin_dark_bottom_plinth',baseColorFactor=[4,6,11,255],metallicFactor=0.,roughnessFactor=.76)

def profile_mesh(shape,depth,y):
 mesh=trimesh.creation.extrude_polygon(shape,height=depth,engine='triangle')
 t=np.array([[1,0,0,0],[0,0,-1,y],[0,1,0,0],[0,0,0,1]],float);mesh.apply_transform(t);return mesh

# Smooth rounded white cabinet with a subtle lid seam and a thin dark floor plinth.
body=rounded('white_cabinet_body',.800,.500,.680,x=0,y=0,z=.358,r=.059,b=.027,mat='cabinet_white')
rounded('white_top_lid',.800,.500,.027,x=0,y=0,z=.7045,r=.059,b=.008,mat='trim')
rounded('dark_recessed_bottom_plinth',.758,.458,.020,x=0,y=0,z=.010,r=.035,b=.005,mat='plinth_dark')
# Reference's L-shaped blue stripe is inset into an actual shallow front channel.
curve=[(-.222,.018),(-.222,.473)]
curve += [(-.103+.119*math.cos(a),.473+.119*math.sin(a)) for a in np.linspace(math.pi,math.pi/2,25)]
curve += [(.335,.592)]
path=LineString(curve)
channel=path.buffer(.026,cap_style='flat',join_style='round')
cutter=profile_mesh(channel,.031,-.233)
body=body.copy();body.merge_vertices();body.fix_normals();assert body.is_watertight
carved=trimesh.boolean.difference([body,cutter],engine='manifold')
carved=trimesh.graph.smooth_shade(carved,angle=math.radians(35),facet_minarea=50)
carved.visual=TextureVisuals(material=materials['cabinet_white']);_=carved.vertex_normals
scene.geometry['white_cabinet_body']=carved
blue=profile_mesh(path.buffer(.022,cap_style='flat',join_style='round'),.013,-.2355)
blue=trimesh.graph.smooth_shade(blue,angle=math.radians(35),facet_minarea=50);add(blue,'recessed_L_shaped_blue_inlay','accent_blue')
# Small open blue handle above the stripe near the right-hand corner.
outer=box(.160,.607,.329,.686).buffer(.009,join_style='round')
inner=box(.179,.620,.310,.664).buffer(.005,join_style='round')
handle=profile_mesh(outer.difference(inner),.011,-.250)
handle=trimesh.graph.smooth_shade(handle,angle=math.radians(35),facet_minarea=50);add(handle,'upper_blue_handle_frame','accent_blue')
# Inset rear cover is inferred; the reference only shows the front, left and top.
upright('plain_rear_cover',.717,.602,.012,x=0,y=.250,z=.355,r=.032,b=.004,mat='shell')
# Same coordinate convention and bottom-center origin as Assets 01-16.
rot=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);scene.apply_transform(rot)
shift=np.eye(4);shift[0,3]=-scene.bounds[:,0].mean();shift[1,3]=-scene.bounds[0,1];scene.apply_transform(shift)
for mesh in scene.geometry.values():_=mesh.vertex_normals
scene.metadata={'asset':'Nodeworks / 17 Side Cabinet','status':'Reference-based reconstruction; not exact 1:1','units':'meter','up_axis':'Y','origin':'bottom-center','animation':False}
file=OUT/'17-nodeworks-side-cabinet.glb';scene.export(str(file))
s=trimesh.load(file,force='scene');checks={}
for name,mesh in s.geometry.items():
 m=mesh.copy();m.merge_vertices();checks[name]=bool(m.is_watertight and m.is_winding_consistent)
report={'meshes':len(s.geometry),'triangles':sum(len(mesh.faces) for mesh in s.geometry.values()),'size_bytes':file.stat().st_size,'dimensions_m':s.extents.tolist(),'bounds':s.bounds.tolist(),'finite_vertices':all(np.isfinite(mesh.vertices).all() for mesh in s.geometry.values()),'valid_face_indices':all(mesh.faces.max()<len(mesh.vertices) for mesh in s.geometry.values()),'closed_and_consistent_meshes':checks,'subtractive_front_channel':True,'external_textures':False}
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
