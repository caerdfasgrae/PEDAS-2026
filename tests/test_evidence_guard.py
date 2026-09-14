"""Unit tests for EvidenceGuard."""

import numpy as np
import pandas as pd
from src.cleaner import CANONICAL_CLASSES
from src.models.evidence_guard import EvidenceGuard


def test_evidence_guard_suppression():
    guard = EvidenceGuard(class_names=CANONICAL_CLASSES)
    fakeshop_idx = CANONICAL_CLASSES.index("fakeshop")
    gambling_idx = CANONICAL_CLASSES.index("online gambling")
    phishing_idx = CANONICAL_CLASSES.index("phishing")
    
    # URL 0: Supposed to be fakeshop, but URL contains 'slot=gacor' -> Must suppress to gambling
    # URL 1: Supposed to be fakeshop, but URL contains 'login' -> Must suppress to phishing
    # URL 2: Pure root URL -> Allowed to remain fakeshop
    urls = pd.Series([
        "https://gov.example.go.id/?slot=gacor77",
        "https://bank.example.my.id/login",
        "http://pure-masked-root.***.id/",
    ])
    
    pred_indices = np.array([fakeshop_idx, fakeshop_idx, fakeshop_idx])
    scores = np.zeros((3, len(CANONICAL_CLASSES)))
    
    filtered = guard.filter_predictions(pred_indices, scores, urls)
    
    assert filtered[0] == gambling_idx, "Gambling token was not suppressed!"
    assert filtered[1] == phishing_idx, "Phishing token was not suppressed!"
    assert filtered[2] == fakeshop_idx, "Legitimate root fakeshop candidate was wrongly suppressed!"


def test_evidence_guard_leaves_majority_alone():
    guard = EvidenceGuard(class_names=CANONICAL_CLASSES)
    gambling_idx = CANONICAL_CLASSES.index("online gambling")
    
    urls = pd.Series(["https://example.com/regular"])
    pred_indices = np.array([gambling_idx])
    scores = np.zeros((1, len(CANONICAL_CLASSES)))
    
    filtered = guard.filter_predictions(pred_indices, scores, urls)
    assert filtered[0] == gambling_idx
