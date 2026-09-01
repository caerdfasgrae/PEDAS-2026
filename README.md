# PeDaS 2026 - Deteksi Phishing Domain (.id)
> **Pesta Data Nasional (PeDaS 2026) | Aptikom Fest 2026 x PANDI**  
> *Membangun Solusi Cerdas Deteksi Phishing untuk Internet Indonesia yang Aman*

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/caerdfasgrae/PEDAS-2026/blob/main/notebooks/01_pemanasan_dan_ekstraksi_fitur.ipynb)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 1. Latar Belakang & Kasus Kompetisi
Kompetisi **PeDaS 2026** diselenggarakan oleh **APTIKOM** bekerja sama dengan **PANDI** (Pengelola Nama Domain Internet Indonesia). Tantangan utama adalah mendeteksi domain/URL phishing yang menargetkan ekosistem domain `.id` (termasuk `.id`, `.co.id`, `.web.id`, `.my.id`, `.biz.id`, dll.).

Serangan phishing di Indonesia sering menggunakan:
1. **Brand Combosquatting / Impersonation**: Menggabungkan nama bank / e-wallet resmi dengan kata kunci tipuan (misal: `http://bca-secure-login.id/verify`, `http://dana-kaget-saldo-gratis-100rb.biz.id/klaim`).
2. **Karakteristik Leksikal & Struktural Mencurigakan**: Penggunaan protokol HTTP tidak aman, subdomain berlebih, pemalsuan token URL, entropy keacakan tinggi.
3. **Anomali DNS & WHOIS**: Domain baru didaftarkan (< 30 hari), ketiadaan catatan MX/SPF, registrar tertentu.

---

## 🗂️ 2. Struktur Repositori
```text
PEDAS-2026/
├── config/
│   └── indonesian_brands.yaml      # Kamus brand perbankan, fintech, & kata kunci phishing Indonesia
├── data/
│   ├── benchmark/
│   │   ├── sample_phishing_id.csv  # Dataset uji coba awal phishing vs legitimate .id
│   │   └── benchmark_expanded_id.csv # Dataset benchmark ekspansi Hermes Agent (212 baris)
│   ├── processed/                  # Fitur hasil ekstraksi & file oof_predictions.csv
│   └── raw/                        # Tempat penyimpanan dataset resmi PANDI
├── notebooks/
│   └── 01_pemanasan_dan_ekstraksi_fitur.ipynb  # Notebook Colab-ready untuk EDA & baseline training
├── src/
│   ├── features/
│   │   ├── lexical.py              # Ekstraksi fitur leksikal, statistik karakter, & entropy
│   │   ├── domain_brand.py         # Deteksi brand impersonation, combosquatting, & typosquatting
│   │   ├── dns_lookup.py           # Ekstraktor record DNS (A, AAAA, MX, NS, TXT)
│   │   ├── whois_parser.py         # Parser usia domain & status kedaluwarsa WHOIS
│   │   ├── nlp_stacking.py         # Out-of-Fold Char N-Gram TF-IDF Stacking
│   │   └── extractor.py            # Master Feature Extractor pipeline (Batch & DataFrame)
│   ├── models/
│   │   ├── metrics.py              # Metrik evaluasi (F1-Score, ROC-AUC, FPR, Precision, Recall)
│   │   ├── validation.py           # DomainGroupSplitter & NestedThresholdOptimizer
│   │   ├── ensemble.py             # WeightedBlender Multi-GBDT (LGBM + CatBoost + XGBoost)
│   │   └── baseline.py             # Stratified K-Fold CV & GBDT Trainer (Bagged Predict)
│   └── utils/
│       └── config.py               # Konfigurasi path, environment Colab/Local, & random seed
├── tests/
│   ├── test_features.py            # Unit tests validasi fitur leksikal & brand
│   └── test_optimizations.py     # Unit tests GroupKFold, N-Gram Stacking, Threshold, & Ensemble
├── run_baseline.py                 # CLI runner cepat untuk melatih & mengevaluasi model
├── requirements.txt                # Kunci dependensi Python
├── .gitignore                      # Mengabaikan file cache, virtualenv, dan model biner
├── HERMES.md                       # Petunjuk pipeline untuk Hermes Agent
├── AGENTS.md                       # SOP umum multi-agent
└── README.md                       # Dokumentasi resmi proyek
```

---

## 🚀 3. Panduan Menjalankan

### Opsi A: Google Colab (Format Pengumpulan PeDaS)
Sesuai tradisi dan format pengumpulan PeDaS, seluruh alur pemodelan dapat langsung dijalankan di Google Colab:
1. Klik badge **Open in Colab** di atas atau buka tautan:
   👉 [Buka di Google Colab](https://colab.research.google.com/github/caerdfasgrae/PEDAS-2026/blob/main/notebooks/01_pemanasan_dan_ekstraksi_fitur.ipynb)
2. Notebook akan otomatis melakukan clone repositori `https://github.com/caerdfasgrae/PEDAS-2026.git` dan menginstal dependensi.
3. Jalankan pipeline ekstraksi fitur dan cross-validation secara berurutan.

### Opsi B: Lingkungan Lokal
1. **Buat & Aktifkan Virtual Environment**:
   ```bash
   python -m venv .venv
   # Windows:
   .\.venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```
2. **Install Dependensi**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Jalankan Pengujian Unit (Unit Tests)**:
   ```bash
   pytest tests/test_features.py -v
   ```

---

## 🔬 4. Rekayasa Fitur (Feature Engineering)
| Kelompok Fitur | Deskripsi | Manfaat untuk Kasus Phishing .id |
|---|---|---|
| **Leksikal & Struktural** | Panjang URL, path depth, subdomain count, rasio simbol/digit, Shannon Entropy URL & domain, keberadaan protokol HTTPS | Mendeteksi URL acak hasil DGA, pemalsuan subdomain, serta situs palsu tanpa SSL resmi. |
| **Indonesian Brand Spoofing** | Pencocokan nama brand perbankan (BCA, Mandiri, BRI, BNI), fintech (DANA, GoPay, OVO), combosquatting detection (`bca-secure-login`) | Mengenali teknik social engineering paling umum di Indonesia yang meniru entitas resmi. |
| **DNS Statistics** | Resolusi record A, AAAA, MX, NS, TXT, dan jumlah IP | Situs phishing seringkali tidak memiliki MX record (server email) atau menggunakan NS murah. |
| **WHOIS Metadata** | Umur domain (`domain_age_days`), sisa waktu kedaluwarsa, registrasi < 30 hari | Mayoritas domain phishing berumur sangat muda dan didaftarkan hanya untuk masa aktif singkat. |

---

## 📊 5. Validasi & Ketentuan Kompetisi
- **Bebas Data Leakage**: Evaluasi menggunakan **Stratified 5-Fold Cross Validation**. Semua penskalaan dan rekayasa hanya difit pada fold pelatihan.
- **Reproducibility**: Parameter acak dikunci menggunakan `RANDOM_STATE = 42`.
- **Kesesuaian Regulasi (Poin 8 & 12 Aturan PeDaS)**:
  - Seluruh kode ditulis murni dalam **Python**.
  - Pipeline deterministik memastikan hasil notebook di Google Colab identik dengan kode di GitHub repository saat diverifikasi dewan juri pada babak final.
