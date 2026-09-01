# PANDUAN KERJA AGENT & PROTOKOL REPOSITORI (AGENT_INSTRUCTIONS.md)
> **Proyek:** Deteksi Phishing Domain (.id) - PeDaS 2026 (APTIKOM Fest x PANDI)  
> **Target Pengguna:** AI Agent (Hermes Agent / DeepSeek / Llama / Antigravity)  
> **Workspace Root:** `c:\Users\SMI-CPU014\Documents\Abyan\PEDAS-2026`

---

## 1. Konteks Kompetisi & Aturan Keras (Non-Negotiable Rules)
1. **Bahasa Pemrograman**: **Python ONLY** (Regulasi resmi Poin 12 PeDaS 2026).
2. **Kesesuaian Pengumpulan**:
   - Kode utama dijalankan via Google Colab (`.ipynb`).
   - Kode harus di-commit ke GitHub untuk verifikasi babak final (Poin 8 aturan PeDaS).
   - Hasil eksekusi harus **100% deterministik dan reproducible** (`RANDOM_STATE = 42`).
3. **Pencegahan Kebocoran Data (*Anti-Data Leakage*)**:
   - Dilarang keras melakukan preprocessing, scaling, atau target encoding sebelum split data!
   - Pemisahan data untuk evaluasi domain `.id` wajib menggunakan **`StratifiedGroupKFold`** berdasarkan registered domain untuk mencegah *domain group leakage*.
4. **Dependensi Terkunci**:
   - Jangan menambahkan library eksternal sembarangan. Gunakan hanya yang terdaftar di `requirements.txt`.

---

## 2. Struktur Repositori & Pembagian Modul
Setiap agen yang bekerja di folder ini **WAJIB** mematuhi tata letak berikut:

```text
PEDAS-2026/
├── config/
│   └── indonesian_brands.yaml      # Kamus brand bank, fintech, dan kata kunci tipuan lokal
├── data/
│   ├── benchmark/                  # Dataset benchmark phishing vs legitimate domain .id
│   │   ├── sample_phishing_id.csv  # Sample awal (50 entri)
│   │   └── benchmark_expanded_id.csv # Dataset ekspansi dari Hermes Agent
│   ├── processed/                  # Fitur hasil ekstraksi siap latih
│   └── raw/                        # Dataset resmi PANDI (rilis 12 Sept)
├── notebooks/
│   └── 01_pemanasan_dan_ekstraksi_fitur.ipynb # Notebook utama untuk juri & Google Colab
├── src/
│   ├── features/
│   │   ├── lexical.py              # Ekstraksi fitur leksikal, entropy, panjang, rasio karakter
│   │   ├── domain_brand.py         # Deteksi combosquatting, typosquatting, subdomain hijacking
│   │   ├── nlp_stacking.py         # Out-of-Fold Char N-Gram (3-5) TF-IDF meta-feature
│   │   ├── dns_lookup.py           # Ekstraktor record DNS (A, AAAA, MX, NS, TXT)
│   │   ├── whois_parser.py         # Parser usia domain WHOIS
│   │   └── extractor.py            # Master PhishingFeatureExtractor pipeline
│   ├── models/
│   │   ├── metrics.py              # Metrik F1-Macro, ROC-AUC, FPR, Precision, Recall
│   │   ├── validation.py           # DomainGroupSplitter & NestedThresholdOptimizer
│   │   ├── baseline.py             # Baseline GBDT trainer
│   │   └── ensemble.py             # Multi-GBDT WeightedBlender (LGBM + CatBoost + XGBoost)
│   └── utils/
│       └── config.py               # Path resolver & RANDOM_STATE = 42
├── tests/
│   ├── test_features.py            # Unit tests fitur dasar
│   └── test_optimizations.py     # Unit tests GroupKFold, N-Gram Stacking, Ensemble
├── run_baseline.py                 # CLI runner evaluasi cepat
├── requirements.txt                # Dependensi terkunci
└── README.md                       # Dokumentasi resmi
```

---

## 3. Pembagian Peran Dual-Agent

### A. Peran ANTIGRAVITY (Lead System Architect & Core Engineer):
- Bertanggung jawab atas integritas arsitektur kode di `src/`.
- Memastikan seluruh unit test lolos (`pytest tests/ -v` -> 100% green).
- Memelihara kompatibilitas Google Colab dan repositori Git.
- Mengintegrasikan modul baru dan mencegah regresi performa.

### B. Peran HERMES AGENT (Threat Intelligence & Red-Teamer):
- **Domain Intelligence**: Meriset tren serangan phishing domain `.id` terbaru (perubahan modus tarif bank, e-wallet, bansos, APK kurir/undangan).
- **Dataset Curation**: Mengompilasi dan memvalidasi dataset URL baru ke dalam format CSV yang kompatibel.
- **Red-Teaming (Adversarial Testing)**: Menciptakan kasus uji ekstrem (*edge cases*) untuk mencari celah/kelemahan model deteksi.
- **Dilarang**: Mengubah arsitektur dasar di `src/models/` atau menghapus file tanpa instruksi eksplisit.

---

## 4. Standar Format Data Masukan (Data Schema Standard)

Jika Hermes Agent menghasilkan dataset CSV baru, kolom **WAJIB** mengikuti format ini:

```csv
url,label,category,attack_type,target_brand
http://bca-secure-login.id/verify,1,banking,combosquatting,bca
https://bank.klikbca.com,0,banking,legitimate_official,bca
http://dana-kaget-saldo-gratis-100rb.biz.id/klaim,1,fintech_ewallet,combosquatting,dana
```

### Definisi Nilai Kolom:
- `url`: String URL lengkap (dengan skema `http://` atau `https://`).
- `label`: Biner (`1` = Phishing, `0` = Legitimate).
- `category`: Salah satu dari: `banking`, `fintech_ewallet`, `ecommerce_marketplace`, `government_public`, `logistics`, `education`, `news_portal`.
- `attack_type`: `combosquatting`, `typosquatting`, `subdomain_hijack`, `apk_malware_lure`, `compromised_legit_domain`, `legitimate_official`.
- `target_brand`: Nama brand resmi (`bca`, `bri`, `mandiri`, `bni`, `cimb`, `dana`, `gopay`, `ovo`, `shopee`, `tokopedia`, `pajak`, `pln`, `bpjs`, atau `none`).

---

## 5. Protokol Pengujian & Verifikasi (Quality Assurance)
Setelah melakukan penambahan data atau fitur, jalankan perintah berikut untuk memvalidasi:
```bash
# 1. Jalankan semua unit test:
pytest tests/ -v

# 2. Jalankan evaluasi ensemble baseline:
python run_baseline.py --model ensemble --ngram-stacking
```
Seluruh 10 unit test **HARUS LOLOS** sebelum perubahan dianggap valid.
