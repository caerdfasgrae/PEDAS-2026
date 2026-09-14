"""Multiclass Probabilistic Calibrator for PeDaS 2026.

Converts raw LinearSVC decision margins into well-calibrated posterior probabilities
P(y = k | x) using fold-isolated temperature scaling / multiclass Platt scaling.
Guarantees:
- Output matrix of shape (N, K) with non-negative entries.
- Row-wise sum strictly equals 1.0.
- No data leakage: fit strictly on training fold margins, transform validation fold margins.
"""

from typing import Optional, List, Any
import numpy as np
from scipy.special import softmax
from sklearn.linear_model import LogisticRegression


class MulticlassPlattCalibrator:
    """Calibrates multiclass decision function margins into posterior probabilities.
    
    Fits a multinomial logistic regression model directly on the raw decision margin vectors:
    margins S in R^{N x K} -> logits -> softmax -> P(y=k | x).
    Guarantees output shape is always (M, n_classes) even if training fold has fewer classes.
    """

    def __init__(
        self,
        n_classes: Optional[int] = None,
        class_labels: Optional[List[Any]] = None,
        random_state: int = 2026,
        max_iter: int = 500,
    ):
        self.n_classes = n_classes
        self.class_labels = list(class_labels) if class_labels is not None else None
        self.random_state = random_state
        self.max_iter = max_iter
        self.calibrator: Optional[LogisticRegression] = None
        self.classes_: Optional[np.ndarray] = None

    def fit(self, margins: np.ndarray, y_true: np.ndarray):
        """Fits calibration parameters on training fold margins and labels."""
        self.classes_ = np.unique(y_true)
        if len(self.classes_) < 2:
            return self

        # Using L-BFGS on small (N, K) feature space converges in a few milliseconds
        self.calibrator = LogisticRegression(
            C=1.0,
            solver="lbfgs",
            max_iter=self.max_iter,
            random_state=self.random_state,
        )
        self.calibrator.fit(margins, y_true)
        return self

    def predict_proba(self, margins: np.ndarray) -> np.ndarray:
        """Transforms decision margins into calibrated probabilities.
        
        Guarantees returned array has shape (M, n_classes) with row-wise sum = 1.0.
        """
        M = margins.shape[0]
        K = self.n_classes or margins.shape[1]
        out_probas = np.full((M, K), 1e-12)

        if self.calibrator is None:
            raw_sm = softmax(margins, axis=1)
            if raw_sm.shape[1] == K:
                return raw_sm
            out_probas[:, :raw_sm.shape[1]] = raw_sm
            return out_probas / out_probas.sum(axis=1, keepdims=True)

        raw_probas = self.calibrator.predict_proba(margins)
        for sub_idx, original_cls in enumerate(self.calibrator.classes_):
            if self.class_labels is not None and original_cls in self.class_labels:
                col_idx = self.class_labels.index(original_cls)
            elif isinstance(original_cls, (int, np.integer)) and 0 <= original_cls < K:
                col_idx = int(original_cls)
            elif sub_idx < K:
                col_idx = sub_idx
            else:
                continue

            if col_idx < K:
                out_probas[:, col_idx] = raw_probas[:, sub_idx]

        out_probas = np.clip(out_probas, 1e-12, 1.0)
        out_probas = out_probas / out_probas.sum(axis=1, keepdims=True)
        return out_probas
