"""Evaluation metrics for PeDaS 2026 Phishing Detection."""

from __future__ import annotations
from typing import Dict, Any
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)


def calculate_classification_metrics(
    y_true: np.ndarray | list,
    y_pred: np.ndarray | list,
    y_prob: np.ndarray | list | None = None,
) -> Dict[str, Any]:
    """Computes comprehensive evaluation metrics for binary phishing classification.

    Args:
        y_true: Ground truth labels (0 = legitimate, 1 = phishing).
        y_pred: Predicted discrete labels (0 or 1).
        y_prob: Predicted probability of phishing (positive class).

    Returns:
        Dictionary of scores and confusion matrix.
    """
    y_t = np.array(y_true)
    y_p = np.array(y_pred)

    acc = accuracy_score(y_t, y_p)
    prec = precision_score(y_t, y_p, zero_division=0)
    rec = recall_score(y_t, y_p, zero_division=0)
    f1_bin = f1_score(y_t, y_p, average="binary", zero_division=0)
    f1_macro = f1_score(y_t, y_p, average="macro", zero_division=0)

    cm = confusion_matrix(y_t, y_p)
    # Confusion matrix components: tn, fp, fn, tp
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
    else:
        tn, fp, fn, tp = 0, 0, 0, 0
        fpr, fnr = 0.0, 0.0

    roc_auc = None
    if y_prob is not None:
        try:
            roc_auc = roc_auc_score(y_t, y_prob)
        except ValueError:
            roc_auc = None

    metrics = {
        "accuracy": round(float(acc), 4),
        "f1_macro": round(float(f1_macro), 4),
        "f1_binary": round(float(f1_bin), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "fpr": round(float(fpr), 4),
        "fnr": round(float(fnr), 4),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "true_negatives": int(tn),
        "false_negatives": int(fn),
    }

    if roc_auc is not None:
        metrics["roc_auc"] = round(float(roc_auc), 4)

    return metrics
