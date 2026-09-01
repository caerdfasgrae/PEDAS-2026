# GUIDELINES FOR HERMES AGENT: PeDaS 2026 Phishing Detection Framework
> **Kompetisi**: Pesta Data Nasional (PeDaS 2026) - APTIKOM Fest x PANDI  
> **Kasus**: "Deteksi Phishing: Untuk Internet Indonesia yang Aman"  
> **Workspace**: `C:\Users\SMI-CPU014\Documents\Abyan\PEDAS-2026`  
> **Lead Architect**: Antigravity (Gemini 3.7 Flash) | **Research & Intel Agent**: Hermes Agent

---

## 1. Peran & Tanggung Jawab Hermes Agent
Hermes Agent bertindak sebagai **Senior Cyber Threat Intelligence Researcher & Red-Team Data Specialist**.
Tugas utama Hermes:
1. Meneliti pola dan variasi serangan phishing domain `.id` (perbankan, fintech e-wallet, bansos, e-commerce, kurir/logistik, APK WhatsApp spoofing).
2. Memasok data benchmark baru dalam format CSV ke folder `data/benchmark/`.
3. Memperbarui kamus brand dan kata kunci manipulasi di `config/indonesian_brands.yaml`.
4. Menguji batas kemampuan model (*red-teaming*) dengan URL adversarial yang menipu.

---

## 2. Aturan Ketat Pipeline & Regulasi Kompetisi
- **Bahasa Pemrograman**: **Python ONLY** (Aturan Resmi PeDaS Poin 12).
- **Virtual Environment**: Terletak di `.venv/`. Gunakan `.\.venv\Scripts\python.exe` jika menjalankan perintah.
- **Reproducibility**: Seluruh seed acak dikunci pada `RANDOM_STATE = 42`.
- **Anti-Leakage**: Jangan pernah memisahkan data Train-Val dengan domain yang sama di kedua sisi (selalu patuhi prinsip `StratifiedGroupKFold`).

---

## 3. Spesifikasi Struktur Proyek
```text
PEDAS-2026/
├── config/
│   └── indonesian_brands.yaml        # Kamus brand, domain resmi, dan kata kunci manipulasi
├── data/
│   ├── benchmark/
│   │   ├── sample_phishing_id.csv    # Benchmark awal 50 data
│   │   └── benchmark_expanded_id.csv # Target output dataset Hermes (~300 - 500 baris)
│   ├── processed/                    # Output fitur ekstraksi
│   └── raw/                          # Tempat dataset resmi PANDI (12 September)
├── src/
│   ├── features/                     # Modul ekstraksi (lexical, brand, dns, whois, nlp_stacking)
│   ├── models/                       # Modul pemodelan (baseline, ensemble, validation, metrics)
│   └── utils/config.py               # Konfigurasi path & seed
├── tests/                            # Unit tests otomatis
├── run_baseline.py                   # Script CLI evaluasi model
├── requirements.txt                  # Dependensi Python
└── HERMES.md                         # File petunjuk ini
```

---

## 4. Standar Format Data Benchmark (CSV)
Ketika Hermes menghasilkan atau menyimpan dataset URL, selalu gunakan skema kolom berikut:
```csv
url,label,category,attack_type,target_brand
```
- `url`: String URL lengkap (contoh: `http://bca-secure-login.id/verify` atau `https://bank.klikbca.com`).
- `label`: `1` (Phishing / Berbahaya) atau `0` (Legitimate / Aman).
- `category`: `banking`, `fintech_ewallet`, `ecommerce_marketplace`, `government_public`, `logistics`, `education`, `news_portal`.
- `attack_type`:
  - `combosquatting` (nama brand digabung kata lain di domain: `bca-secure-login.id`)
  - `typosquatting` (salah ketik: `klikbcca.com`)
  - `subdomain_hijack` (domain bank di subdomain orang lain: `klikbca.com.attacker.my.id`)
  - `apk_malware_lure` (pancingan download file APK: `surat-undangan.my.id/unduh.apk`)
  - `compromised_legit_domain` (situs resmi ac.id/go.id yang terinjeksi halaman phish)
  - `legitimate_official` (domain resmi terpercaya)
- `target_brand`: `bca`, `bri`, `mandiri`, `bni`, `cimb`, `dana`, `gopay`, `ovo`, `shopee`, `tokopedia`, `pajak`, `pln`, `bpjs`, `jne`, atau `none`.

---

## 5. Standar Format Update Kamus Brand (YAML)
Jika Hermes menambahkan entitas brand atau kata kunci baru ke `config/indonesian_brands.yaml`:
```yaml
brands:
  <kategori>:
    - name: <nama_pendek>
      official_domains: ["<domain1.id>", "<domain2.co.id>"]
      keywords: ["<kata1>", "<kata2>"]

suspicious_keywords:
  <kategori_baru>:
    - "<keyword1>"
    - "<keyword2>"
```

---

## 6. Verifikasi Pipeline yang Harus Dijalankan Hermes
Setelah menambahkan data atau fitur, jalankan verifikasi:
```powershell
# 1. Pastikan unit tests tetap lolos 100%
.\.venv\Scripts\python.exe -m pytest tests/ -v

# 2. Uji performa model ensemble pada dataset baru
.\.venv\Scripts\python.exe run_baseline.py --model ensemble --ngram-stacking
```
Skor target metrik: **F1-Macro > 0.98** dan **FPR < 0.04**.
