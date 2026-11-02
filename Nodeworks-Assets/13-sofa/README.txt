NODEWORKS / 13 SOFA

Reference-based reconstruction from the supplied infographic.
Not an exact 1:1 reproduction. Unseen surfaces and physical dimensions are inferred.
This package includes Asset 13 only. Assets 01-12 were delivered separately.

Contents:
13-nodeworks-sofa.glb - actual 3D geometry with embedded PBR materials.
13-nodeworks-sofa-preview.png - rendered from the exported GLB.
build_sofa.py - reproducible model source.
render_preview.py - orthographic GLB preview renderer.
validation.json - export and re-import geometry checks.

Units: meters. Y-up. Origin at bottom-center of the bounding box.
Inferred dimensions: width 1.991 m, height 1.0074 m, depth 0.880 m.
18 named meshes; 14,512 triangles. GLB size: 198,108 bytes.
White upholstered base and arms, two seat cushions, two reclining back cushions,
one blue throw pillow with a separate dark blue seam, four brown feet and black pads.
Cushions use smooth superellipsoid geometry to give them softly rounded, padded forms.
All sampled housing, armrest and cushion meshes pass closed-surface and winding checks
following vertex welding. The exported GLB was re-imported to verify geometry and materials.

No rig, animation, external textures, scene lights, floor or camera are in the GLB.
Upholstery and pillow materials use smooth color and roughness, without fabric textures.
Cushions, blue pillow, arms and feet remain separate named components.
Model dependencies: numpy, trimesh.
Preview dependencies: pyrender, PyOpenGL >= 3.1.7, Pillow, EGL, networkx.
