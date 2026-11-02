NODEWORKS / 19 PERSON PRESENTING

Reference-based stylized reconstruction from the supplied infographic.
Not an exact 1:1 reproduction. Facial likeness, hair, anatomy and unseen surfaces are approximated.
This package includes Asset 19 only. Assets 01-18 were delivered separately.

Contents:
19-nodeworks-person-presenting.glb - actual 3D geometry with embedded PBR materials.
19-nodeworks-person-presenting-preview.png - rendered from the exported GLB.
build_person_presenting.py - reproducible model source.
render_preview.py - orthographic GLB preview renderer.
validation.json - export and re-import geometry checks.

Units: meters. Y-up. Origin at bottom-center of the complete bounding box.
Inferred dimensions including the raised hand: width 0.8509 m, height 1.637 m,
depth 0.3256 m. 60 named meshes; 26,004 triangles. GLB size: 483,052 bytes.
White short-sleeved collared shirt with a blue chest badge, charcoal trousers,
dark belt, light gray shoes, peach skin and dark swept hair.
One hand rests near the waist; the other is lifted outward in an open-palm gesture.
Face and proportions use the same base character as Asset 18 for consistency.
Head, facial details, clothing, sleeves, forearms, hands, fingers and shoes are named meshes.
Sampled head, torso, trouser legs, shoes and presenting palm pass closed-surface
and winding checks following vertex welding. The exported GLB was re-imported
to verify geometry and embedded materials.

STATIC POSE ONLY. No skeleton, skinning, animation clips, facial blend shapes or
animation pivots are included. Separate mesh components are not an animation rig.
Body parts overlap at clothing joints; this is not continuous production character topology.
No external textures, scene lights, floor or camera are included in the GLB.

Model dependencies: numpy, scipy, trimesh, shapely, triangle, manifold3d.
Preview dependencies: pyrender, PyOpenGL >= 3.1.7, Pillow, EGL, networkx.
