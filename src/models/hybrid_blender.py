"""Explainable Hybrid Probabilistic Blender for PeDaS 2026.

Combines:
1. LinearSVC on Character N-grams + Domain Features (High-dimensional linear text space)
   calibrated via Multiclass Platt Scaling.
2. LightGBM on Domain & Network Lifecycle Features (Non-linear tabular interaction space)
   outputting posterior tree probabilities.
3. Cost-Sensitive Bayes Threshold Optimization (maximizing unweighted Macro-F1).
4. Evidence Guard (strict majority preservation against minority false-positive hallucination).

Adheres strictly to Pak Taufik Sutanto's principles:
- Fully auditable: each sub-model has transparent contributions.
- Zero data leakage: all scalers, extractors, calibrators, and threshold optimizers fit strictly on training folds.
- Deterministic: locked random seed 2026.
"""

from typing import Dict, Any, List, Tuple, Optional
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
from src.models.threshold_optimizer import MulticlassThresholdOptimizer
from src.models.evidence_guard import EvidenceGuard


class HybridProbabilisticBlender:
    """Ensemble blender combining calibrated LinearSVC and tabular LightGBM."""

    def __init__(
        self,
        text_weight: float = 0.70,
        random_state: int = 2026,
        n_estimators: int = 120,
        learning_rate: float = 0.08,
        num_leaves: int = 31,
    ):
        self.text_weight = text_weight
        self.gbdt_weight = 1.0 - text_weight
        self.random_state = random_state
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.num_leaves = num_leaves

        self.class_to_idx = {c: i for i, c in enumerate(CANONICAL_CLASSES)}
        self.idx_to_class = {i: c for i, c in enumerate(CANONICAL_CLASSES)}

        # Component pipelines
        self.domain_extractor: Optional[DomainEnsembleExtractor] = None
        self.scaler: Optional[MaxAbsScaler] = None
        self.tfidf: Optional[TfidfTextFeatureExtractor] = None
        self.svc_clf: Optional[LinearSVC] = None
        self.svc_calibrator: Optional[MulticlassPlattCalibrator] = None
        self.lgb_clf: Optional[LGBMClassifier] = None
        self.threshold_optimizer: Optional[MulticlassThresholdOptimizer] = None
        self.guard = EvidenceGuard(CANONICAL_CLASSES)
        self.offsets_: Optional[np.ndarray] = None

    def fit(
        self,
        train_df: pd.DataFrame,
        optimize_thresholds: bool = True,
        search_range: Tuple[float, float] = (-2.0, 2.0),
        frozen_classes: Optional[List[str]] = None,
    ) -> "HybridProbabilisticBlender":
        """Fits all feature extractors, base classifiers, calibrator, and threshold optimizer."""
        y_str = train_df["category_clean"]
        y_idx = y_str.map(self.class_to_idx).values
        urls = train_df["url"]

        # 1. Tabular features
        self.domain_extractor = DomainEnsembleExtractor()
        X_tab_raw = self.domain_extractor.fit_transform(train_df)
        self.scaler = MaxAbsScaler()
        X_tab_scaled = self.scaler.fit_transform(X_tab_raw)

        # 2. Text n-gram features
        self.tfidf = TfidfTextFeatureExtractor(ngram_range=(3, 5), min_df=2, max_features=15000)
        X_text = self.tfidf.fit_transform(train_df["composite_text"])

        # Combined features for LinearSVC
        X_all = hstack([X_text, csr_matrix(X_tab_scaled)])

        # 3. Fit LinearSVC
        self.svc_clf = LinearSVC(
            C=1.0,
            class_weight="balanced",
            random_state=self.random_state,
            dual=False,
            max_iter=2000,
        )
        self.svc_clf.fit(X_all, y_str)

        # Decision margins -> Platt Calibration
        margins_raw = self.svc_clf.decision_function(X_all)
        margins_canon = np.zeros((len(train_df), len(CANONICAL_CLASSES)))
        for c_idx, c_name in enumerate(self.svc_clf.classes_):
            can_idx = self.class_to_idx[c_name]
            margins_canon[:, can_idx] = margins_raw[:, c_idx]

        self.svc_calibrator = MulticlassPlattCalibrator(
            n_classes=len(CANONICAL_CLASSES),
            random_state=self.random_state,
        )
        self.svc_calibrator.fit(margins_canon, y_idx)
        svc_probas = self.svc_calibrator.predict_proba(margins_canon)

        # 4. Fit LightGBM on tabular features
        self.lgb_clf = LGBMClassifier(
            n_estimators=self.n_estimators,
            learning_rate=self.learning_rate,
            num_leaves=self.num_leaves,
            random_state=self.random_state,
            n_jobs=-1,
            verbose=-1,
            class_weight="balanced",
        )
        self.lgb_clf.fit(X_tab_raw, y_idx)

        lgb_probas_raw = self.lgb_clf.predict_proba(X_tab_raw)
        lgb_probas_canon = np.zeros((len(train_df), len(CANONICAL_CLASSES)))
        for c_idx, c_label in enumerate(self.lgb_clf.classes_):
            can_idx = int(c_label) if isinstance(c_label, (int, np.integer)) else self.class_to_idx[c_label]
            if can_idx < len(CANONICAL_CLASSES):
                lgb_probas_canon[:, can_idx] = lgb_probas_raw[:, c_idx]

        # 5. Blend probabilities
        blended_probas = self.text_weight * svc_probas + self.gbdt_weight * lgb_probas_canon

        # 6. Optimize Bayes Thresholds
        if frozen_classes is not None:
            frozen_indices = [self.class_to_idx[c] for c in frozen_classes if c in self.class_to_idx]
        else:
            frozen_indices = []

        self.threshold_optimizer = MulticlassThresholdOptimizer(
            C=len(CANONICAL_CLASSES),
            search_range=search_range,
            n_steps=81,
            max_iter=3,
            frozen_classes=frozen_indices,
            anchor_class=0,
        )
        if optimize_thresholds:
            self.threshold_optimizer.fit_probabilities(blended_probas, y_idx)
            self.offsets_ = self.threshold_optimizer.offsets_
        else:
            self.offsets_ = self.threshold_optimizer.offsets_

        return self

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        """Transforms input DataFrame and returns blended posterior probabilities."""
        if self.svc_clf is None or self.lgb_clf is None:
            raise ValueError("Blender has not been fitted. Call fit() first.")

        work_df = df
        if "composite_text" not in work_df.columns:
            work_df = work_df.copy()
            from src.cleaner import build_composite_text
            work_df["composite_text"] = build_composite_text(work_df)

        # Tabular features
        X_tab_raw = self.domain_extractor.transform(work_df)
        X_tab_scaled = self.scaler.transform(X_tab_raw)

        # Text features
        X_text = self.tfidf.transform(work_df["composite_text"])
        X_all = hstack([X_text, csr_matrix(X_tab_scaled)])

        # LinearSVC probabilities
        margins_raw = self.svc_clf.decision_function(X_all)
        margins_canon = np.zeros((len(df), len(CANONICAL_CLASSES)))
        for c_idx, c_name in enumerate(self.svc_clf.classes_):
            can_idx = self.class_to_idx[c_name]
            margins_canon[:, can_idx] = margins_raw[:, c_idx]
        svc_probas = self.svc_calibrator.predict_proba(margins_canon)

        # LightGBM probabilities
        lgb_probas_raw = self.lgb_clf.predict_proba(X_tab_raw)
        lgb_probas_canon = np.zeros((len(df), len(CANONICAL_CLASSES)))
        for c_idx, c_label in enumerate(self.lgb_clf.classes_):
            can_idx = int(c_label) if isinstance(c_label, (int, np.integer)) else self.class_to_idx[c_label]
            if can_idx < len(CANONICAL_CLASSES):
                lgb_probas_canon[:, can_idx] = lgb_probas_raw[:, c_idx]

        # Blend
        blended = self.text_weight * svc_probas + self.gbdt_weight * lgb_probas_canon
        blended = np.clip(blended, 1e-12, 1.0)
        blended = blended / blended.sum(axis=1, keepdims=True)
        return blended

    def predict(self, df: pd.DataFrame, apply_guard: bool = True) -> List[str]:
        """Predicts canonical category strings with threshold offsets and evidence guard."""
        probas = self.predict_proba(df)

        if self.threshold_optimizer is not None:
            raw_preds = self.threshold_optimizer.predict_probabilities(probas)
        else:
            raw_preds = np.argmax(probas, axis=1)

        if apply_guard and "url" in df.columns:
            final_preds = self.guard.filter_predictions(raw_preds, probas, df["url"])
        else:
            final_preds = raw_preds

        return [self.idx_to_class[p] for p in final_preds]


def run_hybrid_cross_validation(
    train_path: str = "official/training.csv",
    n_splits: int = 5,
    random_state: int = 2026,
    text_weight: float = 0.70,
) -> Dict[str, Any]:
    """Runs strict leak-free 5-fold Stratified Cross-Validation on Hybrid Blender."""
    train_df, _ = load_cleaned_datasets(train_path=train_path)
    y_str = train_df["category_clean"]
    class_to_idx = {c: i for i, c in enumerate(CANONICAL_CLASSES)}
    idx_to_class = {i: c for i, c in enumerate(CANONICAL_CLASSES)}
    y_idx = y_str.map(class_to_idx).values
    urls = train_df["url"]

    folds = get_stratified_folds(train_df["composite_text"], y_str, n_splits=n_splits, random_state=random_state)

    oof_probas = np.zeros((len(train_df), len(CANONICAL_CLASSES)))
    oof_nested_preds = np.zeros(len(train_df), dtype=int)
    frozen_classes = [class_to_idx[c] for c in ["violence", "piiexposure"]]
    guard = EvidenceGuard(CANONICAL_CLASSES)

    for fold, (trn_idx, val_idx) in enumerate(folds):
        blender = HybridProbabilisticBlender(
            text_weight=text_weight,
            random_state=random_state,
        )
        # Fit strictly on trn_idx
        blender.fit(train_df.iloc[trn_idx], optimize_thresholds=False)

        # Predict proba on val_idx
        val_probas = blender.predict_proba(train_df.iloc[val_idx])
        oof_probas[val_idx] = val_probas

        # Fit threshold optimizer strictly on training fold probas (nested OOF)
        trn_probas = blender.predict_proba(train_df.iloc[trn_idx])
        opt = MulticlassThresholdOptimizer(
            C=len(CANONICAL_CLASSES),
            search_range=(-2.0, 2.0),
            n_steps=81,
            max_iter=3,
            frozen_classes=frozen_classes,
            anchor_class=0,
        )
        opt.fit_probabilities(trn_probas, y_idx[trn_idx])
        val_opt_preds = opt.predict_probabilities(val_probas)
        oof_nested_preds[val_idx] = val_opt_preds

    # Apply guard on nested predictions
    oof_guarded_preds = guard.filter_predictions(oof_nested_preds, oof_probas, urls)
    nested_labels = [idx_to_class[p] for p in oof_guarded_preds]
    rep_nested = compute_metrics_report(y_str, nested_labels)

    # Fit a global threshold optimizer on full OOF probas for final inference
    global_opt = MulticlassThresholdOptimizer(
        C=len(CANONICAL_CLASSES),
        search_range=(-2.0, 2.0),
        n_steps=81,
        max_iter=3,
        frozen_classes=frozen_classes,
        anchor_class=0,
    )
    global_opt.fit_probabilities(oof_probas, y_idx)
    global_preds = global_opt.predict_probabilities(oof_probas)
    global_guarded = guard.filter_predictions(global_preds, oof_probas, urls)
    rep_global = compute_metrics_report(y_str, [idx_to_class[p] for p in global_guarded])

    return {
        "nested_report": rep_nested,
        "global_report": rep_global,
        "global_offsets": dict(zip(CANONICAL_CLASSES, global_opt.offsets_)),
        "oof_probas": oof_probas,
    }
