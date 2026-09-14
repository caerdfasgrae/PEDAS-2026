# Implementation Plan: PeDaS 2026 Champion Strategy (Probabilistic Calibration & Operational Pipeline)

## Overview
Rencana kerja terstruktur ini dirancang untuk memaksimalkan skor **Macro-F1** pada Babak Penyisihan secara metodologis, empiris, dan deterministik, sekaligus mempersiapkan keunggulan mutlak pada Babak Final (uji validasi live 5% dan nilai operasional IDADX PANDI). Pendekatan ini mengawinkan **Teori Keputusan Bayes (Cost-Sensitive Probabilistic Thresholding)** dengan model yang terjelaskan (*explainable*), menjaga resistensi overfitting yang telah teruji pada audit Group-KFold (gap hanya 2,18%), serta memanfaatkan sumber daya lokal secara efisien (<45 detik waktu eksekusi).

---

## Architecture Decisions

1. **Teori Keputusan Bayes untuk Macro-F1 (Bukan Argmax Standar)**:
   * Pada klasifikasi multiclass dengan ketimpangan ekstrem (`online gambling` 5.447 vs `fakeshop` 5), keputusan standar $\hat{y} = \arg\max_k P(y=k \mid x)$ secara matematis bias ke kelas mayoritas.
   * Solusi metodologis: Mengonversi skor margin keputusan ke probabilitas terkalibrasi (via Platt Scaling / Sigmoid terisolasi fold) dan menerapkan penyesuaian prior threshold Bayes $\hat{y} = \arg\max_k (S_k(x) + \Delta_k)$ dengan kelas mayoritas terkunci sebagai jangkar acuan ($\Delta_0 = 0.0$).
2. **Isolasi Penuh Lipatan Validasi (Zero-Leakage Guarantee)**:
   * Seluruh ekstraksi fitur teks (TF-IDF), pengkodean kategorikal (SLD/Registrar), dan estimasi parameter kalibrasi probabilitas hanya dipelajari dari *training fold*, kemudian ditransformasikan ke *validation fold*.
3. **Penyisihan berbasis Fault Tolerance**:
   * Kuota 3x submission diperlakukan murni sebagai jaring pengaman redundansi (*fault tolerance*), bukan ajang coba-coba. Kita hanya mengeksekusi 1 submission matang setelah validasi internal mencapai kestabilan optimal.
4. **Live-Ready CLI untuk Babak Final**:
   * Mengemas seluruh alur kerja ke dalam sebuah skrip mandiri (`run_pedas_pipeline.py`) yang deterministik (`random_state=2026`), selesai dieksekusi dalam <45 detik, dan siap diuji secara langsung di hadapan dewan juri pada dataset validasi tersembunyi 5%.

---

## Task List Summary

### Phase 1: Probabilistic Calibration Engine & Cost-Sensitive Bayes Thresholding
- [ ] **Task 1**: Kalibrasi Probabilitas Multiclass (Platt Scaling pada Decision Margins)
- [ ] **Task 2**: Bayes Threshold Optimizer Terisolasi Lipatan (Nested CV)

### Checkpoint: Phase 1
- [ ] Kalibrasi probabilitas terbukti meningkatkan Macro-F1 leak-free tanpa degradasi kelas mayoritas.

### Phase 2: High-Precision Rare Class Detectors & Evidence Guards
- [ ] **Task 3**: Ekstraktor Bukti Leksikal Spesifik untuk `fakeshop`, `piiexposure`, dan `violence`
- [ ] **Task 4**: Anti-False-Positive Guard (Mencegah Halusinasi pada Kelas Mayoritas)

### Checkpoint: Phase 2
- [ ] F1 kelas minoritas meningkat tanpa menimbulkan *false positive* pada kelas `brand` atau `phishing`.

### Phase 3: Explainable Hybrid Blending & Domain Generalization Audit
- [ ] **Task 5**: Ensembling Probabilistik Hibrida (Calibrated LinearSVC + LightGBM / CatBoost)
- [ ] **Task 6**: Stress-Testing Komparatif Ulang pada Strict Domain Group-KFold

### Checkpoint: Phase 3
- [ ] Generalization gap pada domain baru tetap berada di bawah ambang batas aman (< 3,0%).

### Phase 4: Golden Submission Package & Final Live CLI
- [ ] **Task 7**: Generator & Validator Berkas Golden Submission (100% Lolos Format Template)
- [ ] **Task 8**: Pembuatan CLI Runner Babak Final 1-Klik (`run_pedas_pipeline.py`)

### Checkpoint: Complete
- [ ] Berkas submission final tervalidasi 100% bebas cacat.
- [ ] Runner CLI tuntas dieksekusi dalam < 45 detik dengan dokumentasi lengkap.

---

## Risks and Mitigations

| Risiko | Dampak | Strategi Mitigasi |
|---|---|---|
| **Overfitting Threshold pada Data Uji** | Tinggi | Kunci kelas mayoritas sebagai jangkar ($\Delta_0 = 0.0$); optimasi threshold dibatasi dalam ruang koordinat terikat (*bounded coordinate search*) hanya pada fold latih. |
| **False Positive pada Kelas Langka** | Sedang | *Evidence Guard*: threshold untuk kelas minoritas hanya diturunkan jika ada bukti leksikal eksplisit (misal token `shop`/`toko` untuk `fakeshop`). |
| **Diskrepansi Skema Evaluator Panitia** | Kritis | Verifikasi ganda otomatis terhadap `official/submission-template.csv`: baris tepat 1.500, 2 kolom `id,category`, urutan ID identik. |
| **Kegagalan Eksekusi Live di Final** | Tinggi | Skrip CLI mandiri berbobot ringan (<45 detik), bebas dependensi berat GPU/PyTorch, dan seluruh seed diikat permanen pada `2026`. |

---

## Open Questions & Review
- Apakah pembagian tahapan ini sudah mencerminkan kebutuhan tim Anda sebelum kita melangkah mengeksekusi Phase 1?
