from pathlib import Path
import math,json
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial
from trimesh.visual import TextureVisuals
OUT=Path(__file__).parent
scene=trimesh.Scene()
materials={}
for name,col,rough,metal in [('shell','#e2e7f5',.32,.06),('panel','#d7ddec',.42,.02),('trim','#f2f5ff',.28,.04),('blue','#0054ff',.25,.12),('gasket','#344053',.65,.05),('recess','#747f95',.48,.1),('steel','#a7b2c8',.3,.55)]:
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

# 3.6m x 2.5m inferred proportions. Top at 0.16m; origin at floor contact.
rounded('lower_perimeter_gasket',3.54,2.44,.040,z=.035,r=.17,b=.008,mat='gasket')
rounded('main_rounded_chassis',3.60,2.50,.124,z=.096,r=.20,b=.023)
rounded('panel_recess',3.16,2.07,.020,z=.152,r=.08,b=.004,mat='recess')
# Five long panels, each split at the center joint. Thin real gaps expose dark bed.
for i in range(5):
 for j in range(2):
  rounded(f'floor_panel_{i+1}_{j+1}',.618,1.018,.025,x=(i-2)*.628,y=(j-.5)*1.035,z=.162,r=.016,b=.005,mat='panel')
# Perimeter rails match the broad pale rim.
for yy,label in [(-1.151,'front'),(1.151,'back')]:
 rounded(label+'_rail',3.21,.198,.033,y=yy,z=.153,r=.025,b=.007)
for xx,label in [(-1.686,'left'),(1.686,'right')]:
 rounded(label+'_rail',.228,2.12,.033,x=xx,z=.153,r=.035,b=.007)
# Raised coupling sleeves and inset blue strips on front and rear.
for yy,label in [(-1.155,'front'),(1.155,'back')]:
 for xx,k in [(-.99,1),(.99,2)]:
  rounded(f'{label}_coupler_{k}',.74,.224,.076,x=xx,y=yy,z=.131,r=.022,b=.008,mat='trim')
  rounded(f'{label}_led_socket_{k}',.657,.070,.007,x=xx,y=yy,z=.172,r=.016,b=.002,mat='recess')
  rounded(f'{label}_blue_inlay_{k}',.630,.049,.008,x=xx,y=yy,z=.177,r=.012,b=.002,mat='blue')
  rounded(f'{label}_lower_slot_{k}',.54,.012,.020,x=xx,y=yy+(-.115 if yy<0 else .115),z=.098,r=.005,b=.003,mat='recess')
  rounded(f'{label}_slot_insert_{k}',.43,.014,.007,x=xx,y=yy+(-.122 if yy<0 else .122),z=.094,r=.003,b=.002,mat='steel')
# One blue inlay on left edge, aligned along the depth.
rounded('left_led_socket',.082,.77,.008,x=-1.688,y=-.12,z=.173,r=.018,b=.002,mat='recess')
rounded('left_blue_inlay',.058,.74,.009,x=-1.688,y=-.12,z=.178,r=.015,b=.002,mat='blue')
# Visible mechanical joints, edge recesses, and discreet mounting hardware.
for yy,label in [(-1.249,'front'),(1.249,'back')]:
 for k,xx in enumerate([-1.40,-.57,.57,1.40]):
  rounded(f'{label}_edge_joint_{k}',.034,.014,.055,x=xx,y=yy,z=.098,r=.005,b=.003,mat='recess')
for xx,label in [(-1.799,'left'),(1.799,'right')]:
 for k,yy in enumerate([-.84,.74]):
  rounded(f'{label}_dark_port_{k}',.014,.18,.039,x=xx,y=yy,z=.073,r=.006,b=.003,mat='gasket')
  rounded(f'{label}_port_center_{k}',.016,.10,.015,x=xx,y=yy,z=.076,r=.004,b=.003,mat='steel')
for xx in [-1.62,1.62]:
 for yy in [-1.08,1.08]:
  rounded(f'corner_foot_{xx}_{yy}',.22,.17,.025,x=xx,y=yy,z=.013,r=.035,b=.005,mat='gasket')
# Convert to glTF convention: Y-up, front -Z.
rot=trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0])
scene.apply_transform(rot)
scene.metadata={'asset':'Nodeworks / 01 Base Floor','status':'Reference-based reconstruction; not certified 1:1','units':'meter','up_axis':'Y','origin':'bottom-center','dimensions_m':[3.6,.182,2.5]}
scene.export(str(OUT/'01-nodeworks-base-floor.glb'))
# Validate binary and bounds by loading the exported file.
loaded=trimesh.load(OUT/'01-nodeworks-base-floor.glb',force='scene')
report={'meshes':len(loaded.geometry),'triangles':sum(len(m.faces) for m in loaded.geometry.values()),'size_bytes':(OUT/'01-nodeworks-base-floor.glb').stat().st_size,'bounds':loaded.bounds.tolist(),'materials':len(materials)}
(OUT/'validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
