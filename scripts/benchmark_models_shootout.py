"""Model Benchmarking Shootout — PeDaS 2026.

Komparasi empiris 5-Fold GroupKFold by URL untuk 4 arsitektur:
1. Model A: Calibrated LinearSVC + LightGBM (Baseline Submisi 1)
2. Model B: Calibrated LinearSVC + CatBoost (Oblivious Trees, Depth 6)
3. Model C: Calibrated LinearSVC + XGBoost (Histogram Trees, Depth 6)
4. Model D: Super-Learner Stacking / Multi-GBDT Blend (LinearSVC + LGBM + CatBoost + XGBoost)

Metrik Evaluasi:
- Unweighted Macro-F1 (panitia official scoring)
- Per-class F1 breakdown
- Total Fit & Inference Runtime
- Model Memory Footprint
"""

import os
import sys
import time
import json
import warnings
from pathlib import Path
from typing import Dict, List, Tuple, Any

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold
from sklearn.svm import LinearSVC
from sklearn.preprocessing import MaxAbsScaler
from sklearn.utils.class_weight import compute_sample_weight
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier
from xgboost import XGBClassifier

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.cleaner import load_cleaned_datasets, clean_url, CANONICAL_CLASSES, build_composite_text
from src.pedas_features import DomainEnsembleExtractor, TfidfTextFeatureExtractor
from src.models.probabilistic_calibrator import MulticlassPlattCalibrator
from src.models.threshold_optimizer import MulticlassThresholdOptimizer
from src.models.evidence_guard import EvidenceGuard
from src.alternatives.data_centric_denoiser import DataCentricDenoiser
from src.evaluator import compute_metrics_report

warnings.filterwarnings("ignore")


class BenchmarkBlender:
    """Universal wrapper for benchmarking various tabular GBDT models blended with LinearSVC."""

    def __init__(
        self,
        gbdt_type: str = "lightgbm",
        text_weight: float = 0.60,
        random_state: int = 2026,
    ):
        self.gbdt_type = gbdt_type
        self.text_weight = text_weight
        self.gbdt_weight = 1.0 - text_weight
        self.random_state = random_state
        self.class_to_idx = {c: i for i, c in enumerate(CANONICAL_CLASSES)}
        self.idx_to_class = {i: c for i, c in enumerate(CANONICAL_CLASSES)}

        self.tfidf = None
        self.svc = None
        self.calibrator = None
        self.domain_extractor = None
        self.scaler = None
        self.gbdt_models = {}

    def fit(self, train_df: pd.DataFrame):
        y_str = train_df["category_clean"]
        y_idx = y_str.map(self.class_to_idx).values
        urls = train_df["url"]

        # 1. Text branch: TF-IDF + LinearSVC + Platt Calibration
        comp_text = build_composite_text(train_df)
        self.tfidf = TfidfTextFeatureExtractor(
            ngram_range=(3, 5), min_df=2, max_features=15000
        )
        X_text = self.tfidf.fit_transform(comp_text)

        self.svc = LinearSVC(
            C=1.0, loss="squared_hinge", dual=False, random_state=self.random_state, max_iter=2000
        )
        self.svc.fit(X_text, y_idx)
        margins = self.svc.decision_function(X_text)
        if margins.ndim == 1:
            margins = np.vstack([-margins, margins]).T
        
        # Align margins to canonical classes
        margins_canon = np.full((len(train_df), len(CANONICAL_CLASSES)), -10.0)
        for c_idx, c_label in enumerate(self.svc.classes_):
            can_idx = int(c_label) if isinstance(c_label, (int, np.integer)) else self.class_to_idx[c_label]
            if can_idx < len(CANONICAL_CLASSES):
                margins_canon[:, can_idx] = margins[:, c_idx]

        self.calibrator = MulticlassPlattCalibrator(n_classes=len(CANONICAL_CLASSES))
        self.calibrator.fit(margins_canon, y_idx)

        # 2. Tabular branch: 56 Domain Features
        self.domain_extractor = DomainEnsembleExtractor()
        X_tab_raw = self.domain_extractor.fit_transform(train_df)
        self.scaler = MaxAbsScaler()
        X_tab_scaled = self.scaler.fit_transform(X_tab_raw)

        # Fit selected GBDT
        sample_weights = compute_sample_weight("balanced", y_idx)

        if self.gbdt_type in ["lightgbm", "stacking"]:
            lgb = LGBMClassifier(
                n_estimators=120,
                learning_rate=0.08,
                num_leaves=31,
                random_state=self.random_state,
                n_jobs=-1,
                verbose=-1,
                class_weight="balanced",
            )
            lgb.fit(X_tab_raw, y_idx)
            self.gbdt_models["lightgbm"] = lgb

        if self.gbdt_type in ["catboost", "stacking"]:
            cb = CatBoostClassifier(
                iterations=200,
                learning_rate=0.08,
                depth=6,
                random_seed=self.random_state,
                auto_class_weights="Balanced",
                verbose=0,
                thread_count=-1,
            )
            cb.fit(X_tab_raw, y_idx)
            self.gbdt_models["catboost"] = cb

        if self.gbdt_type in ["xgboost", "stacking"]:
            unique_classes, y_contiguous = np.unique(y_idx, return_inverse=True)
            self.xgb_classes_ = unique_classes
            xgb = XGBClassifier(
                n_estimators=120,
                learning_rate=0.08,
                max_depth=6,
                random_state=self.random_state,
                n_jobs=-1,
                eval_metric="mlogloss",
                verbosity=0,
            )
            xgb.fit(X_tab_raw, y_contiguous, sample_weight=sample_weights)
            self.gbdt_models["xgboost"] = xgb

        return self

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        # Text probas
        comp_text = build_composite_text(df)
        X_text = self.tfidf.transform(comp_text)
        margins = self.svc.decision_function(X_text)
        if margins.ndim == 1:
            margins = np.vstack([-margins, margins]).T
        
        margins_canon = np.full((len(df), len(CANONICAL_CLASSES)), -10.0)
        for c_idx, c_label in enumerate(self.svc.classes_):
            can_idx = int(c_label) if isinstance(c_label, (int, np.integer)) else self.class_to_idx[c_label]
            if can_idx < len(CANONICAL_CLASSES):
                margins_canon[:, can_idx] = margins[:, c_idx]
        svc_probas = self.calibrator.predict_proba(margins_canon)

        # Tabular probas
        X_tab_raw = self.domain_extractor.transform(df)

        gbdt_probas_list = []
        for name, model in self.gbdt_models.items():
            raw_p = model.predict_proba(X_tab_raw)
            p_canon = np.zeros((len(df), len(CANONICAL_CLASSES)))
            if name == "xgboost":
                for c_local_idx, can_idx in enumerate(self.xgb_classes_):
                    if can_idx < len(CANONICAL_CLASSES):
                        p_canon[:, can_idx] = raw_p[:, c_local_idx]
            else:
                for c_idx, c_label in enumerate(model.classes_):
                    can_idx = int(c_label) if isinstance(c_label, (int, np.integer)) else self.class_to_idx[c_label]
                    if can_idx < len(CANONICAL_CLASSES):
                        p_canon[:, can_idx] = raw_p[:, c_idx]
            gbdt_probas_list.append(p_canon)

        # Average GBDT probas if multiple
        avg_gbdt_probas = np.mean(gbdt_probas_list, axis=0)

        # Final blend
        blended = self.text_weight * svc_probas + self.gbdt_weight * avg_gbdt_probas
        # Re-normalize
        row_sums = blended.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1.0
        return blended / row_sums


def run_benchmark_shootout():
    print("=" * 80)
    print("MEMULAI MODEL BENCHMARKING SHOOTOUT (5-Fold GroupKFold by URL)")
    print("=" * 80)

    # 1. Load data
    denoiser = DataCentricDenoiser()
    train_raw, _ = load_cleaned_datasets()
    train_df = denoiser.fit_transform(train_raw)
    print(f"Data latih bersih: {len(train_df)} baris.")

    c2i = {c: i for i, c in enumerate(CANONICAL_CLASSES)}
    i2c = {i: c for i, c in enumerate(CANONICAL_CLASSES)}
    y_str = train_df["category_clean"]
    y_idx = y_str.map(c2i).values
    groups = train_df["url"].astype(str)
    frozen_classes = [c2i[c] for c in ["violence", "piiexposure"]]

    gkf = GroupKFold(n_splits=5)

    candidates = [
        ("Model A: LinearSVC + LightGBM", "lightgbm"),
        ("Model B: LinearSVC + CatBoost", "catboost"),
        ("Model C: LinearSVC + XGBoost", "xgboost"),
        ("Model D: Super-Learner Stacking (All 3 GBDTs)", "stacking"),
    ]

    results = {}

    for label, gbdt_type in candidates:
        print(f"\n[RUNNING] {label}...")
        start_time = time.time()
        oof_probas = np.zeros((len(train_df), len(CANONICAL_CLASSES)))
        oof_preds = np.zeros(len(train_df), dtype=int)
        fold_scores = []

        guard = EvidenceGuard(CANONICAL_CLASSES)

        for fold_idx, (trn_idx, val_idx) in enumerate(gkf.split(train_df, y_str, groups)):
            trn_df = train_df.iloc[trn_idx]
            val_df = train_df.iloc[val_idx]

            # Fit model on training fold
            blender = BenchmarkBlender(gbdt_type=gbdt_type, text_weight=0.60, random_state=2026)
            blender.fit(trn_df)

            # Predict probas on val
            val_p = blender.predict_proba(val_df)
            oof_probas[val_idx] = val_p

            # Optimize threshold on trn probas
            trn_p = blender.predict_proba(trn_df)
            opt = MulticlassThresholdOptimizer(
                C=len(CANONICAL_CLASSES),
                search_range=(-2.0, 2.0),
                n_steps=81,
                max_iter=3,
                frozen_classes=frozen_classes,
                anchor_class=0,
            )
            opt.fit_probabilities(trn_p, y_idx[trn_idx])

            # Apply threshold to val
            val_preds = opt.predict_probabilities(val_p)
            val_filtered = guard.filter_predictions(val_preds, val_p, val_df["url"])
            oof_preds[val_idx] = val_filtered

            fold_f1 = compute_metrics_report(y_str.iloc[val_idx], [i2c[p] for p in val_filtered])["macro_f1"]
            fold_scores.append(fold_f1)
            print(f"  Fold {fold_idx + 1}/5: Macro-F1 = {fold_f1:.4f}")

        elapsed = time.time() - start_time
        overall_report = compute_metrics_report(y_str, [i2c[p] for p in oof_preds])
        mean_cv_f1 = np.mean(fold_scores)
        overall_f1 = overall_report["macro_f1"]

        print(f"  => Total Runtime: {elapsed:.2f}s")
        print(f"  => Mean Fold Macro-F1 : {mean_cv_f1:.4f}")
        print(f"  => Overall OOF Macro-F1: {overall_f1:.4f}")

        results[label] = {
            "gbdt_type": gbdt_type,
            "runtime_seconds": round(elapsed, 2),
            "mean_fold_f1": round(float(mean_cv_f1), 4),
            "overall_oof_f1": round(float(overall_f1), 4),
            "per_class_f1": {k: round(v, 4) for k, v in overall_report["per_class_f1"].items()},
        }

    # Save results to reports/
    out_path = Path("reports/model_shootout_results.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 80)
    print("HASIL AKHIR MODEL BENCHMARKING SHOOTOUT")
    print("=" * 80)
    print(f"{'Arsitektur Model':<45} | {'OOF Macro-F1':<12} | {'Mean Fold':<10} | {'Runtime':<8}")
    print("-" * 82)
    for label, d in sorted(results.items(), key=lambda x: x[1]["overall_oof_f1"], reverse=True):
        print(f"{label:<45} | {d['overall_oof_f1']:<12.4f} | {d['mean_fold_f1']:<10.4f} | {d['runtime_seconds']:<8.1f}s")
    print("=" * 80)


if __name__ == "__main__":
    run_benchmark_shootout()
