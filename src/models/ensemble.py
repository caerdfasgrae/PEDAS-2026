"""Multi-GBDT Ensemble Blending Module.

Combines Out-of-Fold predictions from LightGBM, CatBoost, and XGBoost using
optimal constrained weight optimization (SLSQP) and nested thresholding.
"""

from __future__ import annotations
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.metrics import log_loss, f1_score

from src.models.baseline import BaselineModelTrainer
from src.models.metrics import calculate_classification_metrics
from src.models.validation import NestedThresholdOptimizer, DomainGroupSplitter
from src.utils.config import RANDOM_STATE


class WeightedBlender:
    """Ensemble blender that optimizes model weights and decision threshold."""

    def __init__(
        self,
        model_names: List[str] | None = None,
        n_splits: int = 5,
        random_state: int = RANDOM_STATE,
    ):
        self.model_names = model_names or ["lightgbm", "catboost", "xgboost"]
        self.n_splits = n_splits
        self.random_state = random_state
        self.weights: np.ndarray = np.ones(len(self.model_names)) / len(self.model_names)
        self.optimal_threshold: float = 0.5
        self.fitted_trainers: Dict[str, BaselineModelTrainer] = {}
        self.oof_predictions: Dict[str, np.ndarray] = {}

    def fit_cross_validate(
        self,
        X: pd.DataFrame,
        y: np.ndarray | pd.Series,
        urls: List[str] | pd.Series | None = None,
        use_group_kfold: bool = False,
    ) -> Dict[str, Any]:
        """Trains all constituent models, records OOF probabilities, and finds optimal weights & threshold."""
        y_arr = np.array(y)
        num_models = len(self.model_names)

        # 1. Train each model architecture
        for name in self.model_names:
            trainer = BaselineModelTrainer(
                model_type=name,
                n_splits=self.n_splits,
                random_state=self.random_state,
            )
            # BaselineModelTrainer.cross_validate returns (metrics, fi_df, oof_probs)
            metrics, fi_df, oof_probs = trainer.cross_validate(X, y_arr)
            self.fitted_trainers[name] = trainer
            self.oof_predictions[name] = oof_probs

        # 2. Stack OOF probabilities: matrix of shape (n_samples, n_models)
        oof_matrix = np.column_stack([self.oof_predictions[m] for m in self.model_names])

        # 3. Optimize Weights (minimize LogLoss with sum(w)=1 and w>=0)
        def loss_func(weights):
            blended_prob = np.clip(np.dot(oof_matrix, weights), 1e-7, 1 - 1e-7)
            return log_loss(y_arr, blended_prob)

        initial_weights = np.ones(num_models) / num_models
        bounds = [(0.0, 1.0) for _ in range(num_models)]
        constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1.0}

        opt_result = minimize(
            loss_func,
            initial_weights,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )

        if opt_result.success:
            self.weights = opt_result.x
        else:
            self.weights = initial_weights

        # Normalize weights
        self.weights = self.weights / np.sum(self.weights)

        # 4. Compute Blended OOF Probabilities
        blended_oof_prob = np.dot(oof_matrix, self.weights)

        # 5. Optimize Decision Threshold on Blended Probabilities
        thresh_opt = NestedThresholdOptimizer(metric="f1_macro")
        best_thresh, best_f1 = thresh_opt.find_best_threshold(y_arr, blended_oof_prob)
        self.optimal_threshold = best_thresh

        # 6. Compute Final Metrics
        blended_preds_at_05 = (blended_oof_prob >= 0.5).astype(int)
        blended_preds_at_opt = (blended_oof_prob >= self.optimal_threshold).astype(int)

        metrics_at_05 = calculate_classification_metrics(y_arr, blended_preds_at_05, blended_oof_prob)
        metrics_at_opt = calculate_classification_metrics(y_arr, blended_preds_at_opt, blended_oof_prob)

        weights_dict = {
            self.model_names[i]: round(float(self.weights[i]), 4)
            for i in range(num_models)
        }

        return {
            "model_weights": weights_dict,
            "optimal_threshold": round(float(self.optimal_threshold), 3),
            "metrics_at_05": metrics_at_05,
            "metrics_at_optimal_threshold": metrics_at_opt,
            "blended_oof_probabilities": blended_oof_prob,
        }

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predicts blended probabilities on new test data using fold-bagged models."""
        if not self.fitted_trainers:
            raise ValueError("WeightedBlender has not been fitted yet. Call fit_cross_validate first.")

        model_probs = []
        for name in self.model_names:
            trainer = self.fitted_trainers[name]
            p = trainer.predict_proba(X)
            model_probs.append(p)

        prob_matrix = np.column_stack(model_probs)
        blended_prob = np.dot(prob_matrix, self.weights)
        return np.clip(blended_prob, 0.0, 1.0)

    def predict(self, X: pd.DataFrame, use_optimal_threshold: bool = True) -> np.ndarray:
        """Predicts binary classification labels using the calibrated optimal threshold."""
        prob = self.predict_proba(X)
        threshold = self.optimal_threshold if use_optimal_threshold else 0.5
        return (prob >= threshold).astype(int)
