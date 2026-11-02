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

materials['list_gray']=PBRMaterial(name='raised_gray_checklist_lines',baseColorFactor=[95,108,137,255],metallicFactor=.02,roughnessFactor=.55)
# White housing follows the dimensions and finish of the companion Problem Board.
upright('white_solution_board_housing',1.90,1.60,.140,z=.800,r=.137,b=.025,mat='shell')
upright('white_front_face',1.855,1.555,.020,y=-.070,z=.800,r=.121,b=.007,mat='trim')
upright('rear_cover',1.795,1.495,.015,y=.071,z=.800,r=.110,b=.005,mat='panel')
# Rounded blue header badge with a true raised white check symbol.
profile=[[0,-.021],[.155,-.021],[.165,-.017],[.171,-.009],[.171,.009],[.165,.017],[.155,.021],[0,.021]]
badge=trimesh.creation.revolve(np.array(profile),sections=64)
t=np.array([[1,0,0,-.635],[0,0,-1,-.102],[0,1,0,1.265],[0,0,0,1]],float);badge.apply_transform(t)
badge=trimesh.graph.smooth_shade(badge,angle=math.radians(35),facet_minarea=50);add(badge,'blue_solution_badge','icon_blue')
check=LineString([(-.081,.009),(-.024,-.058),(.088,.069)]).buffer(.019,cap_style='round',join_style='round')
relief('white_header_check',check,.008,-.124,x=-.635,z=1.265,mat='trim')
text_relief('solution_title','Solution',1.020,.238,.120,1.265,-.082,.014,'ink')
# Four individual ascending bars. The reference has no axes or numerical labels.
bar_bottom=.315
for k,(x,height) in enumerate([(-.707,.225),(-.488,.337),(-.269,.449),(-.050,.562)],1):
 upright('chart_bar_'+str(k),.149,height,.042,x=x,y=-.101,z=bar_bottom+height/2,r=.014,b=.007,mat='icon_blue' if k%2==0 else 'blue')
# Raised zig-zag trend and arrowhead. Preserved as one named mesh.
points=[(-.779,.641),(-.705,.659),(-.657,.647),(-.550,.766),(-.458,.735),(-.324,.877),(-.233,.842),(-.078,.978),(.025,1.055)]
stroke=LineString(points).buffer(.013,cap_style='round',join_style='round')
end=np.array(points[-1]);direction=end-np.array(points[-2]);direction/=np.linalg.norm(direction);perp=np.array([-direction[1],direction[0]])
base=end-direction*.071
head=LineString([base+perp*.033,end,base-perp*.033]).buffer(.013,cap_style='flat',join_style='mitre')
relief('rising_chart_trend_arrow',stroke.union(head),.017,-.083,mat='icon_blue')
# Three cobalt checklist tiles and corresponding gray placeholder text lines.
for k,z in enumerate([.913,.620,.327],1):
 upright('checklist_'+str(k)+'_blue_tile',.155,.157,.028,x=.331,y=-.095,z=z,r=.018,b=.006,mat='icon_blue')
 smallcheck=LineString([(-.042,.004),(-.014,-.031),(.046,.037)]).buffer(.010,cap_style='round',join_style='round')
 relief('checklist_'+str(k)+'_white_check',smallcheck,.007,-.111,x=.331,z=z,mat='trim')
 upright('checklist_'+str(k)+'_gray_line',.337,.046,.010,x=.664,y=-.087,z=z,r=.006,b=.003,mat='list_gray')
# Y-up, meter units, floor-centered origin to match the previously exported set.
rot=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);scene.apply_transform(rot)
shift=np.eye(4);shift[0,3]=-scene.bounds[:,0].mean();shift[1,3]=-scene.bounds[0,1];scene.apply_transform(shift)
for mesh in scene.geometry.values():_=mesh.vertex_normals
scene.metadata={'asset':'Nodeworks / 12 Solution Board','status':'Reference-based reconstruction; not exact 1:1','units':'meter','up_axis':'Y','origin':'bottom-center','animation':False,'lettering':'extruded DejaVu Sans Bold; reference font approximated'}
path=OUT/'12-nodeworks-solution-board.glb';scene.export(str(path))
s=trimesh.load(path,force='scene')
checks={}
for name in ['white_solution_board_housing','blue_solution_badge','chart_bar_1','chart_bar_4','rising_chart_trend_arrow']:
 mesh=s.geometry[name].copy();mesh.merge_vertices();checks[name]=bool(mesh.is_watertight and mesh.is_winding_consistent)
report={'meshes':len(s.geometry),'triangles':sum(len(mesh.faces) for mesh in s.geometry.values()),'size_bytes':path.stat().st_size,'dimensions_m':s.extents.tolist(),'bounds':s.bounds.tolist(),'finite_vertices':all(np.isfinite(mesh.vertices).all() for mesh in s.geometry.values()),'valid_face_indices':all(mesh.faces.max()<len(mesh.vertices) for mesh in s.geometry.values()),'closed_and_consistent_meshes':checks,'text_geometry':['Solution'],'chart_bars':4,'checklist_rows':3,'external_textures':False}
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
