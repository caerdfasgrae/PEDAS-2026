"""Methodological Evaluation & Cross-Validation Module for PeDaS 2026.

Metric: Macro-F1 with zero_division=0.
"""

import warnings
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold
from src.cleaner import CANONICAL_CLASSES


def competition_macro_f1(y_true, y_pred, labels=CANONICAL_CLASSES) -> float:
    """Official PeDaS 2026 competition evaluation metric.
    
    Macro-F1 (unweighted average of F1 across all classes with zero_division=0).
    """
    return float(f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0))


def get_stratified_folds(
    X: pd.DataFrame | pd.Series,
    y: pd.Series,
    n_splits: int = 5,
    random_state: int = 2026,
):
    """Generates Stratified K-Fold splits.
    
    Handles rare / singleton classes gracefully without data corruption.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
        return list(skf.split(X, y))


def compute_metrics_report(y_true, y_pred, class_names=CANONICAL_CLASSES) -> dict:
    """Computes full evaluation report:
    - macro_f1
    - per_class_f1
    - classification_report
    - confusion_matrix
    """
    macro_f1 = competition_macro_f1(y_true, y_pred, labels=class_names)
    f1_per_class = f1_score(y_true, y_pred, labels=class_names, average=None, zero_division=0)
    class_f1_dict = {cls: float(f1) for cls, f1 in zip(class_names, f1_per_class)}
    
    report_str = classification_report(y_true, y_pred, labels=class_names, zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=class_names)
    
    return {
        "macro_f1": macro_f1,
        "per_class_f1": class_f1_dict,
        "classification_report": report_str,
        "confusion_matrix": cm,
    }
