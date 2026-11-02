NODEWORKS / 10 BUILD YOUR SYSTEM BOARD

Reference-based reconstruction from the supplied infographic.
Not an exact 1:1 reproduction. Unseen surfaces, dimensions and reference font are inferred.
This package includes Asset 10 only. Assets 01-09 were delivered separately.

Contents:
10-nodeworks-build-your-system-board.glb - real 3D geometry with embedded materials.
10-nodeworks-build-your-system-board-preview.png - rendered from the exported GLB.
build_system_board.py - reproducible model source.
render_preview.py - orthographic GLB preview renderer.
validation.json - export and re-import geometry checks.

Units: meters. Y-up. Origin at bottom-center of the bounding box.
Inferred dimensions: width 3.20 m, height 2.04 m, depth 0.341 m.
17 named meshes; 12,304 triangles. GLB size: 337,044 bytes.
White rounded housing, inset navy face and three separate raised white cards.
Title, card labels, header symbol and all three card icons are actual mesh geometry.
The Design icon has three stacked layers, Build has a code symbol, and Integrate
has six radial spokes with rounded ends. Text uses DejaVu Sans Bold as an approximation.
No font files need to be loaded when displaying the GLB: lettering is embedded geometry.
Housing and cards pass closed-surface and winding checks after merging cap seams.
The exported GLB was re-imported to verify vertices, indices and materials.

No rig, animation, external textures, scene lights, floor or camera are in the GLB.
Card, icon and text meshes can be grouped by their node name prefixes in your application.
Model dependencies: numpy, trimesh, shapely, triangle, matplotlib.
Source font path: /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf (adjust for your OS).
Preview dependencies: pyrender, PyOpenGL >= 3.1.7, Pillow, EGL, networkx.
