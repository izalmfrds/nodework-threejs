NODEWORKS / 18 PERSON THINKING

Reference-based stylized reconstruction from the supplied infographic.
Not an exact 1:1 reproduction. Facial likeness, hair, anatomy and unseen surfaces are approximated.
This package includes Asset 18 only. Assets 01-17 were delivered separately.

Contents:
18-nodeworks-person-thinking.glb - actual 3D geometry with embedded PBR materials.
18-nodeworks-person-thinking-preview.png - rendered from the exported GLB.
build_person_thinking.py - reproducible model source.
render_preview.py - orthographic GLB preview renderer.
validation.json - export and re-import geometry checks.

Units: meters. Y-up. Origin at bottom-center of the bounding box.
Inferred dimensions: width 0.642 m, height 1.637 m, depth 0.3371 m.
56 named meshes; 24,276 triangles. GLB size: 454,716 bytes.
White collared shirt with a small blue chest badge, charcoal trousers, dark belt,
light gray shoes, peach face and hands, and a sculpted dark swept hairstyle.
One arm rests at the waist; the other is raised with fingers near the lower face.
Head, facial details, clothing, sleeves, hands, fingers and shoes are separate named meshes.
Sampled head, torso, trouser legs, shoes and hand pass closed-surface and winding checks
following vertex welding. The exported GLB was re-imported to verify geometry and materials.

STATIC POSE ONLY. No skeleton, skinning, animation clips, facial blend shapes or authored
animation pivots are included. Separate components are not equivalent to an animation rig.
Body parts overlap at clothing joints; this is not a continuous production character topology.
No external textures, scene lights, floor or camera are included in the GLB.

Model dependencies: numpy, scipy, trimesh, shapely, triangle, manifold3d.
Preview dependencies: pyrender, PyOpenGL >= 3.1.7, Pillow, EGL, networkx.
