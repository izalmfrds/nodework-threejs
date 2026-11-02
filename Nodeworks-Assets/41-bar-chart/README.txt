Nodeworks — Asset 41: Bar Chart

Rekonstruksi 3D berdasarkan gambar referensi, belum persis 1:1.
Empat batang biru bersudut membulat dengan tinggi bertahap dan dasar
sejajar. Grafik meninggi dari kiri ke kanan bila dilihat dari depan.
Tidak memiliki panel latar, sumbu atau angka. Setiap batang adalah mesh
terpisah bernama sehingga dapat ditargetkan secara individual di aplikasi.

Format GLB / glTF 2.0, Y-up, unit meter, origin bottom-center.
Bagian depan menghadap -Z pada koordinat glTF.
Dimensi X/Y/Z: sekitar 0.131 x 0.132 x 0.012 m.
4 mesh; 2,048 segitiga; ukuran GLB 28,616 byte.
Material PBR tertanam; tanpa tekstur atau dependensi eksternal.
Model statis tanpa rig/animasi. Tidak berisi data numerik nyata.

Isi: GLB, preview render dari GLB aktual, build_bar_chart.py,
render_preview.py, validation.json dan README.txt.
Build memerlukan Python, numpy dan trimesh.
Render memerlukan pyrender, PyOpenGL, Pillow dan OpenGL/EGL.
Jalankan skrip dari folder paket.
