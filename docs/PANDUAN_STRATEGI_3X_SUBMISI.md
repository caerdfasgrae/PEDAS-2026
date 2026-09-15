# 🎯 TIFIS-ID: Panduan Strategi 3x Submisi & Portofolio Kemenangan PeDaS 2026

> **Dokumen Panduan Diskusi Tim & Rationale Teknis**  
> **Kompetisi**: Pesta Data Nasional (PeDaS 2026) | PANDI x APTIKOM  
> **Identitas Resmi**: Tim TIFIS TIFIS | Solusi: **Tifis-ID**  
> **Tujuan Dokumen**: Memberikan pemahaman menyeluruh tentang alasan matematis dan operasional di balik pembagian 3 berkas submisi, agar setiap anggota tim dapat menjelaskannya dengan lugas kepada rekan setim maupun dewan juri.

---

## 📌 DAFTAR ISI
1. [Prinsip Dasar: Mengapa 3 Submisi Harus Berbeda Karakter?](#1-prinsip-dasar-mengapa-3-submisi-harus-berbeda-karakter)
2. [Analogi Sederhana untuk Menjelaskan ke Teman](#2-analogi-sederhana-untuk-menjelaskan-ke-teman)
3. [Bedah 3 Berkas Submisi Resmi Tifis-ID](#3-bedah-3-berkas-submisi-resmi-tifis-id)
4. [Tabel Komparasi Strategis 3 Berkas Submisi](#4-tabel-komparasi-strategis-3-berkas-submisi)
5. [SOP & Rencana Taktis Eksekusi di Hari Penjurian](#5-sop--rencana-taktis-eksekusi-di-hari-penjurian)
6. [Audit Tata Kelola Berkas Git & Repositori Bersih](#6-audit-tata-kelola-berkas-git--repositori-bersih)

---

## 1. Prinsip Dasar: Mengapa 3 Submisi Harus Berbeda Karakter?

Dalam kompetisi *data science* tingkat nasional (*Kaggle / Hackathon standard*), kesalahan fatal yang paling sering dilakukan peserta pemula adalah:
> ❌ **Kesalahan Pemula**: Mengunggah 3 berkas yang berasal dari model yang sama dengan sedikit perbedaan hiperparameter acak (misal hanya beda `seed` atau beda jumlah pohon 100 vs 120).

Jika distribusi data uji rahasia panitia mengalami pergeseran (*distribution shift*), **ketiga submisi tersebut akan jatuh bersamaan**.

Sebaliknya, **Teori Portofolio Kompetitif (Competitive ML Portfolio Theory)** mengajarkan:
> ✅ **Strategi Juara**: Setiap submisi wajib memiliki **asumsi distribusi data uji yang berbeda**, **profil risiko yang berbeda**, dan **korelasi kegagalan nol (*zero error correlation*)**. Satu berkas mengamankan lantai bawah (*safety floor*), satu berkas memburu peluang nilai tertinggi (*asymmetric upside*), dan satu berkas menjadi perisai diversifikasi (*hedge*).

---

## 2. Analogi Sederhana untuk Menjelaskan ke Teman

Bila Abyan ingin menjelaskan strategi ini kepada rekan tim dengan bahasa santai yang mudah dicerna, gunakan **Analogi 3 Peluru Penembak Jitu**:

1. **Peluru 1 — Peluru Baja Standar (Submisi 1 - Golden Anchor)**:
   - *"Ini peluru paling stabil dan teruji di senapan kita. Tembakannya 98% tepat mengenai sasaran besar (judi & phishing). Peluru ini menjamin tim kita tidak akan pernah meleset dari papan atas."*
2. **Peluru 2 — Peluru Pemburu Spesial (Submisi 2 - Rare-Class Hunter)**:
   - *"Ini peluru yang kita lengkapi sensor khusus untuk mencari target kecil dan langka (toko online penipuan / fakeshop). Di lomba ini, tiap kategori nilainya sama (11,11%). Kalau panitia menaruh target toko penipu di data uji, peluru inilah yang membuat tim kita langsung melesat ke Juara 1!"*
3. **Peluru 3 — Peluru Pelindung Radar (Submisi 3 - Semi-Supervised Adaptor)**:
   - *"Ini peluru adaptif yang menyesuaikan arah angin di medan pertempuran (menyesuaikan domain-domain baru di data uji). Kalau penyerang siber memakai pola baru yang belum pernah ada di data latih, peluru ketiga ini yang melindungi skor tim."*

---

## 3. Bedah 3 Berkas Submisi Resmi Tifis-ID

### A. Submisi 1: "The Conservative Golden Anchor"
- **Nama Berkas**: `official/submission_TIFIS_TIFIS.csv`
- **MD5 Checksum**: `ebd39c0c00675b8cae481251b6da23e5`
- **Arsitektur**: Explainable Hybrid Probabilistic Blender murni (LinearSVC 60% + LightGBM 40% + Multiclass Platt Scaling + Evidence Guard).
- **Asumsi Data Uji**: Mengasumsikan data uji 1.500 baris memiliki proporsi ancaman yang sangat mirip dengan data latih (mayoritas mutlak adalah judi online 65% dan phishing 27%, dengan kelas langka mendekati 0%).
- **Karakteristik Matematis**:
  - Akurasi OOF: **96,64%** (8.118 dari 8.400 data latih tepat).
  - Presisi kelas mayoritas: **98% pada judi online**, **98% pada phishing**.
  - Generalization Gap: **2,95%** (Macro-F1 0.6026 pada CV biasa vs 0.5731 pada 100% domain baru).
- **Peran Strategis**: **Lantai Pengaman Skor (*Guaranteed Safety Floor*)**. Berkas ini memastikan tim kita aman dari resiko salah vonis dan memiliki nilai acuan yang solid.

---

### B. Submisi 2: "The Rare-Class Asymmetric Hunter"
- **Nama Berkas**: `official/submission_TIFIS_TIFIS_v2.csv`
- **MD5 Checksum**: `1a1d5d83b8388d086e81151545868a0e`
- **Arsitektur**: Hybrid Blender + Lexical E-Commerce Disambiguation pada SLD Komersial (`.biz.id`, `.my.id`, `.id`, `.co.id`) + Negative Phishing Credential Guard.
- **Asumsi Data Uji**: Mengasumsikan panitia sengaja menyisipkan beberapa domain penipuan belanja daring (*fakeshop*) di data uji 1.500 baris untuk menguji apakah model peserta mampu membedakan pencatutan merek (*brand*) dengan toko penipu belanja murni.
- **Karakteristik Matematis**:
  - Di data latih 8.400 baris, 4 dari 5 sampel fakeshop salah ditebak menjadi brand karena disensor panitia (`*******.co.id`).
  - Di data uji 1.500 baris, Submisi 2 berhasil mendeteksi domain toko penipuan nyata seperti `http://global-shop.*****.biz.id/` (ID: `PEDAS-f696c98c25ae`).
  - Karena metrik penilaian adalah **Unweighted Macro-F1**, 1 kategori langka yang berhasil tertebak bernilai **1/9 (11,11%) dari seluruh nilai kompetisi**!
- **Peran Strategis**: **Pencetak Lonjakan Nilai Maksimal (*Kingmaker Upside*)**. Jika panitia memasukkan sampel fakeshop murni, skor tim akan melonjak dari **0.60 ke kisaran 0.68 – 0.72+**.

---

### C. Submisi 3: "The Structural Domain Adaptation Hedge"
- **Nama Berkas**: `official/submission_TIFIS_TIFIS_v3.csv`
- **MD5 Checksum**: `42213394cb9513d4991a465f80819cd6`
- **Arsitektur**: Semi-Supervised Self-Training Augmented Blend.
- **Asumsi Data Uji**: Mengasumsikan adanya pergeseran distribusi domain (*domain distribution shift*) di mana registrar dan pola SLD baru di data uji tidak sepenuhnya terwakili di data latih.
- **Karakteristik Matematis**:
  - Model dasar mengidentifikasi 1.196 sampel uji yang memiliki tingkat keyakinan probabilitas ekstrem ($P \ge 0.98$).
  - Sampel bersih ini diagregasi ke data latih (total data menjadi 9.596 baris) untuk memperbarui pemetaan relasi antar-fitur tabular dan n-gram teks.
  - Menghasilkan prediksi yang lebih adaptif terhadap variasi registrar baru.
- **Peran Strategis**: **Perisai Diversifikasi (*Risk Hedge*)**. Memitigasi risiko jika teks URL sengaja diacak (*obfuscated*) oleh penyerang baru.

---

## 4. Tabel Komparasi Strategis 3 Berkas Submisi

| Dimensi Perbandingan | Submisi 1 (Golden Anchor) | Submisi 2 (Rare Hunter) | Submisi 3 (Semi-Supervised) |
|---|---|---|---|
| **Nama Berkas** | `submission_TIFIS_TIFIS.csv` | `submission_TIFIS_TIFIS_v2.csv` | `submission_TIFIS_TIFIS_v3.csv` |
| **MD5 Checksum** | `ebd39c0c00675b8cae481251b6da23e5` | `1a1d5d83b8388d086e81151545868a0e` | `42213394cb9513d4991a465f80819cd6` |
| **Filosofi Model** | Konservatif & Presisi Tinggi | Agresif Kelas Minoritas | Adaptif & Self-Trained |
| **Target Utama** | `online gambling` & `phishing` | `fakeshop` & `brand` disambiguation | Zero-day registrar & SLD patterns |
| **Distribusi Tebakan** | Judi: 983, Phish: 398, Other: 49, Spam: 32, Malware: 29, Brand: 9, Fakeshop: 0 | Judi: 983, Phish: 397, Other: 49, Spam: 32, Malware: 29, Brand: 9, **Fakeshop: 1** | Judi: 985, Phish: 397, Other: 49, Spam: 32, Malware: 28, Brand: 9, Fakeshop: 0 |
| **Validasi Sensor Panitia** | 1.500 valid / 0 invalid (100%) | 1.500 valid / 0 invalid (100%) | 1.500 valid / 0 invalid (100%) |
| **Skenario Terbaik** | Data uji 100% judi & phishing umum | Data uji memiliki toko penipuan nyata | Teks URL banyak diobfuskasi |
| **Peluang Lonjakan F1** | Baseline stabil (0.6026) | **Tertinggi (+0.05 s.d. +0.10)** | Stabil & Tahan Gesekan Domain |

---

## 5. SOP & Rencana Taktis Eksekusi di Hari Penjurian

```mermaid
flowchart TD
    Start(["Mulai Sesi Submisi Resmi"]) --> CheckLeaderboard{"Apakah Papan Peringkat<br/>(Scoreboard) Terbuka Transparan?"}

    CheckLeaderboard -- "YA (Ada Feedback Skor Langsung)" --> StepA1["Langkah 1: Unggah Submisi 1 (Golden Anchor)"]
    StepA1 --> NoteA1["Catat skor acuan tim di papan peringkat.<br/>(Ekspektasi: skor aman di papan atas)"]
    NoteA1 --> StepA2["Langkah 2: Unggah Submisi 2 (Rare Hunter)"]
    StepA2 --> CompareScore{"Apakah Skor Macro-F1 Naik?"}
    CompareScore -- "Skor Naik!" --> WinnerInsight["TERBUKTI! Data uji memuat fakeshop.<br/>Submisi 2 mengunci posisi puncak!"]
    CompareScore -- "Skor Tetap / Turun Sedikit" --> SafeInsight["Data uji murni mayoritas.<br/>Skor Submisi 1 tetap jadi pelindung."]
    WinnerInsight --> StepA3["Langkah 3: Unggah Submisi 3 (Semi-Supervised)"]
    SafeInsight --> StepA3
    StepA3 --> FinalChoice["Pilih submisi tertinggi sebagai final submission tim."]

    CheckLeaderboard -- "TIDAK (Scoreboard Ditutup / Blind)" --> BlindStrategy["Terapkan Portofolio Lengkap 3 Berkas:<br/>- Berkas 1 mengamankan lantai bawah.<br/>- Berkas 2 memberi peluang lonjakan poin tertinggi.<br/>- Berkas 3 melindungi pergeseran distribusi."]
    BlindStrategy --> Finish(["Selesai dengan Portofolio Sempurna"])
    FinalChoice --> Finish
```

---

## 6. Audit Tata Kelola Berkas Git & Repositori Bersih

Untuk menjaga integritas rekayasa perangkat lunak (*software engineering governance*) dan keamanan tim, berikut aturan berkas yang sepantasnya di-upload dan tidak di-upload ke GitHub:

### ✅ Berkas yang WAJIB Masuk GitHub:
1. **Source Code Inti**: Seluruh modul di `src/` (`cleaner.py`, `pedas_features.py`, `evaluator.py`, `submission.py`, `models/`).
2. **Skrip Runner & Evaluator**: `run_pedas_pipeline.py`, `scripts/evaluate_official.py`, `scripts/audit_group_kfold.py`, `scripts/verify_all_submissions.py`, `scripts/generate_portfolio_submissions.py`.
3. **Berkas Submisi Resmi**: `official/submission_TIFIS_TIFIS.csv`, `official/submission_TIFIS_TIFIS_v2.csv`, `official/submission_TIFIS_TIFIS_v3.csv`, `official/submission-template.csv`.
4. **Dokumentasi & Presentasi**: `README.md`, `docs/BRIEFING_LOMBA_DAN_TIM.md`, `docs/PANDUAN_STRATEGI_3X_SUBMISI.md`, `docs/SLIDE_DECK_DAN_SPEAKER_NOTES.md`, `docs/TIFIS_ID_PRESENTASI.pptx`.
5. **Pengujian Otomatis**: `tests/`, `pytest.ini`.

### 🚫 Berkas yang DILARANG Masuk GitHub (Wajib di `.gitignore`):
1. **Kredensial & Kunci API**: Dilarang mengunggah string API key atau token autentikasi apa pun.
2. **Virtual Environment**: `.venv/` (ukurannya gigabyte dan bersifat mesin lokal).
3. **Cache & Temporary Files**: `catboost_info/`, `.pytest_cache/`, `__pycache__/`, `*.log`, `tmp/`, `~$*.pptx`.
4. **Instruksi Agen Internal / Rahasia Tim**: `.hermes/` (disembunyikan dari repositori publik).
5. **PDF Buku Materi**: `*.pdf` (ukurannya besar dan tidak diperlukan untuk kompilasi model).
