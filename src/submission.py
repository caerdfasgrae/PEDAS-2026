"""Submission Generator & Validator for PeDaS 2026.

Enforces zero-defect submission files matching official/submission-template.csv.
"""

from pathlib import Path
import pandas as pd
from src.cleaner import CANONICAL_CLASSES


def validate_submission(
    submission_df: pd.DataFrame,
    template_path: str = "official/submission-template.csv",
    predict_path: str = "official/predict.csv",
) -> None:
    """Validates submission DataFrame against official rules:
    
    1. Exactly 1,500 rows and 2 columns.
    2. Column names must be ['id', 'category'].
    3. 'id' values must match predict.csv exactly in sequence and content.
    4. No null, NaN, or empty string values in any column.
    5. All 'category' predictions must belong to CANONICAL_CLASSES.
    """
    predict_df = pd.read_csv(predict_path)
    template_df = pd.read_csv(template_path)
    
    if submission_df.shape != (1500, 2):
        raise ValueError(
            f"Invalid shape: Expected (1500, 2), got {submission_df.shape}"
        )
    
    if list(submission_df.columns) != ["id", "category"]:
        raise ValueError(
            f"Invalid columns: Expected ['id', 'category'], got {list(submission_df.columns)}"
        )
    
    if not (submission_df["id"].values == predict_df["id"].values).all():
        raise ValueError("ID column sequence does not match official/predict.csv exactly!")
    
    null_counts = submission_df.isnull().sum()
    if null_counts.sum() > 0:
        raise ValueError(f"Submission contains null values:\n{null_counts}")
    
    empty_strings = (submission_df["category"].astype(str).str.strip() == "").sum()
    if empty_strings > 0:
        raise ValueError(f"Submission contains {empty_strings} empty string categories!")
    
    invalid_classes = set(submission_df["category"].unique()) - set(CANONICAL_CLASSES)
    if invalid_classes:
        raise ValueError(f"Submission contains invalid class labels: {invalid_classes}")


def export_submission(
    submission_df: pd.DataFrame,
    output_path: str,
    template_path: str = "official/submission-template.csv",
    predict_path: str = "official/predict.csv",
) -> Path:
    """Validates and writes submission CSV file.
    
    Returns the Path to the verified submission file.
    """
    validate_submission(
        submission_df,
        template_path=template_path,
        predict_path=predict_path,
    )
    
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    submission_df.to_csv(out, index=False, encoding="utf-8")
    
    # Re-read and re-validate exported file directly from disk
    reloaded = pd.read_csv(out)
    validate_submission(reloaded, template_path=template_path, predict_path=predict_path)
    
    return out
