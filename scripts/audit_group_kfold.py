import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import warnings
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold, StratifiedKFold
from src.cleaner import load_cleaned_datasets, CANONICAL_CLASSES
from src.evaluator import compute_metrics_report
from src.models.hybrid_blender import HybridProbabilisticBlender


def run_group_kfold_audit():
    print("=" * 65)
    print("PE-DAS 2026: OUT-OF-DOMAIN GENERALIZATION AUDIT (HYBRID BLENDER)")
    print("=" * 65)
    
    train_df, _ = load_cleaned_datasets()
    y = train_df["category_clean"]
    groups = train_df["domain"].fillna("unknown_domain")
    
    n_domains = groups.nunique()
    print(f"Total Rows   : {len(train_df)}")
    print(f"Total Domains: {n_domains}")
    
    # 1. Standard Stratified 5-Fold CV (In-Domain + Cross-Domain)
    print("\n--- TEST 1: Standard Stratified 5-Fold CV (Hybrid Blender) ---")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=2026)
    oof_skf = pd.Series(index=y.index, dtype=str)
    
    for fold, (trn_idx, val_idx) in enumerate(skf.split(train_df["composite_text"], y)):
        blender = HybridProbabilisticBlender(text_weight=0.6, random_state=2026)
        blender.fit(train_df.iloc[trn_idx], optimize_thresholds=False)
        preds = blender.predict(train_df.iloc[val_idx], apply_guard=True)
        oof_skf.iloc[val_idx] = preds
        
    rep_skf = compute_metrics_report(y, oof_skf)
    print(f"--> Stratified CV Hybrid Macro-F1: {rep_skf['macro_f1']:.4f}")

    # 2. Strict Domain GroupKFold (Zero Domain Overlap)
    print("\n--- TEST 2: Strict Domain GroupKFold (100% Unseen Domains) ---")
    gkf = GroupKFold(n_splits=5)
    oof_gkf = pd.Series(index=y.index, dtype=str)
    
    for fold, (trn_idx, val_idx) in enumerate(gkf.split(train_df["composite_text"], y, groups=groups)):
        train_doms = set(groups.iloc[trn_idx].unique())
        val_doms = set(groups.iloc[val_idx].unique())
        overlap = train_doms.intersection(val_doms)
        assert len(overlap) == 0, f"Leakage detected! Overlap: {len(overlap)}"
        
        blender = HybridProbabilisticBlender(text_weight=0.6, random_state=2026)
        blender.fit(train_df.iloc[trn_idx], optimize_thresholds=False)
        preds = blender.predict(train_df.iloc[val_idx], apply_guard=True)
        oof_gkf.iloc[val_idx] = preds
        
    rep_gkf = compute_metrics_report(y, oof_gkf)
    print(f"--> Strict Domain GroupKFold Macro-F1: {rep_gkf['macro_f1']:.4f}")
    
    diff = rep_skf['macro_f1'] - rep_gkf['macro_f1']
    print(f"\n---> Macro-F1 Delta (Generalization Gap): {diff:+.4f} (Gap: {diff * 100:.2f}%)")
    
    print("\nPer-Class Comparison:")
    print(f"{'Class':18s} | {'Stratified CV':13s} | {'GroupKFold (Unseen)':18s}")
    print("-" * 55)
    for cls in CANONICAL_CLASSES:
        f1_s = rep_skf['per_class_f1'].get(cls, 0.0)
        f1_g = rep_gkf['per_class_f1'].get(cls, 0.0)
        print(f"{cls:18s} | {f1_s:13.4f} | {f1_g:18.4f}")


if __name__ == "__main__":
    run_group_kfold_audit()
