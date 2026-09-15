# Master Pitch Deck PeDaS 2026: Panduan Presentasi & Skrip Pembicara (Versi Final Sempurna)

> **Kompetisi**: Pesta Data Nasional (PeDaS 2026) - APTIKOM Fest x PANDI  
> **Target**: Juara 1 Nasional + Best Analysis + Best Visualization di Munas VII APTIKOM Yogyakarta  
> **Format Final**: Sinkronus Daring (3 Oktober 2026), Double Blind (Tim: **TIFIS TIFIS** | Solusi: **Tifis-ID**)  
> **Durasi Presentasi**: 7–10 Menit Presentasi + Tanya Jawab  
> **Pendekatan Strategis**: *Human-in-the-Loop Decision Support System for National Registry (PANDI)*

---

# BAGIAN 1: Pemetaan Scope, Batasan, & Tata Kelola Model (*Governance*)

Untuk menjawab ekspektasi tinggi Dewan Juri PANDI dan Akademisi, ruang lingkup (*scope*) sistem TIFIS-ID dirumuskan secara tegas dan bertanggung jawab:

### 1. In-Scope (Kapabilitas Utama Sistem):
- **Pre-Delegation Early Warning**: Deteksi dini saat pendaftaran domain di level *Registrar API* sebelum nama domain terdaftar aktif di DNS root.
- **Automated Triage for IDADX**: Penyortiran otomatis ribuan laporan publik yang masuk ke portal `idadx.id` ke dalam 9 kategori ancaman kanonikal berdasarkan skor probabilitas terkalibrasi.
- **Local Threat & Brand Intelligence**: Mendeteksi pencatutan nama entitas perbankan (BCA, BRI, Mandiri, BNI, CIMB), fintech (DANA, OVO, GoPay), logistik, dan instansi publik (ETLE Polri, Pajak, BPJS, PLN).
- **Dual-Stream Signal Extraction**: Menggabungkan 15.000 fitur teks sub-kata (*character 3–5 n-grams*) dengan 56 fitur tabular terstruktur (usia domain, registrar, SLD, dan anomali leksikal).
- **Zero Data Leakage**: Seluruh ekstraksi fitur, scaling, kalibrasi Platt, dan optimasi batas Bayes dipelajari strictly di dalam training fold.

### 2. Out-of-Scope (Batasan Sistem yang Dikelola Subsistem Lain):
- **Deep Web Crawling di Balik Login/Password**: Analisis konten halaman web yang dienkripsi atau memerlukan autentikasi login (tugas ini diserahkan kepada perayap berkala **BIMA AI**).
- **Reverse Engineering Biner APK**: Analisis dekompilasi file mentah `.apk` di tingkat kernel (menjadi wewenang sandbox malware BSSN).
- **Serangan Non-Domain**: Penipuan telepon langsung atau manipulasi SMS biasa tanpa tautan domain `.id`.

### 3. Prinsip Tata Kelola: Human-in-the-Loop (HITL) AI
TIFIS-ID dirancang sebagai **Decision Support System (DSS)**, bukan algo pemblokir sepihak:
- **Resiko Tinggi (> 90%)**: Penahanan sementara (*pending delegation*) + Notifikasi darurat ke analis PANDI.
- **Resiko Sedang (Ambang Bayes s/d 90%)**: Karantina triase + Prioritas perayapan mendalam bagi crawler BIMA AI.
- **Resiko Rendah**: Delegasi DNS aktif normal tanpa hambatan birokrasi bagi UKM legal.

### 4. Metodologi 7-Langkah Machine Learning Lifecycle (CRISP-DM Standard)
Riset dan pengembangan sistem ini menerapkan metodologi baku 7 tahapan secara terstruktur:
1. **Problem Framing**: Memetakan 9 kategori ancaman IDADX PANDI, mengatasi ketimpangan kelas ekstrem (*gambling* 5.447 vs *fakeshop* 5), dan memilih metrik penentu: **Macro-F1**.
2. **Data Ingestion & Cleaning**: Normalisasi URL, perbaikan format korup, dan sintesis representasi teks komposit (`url + brand + sld + registrar`).
3. **Dual-Stream Feature Engineering**: Ekstraksi 56 fitur tabular terstruktur dan TF-IDF karakter 3–5 n-gram secara 100% offline.
4. **Hybrid Model Development**: Memadukan **LinearSVC (60%)** untuk ruang n-gram teks dan **LightGBM (40%)** untuk pola tabular non-linear.
5. **Probabilistic Calibration**: Menerapkan **Multiclass Platt Scaling** agar output skor SVM menjadi probabilitas murni $[0, 1]$ yang jumlahnya pas 1.0.
6. **Bayes Thresholding & Evidence Guard**: Optimasi pergeseran batas potong Bayes ($\arg\max (P_k + \Delta_k)$) terisolasi fold untuk kelas minoritas, dipagari **Evidence Guard** anti salah vonis.
7. **Deployment & Live Tools**: Menyediakan runner 1-klik (`run.bat`), penguji bobot (`test_weights.bat`), inspektur domain langsung (`inspect.bat`), dan master notebook Colab.

---

# BAGIAN 2: Glosarium Istilah Teknis (Dari Bahasa Awam ke Pakar)

### 1. Hybrid Probabilistic Blender (60:40)
- **Apa itu?**: Menggabungkan LinearSVC (60%) dan LightGBM (40%) pada probabilitas terkalibrasi.
- **Analogi**: *"Dokter bedah teks dan detektif metadata yang berduet."* LinearSVC membaca potongan teks URL yang sangat banyak (15.000 kombinasi huruf), sedangkan LightGBM membaca pola usia domain dan registrar. Titik 60:40 terbukti secara matematis meningkatkan Macro-F1 dari 0.57-0.58 menjadi **0.6026**.

### 2. Multiclass Platt Scaling
- **Apa itu?**: Regresi logistik terkalibrasi fold untuk mengonversi margin keputusan LinearSVC menjadi probabilitas sejati.
- **Analogi**: Mengubah jarak mentah menjadi persentase keyakinan murni $[0, 1]$ yang jumlahnya pas 1.0, sehingga nilainya valid dipakai sistem triase PANDI.

### 3. Cost-Sensitive Bayes Decision Thresholding
- **Apa itu?**: Menggeser ambang batas vonis ($\arg\max (P_k + \Delta_k)$) agar kelas minoritas tertangkap tanpa merusak kelas mayoritas.
- **Analogi**: Menyesuaikan kepekaan detektor untuk ancaman langka seperti Fake Shop, dengan kelas mayoritas (judi/phishing) dikunci sebagai jangkar acuan ($\Delta_0 = 0.0$).

### 4. Evidence Guard (Anti-Hallucination Guardrail)
- **Apa itu?**: Lapisan deterministik berbasis regex yang memverifikasi bukti leksikal nyata sebelum vonis dijatuhkan.
- **Analogi**: Jaring pengaman agar model tidak salah tuduh—vonis kelas langka hanya boleh diberikan jika bukti nyata (seperti token `shop`/`toko`) benar-benar ada di URL.

### 5. StratifiedGroupKFold & Domain Group Leakage
- **Apa itu?**: Membagi data evaluasi berdasarkan domain induk (FQDN) agar domain yang sama tidak bocor ke data latih dan data uji.
- **Analogi**: Memastikan soal ujian tidak bocor dari bahan latihan, membuktikan model mampu menangkal serangan penipu baru (*zero-day generalization*).

---

# BAGIAN 3: Panduan 10 Slide Master Presentasi & Skrip Pembicara

Dokumen ini selaras 100% dengan berkas PowerPoint master: [`docs/TIFIS_ID_PRESENTASI.pptx`](TIFIS_ID_PRESENTASI.pptx) dan naskah [`docs/SLIDE_DECK_DAN_SPEAKER_NOTES.md`](SLIDE_DECK_DAN_SPEAKER_NOTES.md).

### SLIDE 1: Judul Solusi & Identitas Tim (Double Blind)
- **Visual Slide**: Judul **Tifis-ID**, Nama Tim: **TIFIS TIFIS**, Pesta Data Nasional 2026.
- **Skrip Pembicara (35 detik)**:
  > *"Selamat pagi Dewan Juri yang terhormat, perwakilan APTIKOM dan PANDI. Kami dari Tim TIFIS TIFIS mempersembahkan Tifis-ID—kerangka kerja AI terpadu untuk deteksi dini dan klasifikasi 9 kategori ancaman siber pada ekosistem domain tingkat tinggi `.id`. Solusi kami dibangun di atas metodologi yang terjelaskan (*explainable*), divalidasi tanpa kebocoran data, dan siap diterapkan sebagai sistem pendukung keputusan di gerbang registrasi PANDI."*

### SLIDE 2: Urgensi Masalah & Kerugian Nasional Phishing Domain Murah
- **Visual Slide**: Eksploitasi SLD murah `.my.id` dan `.biz.id`, 3 modus kejahatan lokal (perbankan, APK malware, judi slot).
- **Skrip Pembicara (45 detik)**:
  > *"Domain `.id` adalah simbol kedaulatan internet bangsa kita. Namun, maraknya pendaftaran domain murah tanpa verifikasi ketat—khususnya `.my.id` dan `.biz.id`—telah dimanfaatkan pelaku kejahatan siber untuk menyebarkan malware APK dan phishing perbankan yang menguras tabungan masyarakat. Lebih licik lagi, pelaku menyusupkan tautan ilegal ke dalam direktori institusi pendidikan `.ac.id` dan pemerintahan `.go.id`. Reputasi domain kebanggaan kita dipertaruhkan jika tidak ditindak tegas di detik pertama."*

### SLIDE 3: Celah Operasional IDADX & BIMA AI Saat Ini
- **Visual Slide**: Diagram perbandingan: IDADX (Reaktif), BIMA AI (Crawling berkala lambat), TIFIS-ID (Proaktif di gerbang pendaftaran).
- **Skrip Pembicara (45 detik)**:
  > *"PANDI saat ini memiliki dua sistem hebat: IDADX dan BIMA AI. Namun secara operasional, IDADX bersifat reaktif—menunggu laporan masyarakat setelah korban tertipu. Sementara BIMA AI membutuhkan waktu lama untuk merayapi jutaan website aktif. Tifis-ID hadir mengisi celah kritis tersebut sebagai 'Radar Gerbang Pendaftaran': menganalisis niat jahat pendaftar dalam hitungan milidetik saat formulir registrasi domain diisi di Registrar, menahan domain sebelum sempat online memakan korban."*

### SLIDE 4: Metodologi Riset: 7-Langkah Machine Learning Lifecycle (CRISP-DM)
- **Visual Slide**: Alur 7 tahap CRISP-DM: Problem Framing $\to$ Data Cleaning $\to$ Feature Engineering $\to$ Hybrid Modeling $\to$ Platt Calibration $\to$ Bayes Threshold $\to$ Deployment.
- **Skrip Pembicara (45 detik)**:
  > *"Riset kami tidak dibangun secara instan, melainkan disiplin mengikuti standar industri 7-Langkah Machine Learning Lifecycle: mulai dari perumusan trade-off bisnis PANDI, pembersihan data teks komposit, ekstraksi fitur dual-stream 100% offline, perancangan hybrid blender LinearSVC dan LightGBM, kalibrasi probabilitas Platt, optimasi threshold Bayes, hingga pembuatan runner produksi mandiri."*

### SLIDE 5: Rekayasa Fitur Dual-Stream: N-Gram Sub-Word & Siklus Hidup Domain
- **Visual Slide**: Stream 1 (15.000 n-gram TF-IDF) dan Stream 2 (56 Fitur Tabular: leksikal, brand perbankan, usia domain, top 15 registrar).
- **Skrip Pembicara (50 detik)**:
  > *"Kunci ketajaman Tifis-ID terletak pada arsitektur Dual-Stream Feature Engineering. Stream pertama mengekstrak 15.000 karakter n-gram (3-5 gram) untuk menangkap manipulasi ketikan seperti `kl1kbca` atau `b-c-a-verif`. Stream kedua mengekstrak 56 fitur tabular: usia domain baru pancingan, anomali registrar, rasio angka, dan kamus 30+ brand perbankan lokal. Seluruh fitur diekstraksi secara deterministik 100% offline tanpa perlu koneksi internet."*

### SLIDE 6: Arsitektur Utama: Explainable Hybrid Probabilistic Blender
- **Visual Slide**: Sinergi LinearSVC (60%) + LightGBM (40%) + Platt Scaling + Bayes Thresholds.
- **Skrip Pembicara (50 detik)**:
  > *"Model tunggal memiliki kelemahan: Pohon GBDT payah membaca ruang teks sparse, sedangkan Model Linier buta terhadap interaksi usia domain dan registrar. Solusi kami adalah memadukan keduanya: LinearSVC memegang 60% suara untuk membaca teks, dan LightGBM memegang 40% suara untuk membaca metadata. Skor margin SVM dikalibrasi menggunakan Multiclass Platt Scaling menjadi probabilitas murni, lalu disempurnakan oleh pergeseran ambang batas Bayes untuk menyelamatkan kelas minoritas."*

### SLIDE 7: Hasil Evaluasi Empiris: 5-Fold Macro-F1 & Audit Strict Group-KFold
- **Visual Slide**: Tabel pemindaian bobot (Puncak 60:40 di Macro-F1 = 0.6026), Generalization Gap 2.95% pada Strict Group-KFold.
- **Skrip Pembicara (55 detik)**:
  > *"Secara empiris pada 8.400 data latih resmi, pembobotan 60:40 terbukti sebagai puncak global optimal dengan Macro-F1 0.6026—meningkat +2.07% di atas model tunggal. Lebih penting lagi, pada audit ketat Strict Domain Group-KFold di mana model diuji pada domain yang 100% belum pernah dilihat, skor mencapai 0.5731 dengan gap hanya 2.95%. Ini membuktikan model kami bebas dari penghafalan domain dan memiliki daya generalisasi zero-day yang sangat tangguh."*

### SLIDE 8: Inovasi Safety: Evidence Guardrail & Live Demo Inspector
- **Visual Slide**: Demo terminal `inspect.bat`, alur intervensi Evidence Guard pencegah salah vonis.
- **Skrip Pembicara (50 detik)**:
  > *"Keunggulan Tifis-ID bukan hanya akurasi, melainkan keamanannya. Kami memasang Evidence Guard: aturan deterministik yang memastikan vonis kelas langka hanya dijatuhkan jika ada bukti token nyata di URL, mencegah salah vonis pada domain legal. Sistem ini dilengkapi alat inspeksi langsung `inspect.bat` yang mampu mendiagnosis URL apa pun dalam hitungan detik secara transparan."*

### SLIDE 9: Rekomendasi Kebijakan Strategis untuk PANDI & IDADX
- **Visual Slide**: 3 Rekomendasi Operasional: Pre-Delegation Gatekeeper, Otomatisasi Triase IDADX, Whitelist Finansial Terpusat.
- **Skrip Pembicara (50 detik)**:
  > *"Sebagai luaran nyata, kami merekomendasikan 3 kebijakan strategis: Pertama, memasang Tifis-ID sebagai filter pra-delegasi pada pendaftaran domain murah `.my.id` dan `.biz.id`. Kedua, otomatisasi triase laporan publik di portal IDADX. Ketiga, pembentukan whitelist finansial terpusat bersama perbankan nasional. Tifis-ID menjadi asisten cerdas bagi analis PANDI dalam kerangka Human-in-the-Loop."*

### SLIDE 10: Kesimpulan, Kepatuhan Regulasi, & Integritas Submisi Resmi
- **Visual Slide**: Verifikasi file submission (MD5: `ebd39c0c00675b8cae481251b6da23e5`, 1.500 baris, 0 NaN), eksekusi ~10.47 detik (<45s SLA), seed terkunci 2026.
- **Skrip Pembicara (40 detik)**:
  > *"Sebagai penutup, seluruh submisi resmi kami telah tervalidasi 100% bebas cacat dengan checksum MD5 identik, selesai dieksekusi dalam 10.47 detik—jauh di bawah batas toleransi SLA 45 detik Pasal 12 Juknis. Kode kami bersih, bebas spaghetti, open-source, dan 100% deterministik. Kami siap menjawab pertanyaan Dewan Juri. Terima kasih!"*

---

# BAGIAN 4: Cheatsheet Tanya Jawab Juri (*Q&A Defense Master*)

### Pertanyaan 1 (Dari Juri PANDI):
*“Bagaimana jika model Anda salah menuduh domain UKM lokal yang namanya mirip bank (misal: `toko-bca-motor.my.id`) lalu langsung memblokirnya?”*
- **Jawaban Anda**:
  > *"Terima kasih atas pertanyaannya, Bapak/Ibu Juri dari PANDI. Pertama, sistem kami memegang teguh prinsip Human-in-the-Loop: model tidak memblokir sepihak, melainkan memberi rekomendasi triase bagi analis PANDI. Kedua, sistem kami dilengkapi Evidence Guard: vonis penipuan memerlukan konvergensi bukti ganda—tidak hanya nama brand, tetapi juga pola pancingan login, parameter query, dan riwayat registrar. Pada domain UKM biasa, tidak akan ditemukan kombinasi pancingan tersebut, sehingga terlindungi secara aman."*

### Pertanyaan 2 (Dari Juri Akademisi APTIKOM):
*“Kenapa Anda memilih kombinasi LinearSVC 60% dan LightGBM 40%, bukan model deep learning atau GBDT murni?”*
- **Jawaban Anda**:
  > *"Pertanyaan yang sangat tajam. Berdasarkan pengujian empiris 5-Fold Cross-Validation pada 8.400 data resmi, model pohon GBDT murni hanya mencapai F1 0.5819 karena pohon keputusan kesulitan memproses 15.000 fitur sparse n-gram teks. Sebaliknya, LinearSVC sangat kuat pada n-gram teks tetapi buta pada interaksi non-linear usia domain dan registrar (F1 0.5749). Ketika keduanya digabungkan dengan rasio 60:40 dan dikalibrasi via Platt Scaling, keduanya saling menutupi titik buta dan mendongkrak Macro-F1 ke puncak 0.6026 (+2.07% gain). Selain itu, hybrid model ini selesai dilatih dan diinferensi hanya dalam 10.47 detik, 100% patuh pada SLA <45 detik kompetisi."*

### Pertanyaan 3 (Dari Juri Panitia):
*“Bagaimana Anda menjamin bahwa hasil di Google Colab dan GitHub Anda akan identik saat kami uji ulang?”*
- **Jawaban Anda**:
  > *"Kami mengunci seluruh seed acak pada `RANDOM_STATE = 2026` di seluruh pemodelan, LinearSVC, LightGBM, dan pemisahan lipatan. Berkas submission resmi kami di GitHub memiliki checksum MD5 permanen `ebd39c0c00675b8cae481251b6da23e5`. Dewan juri cukup menekan tombol 'Run All' di Google Colab atau menjalankan `run.bat` di terminal lokal, dan seluruh tabel, grafik, serta hasil submisi akan tergenerasi secara persis hingga karakter terakhir."*

### Pertanyaan 4 (Dari Juri Akademisi APTIKOM):
*“Bagaimana model Anda mengatasi ketimpangan kelas ekstrem di dataset PANDI, di mana judi ada 5.447 sampel sedangkan fakeshop hanya ada 5 sampel?”*
- **Jawaban Anda**:
  > *"Jika menggunakan aturan keputusan argmax standar, model secara matematis akan selalu menebak kelas mayoritas dan memusnahkan kelas minoritas (Recall fakeshop menjadi 0%). Solusi metodologis kami adalah menerapkan Teori Keputusan Bayes melalui Cost-Sensitive Decision Thresholding: kami menggeser ambang batas vonis ($\arg\max (P_k + \Delta_k)$) terisolasi strictly di dalam training fold, dengan kelas mayoritas dikunci sebagai jangkar acuan ($\Delta_0 = 0.0$). Pendekatan ini dipadukan dengan Evidence Guard agar pergeseran batas tersebut tidak memicu lonjakan false positive."*

### Pertanyaan 5 (Dari Juri Panitia / Kurator Lomba):
*“Dari mana dasar pengambilan baseline Anda dan bagaimana Anda membenarkan setiap keputusan metode yang dipilih?”*
- **Jawaban Anda**:
  > *"Riset kami berangkat langsung dari materi resmi repositori Workshop PeDaS 2026 (`taufiksutanto/PeDaS-2026`). Di Sesi 2 Bab 6, pemateri mengajarkan model baseline awal: LinearSVC dengan Karakter 3–5 N-Gram (yang mencatatkan Macro-F1 0.5315).  
  > Dari titik tolak tersebut, kami secara disiplin mengeksekusi rekomendasi pemateri di Bab 11: pertama, memperkaya teks URL dengan metadata registrar dan brand (naik ke 0.5650). Kedua, mengatasi limitasi non-probabilitas LinearSVC yang dicatat di Bab 8 dengan Multiclass Platt Scaling. Ketiga, memadukannya dengan LightGBM tabular (bobot 60:40) dan penyesuaian threshold Bayes. Setiap iterasi dibuktikan dengan angka validasi empiris hingga mencapai puncak Macro-F1 0.6026 dengan waktu eksekusi hanya 10.47 detik."*

