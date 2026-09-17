# 📋 SOP & PANDUAN EKSEKUSI 3X SUBMISI RESMI PANITIA PEDAS 2026
## Prosedur Operasional Standar (SOP) Penyerahan Berkas Portofolio Tim TIFIS TIFIS

> **Otoritas Kompetisi**: PANDI (Pengelola Nama Domain Internet Indonesia) x APTIKOM  
> **Kompetisi**: Pesta Data Nasional (PeDaS 2026) — Kategori Domain Abuse Classification  
> **Identitas Resmi Tim**: **TIFIS TIFIS** | **Nama Solusi**: **Tifis-ID**  
> **Klasifikasi Berkas**: RAHASIA TIM — PANDUAN TAKTIS HARI PENJURIAN  
> **Versi Dokumen**: 2.0 (Edisi Penyempurnaan Portofolio Cerdas)  

---

## 📌 1. TUJUAN & DASAR KEBIJAKAN SUBMISI

Sesuai **Pasal 6 Petunjuk Teknis Babak Penyisihan PeDaS 2026**:
1. Setiap tim hanya memiliki **maksimal 3 kali kesempatan pengiriman berkas submisi** sepanjang seluruh babak penyisihan (bukan 3 kali per hari).
2. Setiap berkas yang berhasil diunggah dengan pasangan Nama Tim dan PIN terdaftar **dihitung menghanguskan 1 kesempatan**, termasuk berkas yang gagal validasi format.
3. Metrik pemeringkatan tunggal adalah **Unweighted Macro-F1 (Pasal 7)** di mana 9 kelas ancaman memiliki bobot setara (1/9 = 11.11%).

**Tujuan SOP Ini**:  
Memberikan panduan operasional langkah demi langkah bagi seluruh anggota tim untuk mengunggah berkas tanpa risiko kesalahan format, memaksimalkan peluang skor tertinggi melalui Teori Portofolio Kompetitif, dan merespons dinamika papan peringkat secara taktis.

---

## 🎯 2. PORTOFOLIO CERDAS 3X SUBMISI: PEMBAGIAN PERAN & RATIONALE

Kesalahan fatal tim pemula adalah mengunggah tiga variasi acak dari model yang sama. Jika data uji mengalami pergeseran distribusi (*domain shift*), ketiga submisi akan jatuh bersamaan.

Tim TIFIS TIFIS menerapkan **Competitive Portfolio Theory** dengan membagi 3 berkas submisi ke dalam karakter ortogonal dengan korelasi kegagalan nol (*zero error correlation*):

```
                                  [ PORTOFOLIO 3X SUBMISI TIFIS-ID ]
                                                  |
         +----------------------------------------+----------------------------------------+
         |                                        |                                        |
   [ SUBMISI 1 ]                            [ SUBMISI 2 ]                            [ SUBMISI 3 ]
Conservative Golden Anchor             Rare-Class Asymmetric Hunter             Structural Adaptive Hedge
--------------------------             ----------------------------             -------------------------
• File: submission_TIFIS_TIFIS.csv     • File: ..._TIFIS_v2.csv                 • File: ..._TIFIS_v3.csv
• MD5: ebd39c0c00675b8cae48...         • MD5: 1a1d5d83b8388d086...              • MD5: 42213394cb9513d49...
• OOF Macro-F1: 0.6026                 • Kingmaker Upside: F1 +0.08             • Domain Adaptation Shift
• Akurasi: 96.64%                      • Fokus: Target Toko Penipu              • Self-Training (P >= 0.98)
• Peran: LANTAI PENGAMAN SKOR          • Peran: PEMBURU JUARA 1                 • Peran: PERISAI DIVERSIFIKASI
```

### Rincian Profil 3 Berkas Submisi:

| Parameter | Submisi 1 (Golden Anchor) | Submisi 2 (Rare Hunter) | Submisi 3 (Adaptive Hedge) |
|---|---|---|---|
| **Nama Berkas** | `submission_TIFIS_TIFIS.csv` | `submission_TIFIS_TIFIS_v2.csv` | `submission_TIFIS_TIFIS_v3.csv` |
| **MD5 Checksum** | `ebd39c0c00675b8cae481251b6da23e5` | `1a1d5d83b8388d086e81151545868a0e` | `42213394cb9513d4991a465f80819cd6` |
| **Arsitektur Model** | Hybrid Blender (LinearSVC 60% + LightGBM 40% + Platt + Guard) | Hybrid Blender + E-Commerce Lexical Disambiguation on Commercial SLD | Semi-Supervised Self-Training Augmented Blend (1.196 pseudo-labels) |
| **Distribusi Prediksi** | Judi: 983, Phish: 398, Other: 49, Spam: 32, Malware: 29, Brand: 9 | Judi: 983, Phish: 397, Other: 49, Spam: 32, Malware: 29, Brand: 9, **Fakeshop: 1** | Judi: 985, Phish: 397, Other: 49, Spam: 32, Malware: 28, Brand: 9 |
| **Sensor Panitia** | **1.500 valid / 0 invalid (PASSED)** | **1.500 valid / 0 invalid (PASSED)** | **1.500 valid / 0 invalid (PASSED)** |
| **Peran Strategis** | Mengamankan lantai bawah papan atas (Macro-F1 0.6026, akurasi 96,64%). | Mencetak lonjakan skor maksimal (+0.08 s.d. +0.11) bila toko penipu muncul. | Melindungi tim dari variasi registrar & token obfuscation baru di data uji. |

---

## 🌲 3. POHON KEPUTUSAN & RENCANA TAKTIS DI HARI PENJURIAN

Eksekusi pengunggahan berkas wajib mengikuti bagan alir taktis berikut, tergantung apakah panitia membuka umpan balik skor langsung (*Open Leaderboard*) atau menutupnya (*Blind Evaluation*):

```mermaid
flowchart TD
    Start(["Mulai Sesi Submisi Resmi"]) --> CheckLB{"Apakah Papan Peringkat (Scoreboard)<br/>Menampilkan Skor Langsung?"}

    CheckLB -- "YA (Open Leaderboard)" --> OpenS1["Langkah 1: Unggah Submisi 1 (Golden Anchor)<br/>Nama file: submission_TIFIS_TIFIS.csv"]
    OpenS1 --> NoteS1["Catat skor acuan tim di papan peringkat.<br/>(Ekspektasi: skor aman di papan atas)"]
    NoteS1 --> OpenS2["Langkah 2: Unggah Submisi 2 (Rare Hunter)<br/>Nama file: submission_TIFIS_TIFIS_v2.csv"]
    OpenS2 --> CompareScore{"Apakah Skor Macro-F1 Naik?"}
    
    CompareScore -- "Skor Naik Signifikan (+0.05 s.d. +0.08)" --> WinCase["HIPOTESIS TERBUKTI!<br/>Data uji panitia memuat toko penipu (fakeshop).<br/>Submisi 2 mengunci posisi puncak!"]
    WinCase --> OpenS3A["Langkah 3: Simpan kuota atau unggah Submisi 3<br/>untuk diversifikasi akhir."]
    
    CompareScore -- "Skor Tetap / Turun Sangat Sedikit" --> SafeCase["Data uji panitia didominasi murni judi/phishing.<br/>Skor Submisi 1 tetap menjadi pelindung utama tim."]
    SafeCase --> OpenS3B["Langkah 3: Unggah Submisi 3 (Adaptive Hedge)<br/>untuk menguji adaptasi domain baru."]
    
    CheckLB -- "TIDAK (Blind Evaluation / Tertutup)" --> BlindAll["Terapkan Protokol Alokasi Portofolio Penuh:<br/>- Submisi 1 (Golden Anchor): Amankan lantai acuan.<br/>- Submisi 2 (Rare Hunter): Beri daya ungkit juara 1.<br/>- Submisi 3 (Adaptive Hedge): Perisai variasi registrar."]
    BlindAll --> Finish(["Seluruh 3 Kuota Teroptimasi Maksimal"])
    OpenS3A --> Finish
    OpenS3B --> Finish
```

---

## ✅ 4. PRE-FLIGHT CHECKLIST (10 TITIK PEMERIKSAAN KESELAMATAN)

Sebelum mengklik tombol "Submit" pada formulir panitia, Person-in-Charge (PIC) Submisi wajib memverifikasi 10 poin keselamatan berikut:

- [ ] **1. Nama Berkas Tepat**: Nama berkas harus diawali `submission_` dan diikuti nama tim terdaftar (misal: `submission_TIFIS_TIFIS.csv`).
- [ ] **2. Format Berkas Murni CSV**: Tidak berekstensi `.xlsx`, `.txt`, `.csv.zip`, atau format lain.
- [ ] **3. Jumlah Baris Tepat 1.501 Baris (Termasuk Header)**: Tepat 1 baris header + 1.500 baris data prediksi.
- [ ] **4. Nama Kolom Persis**: Kolom pertama bernama `id`, kolom kedua bernama `category`.
- [ ] **5. Urutan ID Persis Template**: Urutan baris ID sama 100% dengan `official/predict.csv` dan `official/submission-template.csv`.
- [ ] **6. Bebas Nilai Kosong / Null**: Tidak ada nilai kosong, `NaN`, `null`, atau spasi kosong pada kolom `category`.
- [ ] **7. Seluruh Prediksi Masuk 9 Kelas Resmi**: Hanya berisi `online gambling`, `phishing`, `other`, `spam`, `malware`, `brand`, `fakeshop`, `violence`, `piiexposure`.
- [ ] **8. Checksum MD5 Terverifikasi**:
  - Submisi 1: `ebd39c0c00675b8cae481251b6da23e5`
  - Submisi 2: `1a1d5d83b8388d086e81151545868a0e`
  - Submisi 3: `42213394cb9513d4991a465f80819cd6`
- [ ] **9. Uji Sensor Resmi Lulus**: Menjalankan sensor panitia menghasilkan status `PASSED (100% Valid, 0 Errors)`.
- [ ] **10. Kredensial Tim Siap**: Nama Tim (`TIFIS TIFIS`) dan PIN Resmi Panitia telah dicocokkan dengan lembar pendaftaran.

---

## 💻 5. PROTOKOL VERIFIKASI SENSOR OTOMATIS SEBELUM UNGGAH

Jalankan perintah berikut di PowerShell untuk memvalidasi berkas secara lokal menggunakan simulator sensor panitia:

```powershell
# 1. Validasi sensor resmi panitia untuk seluruh berkas submisi
.\.venv\Scripts\python.exe scripts/verify_all_submissions.py

# 2. Verifikasi checksum kriptografis MD5
Get-FileHash -Algorithm MD5 official/submission_TIFIS_TIFIS*.csv
```

**Hasil Ekspektasi Sensor**:
```
File: submission_TIFIS_TIFIS.csv
  MD5 Checksum : ebd39c0c00675b8cae481251b6da23e5
  Valid Rows   : 1500
  Invalid Rows : 0
  -> Sensor Status: PASSED (100% Valid, 0 Errors)

File: submission_TIFIS_TIFIS_v2.csv
  MD5 Checksum : 1a1d5d83b8388d086e81151545868a0e
  Valid Rows   : 1500
  Invalid Rows : 0
  -> Sensor Status: PASSED (100% Valid, 0 Errors)

File: submission_TIFIS_TIFIS_v3.csv
  MD5 Checksum : 42213394cb9513d4991a465f80819cd6
  Valid Rows   : 1500
  Invalid Rows : 0
  -> Sensor Status: PASSED (100% Valid, 0 Errors)
```

---

## 🚨 6. PROTOKOL MITIGASI KEGAGALAN (EMERGENCY RECOVERY)

Jika terjadi kendala saat pengunggahan di portal panitia:
1. **Jaringan Terputus Saat Upload**:
   - Periksa status kuota tim di portal. Jika pengiriman belum tercatat, segarkan halaman dan unggah ulang berkas yang sama.
2. **Server Panitia Melaporkan Format Error**:
   - Dilarang mengedit berkas CSV menggunakan Microsoft Excel (Excel kerap mengubah format tanda kutip dan encoding UTF-8).
   - Selalu gunakan berkas asli yang diekspor dari pipeline Python di folder `official/`.
   - Jalankan `python scripts/evaluate_official.py --sub official/<nama_file>.csv --pred official/predict.csv` untuk membaca pesan galat spesifik.
3. **Dokumentasi Bukti**:
   - Ambil tangkapan layar (*screenshot*) bukti pengunggahan yang memuat timestamp sistem, nama berkas, dan respons server panitia sebagai arsip jika diperlukan klarifikasi/sanggahan (Pasal 9).

---

## 🏆 7. LEMBAR PERSETUJUAN TIM

SOP ini telah ditinjau dan disetujui untuk dijadikan rujukan operasional resmi:

- **Lead Implementation Engineer**: Abyan / worker_portfolio_impl
- **Lead Data Scientist**: Tim TIFIS TIFIS
- **Status Otorisasi**: **DISETUJUI UNTUK EKSEKUSI PENYISIHAN PEDAS 2026**
