"""Unit test for 1-Click Final Pipeline CLI Runner."""

import sys
import subprocess
from pathlib import Path
import pandas as pd
import pytest

from src.cleaner import CANONICAL_CLASSES
from src.submission import validate_submission


def test_cli_pipeline_execution(tmp_path):
    output_csv = tmp_path / "test_cli_submission.csv"
    
    cmd = [
        sys.executable,
        "run_pedas_pipeline.py",
        "--train", "official/training.csv",
        "--predict", "official/predict.csv",
        "--output", str(output_csv),
        "--seed", "2026",
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"CLI runner failed with error:\n{result.stderr}\n{result.stdout}"
    
    assert output_csv.exists(), "Output submission file was not created"
    
    df = pd.read_csv(output_csv)
    validate_submission(df)
    assert len(df) == 1500
    assert list(df.columns) == ["id", "category"]
    assert set(df["category"].unique()).issubset(set(CANONICAL_CLASSES))
