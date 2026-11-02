NODEWORKS / 14 ROUND TABLE

Reference-based reconstruction from the supplied infographic.
Not an exact 1:1 reproduction. Unseen surfaces and physical dimensions are inferred.
This package includes Asset 14 only. Assets 01-13 were delivered separately.

Contents:
14-nodeworks-round-table.glb - actual 3D geometry with embedded PBR materials.
14-nodeworks-round-table-preview.png - rendered from the exported GLB.
build_round_table.py - reproducible model source.
render_preview.py - orthographic GLB preview renderer.
validation.json - export and re-import geometry checks.

Units: meters. Y-up. Origin at bottom-center of the bounding box.
Inferred tabletop diameter: 1.220 m. Tabletop height: 0.430 m.
Overall height including the blue cube and emblem: 0.54995 m.
9 named meshes; 8,088 triangles. GLB size: 250,340 bytes.
Satin white round top with a softened rim, one dark pedestal, a cobalt lower collar,
a smaller graphite base, floor pad and separate blue tabletop cube.
The cube has a small white hexagonal top emblem with a gray center.
All nine meshes pass closed-surface and winding checks after merging shading seams.
The exported GLB was re-imported to verify geometry, indices and materials.

No rig, animation, external textures, scene lights, floor or camera are in the GLB.
Model dependencies: numpy, trimesh.
Preview dependencies: pyrender, PyOpenGL >= 3.1.7, Pillow, EGL, networkx.
