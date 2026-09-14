"""Unit tests for HybridProbabilisticBlender."""

import pytest
import numpy as np
import pandas as pd
from src.cleaner import CANONICAL_CLASSES
from src.models.hybrid_blender import HybridProbabilisticBlender


@pytest.fixture
def synthetic_data():
    np.random.seed(2026)
    n_samples = 60
    classes = ["online gambling", "phishing", "malware", "brand", "fakeshop"]
    urls = [
        "http://contoh-judi-slot-gacor.id/login",
        "https://bca-verifikasi-akun.id/login",
        "http://download-malware-payload.id/setup.exe",
        "https://bankmandiri.co.id/portal",
        "http://toko-online-murah-promo.id/beli",
    ] * 12

    df = pd.DataFrame({
        "url": urls,
        "category_clean": np.random.choice(classes, size=n_samples),
        "brand": ["unknown_brand", "BCA", "unknown_brand", "Bank Mandiri", "unknown_brand"] * 12,
        "discovered": ["2024-01-01 00:00"] * n_samples,
        "registration_date": ["2023-01-01"] * n_samples,
        "confidence_level": [100.0] * n_samples,
        "ip": ["103.1.2.3"] * n_samples,
        "sld": ["id"] * n_samples,
        "registrar": ["PT Digital Registra Indonesia"] * n_samples,
        "composite_text": [
            "url " + u + " brand unknown sld id registrar pt digital registra indonesia"
            for u in urls
        ],
    })
    return df


def test_hybrid_blender_fit_predict_proba_shape(synthetic_data):
    blender = HybridProbabilisticBlender(
        text_weight=0.7,
        n_estimators=10,
        random_state=2026,
    )
    blender.fit(synthetic_data, optimize_thresholds=True)

    test_df = synthetic_data.iloc[:10].copy()
    probas = blender.predict_proba(test_df)

    assert probas.shape == (10, len(CANONICAL_CLASSES))
    assert np.all(probas >= 0.0)
    assert np.all(probas <= 1.0)
    np.testing.assert_allclose(probas.sum(axis=1), np.ones(10), atol=1e-5)


def test_hybrid_blender_predict_labels(synthetic_data):
    blender = HybridProbabilisticBlender(
        text_weight=0.6,
        n_estimators=10,
        random_state=2026,
    )
    blender.fit(synthetic_data, optimize_thresholds=False)

    preds = blender.predict(synthetic_data.iloc[:5])
    assert len(preds) == 5
    for p in preds:
        assert p in CANONICAL_CLASSES


def test_hybrid_blender_evidence_guard_protection(synthetic_data):
    blender = HybridProbabilisticBlender(
        text_weight=0.7,
        n_estimators=10,
        random_state=2026,
    )
    blender.fit(synthetic_data, optimize_thresholds=False)

    # Artificially set an extreme fakeshop offset
    fakeshop_idx = CANONICAL_CLASSES.index("fakeshop")
    blender.threshold_optimizer.offsets_[fakeshop_idx] = 100.0

    # Explicit gambling URL
    gambling_df = pd.DataFrame({
        "url": ["http://slot-gacor-maxwin-zeus88.id/deposit"],
        "brand": ["unknown_brand"],
        "discovered": ["2024-01-01 00:00"],
        "registration_date": ["2023-01-01"],
        "confidence_level": [100.0],
        "ip": ["103.1.2.3"],
        "sld": ["id"],
        "registrar": ["PT Digital Registra Indonesia"],
        "composite_text": ["url http://slot-gacor-maxwin-zeus88.id/deposit sld id brand unknown"],
    })

    # With evidence guard enabled, it must NOT be predicted as fakeshop
    guarded_preds = blender.predict(gambling_df, apply_guard=True)
    assert guarded_preds[0] == "online gambling", f"Expected online gambling, got {guarded_preds[0]}"
