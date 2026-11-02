NODEWORKS / 12 SOLUTION BOARD

Reference-based reconstruction from the supplied infographic.
Not an exact 1:1 reproduction. Unseen surfaces, dimensions and reference font are inferred.
This package includes Asset 12 only. Assets 01-11 were delivered separately.

Contents:
12-nodeworks-solution-board.glb - actual 3D geometry with embedded materials.
12-nodeworks-solution-board-preview.png - rendered from the exported GLB.
build_solution_board.py - reproducible model source.
render_preview.py - orthographic GLB preview renderer.
validation.json - export and re-import geometry checks.

Units: meters. Y-up. Origin at bottom-center of the bounding box.
Inferred dimensions: width 1.90 m, height 1.60 m, depth 0.2105 m.
20 named meshes; 11,728 triangles. GLB size: 212,012 bytes.
Rounded white panel, blue circular badge with a raised white check, black Solution
title, four separate ascending chart bars, a raised trend arrow and three checklist
rows. Every tile, check symbol and gray placeholder line is independent geometry.
The chart is decorative, reconstructed from the image; it has no quantitative data.
Title lettering uses extruded DejaVu Sans Bold as a reference-font approximation.
No font files are needed to display the GLB; the outlines are embedded mesh geometry.
Panel, badge, sampled chart bars and trend arrow pass closed-surface and winding
checks after welding shading seams. The exported GLB was re-imported to verify
vertices, indices and materials.

No rig, animation, external textures, scene lights, floor or camera are in the GLB.
Named components can be animated by your application.
Model dependencies: numpy, trimesh, shapely, triangle, matplotlib.
Source font path: /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf (adjust for your OS).
Preview dependencies: pyrender, PyOpenGL >= 3.1.7, Pillow, EGL, networkx.
