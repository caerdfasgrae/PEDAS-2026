#!/usr/bin/env python
"""PeDaS 2026 - CLI Runner: Submisi 2 (Rare-Class Asymmetric Hunter).

Deterministically generates and verifies official/submission_TIFIS_TIFIS_v2.csv
with target MD5 checksum: 1a1d5d83b8388d086e81151545868a0e.
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
from src.alternatives.rare_class_hunter import RareClassHunter
from src.submission import validate_submission, export_submission
from scripts.evaluate_official import read_csv, validate_rows, summarize

TARGET_V2_MD5 = "1a1d5d83b8388d086e81151545868a0e"


def main():
    parser = argparse.ArgumentParser(
        description="PeDaS 2026: Submisi 2 (Rare-Class Asymmetric Hunter) Runner"
    )
    parser.add_argument(
        "--sub1",
        default="official/submission_TIFIS_TIFIS.csv",
        help="Path to Submisi 1 Golden Anchor CSV",
    )
    parser.add_argument(
        "--predict",
        default="official/predict.csv",
        help="Path to official predict.csv",
    )
    parser.add_argument(
        "--output",
        default="official/submission_TIFIS_TIFIS_v2.csv",
        help="Path to output submission CSV",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify existing file without overwriting",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("  PeDaS 2026: RUNNER SUBMISI 2 (RARE-CLASS ASYMMETRIC HUNTER)")
    print("=" * 70)
    start_time = time.time()

    out_path = REPO_ROOT / args.output

    if not args.verify_only:
        sub1_file = REPO_ROOT / args.sub1
        predict_file = REPO_ROOT / args.predict

        if not sub1_file.exists():
            print(f"[ERROR] Anchor file missing: {sub1_file}")
            sys.exit(1)
        if not predict_file.exists():
            print(f"[ERROR] Predict file missing: {predict_file}")
            sys.exit(1)

        print(f"[*] Loading Submisi 1 Anchor: {sub1_file}")
        sub1_df = pd.read_csv(sub1_file)
        predict_df = pd.read_csv(predict_file)

        hunter = RareClassHunter()
        v2_df = hunter.hunt_rare_classes(predict_df, sub1_df)

        report = hunter.get_disambiguation_report()
        print(f"[*] Disambiguated {len(report)} candidate(s):")
        for _, r in report.iterrows():
            print(f"    - ID: {r['id']} | Prev: {r['previous_category']} -> New: {r['new_category']}")
            print(f"      URL: {r['url']}")
            print(f"      SLD: {r['sld']} | Reason: {r['reason']}")

        # Validate schema before export
        validate_submission(v2_df)
        export_submission(v2_df, str(out_path))
        print(f"[OK] Successfully exported: {out_path}")

    # Read and verify hash
    with open(out_path, "rb") as f:
        file_bytes = f.read()
        file_md5 = hashlib.md5(file_bytes).hexdigest()

    print(f"\n[*] Output File    : {out_path.name}")
    print(f"[*] MD5 Checksum   : {file_md5}")
    print(f"[*] Target MD5     : {TARGET_V2_MD5}")

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

    if file_md5 == TARGET_V2_MD5 and summary["valid"] == 1500 and summary["invalid"] == 0:
        print("\n[SUCCESS] Submisi 2 reproduction & verification 100% SUCCESSFUL!")
    else:
        print("\n[ERROR] Verification mismatch!")
        sys.exit(1)


if __name__ == "__main__":
    main()
