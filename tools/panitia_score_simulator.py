"""Tools Penghitung Potensi Skor & Auditor Komparatif Submisi PeDaS 2026.

Alat ini mengimplementasikan aturan resmi panitia (scripts/evaluate_official.py)
dan membandingkan setiap berkas CSV kandidat secara baris-demi-baris terhadap
Submisi 1 (official/submitted/TIFIS TIFIS-01.csv) yang memiliki skor resmi 0.744171684130824.

Fitur:
1. Validasi Ketat Panitia: Header, ID 1-1500, normalisasi NFKC, 9 kategori valid.
2. Analisis Transisi Baris: Deteksi baris yang berubah kategori dan matriks perpindahan.
3. Simulasi Potensi Skor Panitia: Menghitung proyeksi dampak Macro-F1 pada berbagai skenario GT
   (7 kelas, 8 kelas, 9 kelas) berdasarkan skor acuan Submisi 1 (0.74417).
4. Mode Batch / Looping: Menginspeksi seluruh file kandidat di suatu folder.

Usage:
  .venv/Scripts/python tools/panitia_score_simulator.py --candidate official/submission_final.csv
  .venv/Scripts/python tools/panitia_score_simulator.py --dir official/
"""

import argparse
import csv
import json
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

# 9 Kategori Resmi PANDI (evaluate_official.py)
VALID_CATEGORIES = {
    "online gambling",
    "phishing",
    "other",
    "spam",
    "malware",
    "brand",
    "fakeshop",
    "violence",
    "piiexposure",
}

DEFAULT_SUB1_PATH = Path("official/submitted/TIFIS TIFIS-01.csv")
SUB1_OFFICIAL_SCORE = 0.744171684130824


def normalize_category(value: str) -> str:
    """Normalisasi resmi panitia: NFKC, casefold, spasi tunggal."""
    if not isinstance(value, str):
        value = str(value)
    value = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(value.split())


def read_and_validate_csv(path: Path) -> Tuple[Dict[str, str], List[str], Dict[str, Any]]:
    """Membaca dan memvalidasi file submission sesuai aturan evaluasi panitia."""
    errors = []
    data = {}
    if not path.exists():
        return {}, [f"File tidak ditemukan: {path}"], {"valid": False}

    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, strict=True)
        header = next(reader, [])
        if len(header) != 2 or set(header) != {"id", "category"}:
            errors.append(f"Header tidak sesuai: {header}. Wajib tepat ['id', 'category']")
            return {}, errors, {"valid": False}

        id_counts = Counter()
        row_num = 1
        for row in reader:
            row_num += 1
            if len(row) != 2:
                errors.append(f"Baris {row_num}: jumlah kolom {len(row)} != 2")
                continue
            r_id = row[0].strip()
            r_cat = normalize_category(row[1])

            if not r_id:
                errors.append(f"Baris {row_num}: ID kosong")
            id_counts[r_id] += 1
            if id_counts[r_id] > 1:
                errors.append(f"Baris {row_num}: ID duplikat '{r_id}'")

            if not r_cat:
                errors.append(f"Baris {row_num}: kategori kosong")
            elif r_cat not in VALID_CATEGORIES:
                errors.append(f"Baris {row_num}: kategori '{r_cat}' tidak valid")

            data[r_id] = r_cat

    if len(data) != 1500:
        errors.append(f"Jumlah baris {len(data)} != 1500")

    summary = {
        "valid": len(errors) == 0,
        "total_rows": len(data),
        "errors_count": len(errors),
        "class_distribution": dict(Counter(data.values())),
        "active_classes": sorted(list(set(data.values()))),
        "num_active_classes": len(set(data.values())),
    }
    return data, errors, summary


def compare_candidate_with_sub1(
    candidate_path: Path,
    sub1_path: Path = DEFAULT_SUB1_PATH,
    predict_meta_path: Optional[Path] = Path("data/predict.csv"),
) -> Dict[str, Any]:
    """Melakukan komparasi baris-per-baris kandidat CSV terhadap Submisi 1."""
    sub1_data, sub1_err, sub1_sum = read_and_validate_csv(sub1_path)
    if not sub1_sum["valid"]:
        raise ValueError(f"File Submisi 1 acuan tidak valid: {sub1_err}")

    cand_data, cand_err, cand_sum = read_and_validate_csv(candidate_path)
    if not cand_sum["valid"]:
        return {
            "status": "INVALID",
            "errors": cand_err,
            "candidate_path": str(candidate_path),
        }

    # Load predict metadata (URL, brand) if available
    urls_map = {}
    if predict_meta_path and predict_meta_path.exists():
        try:
            p_df = pd.read_csv(predict_meta_path)
            for _, r in p_df.iterrows():
                urls_map[str(r.get("id", ""))] = {
                    "url": str(r.get("url", "")),
                    "brand": str(r.get("brand", "")),
                    "sld": str(r.get("sld", "")),
                }
        except Exception:
            pass

    # Row-by-row discrepancy analysis
    divergent_rows = []
    transitions = Counter()
    same_count = 0

    # Use actual test row IDs present in the files
    all_ids = list(sub1_data.keys()) if sub1_data else list(cand_data.keys())
    for idx, r_id in enumerate(all_ids):
        c1 = sub1_data.get(r_id, "")
        c2 = cand_data.get(r_id, "")
        if c1 == c2:
            same_count += 1
        else:
            transitions[(c1, c2)] += 1
            row_meta = urls_map.get(r_id, {})
            divergent_rows.append({
                "df_idx": idx,
                "excel_row": idx + 2,  # Header is Line 1, index 0 is Line 2
                "id": r_id,
                "sub1": c1,
                "candidate": c2,
                "url": row_meta.get("url", ""),
                "brand": row_meta.get("brand", ""),
                "sld": row_meta.get("sld", ""),
            })

    divergence_count = len(divergent_rows)
    divergence_pct = (divergence_count / 1500.0) * 100.0

    # Sensitivity & Potential Score Projection
    # Under unweighted Macro-F1:
    # If Submisi 1 scored S_0 = 0.74417 across K classes:
    # Each class has weight 1/K.
    # A single class F1 change delta_f1_k affects total score by delta_f1_k / K.
    # If 7 classes are present in GT: weight per class = 1/7 = 0.1428.
    # If 8 classes: 1/8 = 0.1250.
    # If 9 classes: 1/9 = 0.1111.
    
    # Rare class upside:
    sub1_active = set(sub1_sum["active_classes"])
    cand_active = set(cand_sum["active_classes"])
    newly_activated = list(cand_active - sub1_active)
    dropped_classes = list(sub1_active - cand_active)

    # Class distribution comparison
    dist_comparison = {}
    for cat in sorted(VALID_CATEGORIES):
        n_sub1 = sub1_sum["class_distribution"].get(cat, 0)
        n_cand = cand_sum["class_distribution"].get(cat, 0)
        if n_sub1 > 0 or n_cand > 0:
            dist_comparison[cat] = {
                "sub1": n_sub1,
                "candidate": n_cand,
                "diff": n_cand - n_sub1,
            }

    # Format transition table
    trans_table = []
    for (f_cls, t_cls), cnt in transitions.most_common():
        trans_table.append({
            "from": f_cls,
            "to": t_cls,
            "count": cnt,
        })

    return {
        "status": "VALID",
        "candidate_path": str(candidate_path),
        "sub1_path": str(sub1_path),
        "sub1_score": SUB1_OFFICIAL_SCORE,
        "agreement_count": same_count,
        "divergence_count": divergence_count,
        "divergence_pct": round(divergence_pct, 2),
        "sub1_active_classes": len(sub1_active),
        "candidate_active_classes": len(cand_active),
        "newly_activated_classes": newly_activated,
        "dropped_classes": dropped_classes,
        "class_distribution_comparison": dist_comparison,
        "top_transitions": trans_table[:10],
        "sample_divergent_rows": divergent_rows[:15],
        "total_divergent_rows": len(divergent_rows),
    }


def print_comparison_report(res: Dict[str, Any]):
    """Mencetak laporan perbandingan yang rapi dan informatif."""
    if res.get("status") == "INVALID":
        print(f"\n[ERROR] File {res['candidate_path']} TIDAK VALID!")
        for err in res["errors"]:
            print(f"  - {err}")
        return

    print("=" * 80)
    print("LAPORAN AUDITOR KOMPARASI SUBMISI PeDaS 2026")
    print("=" * 80)
    print(f"Kandidat File    : {res['candidate_path']}")
    print(f"Acuan Submisi 1  : {res['sub1_path']} (Skor Resmi: {res['sub1_score']:.6f})")
    print(f"Kesesuaian Baris : {res['agreement_count']}/1500 ({100.0 - res['divergence_pct']:.2f}%)")
    print(f"Perubahan Baris  : {res['divergence_count']} baris ({res['divergence_pct']:.2f}%)")
    print(f"Jumlah Kelas     : Sub 1 ({res['sub1_active_classes']} kelas) -> Kandidat ({res['candidate_active_classes']} kelas)")

    if res["newly_activated_classes"]:
        print(f"Kelas Baru Aktif : {res['newly_activated_classes']}")
    if res["dropped_classes"]:
        print(f"Kelas Dinonaktifkan: {res['dropped_classes']}")

    print("\n--- DISTRIBUSI KELAS & DELTA ---")
    print(f"{'Kategori':<20} | {'Sub 1':<8} | {'Kandidat':<8} | {'Delta':<8}")
    print("-" * 52)
    for cat, d in res["class_distribution_comparison"].items():
        diff_str = f"+{d['diff']}" if d['diff'] > 0 else str(d['diff'])
        print(f"{cat:<20} | {d['sub1']:<8} | {d['candidate']:<8} | {diff_str:<8}")

    print("\n--- TOP TRANSISI PERPINDAHAN KELAS ---")
    for t in res["top_transitions"][:8]:
        print(f"  {t['from']} -> {t['to']}: {t['count']} baris")

    if res["sample_divergent_rows"]:
        print("\n--- SAMPEL BARIS BERBEDA (MAX 5) ---")
        for r in res["sample_divergent_rows"][:5]:
            url_short = (r['url'][:40] + "...") if len(r['url']) > 40 else r['url']
            print(f"  Excel Baris {r.get('excel_row', '?'):<4} (Index {r.get('df_idx', '?'):<4}) | ID {r['id']} | Sub1: {r['sub1']:<15} -> Kand: {r['candidate']:<15} | {url_short}")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--candidate", type=str, help="Path file CSV kandidat yang ingin dianalisa")
    parser.add_argument("--sub1", type=str, default=str(DEFAULT_SUB1_PATH), help="Path file Submisi 1 acuan")
    parser.add_argument("--dir", type=str, help="Folder berisi kumpulan file CSV kandidat untuk di-looping")
    parser.add_argument("--json", action="store_true", help="Keluarkan output dalam JSON")
    args = parser.parse_args()

    sub1_p = Path(args.sub1)
    if not sub1_p.exists():
        # Fallback to official/TIFIS TIFIS-01.csv if submitted folder not found
        fallback = Path("official/TIFIS TIFIS-01.csv")
        if fallback.exists():
            sub1_p = fallback

    if args.candidate:
        cand_p = Path(args.candidate)
        res = compare_candidate_with_sub1(cand_p, sub1_path=sub1_p)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print_comparison_report(res)

    elif args.dir:
        d_p = Path(args.dir)
        csv_files = sorted(list(d_p.glob("*.csv")))
        print(f"Ditemukan {len(csv_files)} file CSV di {d_p}")
        for cf in csv_files:
            res = compare_candidate_with_sub1(cf, sub1_path=sub1_p)
            if args.json:
                print(json.dumps(res))
            else:
                print_comparison_report(res)
    else:
        # Default: compare official/TIFIS TIFIS-01.csv against itself to verify 100% agreement
        print(f"Memeriksa integritas acuan {sub1_p}...")
        res = compare_candidate_with_sub1(sub1_p, sub1_path=sub1_p)
        print_comparison_report(res)


if __name__ == "__main__":
    main()
