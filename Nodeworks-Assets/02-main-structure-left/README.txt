NODEWORKS / 02 MAIN STRUCTURE (LEFT)

Reference-based reconstruction from the supplied infographic.
Not an exact 1:1 reproduction. Unseen surfaces and physical dimensions are inferred.
This package includes Asset 02 only; Base Floor was delivered separately.

Contents:
02-nodeworks-main-structure-left.glb - real 3D geometry, embedded PBR materials.
02-nodeworks-main-structure-left-preview.png - rendered from the exported GLB.
build_main_structure_left.py - reproducible model source.
render_preview.py - orthographic GLB preview renderer.
validation.json - re-import geometry checks.

Y-up, meters, origin at bottom-center of the overall bounding box.
Approximate dimensions: width 2.20 m, height 2.5115 m, depth 0.4605 m.
45 named meshes; 24,068 triangles. No rig or animation.
The doorway is open geometry; the shelving niche has actual depth.
No external textures, lights, or cameras are included in the GLB.
Rendering requires your own scene lighting.

Source dependencies: numpy, trimesh, shapely, mapbox_earcut.
Preview dependencies: pyrender, PyOpenGL >= 3.1.7, Pillow, EGL.
