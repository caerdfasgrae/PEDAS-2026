"""PeDaS 2026 - Data-Centric & Adaptive Hedge Pipeline (Submisi 3).

Authoritative Module for Submisi 3:
Submisi 3 serves as the competitive portfolio's risk-hedging shield against domain shifts,
new registrar variations, and adversarial token obfuscation in the unlabelled test dataset.

Key Principles:
1. Data-Centric De-noising: Integrates DataCentricDenoiser to handle synthetic asterisk
   collisions, typos, and redundant duplicates per Juknis Pasal 3 Butir 5.
2. High-Confidence Transductive Self-Training: Identifies test samples with extreme probability
   certainty (P >= 0.98) from the initial base blend.
3. Majority-Class Gating: Only augments clean majority classes (online gambling & phishing)
   to prevent minority noise amplification or hallucinated minority pseudo-labels.
4. Threshold Recalibration: Re-optimizes multiclass decision thresholds on the augmented
   distribution to maintain tight boundary discrimination across domain shifts.
"""

from typing import Optional, Dict, Tuple, Any
import numpy as np
import pandas as pd

from src.cleaner import CANONICAL_CLASSES, load_cleaned_datasets
from src.models.hybrid_blender import HybridProbabilisticBlender
from src.submission import validate_submission, export_submission
from src.alternatives.data_centric_denoiser import DataCentricDenoiser


class AdaptiveHedgePipeline:
    """Semi-Supervised Domain Adaptation and Data-Centric Hedging Pipeline."""

    def __init__(
        self,
        confidence_threshold: float = 0.98,
        text_weight: float = 0.60,
        random_state: int = 2026,
    ):
        self.confidence_threshold = confidence_threshold
        self.text_weight = text_weight
        self.random_state = random_state
        self.blender_base: Optional[HybridProbabilisticBlender] = None
        self.blender_augmented: Optional[HybridProbabilisticBlender] = None
        self.denoiser = DataCentricDenoiser(random_state=random_state)
        self.augmented_samples_count: int = 0

    def fit_base_and_pseudo_label(
        self,
        train_df: pd.DataFrame,
        predict_df: pd.DataFrame,
        apply_denoising: bool = False,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Trains base blender and extracts safe high-confidence pseudo-labels from predict_df."""
        if apply_denoising:
            clean_train = self.denoiser.fit_transform(train_df)
        else:
            clean_train = train_df.copy()

        self.blender_base = HybridProbabilisticBlender(
            text_weight=self.text_weight,
            random_state=self.random_state,
        )
        self.blender_base.fit(clean_train, optimize_thresholds=False)

        # Predict probabilities on test dataset
        test_probas = self.blender_base.predict_proba(predict_df)
        max_p = np.max(test_probas, axis=1)
        high_conf_mask = max_p >= self.confidence_threshold

        pred_indices = np.argmax(test_probas[high_conf_mask], axis=1)
        pseudo_cats = [CANONICAL_CLASSES[p] for p in pred_indices]

        pseudo_df = predict_df[high_conf_mask].copy()
        pseudo_df["category_clean"] = pseudo_cats

        # Majority-class gating: only augment online gambling & phishing
        safe_pseudo = pseudo_df[
            pseudo_df["category_clean"].isin(["online gambling", "phishing"])
        ].copy()

        self.augmented_samples_count = len(safe_pseudo)
        augmented_train = pd.concat([clean_train, safe_pseudo], ignore_index=True)

        return augmented_train, safe_pseudo

    def fit_augmented_and_predict(
        self,
        augmented_train: pd.DataFrame,
        predict_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """Retrains blender on augmented dataset with threshold optimization and returns predictions."""
        self.blender_augmented = HybridProbabilisticBlender(
            text_weight=self.text_weight,
            random_state=self.random_state,
        )
        self.blender_augmented.fit(augmented_train, optimize_thresholds=True)
        preds = self.blender_augmented.predict(predict_df, apply_guard=True)

        v3_df = pd.DataFrame({
            "id": predict_df["id"],
            "category": preds,
        })
        return v3_df

    def reproduce_v3(
        self,
        train_path: str = "official/training.csv",
        predict_path: str = "official/predict.csv",
        output_path: Optional[str] = "official/submission_TIFIS_TIFIS_v3.csv",
    ) -> pd.DataFrame:
        """Deterministically reproduces official Submission v3 (MD5: 42213394cb9513d4991a465f80819cd6)."""
        train_df, predict_df = load_cleaned_datasets(train_path, predict_path)

        augmented_train, _ = self.fit_base_and_pseudo_label(
            train_df,
            predict_df,
            apply_denoising=False,
        )
        v3_df = self.fit_augmented_and_predict(augmented_train, predict_df)

        if output_path is not None:
            export_submission(v3_df, output_path)

        return v3_df
