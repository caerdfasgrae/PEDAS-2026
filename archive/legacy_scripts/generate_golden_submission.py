"""Golden Submission Generator for PeDaS 2026.

Trains the Explainable Hybrid Probabilistic Blender on 100% of training data (8,400 rows),
performs inference on official/predict.csv (1,500 rows), and validates against
official/submission-template.csv with zero defects.
"""

import sys
import hashlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np

from src.cleaner import load_cleaned_datasets, CANONICAL_CLASSES
from src.models.hybrid_blender import HybridProbabilisticBlender
from src.submission import export_submission, validate_submission


def generate_golden_submission(
    train_path: str = "official/training.csv",
    predict_path: str = "official/predict.csv",
    output_path: str = "official/golden_submission_pedas2026.csv",
    random_state: int = 2026,
    text_weight: float = 0.60,
):
    print("=" * 65)
    print("PE-DAS 2026: GOLDEN SUBMISSION GENERATION")
    print("=" * 65)

    print(f"Loading datasets: train={train_path}, predict={predict_path}...")
    train_df, predict_df = load_cleaned_datasets(train_path=train_path, predict_path=predict_path)

    print(f"Training set: {len(train_df)} rows")
    print(f"Predict set : {len(predict_df)} rows")

    # Train full Hybrid Blender on 100% training data
    print("\nFitting full Hybrid Blender (LinearSVC + LightGBM)...")
    blender = HybridProbabilisticBlender(
        text_weight=text_weight,
        random_state=random_state,
    )
    blender.fit(train_df, optimize_thresholds=True)

    print("\nRunning inference on predict dataset...")
    predictions = blender.predict(predict_df, apply_guard=True)

    # Format submission
    sub_df = pd.DataFrame({
        "id": predict_df["id"],
        "category": predictions,
    })

    # Validate against official schema constraints
    print("\nValidating submission against official criteria...")
    validate_submission(sub_df)
    print("--> All validation checks PASSED: (1500 rows, 2 columns, 0 NaNs, canonical classes).")

    # Export
    export_submission(sub_df, output_path)
    print(f"\nSaved golden submission to: {output_path}")

    # Compute MD5 Checksum
    with open(output_path, "rb") as f:
        md5_hash = hashlib.md5(f.read()).hexdigest()
    print(f"MD5 Checksum: {md5_hash}")

    # Display Category Distribution
    print("\n" + "-" * 40)
    print("PREDICTED CATEGORY DISTRIBUTION:")
    print("-" * 40)
    dist = sub_df["category"].value_counts()
    for cat, cnt in dist.items():
        pct = (cnt / len(sub_df)) * 100
        print(f"  {cat:18s}: {cnt:4d} ({pct:5.2f}%)")
    print("-" * 40)
    print(f"  TOTAL             : {len(sub_df):4d} (100.00%)")

    return sub_df


if __name__ == "__main__":
    generate_golden_submission()
