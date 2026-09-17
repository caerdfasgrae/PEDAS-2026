"""Unit tests for isolated alternative modules in src/alternatives/."""

import hashlib
from pathlib import Path
import pandas as pd
import pytest

from src.cleaner import CANONICAL_CLASSES
from src.alternatives.data_centric_denoiser import DataCentricDenoiser
from src.alternatives.rare_class_hunter import RareClassHunter
from src.alternatives.adaptive_hedge_pipeline import AdaptiveHedgePipeline

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_protected_files_invariance():
    """R2 Invariance: Asserts that protected core files maintain exact MD5 checksums."""
    protected = {
        "src/models/hybrid_blender.py": "f09b57c8768c206ed2cfee02b920c3cc",
        "run_pedas_pipeline.py": "7e839b15852507cbc39ca95935020505",
        "official/submission_TIFIS_TIFIS.csv": "ebd39c0c00675b8cae481251b6da23e5",
    }
    for rel_path, expected_md5 in protected.items():
        full_path = REPO_ROOT / rel_path
        assert full_path.exists(), f"Protected file missing: {rel_path}"
        with open(full_path, "rb") as f:
            actual_md5 = hashlib.md5(f.read()).hexdigest()
        assert actual_md5 == expected_md5, f"Checksum violation in {rel_path}: {actual_md5} != {expected_md5}"


def test_data_centric_denoiser_noise_analysis():
    """Verifies that DataCentricDenoiser accurately detects empirical noise patterns."""
    train_path = REPO_ROOT / "official" / "training.csv"
    train_df = pd.read_csv(train_path)

    denoiser = DataCentricDenoiser()
    audit = denoiser.analyze_noise(train_df)

    assert audit["total_rows"] == 8400
    assert audit["exact_duplicate_rows"] == 110
    assert audit["conflicting_urls_count"] == 118
    assert audit["conflicting_rows_total"] == 584
    assert audit["asterisk_collision_rate"] == 1.0
    assert audit["majority_resolvable_count"] == 34
    assert audit["tie_count"] == 84


def test_data_centric_denoiser_fit_transform():
    """Verifies end-to-end cleaning and zero residual conflicts."""
    train_path = REPO_ROOT / "official" / "training.csv"
    train_df = pd.read_csv(train_path)

    denoiser = DataCentricDenoiser()
    cleaned_df = denoiser.fit_transform(train_df, drop_exact_duplicates=True, conflict_strategy="harmonize")

    assert len(cleaned_df) == 8400 - 110
    # Zero remaining conflicts
    conflict_check = cleaned_df.groupby("url")["category_clean"].nunique()
    assert (conflict_check > 1).sum() == 0

    # All classes belong to canonical 9 classes
    assert set(cleaned_df["category_clean"].unique()).issubset(set(CANONICAL_CLASSES))

    # Changelog generated
    cl = denoiser.get_changelog()
    assert len(cl) == 118


def test_rare_class_hunter_candidate_filtering():
    """Verifies precision filtering for rare-class fakeshop detection."""
    hunter = RareClassHunter()

    # Valid candidate on commercial SLD
    is_cand, reason = hunter.is_fakeshop_candidate("http://global-shop.*****.biz.id/", "biz.id")
    assert is_cand is True

    # Invalid due to non-commercial SLD (e.g. go.id)
    is_cand, reason = hunter.is_fakeshop_candidate("http://global-shop.*****.go.id/", "go.id")
    assert is_cand is False
    assert "Non-commercial SLD" in reason

    # Invalid due to exclusion stem (e.g. workshop alongside shop)
    is_cand, reason = hunter.is_fakeshop_candidate("http://shop-workshop.*****.biz.id/", "biz.id")
    assert is_cand is False
    assert "exclusion stem" in reason

    # Invalid due to gambling defacement
    is_cand, reason = hunter.is_fakeshop_candidate("http://shop-slot-gacor.*****.biz.id/", "biz.id")
    assert is_cand is False
    assert "gambling" in reason

    # Invalid due to phishing credential harvesting
    is_cand, reason = hunter.is_fakeshop_candidate("http://shop-login-otp-bca.*****.biz.id/", "biz.id")
    assert is_cand is False
    assert "phishing" in reason


def test_rare_class_hunter_v2_reproduction():
    """Verifies that RareClassHunter exactly reproduces official Submission v2."""
    hunter = RareClassHunter()
    v2_df = hunter.reproduce_v2(output_path=None)

    assert len(v2_df) == 1500
    assert list(v2_df.columns) == ["id", "category"]
    assert "fakeshop" in v2_df["category"].values
    assert (v2_df["category"] == "fakeshop").sum() == 1


def test_adaptive_hedge_structure():
    """Verifies basic structure and parameters of AdaptiveHedgePipeline."""
    pipeline = AdaptiveHedgePipeline(confidence_threshold=0.98, random_state=2026)
    assert pipeline.confidence_threshold == 0.98
    assert pipeline.random_state == 2026
