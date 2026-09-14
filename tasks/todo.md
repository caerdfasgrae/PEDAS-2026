# Task List: PeDaS 2026 Champion Strategy

Status: Ready for Implementation  
Tracking: Markdown Checklist (`tasks/todo.md`)

---

## Phase 1: Probabilistic Calibration Engine & Cost-Sensitive Bayes Thresholding

### Task 1: Kalibrasi Probabilitas Multiclass (Platt Scaling pada Decision Margins)
**Description:** Mengonversi margin keputusan kontinu dari LinearSVC (`decision_function`) menjadi distribusi probabilitas posterior multivariat $P(y=k \mid x)$ menggunakan kalibrasi Sigmoid/Platt Scaling yang dilatih murni di dalam masing-masing fold cross-validation untuk mencegah data leakage.

**Acceptance criteria:**
- [x] Matriks probabilitas berukuran $(N, 9)$ tervalidasi dengan properti $\sum_k P(y=k \mid x) = 1.0 \pm 10^{-5}$ dan seluruh elemen $\ge 0.0$.
- [x] Modul kalibrator dapat melakukan `fit` pada training fold dan `transform` pada validation fold tanpa kebocoran data.

**Verification:**
- [x] Tests pass: `.\.venv\Scripts\pytest.exe -k "test_probability_calibration"`
- [x] Manual check: Verifikasi visual distribusi probabilitas kelas mayoritas vs minoritas pada sampel Out-of-Fold.

**Dependencies:** None  
**Files likely touched:**
- `src/models/probabilistic_calibrator.py`
- `tests/test_probabilistic_calibrator.py`  
**Estimated scope:** Small (1-2 files)

---

### Task 2: Bayes Threshold Optimizer Terisolasi Lipatan (Nested CV)
**Description:** Mengoptimalkan offset threshold keputusan $\Delta_k$ untuk memaksimalkan metrik Macro-F1 dengan mengunci kelas mayoritas `online gambling` pada $\Delta_0 = 0.0$ sebagai jangkar. Optimasi dilakukan murni pada Out-of-Fold predictions dari internal training fold untuk mencegah resubstitution overclaiming.

**Acceptance criteria:**
- [x] Offset $\Delta_k$ dioptimalkan secara terisolasi tanpa mengakses fold evaluasi akhir.
- [x] Macro-F1 leak-free tercatat dan terbukti tidak mengalami degradasi performa pada kelas mayoritas.

**Verification:**
- [x] Tests pass: `.\.venv\Scripts\pytest.exe -k "test_threshold_optimizer"`
- [x] Manual check: Nilai Macro-F1 nested out-of-fold tercatat stabil di $\ge 0.5800$.

**Dependencies:** Task 1  
**Files likely touched:**
- `src/models/threshold_optimizer.py`
- `src/models/calibrated_ensemble_pipeline.py`  
**Estimated scope:** Medium (2-3 files)

---

## Checkpoint: Phase 1
- [x] Seluruh unit test Phase 1 lolos tanpa warning.
- [x] Probabilitas posterior terkalibrasi secara matematis dan terbukti stabil di bawah cross-validation.


---

## Phase 2: High-Precision Rare Class Detectors & Evidence Guards

### Task 3: Ekstraktor Bukti Leksikal Spesifik untuk `fakeshop`, `piiexposure`, dan `violence`
**Description:** Mengembangkan modul ekstraksi sinyal leksikal berpresisi tinggi untuk mengidentifikasi indikator eksplisit kategori minoritas di URL dan path (misal: token transaksi e-commerce, indikator identitas pribadi KTP/NIK/kebocoran data, dan pola kekerasan/isu hukum).

**Acceptance criteria:**
- [x] Mengidentifikasi secara deterministik URL di data latih dan data uji yang memuat indikator retail murni vs judi online berkedok shop.
- [x] Tidak menghasilkan pencocokan palsu (*false matches*) pada URL berlabel `online gambling` atau `phishing`.

**Verification:**
- [x] Tests pass: `.\.venv\Scripts\pytest.exe -k "test_evidence_guard"`
- [x] Manual check: Inspeksi manual terhadap URL yang terpicu di data latih (memastikan 0 false positive pada 5.447 domain judi).

**Dependencies:** None  
**Files likely touched:**
- `src/pedas_features.py`
- `tests/test_evidence_guard.py`  
**Estimated scope:** Small (1-2 files)

---

### Task 4: Anti-False-Positive Guard (Mencegah Halusinasi pada Kelas Mayoritas)
**Description:** Membangun mekanisme pengaman (*evidence guard*) yang memastikan offset threshold untuk kelas langka hanya diaktifkan bila terdapat bukti fitur spesifik. Jika bukti tidak ditemukan, keputusan tetap diserahkan pada margin model utama guna melindungi presisi kelas mayoritas.

**Acceptance criteria:**
- [x] Skor F1 kelas mayoritas (`online gambling`, `phishing`) tidak turun lebih dari 0.001 akibat aktivasi guard minoritas.
- [x] Kategori `fakeshop` berhasil mendeteksi true positive tambahan dengan presisi $\ge 0.50$.

**Verification:**
- [x] Tests pass: `.\.venv\Scripts\pytest.exe -k "test_evidence_guard"`
- [x] Manual check: Evaluasi confusion matrix OOF menunjukkan false positive ke kelas minoritas $\le 3$ domain.

**Dependencies:** Task 2, Task 3  
**Files likely touched:**
- `src/models/evidence_guard.py`
- `src/models/calibrated_ensemble_pipeline.py`  
**Estimated scope:** Medium (2-3 files)

---

## Checkpoint: Phase 2
- [x] Evaluasi 5-Fold Stratified CV menunjukkan peningkatan Macro-F1 melampaui `0.6000`.
- [x] Tidak ada degradasi pada akurasi kelas mayoritas.


---

## Phase 3: Explainable Hybrid Blending & Domain Generalization Audit

### Task 5: Ensembling Probabilistik Hibrida (Calibrated LinearSVC + GBDT)
**Description:** Mengombinasikan probabilitas terkalibrasi dari model linier n-gram berbasis teks (LinearSVC) dengan model pohon keputusan (LightGBM/CatBoost) yang unggul dalam memodelkan interaksi non-linear fitur domain (`sld`, `registrar`, leksikal), menghasilkan ensemble probabilitas terbobot yang transparan.

**Acceptance criteria:**
- [x] Model ensemble menghasilkan probabilitas gabungan yang stabil dan berbobot seimbang (SVC 0.60 + LGB 0.40).
- [x] Skor Macro-F1 out-of-fold dari ensemble lebih tinggi daripada model tunggal individual (0.6026 vs 0.5749).

**Verification:**
- [x] Tests pass: `.\.venv\Scripts\pytest.exe -o pythonpath=. tests/test_hybrid_blender.py` (3 passed in 1.78s)
- [x] Manual check: Perbandingan tabel metrik OOF per kelas sebelum vs sesudah ensemble.

**Dependencies:** Task 1, Task 4  
**Files likely touched:**
- `src/models/hybrid_blender.py`
- `tests/test_hybrid_blender.py`  
**Estimated scope:** Medium (2-3 files)

---

### Task 6: Stress-Testing Komparatif Ulang pada Strict Domain Group-KFold
**Description:** Menjalankan uji ketahanan generalisasi pada skenario *Zero Domain Overlap* (100% domain baru) untuk membuktikan secara empiris bahwa model ensemble dan kalibrasi probabilitas tidak mengalami domain-level overfitting.

**Acceptance criteria:**
- [x] Generalization gap antara Stratified CV dan Strict Group-KFold tetap terkontrol ($\le 3.0\%$): Gap terbukti hanya 2.95% (0.6026 vs 0.5731).
- [x] F1-score pada domain baru untuk kelas `online gambling` $\ge 0.96$ (0.9752) dan `phishing` $\ge 0.94$ (0.9484).

**Verification:**
- [x] Tests pass: `.\.venv\Scripts\python.exe scripts/audit_group_kfold.py`
- [x] Manual check: Konfirmasi selisih Macro-F1 tercatat secara deterministik (+0.0295).

**Dependencies:** Task 5  
**Files likely touched:**
- `scripts/audit_group_kfold.py`  
**Estimated scope:** Small (1 file)

---

## Checkpoint: Phase 3
- [x] Model ensemble hibrida lolos uji audit Group-KFold tanpa tanda-tanda memorisasi domain.
- [x] Seluruh keputusan model dapat dijelaskan berdasarkan kontribusi bobot n-gram dan fitur tabular.

---

## Phase 4: Golden Submission Package & Final Live CLI

### Task 7: Generator & Validator Berkas Golden Submission
**Description:** Menjalankan pelatihan model penuh pada 100% data latih (8.400 baris) dengan konfigurasi teruji, mengekstrak prediksi pada 1.500 data uji [official/predict.csv](file:///c:/Users/SMI-CPU014/Documents/Abyan/PEDAS-2026/official/predict.csv), dan melakukan validasi skema menyeluruh terhadap [official/submission-template.csv](file:///c:/Users/SMI-CPU014/Documents/Abyan/PEDAS-2026/official/submission-template.csv).

**Acceptance criteria:**
- [x] Berkas keluaran memiliki tepat 1.500 baris dan 2 kolom (`id,category`).
- [x] 0 nilai `NaN`, 0 string kosong, seluruh urutan ID cocok sempurna dengan berkas prediksi resmi.
- [x] Berkas lolos fungsi verifikasi [`validate_submission`](file:///c:/Users/SMI-CPU014/Documents/Abyan/PEDAS-2026/src/submission.py).

**Verification:**
- [x] Tests pass: `.\.venv\Scripts\python.exe scripts/generate_golden_submission.py`
- [x] Manual check: Verifikasi checksum MD5 (`ebd39c0c00675b8cae481251b6da23e5`) dan distribusi kategori prediksi pada berkas CSV.

**Dependencies:** Task 5, Task 6  
**Files likely touched:**
- `scripts/generate_golden_submission.py`
- `official/golden_submission_pedas2026.csv`  
**Estimated scope:** Small (1-2 files)

---

### Task 8: Pembuatan CLI Runner Babak Final 1-Klik (`run_pedas_pipeline.py`)
**Description:** Mengemas seluruh alur end-to-end (preprocessing deterministik, ekstraksi fitur, kalibrasi threshold, inferensi, dan validasi format) ke dalam sebuah antarmuka CLI mandiri yang dapat dijalankan secara instan (<45 detik) saat dewan juri menguji pada dataset validasi 5% tersembunyi di Babak Final.

**Acceptance criteria:**
- [x] Perintah CLI: `python run_pedas_pipeline.py --train <path> --predict <path> --output <path>` berjalan mulus tanpa error.
- [x] Waktu eksekusi total dari awal hingga akhir $\le 45$ detik pada mesin lokal biasa: Terbukti hanya **12.43 detik** via `Measure-Command`.
- [x] Menampilkan ringkasan metrik dan log transparan tanpa peringatan *convergence* yang mengganggu.

**Verification:**
- [x] Tests pass: `.\.venv\Scripts\pytest.exe -o pythonpath=. tests/test_pipeline_cli.py` (1 passed in 13.18s)
- [x] Manual check: Verifikasi waktu eksekusi dengan `Measure-Command` di PowerShell (12.43s).

**Dependencies:** Task 7  
**Files likely touched:**
- `run_pedas_pipeline.py`
- `README.md` (instruksi eksekusi final)  
**Estimated scope:** Small (1-2 files)

---

## Checkpoint: Final Ready
- [x] Satu berkas Golden Submission siap kirim tersimpan rapi dengan prinsip *fault tolerance* di `official/golden_submission_pedas2026.csv` (MD5: `ebd39c0c00675b8cae481251b6da23e5`).
- [x] Runner Babak Final tervalidasi siap dipresentasikan di hadapan juri PANDI & APTIKOM (<13 detik).

