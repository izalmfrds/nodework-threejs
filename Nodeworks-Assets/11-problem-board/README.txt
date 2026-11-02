NODEWORKS / 11 PROBLEM BOARD

Reference-based reconstruction from the supplied infographic.
Not an exact 1:1 reproduction. Unseen surfaces, dimensions and reference font are inferred.
This package includes Asset 11 only. Assets 01-10 were delivered separately.

Contents:
11-nodeworks-problem-board.glb - actual 3D geometry with embedded materials.
11-nodeworks-problem-board-preview.png - rendered from the exported GLB.
build_problem_board.py - reproducible model source.
render_preview.py - orthographic GLB preview renderer.
validation.json - export and re-import geometry checks.

Units: meters. Y-up. Origin at bottom-center of the bounding box.
Inferred dimensions: width 1.90 m, height 1.60 m, depth 0.2105 m.
24 named meshes; 15,068 triangles. GLB size: 233,096 bytes.
Rounded white panel, blue circular badge, raised white exclamation mark with a
round dot, black Problem title, three unmarked checkbox tiles, gray placeholder
list lines and three cobalt status blocks. Lower two blocks have true top notches
with separate pale inserts. All graphical details are geometry, not a flat image.
Title lettering uses extruded DejaVu Sans Bold as a reference-font approximation.
No font files are needed to display the GLB; the outlines are embedded mesh geometry.
Panel, badge and notched blocks pass closed-surface and winding checks after welding.
The exported GLB was re-imported to verify vertices, indices and materials.

No rig, animation, external textures, scene lights, floor or camera are in the GLB.
Model dependencies: numpy, trimesh, shapely, triangle, matplotlib.
Source font path: /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf (adjust for your OS).
Preview dependencies: pyrender, PyOpenGL >= 3.1.7, Pillow, EGL, networkx.
