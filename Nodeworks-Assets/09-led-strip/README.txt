NODEWORKS / 09 LED STRIP

Reference-based reconstruction from the supplied infographic.
Not an exact 1:1 reproduction. Unseen surfaces and physical dimensions are inferred.
This package includes Asset 09 only. Assets 01-08 were delivered separately.

Contents:
09-nodeworks-led-strip.glb - actual 3D geometry with embedded PBR materials.
09-nodeworks-led-strip-preview.png - rendered from the exported GLB.
build_led_strip.py - reproducible model source.
render_preview.py - orthographic GLB preview renderer.
validation.json - export and re-import geometry checks.

Units: meters. Y-up. Origin at bottom-center of the bounding box.
Inferred dimensions: length 2.30 m, height 0.054 m, depth 0.18 m.
3 named meshes; 1,536 triangles. GLB size: 24,716 bytes.
Low-profile rounded rigid bar, with pale blue top inlay, white emitting band,
and cobalt blue base. No exposed LED chips or flexible tape are in the reference.
All three meshes pass closed-surface and winding checks after merging cap seams.
The GLB was re-imported to verify geometry, materials, and emissive factors.

The emitting band has emissive RGB factor [0.55, 0.75, 1.0]. It does not illuminate
nearby objects automatically in a raster renderer. Add application-side lights
for illumination and optional bloom for a glow halo.
No bloom, rig, animation, external textures, scene lights, floor or camera are in the GLB.

Model dependencies: numpy, trimesh.
Preview dependencies: pyrender, PyOpenGL >= 3.1.7, Pillow, EGL, networkx.
