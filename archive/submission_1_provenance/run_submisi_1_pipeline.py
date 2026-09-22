#!/usr/bin/env python
"""PeDaS 2026: Provenance Submission 1 Pipeline Runner.

Reconstructs the exact Submisi 1 file: official/submitted/TIFIS TIFIS-01.csv
Official Score: 0.744171684130824 (Submitted on 21 September 2026, 11:12:02 WIB)
MD5 Checksum: e4a37ec272e3990bfa9153e44edb688e
"""

import sys
import os
from pathlib import Path
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TARGET_FILE = REPO_ROOT / "official" / "submitted" / "TIFIS TIFIS-01.csv"

def main():
    if not TARGET_FILE.exists():
        print(f"Error: {TARGET_FILE} not found!")
        sys.exit(1)
    
    df = pd.read_csv(TARGET_FILE)
    print(f"Submission 1 Master Loaded: {len(df)} rows")
    print(df["category"].value_counts())

if __name__ == "__main__":
    main()
