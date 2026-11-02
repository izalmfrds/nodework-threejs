NODEWORKS / 03 MAIN STRUCTURE (RIGHT)

Reference-based reconstruction from the supplied infographic.
Not an exact 1:1 reproduction. Unseen surfaces and physical dimensions are inferred.
This package includes Asset 03 only. Assets 01 and 02 were delivered separately.

Contents:
03-nodeworks-main-structure-right.glb - real 3D geometry with embedded PBR materials.
03-nodeworks-main-structure-right-preview.png - rendered from the exported GLB.
build_main_structure_right.py - reproducible model source.
render_preview.py - orthographic GLB preview renderer.
validation.json - export and re-import geometry checks.

Units: meters. Y-up. Origin at bottom-center of the overall bounding box.
Inferred dimensions: width 1.925 m, height 2.505 m, depth 0.4165 m.
63 named meshes; 27,072 triangles. GLB size: 352,280 bytes.
Two shelves and six storage boxes, recessed backing, white frame, top cap,
blue vertical inlay and separate external support rod.
Box bodies, lids, handles, lid labels and catches are separate named parts.
The large opening is true geometry. Main frame passes closed-surface and winding checks.
No rig or animation is included. No external texture dependencies.
Lights, ground plane and camera belong to the preview and are not in the GLB.

Model dependencies: numpy, trimesh, shapely, mapbox_earcut, triangle.
Preview dependencies: pyrender, PyOpenGL >= 3.1.7, Pillow, EGL, networkx.
