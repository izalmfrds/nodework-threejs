NODEWORKS / 05 GLASS WALL (LEFT)

Reference-based reconstruction from the supplied infographic.
Not an exact 1:1 reproduction. Unseen surfaces and physical dimensions are inferred.
This package includes Asset 05 only. Assets 01-04 were delivered separately.

Contents:
05-nodeworks-glass-wall-left.glb - real 3D geometry with embedded materials.
05-nodeworks-glass-wall-left-preview.png - rendered from the exported GLB.
build_glass_wall_left.py - reproducible model source.
render_preview.py - orthographic GLB preview renderer.
validation.json - export and re-import geometry checks.

Units: meters. Y-up. Origin at bottom-center of the bounding box.
Inferred dimensions: width 1.60 m, height 2.40 m, depth 0.1485 m.
20 named meshes; 10,592 triangles. GLB size: 162,704 bytes.
Rounded graphite perimeter, rear edge, inner glazing seal, paired center stiles,
two thin transparent blue panes, paired central handles and small rear fasteners.
Perimeter geometry is closed with consistent winding after welding cap seams.
GLB was re-imported to verify geometry and transparent material retention.

Glass uses glTF alphaMode BLEND with double-sided rendering. It has no physical
refraction or transmission extension. Transparency sorting depends on the viewer.
The preview uses the same exported materials on a white background, without a
floor plane or opaque glass shadows. Surface reflection accents are geometry.

No rig, animation, external textures, lights, or camera are included in the GLB.
Model dependencies: numpy, trimesh, shapely, mapbox_earcut, triangle.
Preview dependencies: pyrender, PyOpenGL >= 3.1.7, Pillow, EGL, networkx.
