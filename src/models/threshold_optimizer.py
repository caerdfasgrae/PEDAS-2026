"""Multiclass Threshold Calibration and Coordinate Descent Optimizer for PeDaS 2026.

Optimizes class-specific decision boundary offsets Delta_c to maximize unweighted Macro-F1:
    y_hat = argmax_c (s_c(x) + Delta_c)

Fully explainable: Delta_c directly represents an operating-point / prior adjustment
counterbalancing severe class imbalance without altering learned feature representations.
"""

from typing import List, Optional, Tuple, Set
import numpy as np
import pandas as pd


def calculate_fast_macro_f1(
    S: np.ndarray,
    offsets: np.ndarray,
    y_true: np.ndarray,
    C: int = 9,
) -> float:
    """Vectorized calculation of unweighted Macro-F1 score via numpy bincount.
    
    Operates at sub-millisecond speeds (< 0.5 ms for N=8,400, C=9), enabling
    rapid coordinate descent optimization over thousands of candidate offsets.
    """
    P = np.argmax(S + offsets, axis=1)
    cm = np.bincount(y_true * C + P, minlength=C * C).reshape(C, C)
    tp = np.diag(cm)
    fp = cm.sum(axis=0) - tp
    fn = cm.sum(axis=1) - tp
    denom = 2 * tp + fp + fn
    f1 = np.divide(2.0 * tp, denom, out=np.zeros_like(denom, dtype=float), where=denom > 0)
    return float(np.mean(f1))


class MulticlassThresholdOptimizer:
    """Coordinate descent optimizer for multiclass decision function threshold offsets."""

    def __init__(
        self,
        C: int = 9,
        search_range: Tuple[float, float] = (-1.5, 2.5),
        n_steps: int = 81,
        max_iter: int = 3,
        frozen_classes: Optional[List[int]] = None,
        anchor_class: Optional[int] = None,
    ):
        self.C = C
        self.search_range = search_range
        self.n_steps = n_steps
        self.max_iter = max_iter
        self.anchor_class = anchor_class
        frozen_set = set(frozen_classes or [])
        if anchor_class is not None:
            frozen_set.add(anchor_class)
        self.frozen_classes: Set[int] = frozen_set
        self.offsets_: np.ndarray = np.zeros(C, dtype=float)
        self.best_macro_f1_: float = 0.0

    def fit(self, S: np.ndarray, y: np.ndarray) -> "MulticlassThresholdOptimizer":
        """Fits class offsets Delta_c via coordinate descent to maximize Macro-F1."""
        offsets = np.zeros(self.C, dtype=float)
        best_score = calculate_fast_macro_f1(S, offsets, y, self.C)
        candidate_vals = np.linspace(self.search_range[0], self.search_range[1], self.n_steps)

        for iteration in range(self.max_iter):
            improved = False
            for i in range(self.C):
                if i in self.frozen_classes:
                    continue
                best_val = offsets[i]
                for cand in candidate_vals:
                    test_offsets = offsets.copy()
                    test_offsets[i] = cand
                    sc = calculate_fast_macro_f1(S, test_offsets, y, self.C)
                    if sc > best_score + 1e-5:
                        best_score = sc
                        best_val = cand
                        improved = True
                offsets[i] = best_val

            if not improved:
                break

        self.offsets_ = offsets
        self.best_macro_f1_ = best_score
        return self

    def predict(self, S: np.ndarray) -> np.ndarray:
        """Applies learned offsets to decision function scores and predicts class indices."""
        return np.argmax(S + self.offsets_, axis=1)

    def fit_predict(self, S: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Fits offsets on S and returns calibrated predictions."""
        return self.fit(S, y).predict(S)

    def fit_probabilities(self, probas: np.ndarray, y: np.ndarray) -> "MulticlassThresholdOptimizer":
        """Fits cost-sensitive Bayes threshold weights on posterior probabilities via log-odds."""
        log_probas = np.log(np.clip(probas, 1e-12, 1.0))
        return self.fit(log_probas, y)

    def predict_probabilities(self, probas: np.ndarray) -> np.ndarray:
        """Applies Bayes threshold adjustments to posterior probabilities."""
        log_probas = np.log(np.clip(probas, 1e-12, 1.0))
        return self.predict(log_probas)

