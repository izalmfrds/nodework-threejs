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

def add(mesh,name,mat):
 mesh.visual=TextureVisuals(material=materials[mat]);scene.add_geometry(mesh,node_name=name,geom_name=name);return mesh

def rod(name,p1,p2,r,mat='steel',sections=24):
 return add(trimesh.creation.cylinder(radius=r,sections=sections,segment=np.array([p1,p2])),name,mat)

def upright(name,w,h,depth,x=0,y=0,z=0,r=.04,b=.008,mat='shell'):
 mesh=rounded(name,w,h,depth,r=r,b=b,mat=mat)
 transform=np.array([[1,0,0,x],[0,0,-1,y],[0,1,0,z],[0,0,0,1]],dtype=float)
 mesh.apply_transform(transform)
 return mesh

# Nodeworks branding lockup, reconstructed from the supplied component sheet.
materials['white']=PBRMaterial(name='white_logo_nodes',baseColorFactor=[247,251,255,255],metallicFactor=0.,roughnessFactor=.43)
materials['cobalt']=PBRMaterial(name='cobalt_logo_emblem',baseColorFactor=[0,25,255,255],metallicFactor=.02,roughnessFactor=.37)
materials['navy']=PBRMaterial(name='navy_nodeworks_wordmark',baseColorFactor=[0,1,16,255],metallicFactor=0.,roughnessFactor=.58)
upright('rounded_cobalt_logo_emblem',.180,.180,.018,x=.250,y=0,z=.090,r=.039,b=.004,mat='cobalt')
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import unary_union
from shapely.affinity import scale,translate
# Raised white node mark: six spokes and round ends.
pieces=[Point(.250,.090).buffer(.005,quad_segs=12)]
for angle in [90,30,-30,-90,-150,150]:
 a=math.radians(angle);x=.250+.046*math.cos(a);z=.090+.046*math.sin(a)
 pieces.append(LineString([(.250,.090),(x,z)]).buffer(.003,cap_style='round',quad_segs=8))
 pieces.append(Point(x,z).buffer(.0075,quad_segs=12))
def piece(name,poly,depth,front,mat):
 parts=list(poly.geoms) if poly.geom_type=='MultiPolygon' else [poly]
 mesh=trimesh.util.concatenate([trimesh.creation.extrude_polygon(part,height=depth,engine='triangle') for part in parts])
 matrix=np.array([[1,0,0,0],[0,0,-1,front],[0,1,0,0],[0,0,0,1]],float)
 mesh.apply_transform(matrix);mesh.fix_normals();mesh.unmerge_vertices();return add(mesh,name,mat)
piece('white_six_spoke_logo_mark',unary_union(pieces),.004,.013,'white')
# Typeface is an approximation: the original font source was not supplied.
# Convert font contours, preserving interior counters, into solid 3D geometry.
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
font=FontProperties(fname=str(OUT/'DejaVuSans-Bold.ttf'))
path=TextPath((0,0),'Nodeworks',size=100,prop=font)
word=None
for contour in path.to_polygons():
 poly=Polygon(contour)
 if not poly.is_valid:poly=poly.buffer(0)
 if poly.is_empty:continue
 word=poly if word is None else word.symmetric_difference(poly)
word=word.buffer(0)
x0,z0,x1,z1=word.bounds
factor=.078/(z1-z0)
word=translate(word,xoff=-x0,yoff=-z0);word=scale(word,xfact=-factor*.75,yfact=factor,origin=(0,0));word=translate(word,xoff=.128,yoff=.055)
piece('navy_nodeworks_wordmark',word,.006,.010,'navy')
rot=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]);scene.apply_transform(rot)
shift=np.eye(4);shift[0,3]=-scene.bounds[:,0].mean();scene.apply_transform(shift)
for mesh in scene.geometry.values():_=mesh.vertex_normals
scene.metadata={'asset':'Nodeworks / 42 Nodeworks Logo','status':'Reference-based reconstruction; not exact 1:1','units':'meter','up_axis':'Y','origin':'bottom-center','animation':False,'external_textures':False}
f=OUT/'42-nodeworks-logo.glb';scene.export(str(f))
s=trimesh.load(f,force='scene');checks={}
for name in s.geometry:
 m=s.geometry[name].copy();m.merge_vertices();checks[name]=bool(m.is_watertight and m.is_winding_consistent)
report={'meshes':len(s.geometry),'triangles':sum(len(m.faces) for m in s.geometry.values()),'size_bytes':f.stat().st_size,'dimensions_m':s.extents.tolist(),'finite_vertices':all(np.isfinite(m.vertices).all() for m in s.geometry.values()),'valid_face_indices':all(m.faces.max()<len(m.vertices) for m in s.geometry.values()),'closed_and_consistent_meshes':checks,'external_textures':False,'animation':False}
assert report['finite_vertices'] and report['valid_face_indices'] and all(checks.values())
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
