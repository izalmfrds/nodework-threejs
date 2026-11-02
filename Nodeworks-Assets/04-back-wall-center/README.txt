NODEWORKS / 04 BACK WALL (CENTER)

Reference-based reconstruction from the supplied infographic.
Not an exact 1:1 reproduction. Unseen surfaces and physical dimensions are inferred.
This package includes Asset 04 only. Assets 01-03 were delivered separately.

Contents:
04-nodeworks-back-wall-center.glb - real 3D geometry with embedded PBR materials.
04-nodeworks-back-wall-center-preview.png - rendered from the exported GLB.
build_back_wall_center.py - reproducible model source.
render_preview.py - orthographic GLB preview renderer.
validation.json - export and re-import geometry checks.

Units: meters. Y-up. Origin at bottom-center of overall bounding box.
Inferred dimensions: width 2.812 m, height 1.884 m, depth 0.398 m.
29 named meshes; 24,288 triangles. GLB size: 413,576 bytes.
Continuous rounded housing, rear cover, raised white annular bezel,
recessed matte charcoal center, top service covers and left side port details.
The white bezel is actual annular geometry; its center is open.
The exported bezel passes closed-surface and consistent-winding checks.
No rig, animation, external textures, lights, or camera are included in the GLB.
The preview's ground and lighting belong only to the render.

Model dependencies: numpy, trimesh, shapely, mapbox_earcut, triangle.
Preview dependencies: pyrender, PyOpenGL >= 3.1.7, Pillow, EGL, networkx.
