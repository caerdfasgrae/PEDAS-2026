"""Unit tests for the Calibrated Domain Ensemble Pipeline and Threshold Optimizer."""

import pytest
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

from src.cleaner import clean_url, clean_brand, build_composite_text, CANONICAL_CLASSES, clean_category
from src.pedas_features import DomainEnsembleExtractor, extract_domain_ensemble_features
from src.models.threshold_optimizer import MulticlassThresholdOptimizer, calculate_fast_macro_f1
from src.submission import validate_submission


def test_clean_url_strips_site_prefix():
    url_with_site = "site:https://contoh-domain.id/login"
    cleaned = clean_url(url_with_site)
    assert not cleaned.lower().startswith("site:")
    assert cleaned == "https://contoh-domain.id/login"


def test_build_composite_text_normalizes_casing():
    df = pd.DataFrame({
        "url": ["http://contoh.id"],
        "brand": ["BCA"],
        "sld": ["ID"],
        "registrar": ["KEMENTERIAN KOMUNIKASI DAN INFORMATIKA"],
    })
    comp = build_composite_text(df).iloc[0]
    assert "registrar kementerian komunikasi dan informatika" in comp
    assert "sld id" in comp
    assert "brand bca" in comp


def test_domain_ensemble_extractor_alignment():
    train_df = pd.DataFrame({
        "url": ["http://***.id", "http://phish.id/login"],
        "brand": ["unknown_brand", "BCA"],
        "discovered": ["2024-01-15 10:00", "2024-03-20 12:00"],
        "registration_date": ["2020-01-01", "2024-03-01"],
        "confidence_level": [100.0, 90.0],
        "ip": ["103.1.2.3", None],
        "sld": ["id", "co.id"],
        "registrar": ["PT Digital Registra Indonesia", "Unknown"],
    })
    test_df = pd.DataFrame({
        "url": ["https://test.my.id/page"],
        "brand": ["unknown_brand"],
        "discovered": ["2024-04-01 10:00"],
        "registration_date": ["2023-01-01"],
        "confidence_level": [100.0],
        "ip": ["104.21.9.1"],
        "sld": ["my.id"],
        "registrar": ["PT Digital Registra Indonesia"],
    })

    extractor = DomainEnsembleExtractor()
    X_train = extractor.fit_transform(train_df)
    X_test = extractor.transform(test_df)

    assert X_train.shape[1] == X_test.shape[1]
    assert list(X_train.columns) == list(X_test.columns)
    assert not X_train.isna().any().any()
    assert not X_test.isna().any().any()


def test_fast_macro_f1_matches_sklearn():
    np.random.seed(2026)
    N, C = 200, 9
    y_true = np.random.randint(0, C, size=N)
    S = np.random.randn(N, C)
    offsets = np.random.randn(C) * 0.5

    # Fast calculation
    fast_f1 = calculate_fast_macro_f1(S, offsets, y_true, C=C)

    # Sklearn ground truth calculation
    preds = np.argmax(S + offsets, axis=1)
    sk_f1 = f1_score(y_true, preds, average="macro", zero_division=0)

    assert np.isclose(fast_f1, sk_f1, atol=1e-6), f"Fast F1 ({fast_f1}) != Sklearn F1 ({sk_f1})"


def test_multiclass_threshold_optimizer_improvement():
    np.random.seed(2026)
    N, C = 500, 9
    # Imbalanced labels
    probs = np.array([0.5, 0.25, 0.1, 0.05, 0.04, 0.03, 0.015, 0.01, 0.005])
    probs = probs / probs.sum()
    y_true = np.random.choice(C, size=N, p=probs)

    # Synthetic scores slightly biased towards majority
    S = np.random.randn(N, C)
    for i in range(N):
        S[i, y_true[i]] += 1.5

    init_f1 = calculate_fast_macro_f1(S, np.zeros(C), y_true, C=C)
    optimizer = MulticlassThresholdOptimizer(C=C, search_range=(-1.0, 1.0), n_steps=21, max_iter=2)
    optimizer.fit(S, y_true)

    opt_f1 = optimizer.best_macro_f1_
    assert opt_f1 >= init_f1, f"Optimized F1 ({opt_f1}) should be >= Initial F1 ({init_f1})"


def test_submission_validation():
    # Validates that the generated submission file matches template constraints
    sub_path = "official/submission_calibrated_ensemble.csv"
    sub_df = pd.read_csv(sub_path)
    # Should not raise any ValueError
    validate_submission(sub_df)
    assert sub_df.shape == (1500, 2)
    assert set(sub_df["category"].unique()).issubset(set(CANONICAL_CLASSES))


def test_domain_ensemble_extractor_sliced_index():
    # Regression test for positional indexing bug on sliced DataFrames
    sliced_df = pd.DataFrame({
        "url": [
            "http://aged-domain.id",
            "http://future-reg.id",
            "http://fresh-domain.id",
        ],
        "brand": ["unknown_brand", "unknown_brand", "unknown_brand"],
        "discovered": ["2024-04-30 12:00", "2024-04-30 12:00", "2024-04-30 12:00"],
        "registration_date": ["2015-01-01", "2026-05-01", "2024-03-01"], # aged (>1000d), future (<0d), fresh (~60d)
        "confidence_level": [100.0, np.nan, 80.0],
        "ip": ["103.1.2.3", "104.21.1.1", None],
        "sld": ["id", "id", "id"],
        "registrar": ["PT Digital Registra Indonesia", "PT JC Indonesia", "Other"],
    }, index=[105, 210, 315]) # Arbitrary non-zero, non-contiguous index

    extractor = DomainEnsembleExtractor()
    X = extractor.fit_transform(sliced_df)

    assert X.loc[105, "is_aged_domain"] == 1
    assert X.loc[105, "is_fresh_domain"] == 0
    assert X.loc[105, "is_future_reg"] == 0

    assert X.loc[210, "is_future_reg"] == 1
    assert X.loc[210, "is_fresh_domain"] == 0
    assert X.loc[210, "is_aged_domain"] == 0

    assert X.loc[315, "is_fresh_domain"] == 1
    assert X.loc[315, "is_aged_domain"] == 0
    assert X.loc[315, "is_future_reg"] == 0


def test_competition_macro_f1_canonical_labels():
    from src.evaluator import competition_macro_f1
    # Only 7 classes present in true and pred
    present_classes = CANONICAL_CLASSES[:7]
    y_true = np.array(present_classes)
    y_pred = np.array(present_classes)

    # With all 7 perfectly predicted, score over all 9 canonical classes must be 7/9
    score = competition_macro_f1(y_true, y_pred)
    assert np.isclose(score, 7.0 / 9.0), f"Expected 7/9 ({7.0/9.0:.4f}), got {score:.4f}"


def test_threshold_optimizer_anchor_freeze():
    np.random.seed(2026)
    N, C = 300, 9
    y_true = np.random.randint(0, C, size=N)
    S = np.random.randn(N, C)
    for i in range(N):
        S[i, y_true[i]] += 1.0

    optimizer = MulticlassThresholdOptimizer(C=C, search_range=(-1.0, 1.0), n_steps=21, anchor_class=0)
    optimizer.fit(S, y_true)

    assert optimizer.offsets_[0] == 0.0, "Anchor class 0 offset must remain frozen at 0.0"

