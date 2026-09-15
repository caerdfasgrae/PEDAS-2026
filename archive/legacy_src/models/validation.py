"""Validation and Leak-Free Threshold Optimization Module.

Includes StratifiedGroupKFold to prevent domain-level group leakage and
NestedThresholdOptimizer to maximize F1 scores without leaking validation labels.
"""

from __future__ import annotations
from typing import Dict, Any, Tuple, List, Callable
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, StratifiedGroupKFold
from sklearn.metrics import f1_score
import tldextract

from src.utils.config import RANDOM_STATE


class DomainGroupSplitter:
    """Creates Stratified Group K-Fold splits based on registered domain.

    Prevents domain leakage where URLs sharing the same base domain
    appear simultaneously in training and validation sets.
    """

    def __init__(self, n_splits: int = 5, random_state: int = RANDOM_STATE):
        self.n_splits = n_splits
        self.random_state = random_state

    def split(
        self,
        urls: List[str] | pd.Series,
        y: np.ndarray | pd.Series,
        force_standard_skf: bool = False,
    ):
        """Generates train and validation indices.

        Args:
            urls: Collection of raw URLs.
            y: Target binary labels.
            force_standard_skf: If True, falls back to regular StratifiedKFold.
        """
        y_arr = np.array(y)
        if force_standard_skf:
            skf = StratifiedKFold(n_splits=self.n_splits, shuffle=True, random_state=self.random_state)
            return skf.split(urls, y_arr)

        # Extract registered domain as grouping key
        groups = []
        for u in urls:
            ext = tldextract.extract(str(u))
            reg_dom = f"{ext.domain}.{ext.suffix}" if ext.suffix else (ext.domain or "unknown")
            groups.append(reg_dom)

        groups = np.array(groups)
        unique_groups = len(np.unique(groups))

        # Check if enough unique groups exist for StratifiedGroupKFold
        if unique_groups < self.n_splits * 2:
            # Fall back safely if sample dataset has very few unique domains
            skf = StratifiedKFold(n_splits=self.n_splits, shuffle=True, random_state=self.random_state)
            return skf.split(urls, y_arr)

        sgkf = StratifiedGroupKFold(n_splits=self.n_splits, shuffle=True, random_state=self.random_state)
        return sgkf.split(urls, y_arr, groups=groups)


class NestedThresholdOptimizer:
    """Optimizes classification decision threshold to maximize F1 score.

    Uses nested cross-validation or grid search on out-of-fold probabilities
    to prevent threshold overfitting.
    """

    def __init__(
        self,
        metric: str = "f1_macro",
        threshold_range: Tuple[float, float] = (0.1, 0.9),
        step: float = 0.01,
    ):
        self.metric = metric
        self.threshold_range = threshold_range
        self.step = step
        self.optimal_threshold = 0.5

    def _score_threshold(self, y_true: np.ndarray, y_prob: np.ndarray, threshold: float) -> float:
        """Computes F1 score at a given threshold."""
        y_pred = (y_prob >= threshold).astype(int)
        if self.metric == "f1_macro":
            return f1_score(y_true, y_pred, average="macro", zero_division=0)
        elif self.metric == "f1_binary":
            return f1_score(y_true, y_pred, average="binary", zero_division=0)
        else:
            return f1_score(y_true, y_pred, average="macro", zero_division=0)

    def find_best_threshold(self, y_true: np.ndarray, y_prob: np.ndarray) -> Tuple[float, float]:
        """Finds single threshold that maximizes F1 score.

        Returns:
            Tuple of (optimal_threshold, best_f1_score)
        """
        best_thresh = 0.5
        best_score = -1.0

        low, high = self.threshold_range
        for thresh in np.arange(low, high + self.step, self.step):
            score = self._score_threshold(y_true, y_prob, thresh)
            if score > best_score:
                best_score = score
                best_thresh = round(float(thresh), 3)

        self.optimal_threshold = best_thresh
        return best_thresh, best_score

    def nested_optimize(
        self,
        fold_y_val: List[np.ndarray],
        fold_oof_probs: List[np.ndarray],
    ) -> Dict[str, Any]:
        """Finds optimal threshold across K folds in a nested manner.

        For each fold i, optimizes threshold on all other folds (K-1),
        evaluates on fold i, and returns the median threshold and out-of-fold score.
        """
        n_folds = len(fold_y_val)
        fold_optimal_thresholds = []
        fold_scores_at_05 = []
        fold_scores_at_optimal = []

        for i in range(n_folds):
            # Training folds for threshold: all except i
            train_y = np.concatenate([fold_y_val[j] for j in range(n_folds) if j != i])
            train_prob = np.concatenate([fold_oof_probs[j] for j in range(n_folds) if j != i])

            # Find best threshold on training folds
            opt_t, _ = self.find_best_threshold(train_y, train_prob)
            fold_optimal_thresholds.append(opt_t)

            # Evaluate on held-out fold i
            score_at_05 = self._score_threshold(fold_y_val[i], fold_oof_probs[i], 0.5)
            score_at_opt = self._score_threshold(fold_y_val[i], fold_oof_probs[i], opt_t)

            fold_scores_at_05.append(score_at_05)
            fold_scores_at_optimal.append(score_at_opt)

        median_thresh = float(np.median(fold_optimal_thresholds))
        self.optimal_threshold = median_thresh

        return {
            "optimal_threshold": median_thresh,
            "fold_thresholds": fold_optimal_thresholds,
            "mean_f1_at_05": round(float(np.mean(fold_scores_at_05)), 4),
            "mean_f1_at_optimal": round(float(np.mean(fold_scores_at_optimal)), 4),
            "score_gain": round(float(np.mean(fold_scores_at_optimal) - np.mean(fold_scores_at_05)), 4),
        }
