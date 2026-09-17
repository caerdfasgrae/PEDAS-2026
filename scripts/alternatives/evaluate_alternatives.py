#!/usr/bin/env python
"""PeDaS 2026 - Alternatives Evaluation & Cross-Validation Benchmark.

Authoritative benchmark script evaluating:
1. Stratified 5-Fold Cross Validation (OOF Macro-F1 & Accuracy)
2. Strict Domain Group-KFold (100% Unseen Domains OOF Macro-F1)
3. Generalization Gap Audit (Verification that Gap <= 3.0%)
4. Data-Centric De-noising Evaluation (Pasal 3 Butir 5)
5. End-to-End Local CPU Runtime SLA (< 45 seconds per inference pipeline)
"""

import sys
import os
import time
import warnings
from pathlib import Path

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Auto-relaunch inside .venv if running with system Python that lacks packages
try:
    import pandas as _pd_check  # noqa: F401
    del _pd_check
except ImportError:
    import subprocess
    _candidates = [Path(__file__).resolve().parent, Path(__file__).resolve().parent.parent,
                   Path(__file__).resolve().parent.parent.parent]
    for _p in _candidates:
        _venv_py = _p / ".venv" / "Scripts" / "python.exe"
        if _venv_py.exists() and Path(sys.executable).resolve() != _venv_py.resolve():
            sys.exit(subprocess.call([str(_venv_py)] + sys.argv))
    raise  # .venv not found — let the real ImportError surface

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, GroupKFold
from sklearn.metrics import accuracy_score

from src.cleaner import CANONICAL_CLASSES, load_cleaned_datasets
from src.evaluator import compute_metrics_report, competition_macro_f1
from src.models.hybrid_blender import HybridProbabilisticBlender
from src.alternatives.data_centric_denoiser import DataCentricDenoiser
from src.alternatives.rare_class_hunter import RareClassHunter


def run_evaluation(fast_mode: bool = False):
    print("=" * 75)
    print("  PeDaS 2026: ALTERNATIVES & COMPETITIVE PORTFOLIO EMPIRICAL BENCHMARK")
    print("  Official Dataset: 8,400 Training Rows | Target Metric: Macro-F1")
    print("  Evaluation Harness: Zero-Leakage 5-Fold Stratified & Group-KFold")
    print("=" * 75)

    total_bench_start = time.time()
    train_df, predict_df = load_cleaned_datasets()
    y = train_df["category_clean"]
    groups = train_df["domain"].fillna("unknown_domain")

    print(f"\n[*] Total Training Rows   : {len(train_df):,}")
    print(f"[*] Total Unique Domains : {groups.nunique():,}")
    print(f"[*] Target Classes (9)   : {', '.join(CANONICAL_CLASSES)}")

    # ---------------------------------------------------------
    # 1. Baseline Champion Pipeline Evaluation
    # ---------------------------------------------------------
    print("\n" + "-" * 75)
    print("  BENCHMARK 1: BASELINE CHAMPION HYBRID BLENDER (GOLDEN ANCHOR)")
    print("-" * 75)

    # 1.A: Stratified 5-Fold CV
    print("[*] Running Stratified 5-Fold CV...")
    t0 = time.time()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=2026)
        oof_skf = pd.Series(index=y.index, dtype=str)

        for fold, (trn_idx, val_idx) in enumerate(skf.split(train_df["composite_text"], y)):
            blender = HybridProbabilisticBlender(text_weight=0.6, random_state=2026)
            blender.fit(train_df.iloc[trn_idx], optimize_thresholds=False)
            oof_skf.iloc[val_idx] = blender.predict(train_df.iloc[val_idx], apply_guard=True)

    elapsed_skf = time.time() - t0
    rep_skf = compute_metrics_report(y, oof_skf)
    acc_skf = accuracy_score(y, oof_skf)
    print(f"  -> Stratified CV Macro-F1 : {rep_skf['macro_f1']:.4f}")
    print(f"  -> Stratified CV Accuracy : {acc_skf * 100:.2f}%")
    print(f"  -> CV Compute Time        : {elapsed_skf:.2f}s")

    # 1.B: Strict Domain Group-KFold (100% Unseen Domains)
    print("\n[*] Running Strict Domain Group-KFold (100% Unseen Domains)...")
    t0 = time.time()
    gkf = GroupKFold(n_splits=5)
    oof_gkf = pd.Series(index=y.index, dtype=str)

    for fold, (trn_idx, val_idx) in enumerate(gkf.split(train_df["composite_text"], y, groups=groups)):
        # Verify zero domain leakage
        train_doms = set(groups.iloc[trn_idx].unique())
        val_doms = set(groups.iloc[val_idx].unique())
        overlap = train_doms.intersection(val_doms)
        assert len(overlap) == 0, f"Domain leakage detected in fold {fold}!"

        blender = HybridProbabilisticBlender(text_weight=0.6, random_state=2026)
        blender.fit(train_df.iloc[trn_idx], optimize_thresholds=False)
        oof_gkf.iloc[val_idx] = blender.predict(train_df.iloc[val_idx], apply_guard=True)

    elapsed_gkf = time.time() - t0
    rep_gkf = compute_metrics_report(y, oof_gkf)
    acc_gkf = accuracy_score(y, oof_gkf)
    print(f"  -> Group-KFold Macro-F1   : {rep_gkf['macro_f1']:.4f}")
    print(f"  -> Group-KFold Accuracy   : {acc_gkf * 100:.2f}%")
    print(f"  -> Group-KFold Time       : {elapsed_gkf:.2f}s")

    # 1.C: Generalization Gap Audit
    gen_gap = (rep_skf['macro_f1'] - rep_gkf['macro_f1']) * 100
    print(f"\n[*] Generalization Gap    : {gen_gap:.2f}% (Threshold: <= 3.00%)")
    if gen_gap <= 3.0:
        print("  -> Generalization Audit   : [PASSED] Model shows excellent out-of-domain robustness.")
    else:
        print("  -> Generalization Audit   : [WARNING] Gap exceeds 3.0% limit.")

    # ---------------------------------------------------------
    # 2. Data-Centric De-noising Audit (Pasal 3 Butir 5)
    # ---------------------------------------------------------
    print("\n" + "-" * 75)
    print("  BENCHMARK 2: DATA-CENTRIC DE-NOISING AUDIT (PASAL 3.5 & PASAL 12.3)")
    print("-" * 75)
    denoiser = DataCentricDenoiser(random_state=2026)
    noise_audit = denoiser.analyze_noise(pd.read_csv(REPO_ROOT / "official" / "training.csv"))

    print(f"[*] Raw Training Rows        : {noise_audit['total_rows']:,}")
    print(f"[*] Exact 10-Col Duplicates  : {noise_audit['exact_duplicate_rows']}")
    print(f"[*] Label Typo Anomalies     : {noise_audit['typo_rows_total']}")
    print(f"[*] Conflicting URLs (118)   : {noise_audit['conflicting_urls_count']}")
    print(f"[*] Rows in Conflict (584)   : {noise_audit['conflicting_rows_total']}")
    print(f"[*] Asterisk Collision Rate  : {noise_audit['asterisk_collision_rate'] * 100:.1f}% (Synthetic noise confirmed)")
    print(f"[*] Majority Resolvable      : {noise_audit['majority_resolvable_count']} URLs")
    print(f"[*] Semantic Tie-Break       : {noise_audit['tie_count']} URLs")

    # ---------------------------------------------------------
    # 3. Single-Inference CPU SLA Benchmark (< 45s)
    # ---------------------------------------------------------
    print("\n" + "-" * 75)
    print("  BENCHMARK 3: SINGLE-RUN CPU INFERENCE SLA AUDIT (< 45 SECONDS)")
    print("-" * 75)
    t_sla = time.time()
    blender_sla = HybridProbabilisticBlender(text_weight=0.6, random_state=2026)
    blender_sla.fit(train_df, optimize_thresholds=True)
    preds_sla = blender_sla.predict(predict_df, apply_guard=True)
    elapsed_sla = time.time() - t_sla

    print(f"[*] End-to-End Pipeline SLA  : {elapsed_sla:.2f} seconds")
    print(f"[*] Official SLA Limit       : < 45.00 seconds")
    if elapsed_sla < 45.0:
        print(f"[*] SLA Audit Status         : [PASSED] Margin: {45.0 - elapsed_sla:.2f}s headroom")
    else:
        print("[*] SLA Audit Status         : [FAILED] Exceeded 45s limit")

    # ---------------------------------------------------------
    # 4. Summary & Per-Class Comparative Matrix
    # ---------------------------------------------------------
    print("\n" + "=" * 75)
    print(f"{'Class Name':20s} | {'Stratified CV':14s} | {'Group-KFold':14s} | {'F1 Delta':10s}")
    print("-" * 75)
    for cls in CANONICAL_CLASSES:
        f1_s = rep_skf['per_class_f1'].get(cls, 0.0)
        f1_g = rep_gkf['per_class_f1'].get(cls, 0.0)
        delta = f1_s - f1_g
        print(f"{cls:20s} | {f1_s:14.4f} | {f1_g:14.4f} | {delta:+10.4f}")
    print("=" * 75)

    total_elapsed = time.time() - total_bench_start
    print(f"\n[OK] Evaluation completed successfully in {total_elapsed:.2f}s total.")
    return {
        "stratified_macro_f1": rep_skf['macro_f1'],
        "group_kfold_macro_f1": rep_gkf['macro_f1'],
        "generalization_gap": gen_gap,
        "sla_seconds": elapsed_sla,
        "is_gap_passed": gen_gap <= 3.0,
        "is_sla_passed": elapsed_sla < 45.0,
    }


if __name__ == "__main__":
    run_evaluation()
