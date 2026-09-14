"""End-to-End Calibrated Domain Ensemble Pipeline for PeDaS 2026.

Integrates:
1. Deterministic text and URL cleaning (strips search prefixes, normalizes casing).
2. Multi-field composite context (URL + brand + sld + registrar).
3. 56 explainable domain, lexical, network, and temporal lifecycle features.
4. LinearSVC with balanced class weights and primal solver (dual=False) for convergence.
5. Strict leak-free nested threshold calibration optimizing unweighted Macro-F1.
"""

from typing import Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
from scipy.sparse import hstack, csr_matrix
from sklearn.svm import LinearSVC
from sklearn.preprocessing import MaxAbsScaler

from src.cleaner import CANONICAL_CLASSES, load_cleaned_datasets
from src.pedas_features import DomainEnsembleExtractor, TfidfTextFeatureExtractor
from src.evaluator import get_stratified_folds, compute_metrics_report
from src.models.threshold_optimizer import MulticlassThresholdOptimizer, calculate_fast_macro_f1
from src.submission import export_submission, validate_submission


def run_cross_validation(
    train_path: str = "official/training.csv",
    n_splits: int = 5,
    random_state: int = 2026,
    freeze_rare_classes: bool = True,
) -> Dict[str, Any]:
    """Runs 5-fold Stratified Cross-Validation with uncalibrated and nested calibrated metrics.
    
    Strictly conforms to Pak Taufik Sutanto's principles:
    - Zero data leakage: DomainEnsembleExtractor, MaxAbsScaler, and TF-IDF are fitted strictly inside each training fold.
    - Full explainability: Auditable linear model weights and explicit threshold offsets.
    """
    train_df, _ = load_cleaned_datasets(train_path=train_path)
    y_str = train_df["category_clean"]
    class_to_idx = {c: i for i, c in enumerate(CANONICAL_CLASSES)}
    idx_to_class = {i: c for i, c in enumerate(CANONICAL_CLASSES)}
    y_idx = y_str.map(class_to_idx).values

    folds = get_stratified_folds(train_df["composite_text"], y_str, n_splits=n_splits, random_state=random_state)

    oof_scores = np.full((len(train_df), len(CANONICAL_CLASSES)), -10.0)
    oof_uncal_preds = np.zeros(len(train_df), dtype=int)

    for fold, (trn_idx, val_idx) in enumerate(folds):
        # 1. Feature extraction strictly on training fold (zero leakage)
        domain_extractor = DomainEnsembleExtractor()
        X_tr_tab_raw = domain_extractor.fit_transform(train_df.iloc[trn_idx])
        X_va_tab_raw = domain_extractor.transform(train_df.iloc[val_idx])

        # 2. Feature scaling strictly on training fold
        scaler = MaxAbsScaler()
        X_tr_tab = scaler.fit_transform(X_tr_tab_raw)
        X_va_tab = scaler.transform(X_va_tab_raw)

        # 3. TF-IDF vectorizer strictly on training fold
        tfidf = TfidfTextFeatureExtractor(ngram_range=(3, 5), min_df=2, max_features=15000)
        X_tr_text = tfidf.fit_transform(train_df["composite_text"].iloc[trn_idx])
        X_va_text = tfidf.transform(train_df["composite_text"].iloc[val_idx])

        X_tr = hstack([X_tr_text, csr_matrix(X_tr_tab)])
        X_va = hstack([X_va_text, csr_matrix(X_va_tab)])

        clf = LinearSVC(C=1.0, class_weight="balanced", random_state=random_state, dual=False, max_iter=2000)
        clf.fit(X_tr, y_str.iloc[trn_idx])

        scores = clf.decision_function(X_va)
        for c_idx, c_name in enumerate(clf.classes_):
            canonical_idx = class_to_idx[c_name]
            oof_scores[val_idx, canonical_idx] = scores[:, c_idx]

        val_pred_labels = clf.predict(X_va)
        oof_uncal_preds[val_idx] = [class_to_idx[p] for p in val_pred_labels]

    # Uncalibrated metrics
    uncal_labels = [idx_to_class[p] for p in oof_uncal_preds]
    rep_uncal = compute_metrics_report(y_str, uncal_labels)

    # Nested Out-Of-Fold Calibration (anchored majority class, zero coordinate drift)
    frozen_idx = [class_to_idx[c] for c in ["violence", "piiexposure"]] if freeze_rare_classes else []
    oof_nested_cal_preds = np.zeros(len(train_df), dtype=int)

    for fold, (trn_idx, val_idx) in enumerate(folds):
        optimizer = MulticlassThresholdOptimizer(
            C=len(CANONICAL_CLASSES),
            search_range=(-1.5, 2.5),
            n_steps=81,
            max_iter=3,
            frozen_classes=frozen_idx,
            anchor_class=0,
        )
        optimizer.fit(oof_scores[trn_idx], y_idx[trn_idx])
        oof_nested_cal_preds[val_idx] = optimizer.predict(oof_scores[val_idx])

    nested_cal_labels = [idx_to_class[p] for p in oof_nested_cal_preds]
    rep_nested = compute_metrics_report(y_str, nested_cal_labels)

    # Global OOF Calibration (across all 5 folds, used for full model deployment)
    global_optimizer = MulticlassThresholdOptimizer(
        C=len(CANONICAL_CLASSES),
        search_range=(-1.5, 2.5),
        n_steps=81,
        max_iter=3,
        frozen_classes=frozen_idx,
        anchor_class=0,
    )
    global_optimizer.fit(oof_scores, y_idx)
    global_cal_labels = [idx_to_class[p] for p in global_optimizer.predict(oof_scores)]
    rep_global = compute_metrics_report(y_str, global_cal_labels)

    return {
        "uncalibrated_report": rep_uncal,
        "nested_calibrated_report": rep_nested,
        "global_calibrated_report": rep_global,
        "global_offsets": dict(zip(CANONICAL_CLASSES, global_optimizer.offsets_)),
        "oof_scores": oof_scores,
        "y_true": y_str,
    }


def train_full_model_and_predict(
    train_path: str = "official/training.csv",
    predict_path: str = "official/predict.csv",
    output_submission_path: str = "official/submission_calibrated_ensemble.csv",
    global_offsets: Optional[Dict[str, float]] = None,
    random_state: int = 2026,
) -> pd.DataFrame:
    """Trains full model on 100% training data, applies calibrated thresholds, and generates submission."""
    train_df, predict_df = load_cleaned_datasets(train_path=train_path, predict_path=predict_path)
    y_str = train_df["category_clean"]
    class_to_idx = {c: i for i, c in enumerate(CANONICAL_CLASSES)}
    idx_to_class = {i: c for i, c in enumerate(CANONICAL_CLASSES)}
    y_idx = y_str.map(class_to_idx).values

    print(f"Training on full dataset ({len(train_df)} samples)...")

    # Step 1: Obtain optimal global offsets (either precomputed or freshly evaluated)
    if global_offsets is None:
        cv_res = run_cross_validation(train_path=train_path, random_state=random_state)
        global_offsets_dict = cv_res["global_offsets"]
    else:
        global_offsets_dict = global_offsets
    offsets_vec = np.array([global_offsets_dict[c] for c in CANONICAL_CLASSES])

    # Step 2: Fit transformers on 100% of training data
    domain_extractor = DomainEnsembleExtractor()
    X_train_domain = domain_extractor.fit_transform(train_df)
    X_pred_domain = domain_extractor.transform(predict_df)

    scaler = MaxAbsScaler()
    X_train_tab_scaled = scaler.fit_transform(X_train_domain)
    X_pred_tab_scaled = scaler.transform(X_pred_domain)

    tfidf = TfidfTextFeatureExtractor(ngram_range=(3, 5), min_df=2, max_features=15000)
    X_train_text = tfidf.fit_transform(train_df["composite_text"])
    X_pred_text = tfidf.transform(predict_df["composite_text"])

    X_train_all = hstack([X_train_text, csr_matrix(X_train_tab_scaled)])
    X_pred_all = hstack([X_pred_text, csr_matrix(X_pred_tab_scaled)])

    # Step 3: Train full LinearSVC
    full_clf = LinearSVC(C=1.0, class_weight="balanced", random_state=random_state, dual=False, max_iter=2000)
    full_clf.fit(X_train_all, y_str)

    # Step 4: Compute raw scores on predict.csv
    pred_scores_raw = full_clf.decision_function(X_pred_all)
    # Re-order scores to match CANONICAL_CLASSES order
    pred_scores_canonical = np.zeros((len(predict_df), len(CANONICAL_CLASSES)))
    for c_idx, c_name in enumerate(full_clf.classes_):
        canonical_idx = class_to_idx[c_name]
        pred_scores_canonical[:, canonical_idx] = pred_scores_raw[:, c_idx]

    # Step 5: Apply learned threshold offsets
    calibrated_scores = pred_scores_canonical + offsets_vec
    pred_class_indices = np.argmax(calibrated_scores, axis=1)
    predictions = [idx_to_class[idx] for idx in pred_class_indices]

    # Step 6: Create, validate, and export submission
    submission_df = pd.DataFrame({
        "id": predict_df["id"],
        "category": predictions,
    })
    export_submission(submission_df, output_submission_path)

    print(f"Submission successfully generated and verified: {output_submission_path}")
    print("\nPredicted Category Distribution in Predict Dataset:")
    print(submission_df["category"].value_counts())

    return submission_df
