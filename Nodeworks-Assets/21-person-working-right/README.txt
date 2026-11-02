Nodeworks — Asset 21: Person Working (Right)

Rekonstruksi 3D berdasarkan gambar referensi; bukan salinan persis 1:1.
Paket mencakup karakter perempuan duduk dengan rambut diikat, kursi putih-biru, dan laptop layar dashboard.

Format: glTF 2.0 binary (.glb), Y-up, unit meter, origin bottom-center.
Dimensi gabungan: sekitar 0.679 x 1.443 x 1.230 m (X/Y/Z).
140 mesh; 58,152 segitiga; ukuran GLB 1,011,984 byte.
Material PBR tertanam; tidak memerlukan tekstur eksternal.

Pose statis. Tidak memiliki rig, skinning, blendshape, atau animasi.
Bagian tubuh memakai geometri modular yang saling bertumpuk, bukan satu
mesh karakter kontinu. Laptop ditempatkan mengikuti pose referensi tanpa
meja. Grafik dashboard merupakan geometri dekoratif, bukan data nyata.

Isi:
- 21-nodeworks-person-working-right.glb: asset lengkap
- 21-nodeworks-person-working-right-preview.png: render dari GLB aktual
- build_person_working_right.py: sumber pembuatan
- render_preview.py: sumber render
- 16-nodeworks-office-chair.glb: dependensi kursi untuk membangun ulang
- validation.json: pemeriksaan geometri dan statistik

Sumber memerlukan Python, numpy, scipy, trimesh, shapely, triangle,
manifold3d, pyrender, PyOpenGL dan Pillow. Jalankan sumber build dari
folder paket. Preview memerlukan dukungan OpenGL/EGL.
