"""URL Character N-Gram Stacking Meta-Feature Generator.

Extracts sub-word lexical patterns using Character N-Gram TF-IDF and regularized
linear stacking, providing high-signal probability meta-features without
blowing up GBDT tree complexity.
"""

from __future__ import annotations
from typing import List, Tuple
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

from src.utils.config import RANDOM_STATE


class URLNgramStacker:
    """Extracts Character N-Gram patterns and converts them into a dense meta-feature via Stacking."""

    def __init__(
        self,
        ngram_range: Tuple[int, int] = (3, 5),
        max_features: int = 5000,
        n_splits: int = 5,
        random_state: int = RANDOM_STATE,
    ):
        self.ngram_range = ngram_range
        self.max_features = max_features
        self.n_splits = n_splits
        self.random_state = random_state

        self.vectorizer = TfidfVectorizer(
            analyzer="char",
            ngram_range=self.ngram_range,
            max_features=self.max_features,
            sublinear_tf=True,
        )
        self.meta_model = LogisticRegression(
            C=1.0,
            solver="liblinear",
            random_state=self.random_state,
        )
        self.is_fitted = False

    def fit_transform(self, urls: List[str] | pd.Series, y: np.ndarray | pd.Series) -> pd.DataFrame:
        """Fits vectorizer and computes Out-of-Fold (OOF) stacking probability to prevent target leakage.

        Returns:
            DataFrame with column 'ngram_phish_prob'.
        """
        urls_list = list(urls)
        y_arr = np.array(y)

        # Fit vectorizer on full training URLs
        X_tfidf = self.vectorizer.fit_transform(urls_list)

        oof_probs = np.zeros(len(y_arr))
        skf = StratifiedKFold(n_splits=self.n_splits, shuffle=True, random_state=self.random_state)

        for train_idx, val_idx in skf.split(urls_list, y_arr):
            X_tr, y_tr = X_tfidf[train_idx], y_arr[train_idx]
            X_va = X_tfidf[val_idx]

            fold_clf = LogisticRegression(C=1.0, solver="liblinear", random_state=self.random_state)
            fold_clf.fit(X_tr, y_tr)

            # Predict probability of phishing (class 1)
            oof_probs[val_idx] = fold_clf.predict_proba(X_va)[:, 1]

        # Finally fit full meta_model on all training TF-IDF
        self.meta_model.fit(X_tfidf, y_arr)
        self.is_fitted = True

        return pd.DataFrame({
            "ngram_phish_prob": np.round(oof_probs, 4),
        })

    def transform(self, urls: List[str] | pd.Series) -> pd.DataFrame:
        """Transforms unseen test URLs using the fitted vectorizer and meta_model."""
        if not self.is_fitted:
            raise ValueError("URLNgramStacker is not fitted yet. Call fit_transform first.")

        urls_list = list(urls)
        X_tfidf = self.vectorizer.transform(urls_list)
        test_probs = self.meta_model.predict_proba(X_tfidf)[:, 1]

        return pd.DataFrame({
            "ngram_phish_prob": np.round(test_probs, 4),
        })
