"""Baseline Model Trainer with Stratified K-Fold Cross-Validation.

Implements leak-free cross-validation and feature importance analysis using
Gradient Boosted Decision Trees (LightGBM, XGBoost, CatBoost, Random Forest).
"""

from __future__ import annotations
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier

from src.models.metrics import calculate_classification_metrics
from src.utils.config import RANDOM_STATE


class BaselineModelTrainer:
    """Trains and validates baseline machine learning models with Stratified K-Fold."""

    def __init__(
        self,
        model_type: str = "lightgbm",
        n_splits: int = 5,
        random_state: int = RANDOM_STATE,
        model_params: Dict[str, Any] | None = None,
    ):
        self.model_type = model_type.lower()
        self.n_splits = n_splits
        self.random_state = random_state
        self.model_params = model_params or {}

    def _get_model_instance(self):
        """Instantiates the specified classifier with fixed random state."""
        if self.model_type == "lightgbm":
            from lightgbm import LGBMClassifier
            params = {
                "n_estimators": 150,
                "learning_rate": 0.05,
                "random_state": self.random_state,
                "verbose": -1,
                **self.model_params,
            }
            return LGBMClassifier(**params)

        elif self.model_type == "xgboost":
            from xgboost import XGBClassifier
            params = {
                "n_estimators": 150,
                "learning_rate": 0.05,
                "random_state": self.random_state,
                "eval_metric": "logloss",
                **self.model_params,
            }
            return XGBClassifier(**params)

        elif self.model_type == "catboost":
            from catboost import CatBoostClassifier
            params = {
                "iterations": 150,
                "learning_rate": 0.05,
                "random_seed": self.random_state,
                "verbose": 0,
                **self.model_params,
            }
            return CatBoostClassifier(**params)

        elif self.model_type == "rf":
            params = {
                "n_estimators": 150,
                "random_state": self.random_state,
                "n_jobs": -1,
                **self.model_params,
            }
            return RandomForestClassifier(**params)

        else:
            raise ValueError(f"Unsupported model_type: {self.model_type}. Choose from 'lightgbm', 'xgboost', 'catboost', 'rf'.")

    def cross_validate(
        self,
        X: pd.DataFrame,
        y: np.ndarray | pd.Series,
    ) -> Tuple[Dict[str, Any], pd.DataFrame, np.ndarray]:
        """Performs Stratified K-Fold Cross Validation.

        Returns:
            Tuple of (overall_metrics, feature_importance_df, oof_probabilities)
        """
        X_df = X.copy()
        y_arr = np.array(y)

        # Impute any missing values safely (e.g. median)
        X_clean = X_df.fillna(0.0)
        feature_names = list(X_clean.columns)

        skf = StratifiedKFold(n_splits=self.n_splits, shuffle=True, random_state=self.random_state)
        oof_probs = np.zeros(len(y_arr))
        oof_preds = np.zeros(len(y_arr))
        feature_importances = np.zeros(len(feature_names))

        fold_metrics = []

        for fold, (train_idx, val_idx) in enumerate(skf.split(X_clean, y_arr), 1):
            X_train, y_train = X_clean.iloc[train_idx], y_arr[train_idx]
            X_val, y_val = X_clean.iloc[val_idx], y_arr[val_idx]

            model = self._get_model_instance()
            model.fit(X_train, y_train)

            # Predict probabilities
            if hasattr(model, "predict_proba"):
                val_probs = model.predict_proba(X_val)[:, 1]
            else:
                val_probs = model.predict(X_val)

            val_preds = (val_probs >= 0.5).astype(int)

            oof_probs[val_idx] = val_probs
            oof_preds[val_idx] = val_preds

            m = calculate_classification_metrics(y_val, val_preds, val_probs)
            fold_metrics.append(m)

            # Accumulate feature importance
            if hasattr(model, "feature_importances_"):
                feature_importances += model.feature_importances_ / self.n_splits

        # Compute overall OOF metrics
        overall_metrics = calculate_classification_metrics(y_arr, oof_preds, oof_probs)
        overall_metrics["fold_f1_macros"] = [f["f1_macro"] for f in fold_metrics]

        # Build feature importance DataFrame
        fi_df = pd.DataFrame({
            "feature": feature_names,
            "importance": feature_importances,
        }).sort_values(by="importance", ascending=False).reset_index(drop=True)

        return overall_metrics, fi_df, oof_probs
