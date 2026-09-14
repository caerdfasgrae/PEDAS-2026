import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
from scipy.sparse import hstack, csr_matrix
from sklearn.svm import LinearSVC
from sklearn.preprocessing import MaxAbsScaler
from lightgbm import LGBMClassifier

from src.cleaner import CANONICAL_CLASSES, load_cleaned_datasets
from src.pedas_features import DomainEnsembleExtractor, TfidfTextFeatureExtractor
from src.evaluator import get_stratified_folds, compute_metrics_report
from src.models.probabilistic_calibrator import MulticlassPlattCalibrator
from src.models.threshold_optimizer import MulticlassThresholdOptimizer, calculate_fast_macro_f1
from src.models.evidence_guard import EvidenceGuard

def run_hybrid_cv():
    train_df, _ = load_cleaned_datasets()
    y_str = train_df["category_clean"]
    class_to_idx = {c: i for i, c in enumerate(CANONICAL_CLASSES)}
    idx_to_class = {i: c for i, c in enumerate(CANONICAL_CLASSES)}
    y_idx = y_str.map(class_to_idx).values
    urls = train_df["url"]

    folds = get_stratified_folds(train_df["composite_text"], y_str, n_splits=5, random_state=2026)

    oof_svc_proba = np.zeros((len(train_df), len(CANONICAL_CLASSES)))
    oof_lgb_proba = np.zeros((len(train_df), len(CANONICAL_CLASSES)))

    guard = EvidenceGuard(CANONICAL_CLASSES)

    for fold, (trn_idx, val_idx) in enumerate(folds):
        print(f"--- FOLD {fold + 1}/5 ---")
        
        # 1. Feature extraction strictly inside training fold
        domain_ext = DomainEnsembleExtractor()
        X_tr_tab = domain_ext.fit_transform(train_df.iloc[trn_idx])
        X_va_tab = domain_ext.transform(train_df.iloc[val_idx])

        scaler = MaxAbsScaler()
        X_tr_tab_scaled = scaler.fit_transform(X_tr_tab)
        X_va_tab_scaled = scaler.transform(X_va_tab)

        tfidf = TfidfTextFeatureExtractor(ngram_range=(3, 5), min_df=2, max_features=15000)
        X_tr_text = tfidf.fit_transform(train_df["composite_text"].iloc[trn_idx])
        X_va_text = tfidf.transform(train_df["composite_text"].iloc[val_idx])

        X_tr_all = hstack([X_tr_text, csr_matrix(X_tr_tab_scaled)])
        X_va_all = hstack([X_va_text, csr_matrix(X_va_tab_scaled)])

        # Train LinearSVC
        svc = LinearSVC(C=1.0, class_weight="balanced", random_state=2026, dual=False, max_iter=2000)
        svc.fit(X_tr_all, y_str.iloc[trn_idx])

        svc_margins_tr = svc.decision_function(X_tr_all)
        svc_margins_va = svc.decision_function(X_va_all)

        # Align margins to canonical classes
        svc_margins_tr_canon = np.zeros((len(trn_idx), len(CANONICAL_CLASSES)))
        svc_margins_va_canon = np.zeros((len(val_idx), len(CANONICAL_CLASSES)))
        for c_idx, c_name in enumerate(svc.classes_):
            can_idx = class_to_idx[c_name]
            svc_margins_tr_canon[:, can_idx] = svc_margins_tr[:, c_idx]
            svc_margins_va_canon[:, can_idx] = svc_margins_va[:, c_idx]

        # Calibrate SVC via Platt Calibrator
        calibrator = MulticlassPlattCalibrator(n_classes=len(CANONICAL_CLASSES), random_state=2026)
        calibrator.fit(svc_margins_tr_canon, y_idx[trn_idx])
        oof_svc_proba[val_idx] = calibrator.predict_proba(svc_margins_va_canon)

        # Train LightGBM on tabular features
        lgb = LGBMClassifier(
            n_estimators=120,
            learning_rate=0.08,
            num_leaves=31,
            random_state=2026,
            n_jobs=-1,
            verbose=-1,
            class_weight="balanced",
        )
        lgb.fit(X_tr_tab, y_idx[trn_idx])
        
        # Get LGBM proba
        lgb_proba_va = lgb.predict_proba(X_va_tab)
        # Ensure all classes align to canonical indices
        for c_idx, c_label in enumerate(lgb.classes_):
            oof_lgb_proba[val_idx, c_label] = lgb_proba_va[:, c_idx]

    # Evaluate across blending weights w from 0.0 to 1.0
    print("\n" + "=" * 60)
    print("WEIGHT SCANNING ON OOF PROBABILITIES (WITHOUT THRESHOLD TUNING):")
    print("=" * 60)
    best_w = 0.5
    best_raw_f1 = 0.0
    for w in np.linspace(0.0, 1.0, 11):
        blended_p = w * oof_svc_proba + (1.0 - w) * oof_lgb_proba
        raw_preds = np.argmax(blended_p, axis=1)
        raw_pred_labels = [idx_to_class[p] for p in raw_preds]
        rep = compute_metrics_report(y_str, raw_pred_labels)
        print(f"Weight SVC={w:.1f}, LGB={1.0-w:.1f} -> Macro-F1 = {rep['macro_f1']:.4f}")
        if rep['macro_f1'] > best_raw_f1:
            best_raw_f1 = rep['macro_f1']
            best_w = w

    # Now evaluate with Bayes Threshold Optimizer + Evidence Guard on the blended probabilities
    print("\n" + "=" * 60)
    print(f"EVALUATING WITH BAYES THRESHOLD OPTIMIZER + EVIDENCE GUARD (Best w={best_w:.1f}):")
    print("=" * 60)
    
    blended_p = best_w * oof_svc_proba + (1.0 - best_w) * oof_lgb_proba
    frozen_idx = [class_to_idx[c] for c in ["violence", "piiexposure"]]

    # Run nested CV threshold optimization
    oof_opt_preds = np.zeros(len(train_df), dtype=int)
    for fold, (trn_idx, val_idx) in enumerate(folds):
        opt = MulticlassThresholdOptimizer(
            C=len(CANONICAL_CLASSES),
            search_range=(-2.0, 2.0),
            n_steps=81,
            max_iter=3,
            frozen_classes=frozen_idx,
            anchor_class=0,
        )
        opt.fit_probabilities(blended_p[trn_idx], y_idx[trn_idx])
        oof_opt_preds[val_idx] = opt.predict_probabilities(blended_p[val_idx])

    # Apply evidence guard
    oof_guarded_preds = guard.filter_predictions(oof_opt_preds, blended_p, urls)
    guarded_labels = [idx_to_class[p] for p in oof_guarded_preds]
    rep_guarded = compute_metrics_report(y_str, guarded_labels)

    print(f"--> Hybrid Blender Nested Macro-F1 (with Guard): {rep_guarded['macro_f1']:.4f}")
    print("\nPer-class F1:")
    for cls in CANONICAL_CLASSES:
        print(f"  {cls:18s}: {rep_guarded['per_class_f1'].get(cls, 0.0):.4f}")

if __name__ == "__main__":
    run_hybrid_cv()
