"""Unit tests for the jury-defensible PosteriorAnchorPolicy."""

import numpy as np
import pandas as pd

from src.cleaner import CANONICAL_CLASSES
from src.models.posterior_anchor import PosteriorAnchorPolicy


def _make_predict_df(urls):
    return pd.DataFrame({
        "id": [f"PEDAS-test{i:04d}" for i in range(len(urls))],
        "url": urls,
    })


def _probas(n_rows, class_name, probability):
    p = np.full((n_rows, len(CANONICAL_CLASSES)), 1e-9)
    idx = CANONICAL_CLASSES.index(class_name)
    p[:, idx] = probability
    return p


def test_anchor_accepts_when_posterior_meets_threshold():
    df = _make_predict_df(["http://****.co.id"])
    probas = _probas(1, "fakeshop", 0.66)
    policy = PosteriorAnchorPolicy(posterior_threshold=0.50)
    decisions = policy.evaluate(df, probas, [(0, "fakeshop")])
    assert decisions[0].decision == "ACCEPT"
    assert decisions[0].posterior == 0.66
    updated = policy.apply(["brand"], decisions)
    assert updated[0] == "fakeshop"


def test_anchor_rejects_without_posterior_or_lexical_evidence():
    df = _make_predict_df(["https://***********.id/trapstar-borsello-95693/"])
    probas = _probas(1, "phishing", 0.73)
    policy = PosteriorAnchorPolicy(posterior_threshold=0.50)
    decisions = policy.evaluate(df, probas, [(0, "fakeshop")])
    assert decisions[0].decision == "REJECT"
    updated = policy.apply(["phishing"], decisions)
    assert updated[0] == "phishing"


def test_anchor_marks_lexical_only_when_enabled():
    df = _make_predict_df(["https://www.******.co.id/professionals/online-shop-in-jakarta"])
    probas = _probas(1, "online gambling", 0.99)
    policy = PosteriorAnchorPolicy(posterior_threshold=0.50, allow_lexical_only=True)
    decisions = policy.evaluate(df, probas, [(0, "fakeshop")])
    assert decisions[0].decision == "LEXICAL_ONLY"
    assert decisions[0].lexical_match is True
    assert decisions[0].posterior_rank > 1


def test_anchor_lexical_only_disabled_by_default():
    df = _make_predict_df(["http://global-shop.*****.biz.id/"])
    probas = _probas(1, "phishing", 1.0)
    policy = PosteriorAnchorPolicy(posterior_threshold=0.50)
    decisions = policy.evaluate(df, probas, [(0, "fakeshop")])
    assert decisions[0].decision == "REJECT"


def test_anchor_veto_blocks_acceptance():
    df = _make_predict_df(["http://slot-gacor-shop.id/beli"])
    probas = _probas(1, "fakeshop", 0.80)
    policy = PosteriorAnchorPolicy(posterior_threshold=0.50)
    decisions = policy.evaluate(df, probas, [(0, "fakeshop")])
    assert decisions[0].vetoed is True
    assert decisions[0].decision == "REJECT"


def test_anchor_audit_dataframe_columns():
    df = _make_predict_df(["http://****.co.id", "http://global-shop.*****.biz.id/"])
    probas = _probas(2, "fakeshop", 0.60)
    policy = PosteriorAnchorPolicy(posterior_threshold=0.50, allow_lexical_only=True)
    decisions = policy.evaluate(df, probas, [(0, "fakeshop"), (1, "fakeshop")])
    table = PosteriorAnchorPolicy.to_dataframe(decisions)
    assert len(table) == 2
    for col in ["row_index", "posterior", "decision", "rationale", "lexical_match"]:
        assert col in table.columns
