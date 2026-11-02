import os
os.environ['PYOPENGL_PLATFORM']='egl'
import numpy as np
np.infty=np.inf
import pyrender,trimesh
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
p=Path(__file__).parent
ts=trimesh.load(p/'39-nodeworks-check-box.glb',force='scene')
sc=pyrender.Scene.from_trimesh_scene(ts,bg_color=[1.,1.,1.,1.],ambient_light=[.24,.24,.27])
def pose(eye,target):
 z=np.array(eye,dtype=float)-np.array(target);z/=np.linalg.norm(z);x=np.cross([0,1,0],z);x/=np.linalg.norm(x);y=np.cross(z,x)
 m=np.eye(4);m[:3,:3]=np.array([x,y,z]).T;m[:3,3]=eye;return m
cam=pyrender.OrthographicCamera(xmag=.095,ymag=.095)
sc.add(cam,pose=pose([.6,.7,-6.0],[0,.060,0]))
for eye,intensity in [([-3,6,4],1.5),([4,3,2],.65),([2,5,-4],.85),([-2,4,-6],1.2)]:
 sc.add(pyrender.DirectionalLight(color=[1.,1.,1.],intensity=intensity),pose=pose(eye,[0,1,0]))
ground=trimesh.creation.box(extents=[7,.001,7]);ground.apply_translation([0,-.00055,0])
ground.visual=trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(baseColorFactor=[250,251,255,255],metallicFactor=0.,roughnessFactor=.9))
# Isolated asset preview on white background.
r=pyrender.OffscreenRenderer(1300,1300)
color,_=r.render(sc,flags=0)
im=Image.fromarray(color);d=ImageDraw.Draw(im);f='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
d.text((50,38),'39 / CHECK BOX',font=ImageFont.truetype(f,30),fill='#10234a')
d.text((50,85),'Nodeworks · Reference-based 3D reconstruction',font=ImageFont.truetype(f,19),fill='#67748e')
im.save(p/'39-nodeworks-check-box-preview.png');r.delete()
