NODEWORKS / 16 OFFICE CHAIR

Reference-based reconstruction from the supplied infographic.
Not an exact 1:1 reproduction. Unseen surfaces, physical dimensions and mechanics are inferred.
This package includes Asset 16 only. Assets 01-15 were delivered separately.

Contents:
16-nodeworks-office-chair.glb - actual 3D geometry with embedded PBR materials.
16-nodeworks-office-chair-preview.png - rendered from the exported GLB.
build_office_chair.py - reproducible model source.
render_preview.py - orthographic GLB preview renderer.
validation.json - export and re-import geometry checks.

Units: meters. Y-up. Origin at bottom-center of the bounding box.
Inferred dimensions: width 0.6786 m, height 1.0413 m, depth 0.6649 m.
40 named meshes; 15,072 triangles. GLB size: 300,644 bytes.
White seat and reclining back cushions, cobalt back shell, paired white U-shaped arm
supports, hooked blue arm pads, dark under-seat mechanism and an adjustment lever.
The white five-spoke base has five caster assemblies, each with two black tires.
Wheel hub caps, caster housings and stems are separate named components.
Tested cushion, shell, arm, spoke and wheel meshes pass closed-surface and winding
checks after welding shading seams. The GLB was re-imported to verify geometry and materials.

No rig, animation, external textures, scene lights, floor or camera are in the GLB.
Caster and chair components are static meshes; animation pivots and rigging are not authored.
Model dependencies: numpy, trimesh.
Preview dependencies: pyrender, PyOpenGL >= 3.1.7, Pillow, EGL, networkx.
