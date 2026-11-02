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

from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
materials['navy']=PBRMaterial(name='deep_blue_board_face',baseColorFactor=[0,4,42,255],metallicFactor=.03,roughnessFactor=.41,emissiveFactor=[0,.004,.02])
materials['ink']=PBRMaterial(name='near_black_card_labels',baseColorFactor=[1,2,4,255],metallicFactor=0.,roughnessFactor=.72)
materials['icon_blue']=PBRMaterial(name='cobalt_icon_blue',baseColorFactor=[0,18,255,255],metallicFactor=.03,roughnessFactor=.34)
materials['icon_cyan']=PBRMaterial(name='design_top_blue',baseColorFactor=[0,65,255,255],metallicFactor=.03,roughnessFactor=.34)

def relief(name,shape,depth,y,x=0,z=0,mat='icon_blue'):
 shapes=[shape] if shape.geom_type=='Polygon' else list(shape.geoms)
 meshes=[]
 for poly in shapes:
  if poly.is_empty or poly.area<1e-9:continue
  mesh=trimesh.creation.extrude_polygon(poly,height=depth,engine='triangle')
  t=np.array([[1,0,0,x],[0,0,-1,y],[0,1,0,z],[0,0,0,1]],float);mesh.apply_transform(t);meshes.append(mesh)
 mesh=trimesh.util.concatenate(meshes)
 mesh=trimesh.graph.smooth_shade(mesh,angle=math.radians(35),facet_minarea=50)
 return add(mesh,name,mat)

def text_relief(name,label,width,height,x,z,y,depth,mat):
 prop=FontProperties(fname='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
 outline=TextPath((0,0),label,size=1,prop=prop)
 # Symmetric difference preserves holes in letters such as B, D, e and g.
 shape=Polygon()
 for points in outline.to_polygons():
  poly=Polygon(points)
  if not poly.is_valid:poly=poly.buffer(0)
  shape=shape.symmetric_difference(poly)
 from shapely import affinity
 a,b,c,d=shape.bounds
 shape=affinity.translate(shape,xoff=-(a+c)/2,yoff=-(b+d)/2)
 shape=affinity.scale(shape,xfact=width/(c-a),yfact=height/(d-b),origin=(0,0))
 return relief(name,shape,depth,y,x=x,z=z,mat=mat)

from shapely.geometry import Point,box
materials['list_gray']=PBRMaterial(name='raised_gray_list_lines',baseColorFactor=[95,108,137,255],metallicFactor=.02,roughnessFactor=.55)
materials['subtle_inset']=PBRMaterial(name='checkbox_subtle_inset',baseColorFactor=[191,201,223,255],metallicFactor=0.,roughnessFactor=.65)
# Compact rounded white panel and its slightly inset front and rear faces.
upright('white_problem_board_housing',1.90,1.60,.140,z=.800,r=.137,b=.025,mat='shell')
upright('white_front_face',1.855,1.555,.020,y=-.070,z=.800,r=.121,b=.007,mat='trim')
upright('rear_cover',1.795,1.495,.015,y=.071,z=.800,r=.110,b=.005,mat='panel')
# Rounded blue badge with a white extruded exclamation mark.
# Revolve a bevelled cross-section for a flat-faced, softly rounded disk.
profile=[[0,-.021],[.155,-.021],[.165,-.017],[.171,-.009],[.171,.009],[.165,.017],[.155,.021],[0,.021]]
badge=trimesh.creation.revolve(np.array(profile),sections=64)
# Revolve uses the Z axis; map the disk face to the front (-Y) of the panel.
t=np.array([[1,0,0,-.635],[0,0,-1,-.102],[0,1,0,1.265],[0,0,0,1]],float);badge.apply_transform(t)
badge=trimesh.graph.smooth_shade(badge,angle=math.radians(35),facet_minarea=50)
add(badge,'blue_problem_badge','icon_blue')
stem=Polygon([(-.024,.110),(.024,.110),(.017,-.048),(-.017,-.048)]).buffer(.002,join_style='round')
mark=stem.union(Point(0,-.089).buffer(.022,quad_segs=16))
relief('white_exclamation_mark',mark,.008,-.124,x=-.635,z=1.266,mat='trim')
text_relief('problem_title','Problem',.945,.238,.080,1.265,-.082,.014,'ink')
# Three unmarked white checkboxes and raised gray placeholder lines.
for k,z in enumerate([.855,.565,.275],1):
 upright('row_'+str(k)+'_checkbox',.145,.150,.022,x=-.701,y=-.093,z=z,r=.013,b=.005,mat='trim')
 upright('row_'+str(k)+'_checkbox_inner',.044,.044,.002,x=-.701,y=-.105,z=z,r=.007,b=.0006,mat='subtle_inset')
 upright('row_'+str(k)+'_primary_gray_line',.610,.044,.010,x=-.234,y=-.087,z=z+.037,r=.008,b=.003,mat='list_gray')
 if k<3:
  upright('row_'+str(k)+'_secondary_gray_line',.405,.031,.008,x=-.3365,y=-.087,z=z-.024,r=.006,b=.002,mat='list_gray')
# Three stacked cobalt status blocks; the lower two have real top notches.
x=.587;w=.440;h=.180
upright('status_block_1',w,h,.030,x=x,y=-.098,z=.869,r=.021,b=.007,mat='icon_blue')
upright('status_block_1_white_label',.127,.035,.008,x=x-.080,y=-.117,z=.852,r=.005,b=.002,mat='trim')
upright('status_block_1_small_indicator',.018,.013,.004,x=x+.158,y=-.116,z=.872,r=.004,b=.001,mat='icon_cyan')
for k,z,notch_h in [(2,.579,.065),(3,.289,.053)]:
 body=box(-w/2,-h/2,w/2,h/2)
 notch=box(-.147,h/2-notch_h,.147,h/2+.02)
 silhouette=body.difference(notch).buffer(.008,join_style='round')
 relief('status_block_'+str(k)+'_notched_body',silhouette,.031,-.083,x=x,z=z,mat='icon_blue')
 # The pale insert sits inside the top recess and remains an independent mesh.
 upright('status_block_'+str(k)+'_white_insert',.250,notch_h-.012,.010,x=x-.003,y=-.107,z=z+h/2-notch_h/2+.003,r=.006,b=.002,mat='trim')
# Export conventions consistent with Assets 01-10.
rot=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);scene.apply_transform(rot)
shift=np.eye(4);shift[0,3]=-scene.bounds[:,0].mean();shift[1,3]=-scene.bounds[0,1];scene.apply_transform(shift)
for mesh in scene.geometry.values():_=mesh.vertex_normals
scene.metadata={'asset':'Nodeworks / 11 Problem Board','status':'Reference-based reconstruction; not exact 1:1','units':'meter','up_axis':'Y','origin':'bottom-center','animation':False,'lettering':'extruded DejaVu Sans Bold; reference font approximated'}
path=OUT/'11-nodeworks-problem-board.glb';scene.export(str(path))
s=trimesh.load(path,force='scene')
checks={}
for name in ['white_problem_board_housing','blue_problem_badge','status_block_2_notched_body','status_block_3_notched_body']:
 mesh=s.geometry[name].copy();mesh.merge_vertices();checks[name]=bool(mesh.is_watertight and mesh.is_winding_consistent)
report={'meshes':len(s.geometry),'triangles':sum(len(mesh.faces) for mesh in s.geometry.values()),'size_bytes':path.stat().st_size,'dimensions_m':s.extents.tolist(),'bounds':s.bounds.tolist(),'finite_vertices':all(np.isfinite(mesh.vertices).all() for mesh in s.geometry.values()),'valid_face_indices':all(mesh.faces.max()<len(mesh.vertices) for mesh in s.geometry.values()),'closed_and_consistent_meshes':checks,'text_geometry':['Problem','!'],'external_textures':False}
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
