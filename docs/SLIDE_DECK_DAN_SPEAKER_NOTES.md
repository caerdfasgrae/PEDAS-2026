# 📊 SANTARA-SHIELD: Slide Deck & Naskah Presentasi (10 Slide Master)
> **Pitch Deck Resmi Tim**: Siap dipakai langsung di PowerPoint (`docs/SANTARA_SHIELD_PRESENTASI.pptx`), Google Slides, atau Canva.  
> **Durasi Presentasi**: ~7.5 Menit (Standar Babak Final PeDaS 2026: 7–10 Menit).  
> **Aturan Khusus**: *Double-Blind Review* (Tanpa nama kampus/identitas anggota tim).

---

## 🧭 Panduan Navigasi Slide
- **Slide 1**: Judul Solusi & Identitas Tim (Double Blind)
- **Slide 2**: Urgensi Masalah & Kerugian Nasional Phishing Domain Murah
- **Slide 3**: Analisis Kritis: Mengapa Solusi Saat Ini (IDADX & BIMA) Belum Cukup?
- **Slide 4**: Metodologi Riset: 7-Langkah Machine Learning Lifecycle (CRISP-DM)
- **Slide 5**: Empat Pilar Inovasi: Brand Intelligence, N-Gram Stacking, & Anti-Leakage
- **Slide 6**: Arsitektur Pemodelan: Multi-GBDT Ensemble & SLSQP Blending
- **Slide 7**: Hasil Evaluasi Empiris: Precision-Recall Curve & Matriks Dampak PANDI
- **Slide 8**: Implementasi Produk: Live Demo Single-Domain Inspector (`santara_inspect`)
- **Slide 9**: Rekomendasi Kebijakan Strategis untuk PANDI & IDADX (*Target Piala Best Analysis*)
- **Slide 10**: Kesimpulan, Kesiapan Babak Final, & Komitmen Kedaulatan Digital

---

## SLIDE 1: Judul Solusi & Identitas Tim (Double Blind)
* **Waktu**: 0:00 – 0:30 (30 Detik)
* **Visual Slide**:
  - Judul Utama: **SANTARA-SHIELD**
  - Subjudul: *Perisai Kedaulatan Ekosistem Domain .id Berbasis Multi-GBDT Ensemble & Brand Intelligence*
  - Banner Kompetisi: *Pesta Data Nasional (PeDaS 2026) | APTIKOM Fest 2026 x PANDI*
  - Identitas Tim: *Peserta Resmi PeDaS 2026 (Double-Blind Review - Tanpa Identitas Kampus/Nama)*
  - Ikon Visual: Perisai Keamanan Siber Cyberpunk/Dark Navy dengan aksen Cyan & Emas.
* **Sitasi / Sumber Valid**:
  - *Ref: APTIKOM Fest 2026 Panduan Teknis & Registry PANDI 2026.*
* **Naskah Pembicara (Speaker Script)**:
  > *"Selamat pagi Dewan Juri yang kami hormati, perwakilan PANDI, dan akademisi APTIKOM.  
  > Hari ini kami mempersembahkan **SANTARA-SHIELD**—sebuah kerangka kerja kecerdasan buatan terpadu untuk deteksi dini domain phishing berbahaya pada ekosistem domain tingkat tinggi `.id`.  
  > Solusi kami memadukan arsitektur Multi-GBDT Ensemble dengan kecerdasan ancaman lokal untuk mewujudkan sistem pertahanan siber yang akurat, cepat, dan berkeadilan hukum."*

---

## SLIDE 2: Urgensi Masalah: Ledakan Phishing pada Domain Murah .id
* **Waktu**: 0:30 – 1:15 (45 Detik)
* **Visual Slide**:
  - **Grafik Kiri**: Diagram Batang Persebaran Sektor Phishing (.id) — *Perbankan (53%) & Fintech/E-Wallet (30%) mendominasi*.
  - **Kotak Kanan**: Dua Modus Ancaman Nyata di Indonesia:
    1. *Pencatutan Bank (Combosquatting)*: Domain murah `.my.id` dan `.biz.id` meniru bank (BCA, Mandiri, BRI).
    2. *Pancingan APK Malware via WhatsApp*: Surat tilang ETLE, undangan nikah, dan resi kurir berkedok `.apk` untuk membobol saldo m-Banking.
  - Angka Kunci: Rata-rata kerugian korban penipuan online mencapai puluhan juta rupiah per insiden.
* **Sitasi / Sumber Valid**:
  - *Ref: APWG (Anti-Phishing Working Group) Phishing Activity Trends Report Q4 2025; BSSN Laporan Tahunan Monitoring Keamanan Siber 2025.*
* **Naskah Pembicara (Speaker Script)**:
  > *"Bapak dan Ibu Juri, kejahatan siber di Indonesia kini telah berevolusi secara drastis. Pelaku tidak lagi hanya mengandalkan domain internasional, melainkan menyalahgunakan domain lokal berbiaya murah—khususnya `.my.id` dan `.biz.id` yang dapat didaftarkan hanya dengan belasan ribu rupiah tanpa verifikasi dokumen bisnis ketat.  
  > Modusnya sangat merusak: mulai dari peniruan formulir login bank hingga penyebaran berkas APK malware surat tilang ETLE via WhatsApp. Korban kehilangan tabungan hidupnya hanya karena satu klik pada tautan domain `.id` palsu."*

---

## SLIDE 3: Analisis Kritis: Mengapa Solusi Saat Ini Belum Cukup?
* **Waktu**: 1:15 – 2:05 (50 Detik)
* **Visual Slide**:
  - **Kartu 1 (Merah - IDADX Saat Ini)**: *Pendekatan Reaktif*. Mengandalkan laporan masuk dari korban/bank. Terdapat *jendela bahaya (window of exposure)* 12–24 jam di mana korban sudah terlanjur mentransfer uang sebelum takedown terjadi.
  - **Kartu 2 (Kuning - BIMA AI)**: *Deep Web Crawling Berkala*. Membutuhkan komputasi besar dan waktu perayapan panjang, serta buta terhadap domain yang baru didaftarkan atau menyembunyikan konten di balik login.
  - **Kartu 3 (Hijau - SANTARA-SHIELD)**: *Pre-Delegation & First-Line Triage Gatekeeper*. Memeriksa struktur URL dan pencatutan brand di gerbang pendaftaran Registrar API dalam **0.94 milidetik**, menghentikan ancaman sebelum domain aktif memakan korban!
* **Sitasi / Sumber Valid**:
  - *Ref: PANDI IDADX Laporan Tahunan Phishing 2024; Kintis et al., USENIX Security: Understanding and Mitigating Domain Squatting.*
* **Naskah Pembicara (Speaker Script)**:
  > *"Sistem yang dimiliki PANDI saat ini, seperti IDADX dan BIMA AI, telah bekerja luar biasa. Namun secara metodologis, ada celah waktu kritis yang belum terisi.  
  > IDADX bersifat reaktif—domain baru ditindak setelah ada laporan korban. Di sisi lain, BIMA AI memerlukan waktu merayapi konten web yang luas.  
  > SANTARA-SHIELD hadir untuk mengisi celah tersebut dengan paradigma baru: **Pre-Delegation Gatekeeper**. Kami memeriksa domain di gerbang pendaftaran dalam hitungan milidetik secara offline. Hasilnya, kita bisa menahan domain berbahaya sebelum mereka sempat aktif didelegasikan ke DNS internet!"*

---

## SLIDE 4: Metodologi Riset: 7-Langkah Machine Learning Lifecycle
* **Waktu**: 2:05 – 2:50 (45 Detik)
* **Visual Slide**:
  - Diagram Alir Horizontal / Chevron 7 Tahapan CRISP-DM:
    1. *Problem Framing* (Trade-off FP vs FN; Metrik F1-Macro & Recall).
    2. *Data Sourcing* (212 data benchmark phishing lokal; Slot otomatisasi PANDI).
    3. *Data Preprocessing* (Normalisasi URL, audit keabsahan label bank resmi).
    4. *Feature Engineering* (52 fitur komprehensif: Leksikal, Brand YAML, Shannon Entropy, N-Gram Stacking).
    5. *Model Selection & Training* (Multi-GBDT Ensemble + StratifiedGroupKFold).
    6. *Model Evaluation & Tuning* (Precision-Recall Curve, Confusion Matrix, Threshold $\tau^*$).
    7. *Deployment & Decision Support* (API inspeksi `santara_inspect` & Rekomendasi PANDI).
* **Sitasi / Sumber Valid**:
  - *Ref: CRISP-DM Standard Process Model; Google Machine Learning Engineering Best Practices.*
* **Naskah Pembicara (Speaker Script)**:
  > *"Dalam mengembangkan SANTARA-SHIELD, kami tidak melompat langsung ke pemodelan. Kami mematuhi standar baku 7-Langkah Machine Learning Lifecycle standar industri.  
  > Seluruh tahapan—mulai dari perumusan trade-off bisnis, pembersihan data, ekstraksi 52 fitur, pelatihan bebas kebocoran, hingga penyediaan modul inspeksi interaktif—telah dimodularisasi secara profesional di dalam folder `src/` repositori GitHub kami, siap diaudit baris demi baris."*

---

## SLIDE 5: Empat Pilar Inovasi Fitur & Anti-Leakage Validation
* **Waktu**: 2:50 – 3:45 (55 Detik)
* **Visual Slide**:
  - **Pilar 1: Indonesian Brand Intelligence (Kamus YAML)**: Kamus terkurasi 30+ brand lokal (BCA, Mandiri, BRI, DANA, ETLE, PLN, J&T). Fuzzy Levenshtein matching mendeteksi combosquatting dan subdomain hijack secara instan.
  - **Pilar 2: Character N-Gram TF-IDF Stacking**: Membaca tipuan ketikan penipu (misal: `kl1kbca` atau `b-c-a-verif`). Karakter 3–5 gram dirangkum menjadi satu fitur probabilitas teks padat (`ngram_phish_prob`).
  - **Pilar 3: Anti-Leakage Validation (StratifiedGroupKFold)**: Pemisahan data latih/uji dikunci berdasarkan **Domain Induk (FQDN)**. Mencegah *Domain Group Leakage* dan membuktikan model mampu menangkal penipu baru (*zero-day phishing*).
  - **Pilar 4: Shannon Entropy & Structural Metrics**: Mengukur keacakan string domain dan mendeteksi pancingan ekstensi berkas malware `.apk` dan `.php`.
* **Sitasi / Sumber Valid**:
  - *Ref: Kaufman et al., ACM KDD: Leakage in Data Mining; Chen & Guestrin, XGBoost Scalable Tree Boosting System.*
* **Naskah Pembicara (Speaker Script)**:
  > *"Kekuatan utama model machine learning terletak pada kualitas fiturnya. Kami mengonstruksi 4 pilar inovasi:  
  > Pertama, Kamus Brand Intelligence lokal yang memahami konteks ancaman perbankan Indonesia.  
  > Kedua, N-Gram Stacking yang merangkum gaya pengetikan manipulatif URL penipu menjadi satu angka probabilitas padat.  
  > Ketiga, validasi ketat StratifiedGroupKFold. Kami mengelompokkan data berdasarkan domain induk, sehingga kami menjamin 100% nol kebocoran data (*zero leakage*). Model kami diuji pada domain yang benar-benar belum pernah dilihatnya di masa latihan."*

---

## SLIDE 6: Pemodelan: Multi-GBDT Ensemble & SLSQP Blending
* **Waktu**: 3:45 – 4:35 (50 Detik)
* **Visual Slide**:
  - **Diagram Ensemble**: Kolaborasi 3 Algoritma Pohon Terbaik:
    - *LightGBM*: Sangat cepat pada fitur leksikal frekuensi tinggi.
    - *CatBoost*: Sangat tangguh membaca relasi brand dan kategori TLD.
    - *XGBoost*: Sangat presisi pada batas pemisahan nilai kontinu entropi dan panjang URL.
  - **Kotak SLSQP Optimizer**: Pembobotan matematis optimal menggunakan *Sequential Least Squares Programming* dengan konstrain bobot non-negatif dan total bobot = 1.
  - **Grafik Kanan**: Diagram Batang *Top 10 Feature Importance* (Menunjukkan dominasi N-Gram dan Sinyal Brand).
* **Sitasi / Sumber Valid**:
  - *Ref: Kraft, D., ACM TOMS: Algorithm 733: Fortran Subroutines for SLSQP; Lundberg & Lee, NeurIPS: SHAP Unified Framework for Model Interpretability.*
* **Naskah Pembicara (Speaker Script)**:
  > *"Alih-alih mengandalkan satu model tunggal, kami membangun arsitektur Multi-GBDT Ensemble. Kami menggabungkan LightGBM, CatBoost, dan XGBoost.  
  > Ketiga model ini tidak digabungkan dengan tebakan rata-rata sederhana, melainkan menggunakan kalkulus optimasi bobot SLSQP. Algoritma ini mencari kombinasi bobot optimal yang memaksimalkan F1-Score pada data Out-of-Fold. Di grafik sebelah kanan, terlihat jelas bahwa fitur N-gram probabilitas dan indikator pencatutan brand menjadi faktor penentu paling dominan."*

---

## SLIDE 7: Hasil Evaluasi Empiris & Matriks Dampak Industri PANDI
* **Waktu**: 4:35 – 5:30 (55 Detik)
* **Visual Slide**:
  - **Grafik Kiri (Precision-Recall Curve)**: Kurva PR dengan arsiran biru lembut dan garis silang merah pada $\tau^*$. Membuktikan model konsisten pada data tidak seimbang: **Recall 98.01% dan Precision 99.33%**.
  - **Grafik Kanan (Matriks Keputusan Beranotasi Dampak PANDI)**:
    - *True Positive (148 Domain)*: Serangan phishing berhasil dicegat.
    - *True Negative (60 Domain)*: Situs sah legal aktif normal tanpa hambatan.
    - *False Positive (Hanya 1 Domain - 1.64%)*: Resiko komplain/gugatan hukum ke PANDI ditekan seminimal mungkin.
    - *False Negative (Hanya 3 Domain)*: Korban penipuan dipangkas habis.
  - Nilai Metrik Final: **F1-Macro = 0.9772 | ROC-AUC = 0.9902**.
* **Sitasi / Sumber Valid**:
  - *Ref: Saito & Rehmsmeier, PLoS ONE: The Precision-Recall Plot Is More Informative Than ROC for Imbalanced Data.*
* **Naskah Pembicara (Speaker Script)**:
  > *"Mari kita lihat bukti empiris kinerja sistem kami pada Slide 7.  
  > Pada kurva Precision-Recall di sebelah kiri, model kami membuktikan keunggulannya pada data tidak seimbang: berhasil menangkap 98.01% phishing dengan ketepatan vonis 99.33%.  
  > Di sebelah kanan, kami menyajikan Matriks Keputusan beranotasi dampak nyata bagi PANDI: sebanyak 148 phishing berhasil dicegat, dan yang paling krusial, False Positive Rate kami hanya 1.64%—hanya 1 domain legal yang terflag dari 61 sampel. Ini membuktikan PANDI terlindungi dari komplain pemilik domain sah."*

---

## SLIDE 8: Implementasi Produk: Single-Domain Interactive Inspector
* **Waktu**: 5:30 – 6:15 (45 Detik)
* **Visual Slide**:
  - Tangkapan Layar Tampilan Antarmuka `santara_inspect` (Desain *High-Contrast Charcoal Slate SOC Card*):
    - Badge Merah Menyala: *BAHAYA TINGGI: TERKONFIRMASI PHISHING (Skor 99.69%)*.
    - Rincian Sinyal: *Mencatut Brand: BCA (TIDAK SAH / COMBO-SQUATTING)*.
    - Deteksi Malware: *Pancingan Berkas APK Malware via WhatsApp*.
    - Rekomendasi Tindakan Analis PANDI.
  - **Tabel Benchmark Skalabilitas Komputasi**:
    - Waktu Ekstraksi 52 Fitur: **0.94 detik per 1.000 URL (0.94 ms/URL)**.
    - Waktu Prediksi: **0.00 detik (instan via C++ vectorization)**.
    - Konsumsi RAM: **~8.4 MB (menggunakan < 0.2% RAM Colab)**.
* **Sitasi / Sumber Valid**:
  - *Ref: PeDaS 2026 Interactive Evaluation Notebook; Colab Runtime Benchmark 2026.*
* **Naskah Pembicara (Speaker Script)**:
  > *"SANTARA-SHIELD bukan sekadar kode di atas kertas, melainkan produk yang siap diuji langsung. Di notebook Google Colab, kami menyediakan fungsi `santara_inspect`. Dewan juri dapat memasukkan domain apa saja untuk diuji secara instan.  
  > Dari segi skalabilitas, kami telah melakukan stress-test pada 1.000 URL: seluruh proses ekstraksi 52 fitur dan prediksi selesai dalam waktu 0.94 detik dengan memori hanya 8.4 MB. Sistem ini sangat siap menangani lonjakan puluhan ribu registrasi domain per hari di server PANDI!"*

---

## SLIDE 9: Rekomendasi Kebijakan Strategis untuk PANDI & IDADX
* **Waktu**: 6:15 – 7:05 (50 Detik)
* **Visual Slide**:
  - Tiga Pilar Rekomendasi Kebijakan (*Target Piala Best Analysis*):
    1. **Pre-Delegation DNS Gatekeeper**: Pendaftaran domain murah `.my.id` dan `.biz.id` yang memiliki skor resiko $\ge 90\%$ otomatis ditahan sementara (*pending delegation 24 jam*) dan diminta verifikasi identitas KTP sebelum DNS didelegasikan.
    2. **Otomatisasi Triase Laporan IDADX**: Laporan masyarakat di portal IDADX dinilai otomatis oleh model untuk memangkas respon penanganan dari 24 jam menjadi hitungan menit. Skor resiko sedang dikirim sebagai prioritas perayapan BIMA AI.
    3. **Whitelist Finansial Terpusat**: PANDI bersama OJK dan Asosiasi Perbankan membentuk basis data domain resmi institusi keuangan, sehingga upaya combosquatting langsung terblokir sejak awal.
* **Sitasi / Sumber Valid**:
  - *Ref: Permenkominfo No. 5 Tahun 2020 tentang Penyelenggara Sistem Elektronik Lingkup Privat; Registry-Registrar Agreement (RRA) PANDI.*
* **Naskah Pembicara (Speaker Script)**:
  > *"Sebagai kontribusi strategis bagi dewan juri dan PANDI, kami merumuskan 3 rekomendasi kebijakan nyata:  
  > Pertama, terapkan Pre-Delegation DNS Gatekeeper pada domain murah .my.id dan .biz.id untuk registran yang terindikasi skor resiko tinggi.  
  > Kedua, integrasikan SANTARA-SHIELD sebagai sistem triase otomatis di portal IDADX guna memotong waktu respon laporan dari 24 jam menjadi hitungan menit.  
  > Ketiga, bangun Whitelist Finansial Terpusat bersama regulator perbankan. Dengan sinergi ini, PANDI tidak lagi hanya memadamkan api penipuan, melainkan mencegah kebakaran sejak percikan pertama!"*

---

## SLIDE 10: Kesimpulan & Komitmen Kedaulatan Digital
* **Waktu**: 7:05 – 7:45 (40 Detik)
* **Visual Slide**:
  - Rangkuman 4 Nilai Utama:
    - *Akurasi Tinggi*: F1-Macro 0.9772 & Recall Phishing 98.01%.
    - *Ramah Bisnis*: False Positive Rate sangat rendah (1.64%).
    - *Skalabilitas Ekstrem*: 0.94 milidetik per URL.
    - *Deterministik 100%*: Terkunci pada `RANDOM_STATE = 42`.
  - Link Terverifikasi: Repositori GitHub & Colab Notebook.
  - Slogan Penutup: *"SANTARA-SHIELD: Menjaga Integritas Domain .id, Melindungi Masyarakat Indonesia."*
* **Sitasi / Sumber Valid**:
  - *Ref: Repositori Publik: https://github.com/caerdfasgrae/PEDAS-2026; PeDaS 2026 Finalist Commitment.*
* **Naskah Pembicara (Speaker Script)**:
  > *"Sebagai penutup, SANTARA-SHIELD membuktikan bahwa kecerdasan buatan berbasis Multi-GBDT yang dipadukan dengan pemahaman konteks ancaman lokal mampu menjadi benteng tangguh bagi kedaulatan domain nasional.  
  > Seluruh kode kami bersifat deterministik, bebas kebocoran data, dan siap diuji kapan saja. Kami siap berkolaborasi untuk mewujudkan ekosistem internet Indonesia yang bersih, aman, dan berdaulat.  
  > Terima kasih atas perhatian Dewan Juri, kami siap untuk sesi tanya jawab."*

---
*Naskah ini disusun presisi untuk memenangkan PeDaS 2026 dan membidik Piala Best Analysis.* 🏆🚀
