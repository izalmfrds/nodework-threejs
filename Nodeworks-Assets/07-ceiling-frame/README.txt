NODEWORKS / 07 CEILING FRAME

Reference-based reconstruction from the supplied infographic.
Not an exact 1:1 reproduction. Unseen surfaces and physical dimensions are inferred.
This package includes Asset 07 only. Assets 01-06 were delivered separately.

Contents:
07-nodeworks-ceiling-frame.glb - actual 3D geometry with embedded PBR materials.
07-nodeworks-ceiling-frame-preview.png - rendered from the exported GLB.
build_ceiling_frame.py - reproducible model source.
render_preview.py - orthographic GLB preview renderer.
validation.json - export and re-import geometry checks.

Units: meters. Y-up. Origin at bottom-center of the bounding box.
Inferred dimensions: width 3.040 m, height 0.6068 m, depth 0.3515 m.
14 named meshes; 11,754 triangles. GLB size: 323,220 bytes.
Three-section white casing: long crossbeam and two downturned end brackets.
Four sockets are genuinely subtracted from the bracket geometry: two at the top,
one on the left exterior face, one on the right interior face.
Dark inserts sit inside the sockets. An additional upper-bevel port is a surface detail.
The brackets pass closed-surface and winding checks after merging shading seams.
The file was re-imported to verify geometry and embedded materials.

No rig, animation, external textures, lights, floor, or camera are included in the GLB.
Set its ceiling position in the assembled scene; the origin is at the bracket base.
Model dependencies: numpy, trimesh, shapely, triangle, manifold3d.
Preview dependencies: pyrender, PyOpenGL >= 3.1.7, Pillow, EGL, networkx.
