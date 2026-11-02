import os
os.environ['PYOPENGL_PLATFORM']='egl'
import numpy as np
np.infty=np.inf
import pyrender,trimesh
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
p=Path(__file__).parent
ts=trimesh.load(p/'29-nodeworks-plant-square-pot.glb',force='scene')
sc=pyrender.Scene.from_trimesh_scene(ts,bg_color=[1.,1.,1.,1.],ambient_light=[.24,.24,.27])
def pose(eye,target):
 z=np.array(eye,dtype=float)-np.array(target);z/=np.linalg.norm(z);x=np.cross([0,1,0],z);x/=np.linalg.norm(x);y=np.cross(z,x)
 m=np.eye(4);m[:3,:3]=np.array([x,y,z]).T;m[:3,3]=eye;return m
cam=pyrender.OrthographicCamera(xmag=.205,ymag=.205)
sc.add(cam,pose=pose([4.0,3.1,-5.0],[0,.135,0]))
for eye,intensity in [([-3,6,4],1.5),([4,3,2],.65),([2,5,-4],.85)]:
 sc.add(pyrender.DirectionalLight(color=[1.,1.,1.],intensity=intensity),pose=pose(eye,[0,1,0]))
ground=trimesh.creation.box(extents=[2,.001,2]);ground.apply_translation([0,-.00055,0])
ground.visual=trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(baseColorFactor=[250,251,255,255],metallicFactor=0.,roughnessFactor=.9))
sc.add(pyrender.Mesh.from_trimesh(ground))
r=pyrender.OffscreenRenderer(1300,1300)
color,_=r.render(sc,flags=pyrender.RenderFlags.SHADOWS_DIRECTIONAL)
im=Image.fromarray(color);d=ImageDraw.Draw(im);f='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
d.text((50,38),'29 / PLANT — SQUARE POT',font=ImageFont.truetype(f,30),fill='#10234a')
d.text((50,85),'Nodeworks · Reference-based 3D reconstruction',font=ImageFont.truetype(f,19),fill='#67748e')
im.save(p/'29-nodeworks-plant-square-pot-preview.png');r.delete()
