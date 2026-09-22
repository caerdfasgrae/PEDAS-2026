# Artefak & Provenance Submisi 1 (PeDaS 2026)

Dokumen ini mencatat seluruh rekam jejak, konfigurasi, dan berkas pembangun resmi untuk **Submisi 1** yang disubmit pada Leaderboard PeDaS 2026.

## 1. Identitas Submisi Resmi
- **Waktu Submit**: Minggu, 21 September 2026, 11:12:02 WIB
- **Nama File**: `TIFIS TIFIS-01.csv`
- **Lokasi Master Terkunci**: [`official/submitted/TIFIS TIFIS-01.csv`](../../official/submitted/TIFIS%20TIFIS-01.csv)
- **MD5 Checksum**: `e4a37ec272e3990bfa9153e44edb688e`
- **Jumlah Baris**: 1.500 baris data + 1 baris header (`id,category`)
- **Skor Leaderboard Resmi**: **`0.744171684130824`** (Peringkat 8 saat submit)

## 2. Distribusi Kelas Submisi 1 (9 Kelas Aktif)
| Kategori | Jumlah Baris | Persentase |
|---|:---:|:---:|
| `online gambling` | 980 | 65.33% |
| `phishing` | 397 | 26.47% |
| `other` | 47 | 3.13% |
| `spam` | 31 | 2.07% |
| `malware` | 27 | 1.80% |
| `brand` | 15 | 1.00% |
| `violence` | 1 | 0.07% |
| `piiexposure` | 1 | 0.07% |
| `fakeshop` | 1 | 0.07% |
| **Total** | **1.500** | **100.0%** |

## 3. Berkas Provenance yang Diarsipkan
- `archive/submission_1_provenance/indonesian_brands.yaml`: Kamus brand legacy eksplorasi awal. Di runtime produksi Submisi 1, model menggunakan 18 token hardcoded in-memory di `src/pedas_features.py:189`.
- `archive/submission_1_provenance/`: Tempat penyimpanan artefak statis pembangun Submisi 1 jika panitia/juri meminta audit reproduktibilitas sejarah Submisi 1.
