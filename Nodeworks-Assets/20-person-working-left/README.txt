Nodeworks — Asset 20: Person Working (Left)

Rekonstruksi 3D berdasarkan gambar referensi; bukan salinan persis 1:1.
Paket mencakup karakter pria duduk, kursi putih-biru, dan laptop layar kode.

Format: glTF 2.0 binary (.glb), Y-up, unit meter, origin bottom-center.
Dimensi gabungan: sekitar 0.679 x 1.449 x 1.230 m (X/Y/Z).
121 mesh; 53,044 segitiga; ukuran GLB 918,780 byte.
Material PBR tertanam; tidak memerlukan tekstur eksternal.

Pose statis. Tidak memiliki rig, skinning, blendshape, atau animasi.
Bagian tubuh memakai geometri modular yang saling bertumpuk, bukan satu
mesh karakter kontinu. Laptop ditempatkan mengikuti pose referensi tanpa
meja. Garis kode merupakan dekorasi, bukan teks kode yang dapat dijalankan.

Isi:
- 20-nodeworks-person-working-left.glb: asset lengkap
- 20-nodeworks-person-working-left-preview.png: render dari GLB aktual
- build_person_working_left.py: sumber pembuatan
- render_preview.py: sumber render
- 16-nodeworks-office-chair.glb: dependensi kursi untuk membangun ulang
- validation.json: pemeriksaan geometri dan statistik

Sumber memerlukan Python, numpy, scipy, trimesh, shapely, triangle,
manifold3d, pyrender, PyOpenGL dan Pillow. Jalankan sumber build dari
folder paket. Preview memerlukan dukungan OpenGL/EGL.
