#!/usr/bin/env python
"""PeDaS 2026 - CLI Runner: Submisi 3 (Data-Centric & Adaptive Hedge).

Deterministically generates and verifies official/submission_TIFIS_TIFIS_v3.csv
with target MD5 checksum: 42213394cb9513d4991a465f80819cd6.
"""

import sys
import os
import argparse
import hashlib
import time
from pathlib import Path

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pandas as pd
from src.alternatives.adaptive_hedge_pipeline import AdaptiveHedgePipeline
from src.cleaner import load_cleaned_datasets
from src.submission import validate_submission, export_submission
from scripts.evaluate_official import read_csv, validate_rows, summarize

TARGET_V3_MD5 = "42213394cb9513d4991a465f80819cd6"


def main():
    parser = argparse.ArgumentParser(
        description="PeDaS 2026: Submisi 3 (Data-Centric & Adaptive Hedge) Runner"
    )
    parser.add_argument(
        "--train",
        default="official/training.csv",
        help="Path to training CSV",
    )
    parser.add_argument(
        "--predict",
        default="official/predict.csv",
        help="Path to predict CSV",
    )
    parser.add_argument(
        "--output",
        default="official/submission_TIFIS_TIFIS_v3.csv",
        help="Path to output submission CSV",
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.98,
        help="Confidence threshold for pseudo-labeling (default: 0.98)",
    )
    parser.add_argument(
        "--denoise",
        action="store_true",
        help="Optionally apply data-centric de-noising before training",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify existing file without retraining",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("  PeDaS 2026: RUNNER SUBMISI 3 (DATA-CENTRIC & ADAPTIVE HEDGE)")
    print("=" * 70)
    start_time = time.time()

    out_path = REPO_ROOT / args.output

    if not args.verify_only:
        train_file = REPO_ROOT / args.train
        predict_file = REPO_ROOT / args.predict

        if not train_file.exists():
            print(f"[ERROR] Train file missing: {train_file}")
            sys.exit(1)
        if not predict_file.exists():
            print(f"[ERROR] Predict file missing: {predict_file}")
            sys.exit(1)

        print(f"[*] Loading datasets: train={train_file.name}, predict={predict_file.name}")
        train_df, predict_df = load_cleaned_datasets(str(train_file), str(predict_file))

        pipeline = AdaptiveHedgePipeline(
            confidence_threshold=args.confidence,
            random_state=2026,
        )

        print(f"[*] Extracting high-confidence pseudo-labels (P >= {args.confidence})...")
        augmented_train, safe_pseudo = pipeline.fit_base_and_pseudo_label(
            train_df,
            predict_df,
            apply_denoising=args.denoise,
        )
        print(f"[*] Augmented training set with {len(safe_pseudo)} samples (Total: {len(augmented_train):,} rows)")

        print("[*] Retraining Hybrid Blender on augmented distribution...")
        v3_df = pipeline.fit_augmented_and_predict(augmented_train, predict_df)

        validate_submission(v3_df)
        export_submission(v3_df, str(out_path))
        print(f"[OK] Successfully exported: {out_path}")

    # Read and verify hash
    with open(out_path, "rb") as f:
        file_bytes = f.read()
        file_md5 = hashlib.md5(file_bytes).hexdigest()

    print(f"\n[*] Output File    : {out_path.name}")
    print(f"[*] MD5 Checksum   : {file_md5}")
    print(f"[*] Target MD5     : {TARGET_V3_MD5}")

    # Panitia sensor validation
    template_path = REPO_ROOT / "official" / "submission-template.csv"
    template_rows = read_csv(str(template_path))
    expected_ids = {r["id"] for r in template_rows if r["id"]}
    rows = read_csv(str(out_path))
    validate_rows(rows, expected_ids)
    summary = summarize(rows)

    print(f"[*] Sensor Read    : {summary['read']}")
    print(f"[*] Valid Rows     : {summary['valid']}")
    print(f"[*] Invalid Rows   : {summary['invalid']}")

    elapsed = time.time() - start_time
    print(f"[*] Runtime        : {elapsed:.2f}s (SLA < 45s: {'PASSED' if elapsed < 45 else 'FAILED'})")

    if file_md5 == TARGET_V3_MD5 and summary["valid"] == 1500 and summary["invalid"] == 0:
        print("\n[SUCCESS] Submisi 3 reproduction & verification 100% SUCCESSFUL!")
    else:
        print("\n[ERROR] Verification mismatch!")
        sys.exit(1)


if __name__ == "__main__":
    main()
