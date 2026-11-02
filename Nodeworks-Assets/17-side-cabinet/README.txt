NODEWORKS / 17 SIDE CABINET

Reference-based reconstruction from the supplied infographic.
Not an exact 1:1 reproduction. Unseen surfaces and physical dimensions are inferred.
This package includes Asset 17 only. Assets 01-16 were delivered separately.

Contents:
17-nodeworks-side-cabinet.glb - actual 3D geometry with embedded PBR materials.
17-nodeworks-side-cabinet-preview.png - rendered from the exported GLB.
build_side_cabinet.py - reproducible model source.
render_preview.py - orthographic GLB preview renderer.
validation.json - export and re-import geometry checks.

Units: meters. Y-up. Origin at bottom-center of the bounding box.
Inferred dimensions: width 0.800 m, height 0.718 m, depth 0.517 m.
6 named meshes; 3,740 triangles. GLB size: 106,580 bytes.
Rounded white body, top lid, thin dark recessed plinth, plain rear cover,
L-shaped blue front inlay and a small open blue upper handle.
The body has a real subtractive front channel; the blue insert is inset into it.
The rear cover and full cabinet depth are inferred from the visible front/left/top view.
All six meshes pass closed-surface and winding checks after welding shading seams.
The exported GLB was re-imported to verify geometry, indices and materials.

No rig, animation, door hinges, external textures, scene lights, floor or camera are in the GLB.
Cabinet body, lid, blue inlay and handle remain separate named components.
Model dependencies: numpy, trimesh, shapely, triangle, manifold3d.
Preview dependencies: pyrender, PyOpenGL >= 3.1.7, Pillow, EGL, networkx.
