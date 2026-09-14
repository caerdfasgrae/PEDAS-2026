"""Unit tests for MulticlassPlattCalibrator."""

import numpy as np
from src.models.probabilistic_calibrator import MulticlassPlattCalibrator


def test_probabilistic_calibrator_properties():
    # Synthetic 3-class margins
    np.random.seed(2026)
    N = 200
    K = 3
    margins = np.random.randn(N, K)
    y_true = np.random.choice(["A", "B", "C"], size=N)
    
    calibrator = MulticlassPlattCalibrator(random_state=2026)
    calibrator.fit(margins, y_true)
    
    val_margins = np.random.randn(50, K)
    probas = calibrator.predict_proba(val_margins)
    
    assert probas.shape == (50, K)
    assert np.all(probas >= 0.0)
    assert np.all(probas <= 1.0)
    np.testing.assert_allclose(probas.sum(axis=1), np.ones(50), atol=1e-5)


def test_probabilistic_calibrator_unfitted_fallback():
    K = 4
    margins = np.array([[1.0, 2.0, 0.5, -1.0], [0.0, 0.0, 0.0, 0.0]])
    calibrator = MulticlassPlattCalibrator()
    probas = calibrator.predict_proba(margins)
    
    assert probas.shape == (2, K)
    np.testing.assert_allclose(probas.sum(axis=1), np.ones(2), atol=1e-5)


def test_probabilistic_calibrator_subset_classes():
    # Test case where only classes 0, 1, 3, 4 are present in training labels out of 9 canonical classes
    np.random.seed(2026)
    N = 100
    K = 9
    margins = np.random.randn(N, K)
    # Only 4 distinct integer classes present
    y_true = np.random.choice([0, 1, 3, 4], size=N)

    calibrator = MulticlassPlattCalibrator(n_classes=K, random_state=2026)
    calibrator.fit(margins, y_true)

    val_margins = np.random.randn(20, K)
    probas = calibrator.predict_proba(val_margins)

    assert probas.shape == (20, K)
    assert np.all(probas >= 0.0)
    np.testing.assert_allclose(probas.sum(axis=1), np.ones(20), atol=1e-5)

