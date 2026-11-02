NODEWORKS / 06 GLASS WALL (RIGHT)

Reference-based reconstruction from the supplied infographic.
Not an exact 1:1 reproduction. Unseen surfaces and physical dimensions are inferred.
This package includes Asset 06 only. Assets 01-05 were delivered separately.

Contents:
06-nodeworks-glass-wall-right.glb - real 3D geometry with embedded materials.
06-nodeworks-glass-wall-right-preview.png - rendered from the exported GLB.
build_glass_wall_right.py - reproducible model source.
render_preview.py - orthographic GLB preview renderer.
validation.json - export and re-import geometry checks.

Units: meters. Y-up. Origin at bottom-center of the bounding box.
Inferred dimensions: width 2.50 m, height 2.4835 m, depth 0.215 m.
35 named meshes; 18,272 triangles. GLB size: 233,736 bytes.
Three fixed transparent blue panes, two dark mullions, graphite frame,
rounded lower rail and white upper cap with two service hatches and end sockets.
The perimeter is actual annular geometry, closed with consistent winding.
The GLB was re-imported to verify geometry and glass material retention.

Glass uses glTF alphaMode BLEND with double-sided rendering. It has no physical
refraction or transmission extension. Transparency sorting depends on the viewer.
Preview renders the exported material on a white background, without opaque
glass shadows. Small glass-edge reflections are separate geometry.
No rig, animation, external textures, lights, or camera are included in the GLB.

Model dependencies: numpy, trimesh, shapely, triangle.
Preview dependencies: pyrender, PyOpenGL >= 3.1.7, Pillow, EGL, networkx.
