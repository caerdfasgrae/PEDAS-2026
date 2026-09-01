"""Unit tests for advanced optimizations: GroupKFold, Threshold Optimizer, N-Gram Stacking, and Ensemble."""

import pytest
import numpy as np
import pandas as pd
import tldextract

from src.models.validation import DomainGroupSplitter, NestedThresholdOptimizer
from src.features.nlp_stacking import URLNgramStacker
from src.models.ensemble import WeightedBlender
from src.utils.config import RANDOM_STATE


def test_domain_group_splitter_no_leakage():
    # Construct synthetic URLs where same domain appears multiple times with different paths
    urls = [
        "http://attacker.my.id/login",
        "http://attacker.my.id/verify",
        "http://attacker.my.id/claim",
        "https://bank.klikbca.com/index",
        "https://bank.klikbca.com/auth",
        "http://phish-dana.web.id/1",
        "http://phish-dana.web.id/2",
        "https://dana.id/page1",
        "https://dana.id/page2",
        "http://evil-bri.biz.id/form",
        "http://evil-bri.biz.id/submit",
        "https://bri.co.id/brimo",
    ]
    y = [1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0]

    splitter = DomainGroupSplitter(n_splits=3, random_state=RANDOM_STATE)
    splits = list(splitter.split(urls, y))

    assert len(splits) == 3
    for train_idx, val_idx in splits:
        train_domains = {f"{ext.domain}.{ext.suffix}" if ext.suffix else ext.domain for ext in [tldextract.extract(urls[i]) for i in train_idx]}
        val_domains = {f"{ext.domain}.{ext.suffix}" if ext.suffix else ext.domain for ext in [tldextract.extract(urls[i]) for i in val_idx]}
        # Check strict disjoint intersection between train domains and val domains
        overlap = train_domains.intersection(val_domains)
        assert len(overlap) == 0, f"Domain group leakage detected! Overlapping domains: {overlap}"


def test_nested_threshold_optimizer():
    optimizer = NestedThresholdOptimizer(metric="f1_macro")
    y_true = np.array([1, 1, 1, 1, 0, 0, 0, 0, 0, 0])
    # Skewed probabilities where optimal threshold is lower than 0.5
    y_prob = np.array([0.45, 0.42, 0.48, 0.40, 0.10, 0.15, 0.20, 0.05, 0.12, 0.18])

    best_thresh, best_f1 = optimizer.find_best_threshold(y_true, y_prob)

    assert 0.1 <= best_thresh <= 0.5
    assert best_f1 > 0.8


def test_url_ngram_stacker():
    train_urls = [
        "http://bca-secure-login.id/verify",
        "http://dana-kaget-saldo.biz.id/klaim",
        "https://bank.klikbca.com",
        "https://dana.id",
        "http://bri-mo-aktivasi.web.id/auth",
        "https://bri.co.id/brimo",
    ]
    train_y = np.array([1, 1, 0, 0, 1, 0])

    test_urls = [
        "http://mandiri-livin-palsu.web.id/login",
        "https://bankmandiri.co.id",
    ]

    stacker = URLNgramStacker(n_splits=2, random_state=RANDOM_STATE)
    train_meta = stacker.fit_transform(train_urls, train_y)
    test_meta = stacker.transform(test_urls)

    assert "ngram_phish_prob" in train_meta.columns
    assert len(train_meta) == len(train_urls)
    assert not train_meta.isna().any().any()

    assert "ngram_phish_prob" in test_meta.columns
    assert len(test_meta) == len(test_urls)
    assert not test_meta.isna().any().any()


def test_weighted_blender():
    # Test blender on a simple synthetic DataFrame
    X = pd.DataFrame({
        "feat_1": [10.0, 12.0, 15.0, 2.0, 1.0, 3.0, 14.0, 2.5],
        "feat_2": [1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0],
        "feat_3": [0.8, 0.9, 0.85, 0.1, 0.2, 0.15, 0.95, 0.05],
    })
    y = np.array([1, 1, 1, 0, 0, 0, 1, 0])

    blender = WeightedBlender(model_names=["lightgbm", "catboost"], n_splits=2, random_state=RANDOM_STATE)
    res = blender.fit_cross_validate(X, y)

    assert "model_weights" in res
    assert "optimal_threshold" in res
    assert np.isclose(sum(res["model_weights"].values()), 1.0, atol=1e-3)

    # Test test-set prediction
    test_X = pd.DataFrame({
        "feat_1": [11.0, 1.5],
        "feat_2": [1.0, 0.0],
        "feat_3": [0.88, 0.12],
    })
    probs = blender.predict_proba(test_X)
    preds = blender.predict(test_X)

    assert len(probs) == 2
    assert len(preds) == 2
    assert probs[0] > probs[1]
    assert preds[0] == 1 and preds[1] == 0
