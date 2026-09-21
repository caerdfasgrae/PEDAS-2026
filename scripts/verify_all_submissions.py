#!/usr/bin/env python
"""Verify all official submissions against official rules."""

import sys
import hashlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.evaluate_official import read_csv, validate_rows, summarize

template_rows = read_csv(str(REPO_ROOT / "official" / "submission-template.csv"))
expected_ids = {r["id"] for r in template_rows if r["id"]}

submissions = [
    REPO_ROOT / "official" / "TIFIS TIFIS-01.csv",
    REPO_ROOT / "official" / "TIFIS TIFIS-02.csv",
    REPO_ROOT / "official" / "TIFIS TIFIS-03.csv",
    REPO_ROOT / "official" / "submission_TIFIS_TIFIS.csv",
    REPO_ROOT / "official" / "submission_TIFIS_TIFIS_v2.csv",
    REPO_ROOT / "official" / "submission_TIFIS_TIFIS_v3.csv",
]

print("=" * 65)
print("  OFFICIAL EVALUATION SENSOR AUDIT (3X SUBMISSION PORTFOLIO)")
print("=" * 65)

all_passed = True
for sub_path in submissions:
    rows = read_csv(str(sub_path))
    validate_rows(rows, expected_ids)
    summary = summarize(rows)
    
    with open(sub_path, "rb") as f:
        md5 = hashlib.md5(f.read()).hexdigest()
        
    print(f"\nFile: {sub_path.name}")
    print(f"  MD5 Checksum : {md5}")
    print(f"  Total Read   : {summary['read']}")
    print(f"  Valid Rows   : {summary['valid']}")
    print(f"  Invalid Rows : {summary['invalid']}")
    
    if summary["valid"] == 1500 and summary["invalid"] == 0:
        print("  -> Sensor Status: PASSED (100% Valid, 0 Errors)")
    else:
        print(f"  -> Sensor Status: FAILED ({summary['invalid']} errors)")
        all_passed = False

print("\n" + "=" * 65)
if all_passed:
    print("[SUCCESS] All 3 submissions are 100% compliant with PANDI evaluation rules.")
else:
    print("[ERROR] One or more submissions failed validation!")
    sys.exit(1)
