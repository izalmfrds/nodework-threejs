NODEWORKS / 08 HANGING LIGHT

Reference-based reconstruction from the supplied infographic.
Not an exact 1:1 reproduction. Unseen surfaces and physical dimensions are inferred.
This package includes Asset 08 only. Assets 01-07 were delivered separately.

Contents:
08-nodeworks-hanging-light.glb - actual 3D geometry with embedded PBR materials.
08-nodeworks-hanging-light-preview.png - rendered from the exported GLB.
build_hanging_light.py - reproducible model source.
render_preview.py - orthographic GLB preview renderer.
validation.json - export and re-import geometry checks.

Units: meters. Y-up. Origin at bottom-center of the bounding box.
Inferred dimensions: width 2.80 m, height 0.721 m, depth 0.56 m.
16 named meshes; 5,056 triangles. GLB size: 88,324 bytes.
White upper cover, broad cobalt band, white perimeter diffuser, lower blue rim,
underside diffuser, two dark suspension rods with socket collars and a white mount.
The upper mount has two genuinely recessed fixing slots.
The upper mount passes closed-surface and winding checks after merging shading seams.
The GLB was re-imported to verify geometry, materials, and emissive factors.

The diffuser has an emissive material: RGB factor [0.65, 0.82, 1.0].
It does not automatically illuminate nearby objects in a raster renderer.
Add application-side lights for illumination and optional bloom for a glow halo.
No bloom, rig, animation, external textures, scene lights, floor or camera are in the GLB.
Position the complete asset under the ceiling in the assembled scene.

Model dependencies: numpy, trimesh, shapely, triangle, manifold3d.
Preview dependencies: pyrender, PyOpenGL >= 3.1.7, Pillow, EGL, networkx.
