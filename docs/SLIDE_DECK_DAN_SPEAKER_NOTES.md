# 📊 TIFIS-ID: Slide Deck & Naskah Presentasi (10 Slide Master)
> **Pitch Deck Resmi Tim TIFIS TIFIS**: Siap dipakai langsung di PowerPoint (`docs/TIFIS_ID_PRESENTASI.pptx`), Google Slides, atau Canva.  
> **Kompetisi**: Pesta Data Nasional (PeDaS 2026) | APTIKOM Fest 2026 x PANDI  
> **Target Juara**: Juara 1 Nasional & **Piala Best Analysis**  
> **Durasi Presentasi**: 7–10 Menit (Alokasi waktu per slide: 45–60 detik)  
> **Kepatuhan Aturan**: 100% Netral Double-Blind (Nama Tim: **TIFIS TIFIS** | Nama Solusi: **Tifis-ID**)

---

## 🧭 Panduan Navigasi Slide
- **Slide 1**: Judul Solusi & Identitas Tim (Double Blind: Tifis-ID oleh Tim TIFIS TIFIS)
- **Slide 2**: Urgensi Masalah & Kerugian Nasional Phishing Domain Murah (.id)
- **Slide 3**: Analisis Kritis: Celah Operasional IDADX & BIMA AI Saat Ini
- **Slide 4**: Metodologi Riset: 7-Langkah Machine Learning Lifecycle (CRISP-DM Standard)
- **Slide 5**: Rekayasa Fitur Dual-Stream: N-Gram Sub-Word & Siklus Hidup Domain
- **Slide 6**: Arsitektur Utama: Explainable Hybrid Probabilistic Blender (LinearSVC + LightGBM)
- **Slide 7**: Hasil Evaluasi Empiris: 5-Fold Macro-F1 & Audit Strict Group-KFold (Gap 2.95%)
- **Slide 8**: Inovasi Safety: Evidence Guardrail & Live Demo Inspector (`tifis_inspect`)
- **Slide 9**: Rekomendasi Kebijakan Strategis: Pre-Delegation DNS Gatekeeper untuk PANDI
- **Slide 10**: Kesimpulan, Kepatuhan Regulasi Juknis, & Integritas Submisi Resmi

---

## SLIDE 1: Judul Solusi & Identitas Tim (Double Blind)
* **Waktu**: 0:00 – 0:35 (35 Detik)
* **Visual Slide**:
  - Judul Utama: **Tifis-ID**
  - Subjudul: *Sistem Deteksi & Klasifikasi Ancaman Cerdas Domain (.id) Berbasis Explainable Hybrid Probabilistic Blender & Evidence Guardrail*
  - Identitas Peserta: **Tim TIFIS TIFIS**
  - Kategori: Pesta Data Nasional (PeDaS 2026) — APTIKOM Fest 2026 x PANDI
  - Tiga Pilar Kunci: *Zero-Leakage GroupKFold | Cost-Sensitive Bayes Threshold | < 11s SLA Inference*
* **Sitasi / Sumber Valid**:
  - *Ref: Panduan Teknis & Regulasi PeDaS 2026 (Slide 8 Ketentuan Double Blind), APTIKOM & PANDI, 2026.*
* **Naskah Pembicara (Speaker Script)**:
  > *"Selamat pagi Dewan Juri yang terhormat, perwakilan APTIKOM dan PANDI.  
  > Kami dari **Tim TIFIS TIFIS** mempersembahkan **Tifis-ID**—sebuah kerangka kerja kecerdasan buatan terpadu untuk deteksi dini dan klasifikasi 9 kategori ancaman siber pada ekosistem domain tingkat tinggi `.id`.  
  > Solusi kami dirancang bukan sekadar untuk mengejar metrik leaderboard, melainkan dibangun di atas metodologi yang terjelaskan (*explainable*), divalidasi tanpa kebocoran data, dan siap diterapkan sebagai sistem pendukung keputusan (*Decision Support System*) di gerbang PANDI."*

---

## SLIDE 2: Urgensi Masalah & Kerugian Nasional Phishing Domain Murah
* **Waktu**: 0:35 – 1:20 (45 Detik)
* **Visual Slide**:
  - Tiga Kartu Metrik Masalah:
    - **Kartu 1 (Merah)**: Eksploitasi Second-Level Domain (SLD) Murah (`.my.id` & `.biz.id` harga Rp10.000–Rp15.000 tanpa KTP).
    - **Kartu 2 (Kuning)**: 3 Modus Dominan Indonesia: Pencatutan Bank/Fintech (BCA/DANA), Injeksi Web Kampus/Pemerintah (`.ac.id`/`.go.id`), dan Pancingan APK WhatsApp.
    - **Kartu 3 (Abu-abu)**: Kerugian Finansial Korban Penipuan Online Nasional mencapai puluhan miliar rupiah per tahun.
* **Sitasi / Sumber Valid**:
  - *Ref: Laporan Tahunan Ancaman Siber IDADX PANDI 2025/2026; APWG Phishing Activity Trends Report.*
* **Naskah Pembicara (Speaker Script)**:
  > *"Mari kita mulai dari akar permasalahan nyata di ekosistem digital Indonesia.  
  > Domain `.id` adalah simbol kedaulatan internet kita. Namun, maraknya pendaftaran domain murah tanpa verifikasi ketat—khususnya `.my.id` dan `.biz.id`—telah dimanfaatkan pelaku kejahatan siber untuk menyebarkan malware APK dan phishing perbankan yang menguras tabungan masyarakat.  
  > Lebih licik lagi, pelaku kerap menyusupkan tautan ilegal ke dalam direktori institusi pendidikan `.ac.id` dan pemerintahan `.go.id`. Jika tidak ditanggulangi dengan cepat, reputasi domain kebanggaan kita akan terpuruk di lembaga pemantau internet internasional."*

---

## SLIDE 3: Analisis Kritis: Celah Operasional IDADX & BIMA AI
* **Waktu**: 1:20 – 2:05 (45 Detik)
* **Visual Slide**:
  - Diagram Banding 3 Pendekatan:
    - **IDADX**: Bersifat Reaktif. Domain baru ditindak setelah korban melapor (biasanya setelah 24 jam kejahatan berlangsung).
    - **BIMA AI**: Deep Web Crawling. Memindai isi web secara mendalam, namun membutuhkan waktu perayapan berjam-jam untuk jutaan domain aktif.
    - **Tifis-ID (Hijau - Solusi Tim)**: *Pre-Delegation & First-Line Triage Gatekeeper*. Memeriksa struktur URL dan metadata registrar di gerbang pendaftaran dalam **~10.5 detik untuk 1.500 domain**, menghentikan ancaman sebelum domain aktif memakan korban!
* **Sitasi / Sumber Valid**:
  - *Ref: Arsitektur Alur Penanganan Insiden IDADX PANDI & Paparan Teknis BIMA AI.*
* **Naskah Pembicara (Speaker Script)**:
  > *"PANDI saat ini memiliki dua instrumen utama: IDADX yang menampung laporan publik, dan BIMA AI yang merayapi web.  
  > Namun, terdapat celah waktu krusial: IDADX bersifat reaktif setelah ada korban, sementara perayapan konten web membutuhkan waktu dan sumber daya komputasi besar.  
  > Tifis-ID hadir untuk mengisi celah tersebut dengan paradigma **Pre-Delegation Gatekeeper**. Kami memeriksa domain di gerbang pendaftaran dalam hitungan milidetik secara offline berbasis struktur URL dan jejak registrar. Hasilnya, kita bisa menahan domain berbahaya sebelum sempat online didelegasikan ke DNS!"*

---

## SLIDE 4: Metodologi Riset: 7-Langkah Machine Learning Lifecycle
* **Waktu**: 2:05 – 2:50 (45 Detik)
* **Visual Slide**:
  - Alur 7 Tahapan CRISP-DM Terstandar:
    1. *Problem Framing* (Dilema FP vs FN; Target Metrik Unweighted Macro-F1).
    2. *Data Ingestion* (8.400 data latih resmi & 1.500 data uji predict PANDI).
    3. *Data Preprocessing* (Normalisasi Unicode NFKC, pembersihan URL, sintesis konteks komposit).
    4. *Feature Engineering* (Karakter N-Gram 3–5 gram + 56 Fitur Domain Lifecycle).
    5. *Model Training* (LinearSVC 60% + LightGBM 40% + Multiclass Platt Scaling).
    6. *Decision Tuning* (Cost-Sensitive Bayes Thresholding & Evidence Guard).
    7. *Deployment & CLI* (Runner 1-Klik `run_pedas_pipeline.py` & API `tifis_inspect`).
* **Sitasi / Sumber Valid**:
  - *Ref: CRISP-DM Standard Process Model; Google Machine Learning Engineering Best Practices.*
* **Naskah Pembicara (Speaker Script)**:
  > *"Dalam mengembangkan Tifis-ID, kami mematuhi standar baku 7-Langkah Machine Learning Lifecycle.  
  > Kami tidak menggunakan trik 'black-box' yang rapuh. Seluruh tahapan—mulai dari perumusan trade-off, pembersihan data, ekstraksi fitur dual-stream, kalibrasi probabilitas, hingga pengaman bukti leksikal—dirancang secara modular dan deterministik dengan random seed 2026, siap diaudit baris demi baris di repositori kami."*

---

## SLIDE 5: Rekayasa Fitur Dual-Stream: N-Gram & Siklus Hidup Domain
* **Waktu**: 2:50 – 3:45 (55 Detik)
* **Visual Slide**:
  - Diagram Aliran Dua Sisi:
    - **Stream A (Linguistik & Sub-word)**: TF-IDF 15.000 n-gram karakter (3–5 huruf). Menangkap manipulasi huruf (*typosquatting*) seperti `kl1k`, `b-c-a`, kata pancingan judi (`gacor`, `maxwin`, `deposit`), dan malware (`.apk`).
    - **Stream B (Infrastruktur & Siklus Hidup)**: 56 fitur terstruktur: Shannon Entropy domain, rasio simbol, kecocokan fuzzy Levenshtein terhadap 30+ brand nasional, usia domain (`domain_age_days`), dan riwayat registrar.
* **Sitasi / Sumber Valid**:
  - *Ref: Shannon, C. E., Bell System Technical Journal (Entropy); TF-IDF Sub-word Tokenization Standards.*
* **Naskah Pembicara (Speaker Script)**:
  > *"Kekuatan model kami terletak pada arsitektur fitur Dual-Stream yang saling melengkapi:  
  > Stream pertama membaca nuansa teks menggunakan n-gram karakter 3 hingga 5 huruf. Ini memungkinkan model mengenali kamuflase ketikan penipu tanpa terpengaruh kesalahan ejaan.  
  > Stream kedua mengekstrak 56 fitur tabular siklus hidup domain: mengukur keacakan nama domain hasil Domain Generation Algorithm, mencocokkan pencatutan brand perbankan lokal, serta menganalisis pola usia domain pancingan yang baru berumur beberapa hari."*

---

## SLIDE 6: Arsitektur Utama: Explainable Hybrid Probabilistic Blender
* **Waktu**: 3:45 – 4:35 (50 Detik)
* **Visual Slide**:
  - Diagram Alir Arsitektur Hibrida:
    - *LinearSVC (Bobot 60%)*: Membedah ruang teks berdimensi tinggi, dikonversi ke probabilitas posterior via **Multiclass Platt Scaling**.
    - *LightGBM (Bobot 40%)*: Memodelkan interaksi non-linear fitur tabular dan infrastruktur registrar.
    - *Convex Blending*: $P_{\text{blend}} = 0.60 \times P_{\text{SVC}} + 0.40 \times P_{\text{LGB}}$.
    - *Cost-Sensitive Bayes Threshold Optimizer*: Menggeser ambang batas keputusan $\hat{y} = \arg\max_k (P_k + \Delta_k)$ dengan mengunci kelas judi online sebagai jangkar ($\Delta_0 = 0.0$).
* **Sitasi / Sumber Valid**:
  - *Ref: Platt, J., Probabilistic Outputs for Support Vector Machines; Ke et al., LightGBM: A Highly Efficient GBDT.*
* **Naskah Pembicara (Speaker Script)**:
  > *"Untuk klasifikasi 9 kategori ancaman, kami merancang Explainable Hybrid Probabilistic Blender.  
  > Kami memadukan LinearSVC berbasis n-gram dengan LightGBM berbasis data tabular. Margin keputusan linier dikalibrasi menjadi probabilitas sejati menggunakan Multiclass Platt Scaling.  
  > Mengapa kami tidak memakai argmax standar? Karena pada data yang sangat tidak seimbang, argmax standar bias ke kelas mayoritas. Melalui penyesuaian threshold Bayes terisolasi lipatan, kami menaikkan skor Macro-F1 secara adil tanpa mengorbankan presisi kelas mayoritas."*

---

## SLIDE 7: Hasil Evaluasi Empiris & Stress-Test Generalisasi
* **Waktu**: 4:35 – 5:30 (55 Detik)
* **Visual Slide**:
  - Tangga Peningkatan Kinerja (5-Fold CV):
    - *Workshop Starter Baseline (taufiksutanto Sesi 2 Bab 6)*: Macro-F1 = `0.5315`
    - *Metadata Enrichment (URL + Registrar/Brand Sesi 2 Bab 11)*: Macro-F1 = `0.5650`
    - *Model Tunggal (LightGBM 0.5819 / LinearSVC 0.5749)*
    - **Tifis-ID Champion (Hybrid 60:40 + Bayes Calibration)**: **Macro-F1 = `0.6026`** (+7.11% lonjakan performa).
  - Kotak Metrik Produksi & Audit Generalisasi:
    - *Akurasi Riil Out-of-Fold (OOF)*: **`96.64%`** (8.118 dari 8.400 baris tepat).
    - *Skor pada 100% Unseen Domains (Strict Group-KFold)*: **`0.5731`** (Generalization Gap hanya **`2.95%`**, membuktikan model bebas memorisasi domain).
    - *Kecepatan Inferensi Penuh*: **10.47 Detik** (Jauh melampaui SLA Juknis PeDaS < 45 Detik).
* **Sitasi / Sumber Valid**:
  - *Ref: Repositori Resmi Workshop PeDaS 2026 (taufiksutanto/PeDaS-2026 Sesi 2); Hasil Evaluasi CV dan Stress-Test Group-KFold Repositori TIFIS-ID.*
* **Naskah Pembicara (Speaker Script)**:
  > *"Mari kita lihat bukti empiris keunggulan Tifis-ID pada Slide 7.  
  > Kami tidak asal memilih model. Kami bertolak langsung dari model baseline workshop resmi PeDaS 2026 (LinearSVC dengan Macro-F1 0.5315). Melalui pengayaan konteks metadata registrar, kalibrasi Platt probabilitas, perpaduan hybrid 60:40, dan penyesuaian threshold Bayes, kami berhasil melompatkan performa hingga mencapai puncak **Macro-F1 0.6026** dengan akurasi riil **96.64%**.  
  > Yang terpenting, saat kami uji pada skenario ekstrem Zero Domain Overlap di mana 100% domain uji adalah domain baru, skor tetap kokoh di **0.5731** dengan selisih generalisasi hanya 2.95%. Ini membuktikan model kita benar-benar siap dan aman beroperasi di gerbang PANDI."*


---

## SLIDE 8: Inovasi Safety: Evidence Guardrail & Live Demo Inspector
* **Waktu**: 5:30 – 6:20 (50 Detik)
* **Visual Slide**:
  - **Prinsip Evidence Guard**: Threshold untuk kelas minoritas (`fakeshop`, `violence`, `piiexposure`) hanya aktif jika terdapat bukti teks keras. Jika URL memuat kata judi/phishing/malware tak terbantahkan, vonis minoritas dibatalkan demi melindungi presisi kelas mayoritas.
  - Tangkapan Layar Demo: Kartu Diagnosis Interaktif **`tifis_inspect(url)`** (Desain High-Contrast Slate SOC Card menampilkan vonis, probabilitas, dan rekomendasi aksi PANDI).
* **Sitasi / Sumber Valid**:
  - *Ref: Guardrails for Trustworthy AI; Human-in-the-Loop Cybersecurity Systems.*
* **Naskah Pembicara (Speaker Script)**:
  > *"Satu inovasi keselamatan penting yang kami bangun adalah **Evidence Guardrail**.  
  > Pada data tidak seimbang, model sering kali 'berhalusinasi' menebak kelas langka hanya karena ada kata umum seperti 'product' di situs judi. Evidence Guard mengunci aturan bahwa vonis kelas langka hanya diizinkan bila terdapat bukti leksikal nyata.  
  > Untuk membuktikan transparansinya, kami menyediakan fungsi `tifis_inspect`. Hanya dalam 8 milidetik, sistem mampu membedah URL apa pun yang diuji oleh dewan juri, menampilkan probabilitas terkalibrasi dan rekomendasi tindakan operasional."*

---

## SLIDE 9: Rekomendasi Kebijakan Strategis untuk PANDI & IDADX
* **Waktu**: 6:20 – 7:10 (50 Detik)
* **Visual Slide**:
  - Tiga Rekomendasi Aksi Industri:
    1. **Pre-Delegation DNS Gatekeeper pada SLD Murah (`.my.id` & `.biz.id`)**: Menahan pendaftaran domain baru berprobabilitas ancaman tinggi hingga pendaftar memverifikasi identitas.
    2. **Otomatisasi Triase Prioritas IDADX**: Laporan publik yang masuk dipilah otomatis; domain dengan ancaman > 90% langsung dialirkan ke antrean penanganan prioritas tim CSIRT.
    3. **Whitelist Finansial Terintegrasi**: Sinkronisasi database resmi perbankan nasional untuk mendeteksi peniruan subdomain legal secara instan.
* **Sitasi / Sumber Valid**:
  - *Ref: Rekomendasi Kebijakan Kedaulatan Internet PANDI; Kerangka Kerja Incident Response BSSN.*
* **Naskah Pembicara (Speaker Script)**:
  > *"Sebagai luaran aplikatif bagi PANDI dan industri internet Indonesia, kami merumuskan 3 rekomendasi:  
  > Pertama, pasang Tifis-ID sebagai radar pre-delegasi pada Registrar API untuk SLD murah. Domain yang mencatut bank ditahan sebelum sempat aktif.  
  > Kedua, gunakan model ini untuk triase otomatis portal aduan IDADX agar analis PANDI dapat memprioritaskan situs paling berbahaya dalam hitungan detik.  
  > Ketiga, bangun integrasi whitelist terpusat dengan perbankan nasional demi melindungi konsumen finansial digital Indonesia."*

---

## SLIDE 10: Kesimpulan, Kepatuhan Regulasi Juknis, & Submisi Resmi
* **Waktu**: 7:10 – 7:45 (35 Detik)
* **Visual Slide**:
  - Tiga Poin Kepatuhan Regulasi PeDaS 2026:
    - **100% Python Native (Slide 8 Poin 12)**: Tanpa dependensi GPU rumit, eksekusi lokal hanya 10.49 detik.
    - **Reproducibility Terjamin (Slide 8 Poin 8)**: Random state terkunci di `2026`, hasil Colab dan lokal identik.
    - **Double Blind Ready (Slide 8 Poin 7)**: Netral tanpa identitas institusi, nama tim: **TIFIS TIFIS**.
  - **Status Submisi Resmi**: Berkas `official/submission_TIFIS_TIFIS.csv` (MD5: `ebd39c0c00675b8cae481251b6da23e5`, 1.500 baris tervalidasi bebas cacat).
* **Sitasi / Sumber Valid**:
  - *Ref: Petunjuk Teknis Resmi PeDaS 2026; Skrip Evaluator Resmi taufiksutanto/PeDaS-2026.*
* **Naskah Pembicara (Speaker Script)**:
  > *"Sebagai penutup, Tifis-ID telah membuktikan keunggulan metodologi, ketahanan generalisasi, efisiensi eksekusi 10 detik, dan kepatuhan penuh pada regulasi PeDaS 2026.  
  > Berkas submisi resmi kami `submission_TIFIS_TIFIS.csv` telah tervalidasi 100% lolos sensor skrip evaluator panitia.  
  > Kami dari Tim TIFIS TIFIS siap menjawab pertanyaan Dewan Juri. Terima kasih dan salam kedaulatan digital Indonesia!"*
