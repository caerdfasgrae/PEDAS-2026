#!/usr/bin/env python
"""Tifis-ID Domain Threat Inspector CLI.

Allows manual inspection of any domain name or URL to view:
1. Feature extraction signals (lexical, brand detection, registrar).
2. LinearSVC vs LightGBM individual predictions.
3. Platt-calibrated probability distributions across all 9 canonical classes.
4. Evidence Guard filtering and final decision.
"""

import sys
import os
import time
import argparse
import subprocess
from pathlib import Path

# Safe UTF-8 encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Auto-relaunch in .venv if needed
try:
    import numpy as np
    import pandas as pd
    import lightgbm
    import sklearn
except ImportError:
    repo_dir = Path(__file__).resolve().parent.parent
    venv_py_win = repo_dir / ".venv" / "Scripts" / "python.exe"
    venv_py_nix = repo_dir / ".venv" / "bin" / "python"
    target_py = venv_py_win if venv_py_win.exists() else (venv_py_nix if venv_py_nix.exists() else None)
    if target_py and Path(sys.executable).resolve() != target_py.resolve():
        cmd = [str(target_py)] + sys.argv
        sys.exit(subprocess.call(cmd))
    else:
        raise

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.cleaner import CANONICAL_CLASSES, load_cleaned_datasets, clean_url, clean_brand, build_composite_text
from src.models.hybrid_blender import HybridProbabilisticBlender


def inspect(url: str, brand: str = "unknown_brand", registrar: str = "unknown_registrar"):
    train_csv = str(REPO_ROOT / "official" / "training.csv")
    predict_csv = str(REPO_ROOT / "official" / "predict.csv")

    print("=" * 65, flush=True)
    print("  TIFIS-ID: LIVE DOMAIN THREAT INSPECTOR", flush=True)
    print("=" * 65, flush=True)
    print(f"Target URL       : {url}", flush=True)
    print(f"Target Brand     : {brand}", flush=True)
    print(f"Target Registrar : {registrar}", flush=True)
    print("\n[*] Melatih model Tifis-ID pada dataset resmi (CRISP-DM Engine)...", flush=True)

    t0 = time.time()
    train_df, _ = load_cleaned_datasets(train_path=train_csv, predict_path=predict_csv)
    blender = HybridProbabilisticBlender(text_weight=0.60, random_state=2026)
    blender.fit(train_df, optimize_thresholds=True)
    print(f"[OK] Model siap dalam {time.time() - t0:.2f} detik!\n", flush=True)

    # Prepare single row dataframe
    single_df = pd.DataFrame([{
        "id": 999999,
        "url": url,
        "brand": brand,
        "sld": url.split(".")[-2] if "." in url else "unknown_sld",
        "registrar": registrar,
        "ip": np.nan,
        "confidence_level": 1.0,
        "discovered": "2026-09-15",
        "registration_date": "2026-09-01",
    }])
    single_df["composite_text"] = build_composite_text(single_df)

    # 1. Feature view
    X_tab = blender.domain_extractor.transform(single_df)
    active_features = {col: X_tab.iloc[0][col] for col in X_tab.columns if X_tab.iloc[0][col] > 0}

    print("--- 1. FITUR YANG TERDETEKSI ---", flush=True)
    print(f"Teks Komposit    : {single_df['composite_text'].iloc[0]}", flush=True)
    print(f"Fitur Aktif (>0) :", flush=True)
    for k, v in list(active_features.items())[:12]:
        print(f"  * {k:22s} = {v}", flush=True)
    if len(active_features) > 12:
        print(f"  ... dan {len(active_features) - 12} fitur aktif lainnya.", flush=True)

    # 2. Probability prediction
    proba_matrix = blender.predict_proba(single_df)
    proba = proba_matrix[0]

    print("\n--- 2. DISTRIBUSI PROBABILITAS TERKALIBRASI (PLATT SCALING) ---", flush=True)
    print(f"  {'Kategori':<18} | {'Probabilitas':<12} | {'Visualisasi Bar'}", flush=True)
    print("  " + "-" * 55, flush=True)

    sorted_indices = np.argsort(-proba)
    for idx in sorted_indices:
        c_name = CANONICAL_CLASSES[idx]
        p_val = proba[idx]
        bar_len = int(p_val * 30)
        bar = "#" * bar_len + "-" * (30 - bar_len)
        print(f"  {c_name:<18} | {p_val:>10.2%} | [{bar}]", flush=True)

    # 3. Final prediction with Evidence Guard
    final_pred_class = blender.predict(single_df, apply_guard=True)[0]
    raw_pred_class = CANONICAL_CLASSES[np.argmax(proba)]

    print("\n--- 3. KEPUTUSAN FINAL TIFIS-ID ---", flush=True)
    print(f"Prediksi Probabilistik Mentah : {raw_pred_class}", flush=True)
    if raw_pred_class != final_pred_class:
        print(f"Intervensi Evidence Guard     : [AKTIF] Mencegah salah vonis -> Diubah ke {final_pred_class}", flush=True)
    else:
        print(f"Intervensi Evidence Guard     : [LOLOS] Bukti leksikal valid & konsisten.", flush=True)
    print(f"HASIL AKHIR KLASIFIKASI       : >>> {final_pred_class.upper()} <<< (Keyakinan: {np.max(proba):.2%})\n", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tifis-ID Live Domain Threat Inspector")
    parser.add_argument("url", nargs="?", default="klikbca-undian-berhadiah.id", help="Domain atau URL yang ingin diuji")
    parser.add_argument("--brand", default="bca", help="Nama brand jika diketahui")
    parser.add_argument("--registrar", default="unknown_registrar", help="Registrar jika diketahui")
    args = parser.parse_args()

    inspect(args.url, args.brand, args.registrar)
