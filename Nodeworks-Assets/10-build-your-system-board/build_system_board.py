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

def code_icon(name,x,z,y,w=.40,h=.24,mat='icon_blue'):
 # Scalable </> mark, with all three strokes extruded as one named icon.
 sx=w/.44;sz=h/.24
 paths=[[(-.12,.10),(-.21,0),(-.12,-.10)],[(.12,.10),(.21,0),(.12,-.10)],[(-.033,-.12),(.033,.12)]]
 pieces=[]
 for path in paths:pieces.append(LineString([(a*sx,b*sz) for a,b in path]).buffer(.019*min(sx,sz),cap_style='flat',join_style='round'))
 return relief(name,unary_union(pieces),.018,y,x=x,z=z,mat=mat)

# Broad rounded white housing with an inset navy face and a fine pale border.
upright('white_board_housing',3.20,2.04,.170,z=1.02,r=.155,b=.029,mat='shell')
upright('white_front_border',3.155,1.995,.022,y=-.084,z=1.02,r=.142,b=.007,mat='trim')
upright('navy_main_face',3.055,1.895,.026,y=-.100,z=1.02,r=.121,b=.008,mat='navy')
upright('rear_board_cover',3.07,1.91,.016,y=.086,z=1.02,r=.125,b=.005,mat='panel')
# Three raised square-ish white cards, deliberately distinct scene meshes.
for x,label in [(-.925,'design'),(0,'build'),(.925,'integrate')]:
 upright(label+'_white_card',.840,1.095,.085,x=x,y=-.1555,z=.8175,r=.115,b=.019,mat='trim')
# Header: separate code symbol and complete extruded white title.
code_icon('header_code_icon',-1.16,1.664,-.115,w=.375,h=.240,mat='trim')
text_relief('header_build_your_system','Build Your System',2.22,.235,.240,1.663,-.115,.014,'trim')
# Three stacked blue diamond shapes, matching the Design card.
for zz,mat,k in [(.951,'icon_blue',1),(1.022,'icon_blue',2),(1.093,'icon_cyan',3)]:
 diamond=Polygon([(-.197,0),(0,.095),(.197,0),(0,-.095)]).buffer(.010,join_style='round')
 relief('design_stack_layer_'+str(k),diamond,.024,-.201-.006*(k-1),x=-.925,z=zz,mat=mat)
# Center Build icon.
code_icon('build_card_code_icon',0,1.033,-.201,w=.407,h=.288,mat='icon_blue')
# Integrate icon: six rounded radial spokes with circular endpoints.
parts=[];cx=.925;cz=1.037;yy=-.216
for i in range(6):
 a=math.radians(90+i*60);end=np.array([cx+math.cos(a)*.169,yy,cz+math.sin(a)*.169])
 parts.append(trimesh.creation.cylinder(radius=.0125,sections=16,segment=[[cx,yy,cz],end]))
 ball=trimesh.creation.icosphere(subdivisions=2,radius=.027);ball.apply_translation(end);parts.append(ball)
hub=trimesh.creation.icosphere(subdivisions=2,radius=.031);hub.apply_translation([cx,yy,cz]);parts.append(hub)
add(trimesh.util.concatenate(parts),'integrate_network_icon','icon_blue')
# All card labels remain real extruded letter geometry.
text_relief('design_card_label','Design',.595,.187,-.925,.542,-.200,.012,'ink')
text_relief('build_card_label','Build',.451,.187,0,.542,-.200,.012,'ink')
text_relief('integrate_card_label','Integrate',.724,.180,.925,.542,-.200,.012,'ink')
# Match Y-up coordinates and bottom-center origin of Assets 01-09.
rot=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);scene.apply_transform(rot)
shift=np.eye(4);shift[0,3]=-scene.bounds[:,0].mean();shift[1,3]=-scene.bounds[0,1];scene.apply_transform(shift)
for m in scene.geometry.values():_=m.vertex_normals
scene.metadata={'asset':'Nodeworks / 10 Build Your System Board','status':'Reference-based reconstruction; not exact 1:1','units':'meter','up_axis':'Y','origin':'bottom-center','animation':False,'lettering':'extruded DejaVu Sans Bold; reference font approximated'}
path=OUT/'10-nodeworks-build-your-system-board.glb';scene.export(str(path))
s=trimesh.load(path,force='scene')
checks={}
for name in ['white_board_housing','design_white_card','build_white_card','integrate_white_card']:
 m=s.geometry[name].copy();m.merge_vertices();checks[name]=bool(m.is_watertight and m.is_winding_consistent)
report={'meshes':len(s.geometry),'triangles':sum(len(m.faces) for m in s.geometry.values()),'size_bytes':path.stat().st_size,'dimensions_m':s.extents.tolist(),'bounds':s.bounds.tolist(),'finite_vertices':all(np.isfinite(m.vertices).all() for m in s.geometry.values()),'valid_face_indices':all(m.faces.max()<len(m.vertices) for m in s.geometry.values()),'housing_and_cards_closed_and_consistent':checks,'text_geometry':['Build Your System','Design','Build','Integrate'],'external_textures':False}
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
