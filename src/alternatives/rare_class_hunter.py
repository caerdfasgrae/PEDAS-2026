"""PeDaS 2026 - Rare-Class Asymmetric Hunter (Submisi 2).

Authoritative Module for Submisi 2:
In unweighted Macro-F1 (Pasal 7 Sub-bab 7.1), each of the 9 classes carries equal weight (1/9 = 11.11%).
Detecting even 1 true positive in an ultra-rare class (e.g. fakeshop, which has only 5 samples in
training) produces an asymmetric score surge (+0.08 to +0.11 Macro-F1), provided false positives
are strictly constrained by high-precision domain and anti-defacement guards.

Key Architectural Components:
1. Commercial SLD Filter: Constrains fakeshop search to commercial top-level/second-level domains
   ('.biz.id', '.my.id', '.id', '.co.id') where registered commercial retail operations reside.
2. Word-Boundary Shopping Lexical Intent: Matches clean ecommerce keywords (shop, store, toko, etc.)
   while rejecting academic/institutional false positive stems (workshop, tokoh, perpustakaan, etc.).
3. Negative Phishing Credential Guard: Rejects URLs containing banking, wallet, or credential-harvesting
   tokens (otp, login, verifikasi, rekening, saldo, bca, bri, dana, etc.).
4. Negative Gambling Guard: Rejects URLs containing gambling and slot tokens.
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from urllib.parse import unquote
from pathlib import Path
import numpy as np
import pandas as pd

from src.cleaner import CANONICAL_CLASSES, load_cleaned_datasets
from src.pedas_features import RE_GAMBLING, RE_PHISHING
from src.submission import validate_submission, export_submission

# Precise word-boundary regex for ecommerce intent
RE_CLEAN_SHOP = re.compile(
    r"\b(shop|toko|belanja|store|cart|checkout|fakeshop|katalog|sale|diskon|promo)\b",
    re.IGNORECASE,
)
# Institutional & false positive exclusion terms
RE_SHOP_EXCLUSIONS = re.compile(
    r"(workshop|protokol|tokoh|perpustakaan|perpus|jurnal|fakultas|baak|alumni)",
    re.IGNORECASE,
)

# Credential harvesting & financial phishing tokens
PHISH_CREDENTIAL_TOKENS = [
    "login", "signin", "verifikasi", "otp", "rekening", "saldo",
    "bca", "bri", "mandiri", "bni", "cimb", "dana", "ovo", "gopay"
]

COMMERCIAL_SLDS = {"biz.id", "my.id", "id", "co.id"}


class RareClassHunter:
    """Asymmetric detector for ultra-rare competition categories."""

    def __init__(
        self,
        commercial_slds: Optional[set] = None,
        target_rare_class: str = "fakeshop",
    ):
        self.commercial_slds = commercial_slds or COMMERCIAL_SLDS
        self.target_rare_class = target_rare_class
        self.disambiguated_records: List[Dict[str, Any]] = []

    def is_fakeshop_candidate(self, url: str, sld: str) -> Tuple[bool, str]:
        """Evaluates whether a given URL meets strict fakeshop disambiguation criteria."""
        u = unquote(str(url)).lower()
        sld_str = str(sld).strip().lower()

        # Check commercial SLD constraint
        if sld_str not in self.commercial_slds:
            return False, f"Non-commercial SLD: {sld_str}"

        # Check shopping lexical intent
        if not bool(RE_CLEAN_SHOP.search(u)):
            return False, "No ecommerce keywords found"

        # Check exclusion stems
        if bool(RE_SHOP_EXCLUSIONS.search(u)):
            return False, "Matched false-positive exclusion stem"

        # Check gambling guard
        if bool(RE_GAMBLING.search(u)) or "judi" in u:
            return False, "Matched gambling keywords (defacement/compromised site)"

        # Check phishing credential guard
        if any(token in u for token in PHISH_CREDENTIAL_TOKENS):
            return False, "Matched credential harvesting/banking phishing tokens"

        return True, "Valid high-precision commercial fakeshop candidate"

    def hunt_rare_classes(
        self,
        predict_df: pd.DataFrame,
        base_predictions_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """Applies asymmetric rare-class hunting onto base submission predictions.

        Parameters
        ----------
        predict_df : pd.DataFrame
            Official test/predict dataset containing columns ['id', 'url', 'sld', ...].
        base_predictions_df : pd.DataFrame
            Base predictions DataFrame (e.g. Submisi 1 Golden Anchor) with ['id', 'category'].

        Returns
        -------
        pd.DataFrame
            New DataFrame with rare-class candidates disambiguated to 'fakeshop'.
        """
        output_df = base_predictions_df.copy()
        self.disambiguated_records.clear()

        # Index base predictions by ID for fast safe lookup
        pred_map = dict(zip(output_df["id"], output_df["category"]))

        for _, row in predict_df.iterrows():
            p_id = row["id"]
            current_cat = pred_map.get(p_id, "")
            url = row["url"]
            sld = row["sld"]

            is_candidate, reason = self.is_fakeshop_candidate(url, sld)
            if is_candidate:
                # Disambiguate if previously classified as brand, phishing, or other
                if current_cat in {"brand", "phishing", "other"}:
                    pred_map[p_id] = self.target_rare_class
                    self.disambiguated_records.append({
                        "id": p_id,
                        "url": url,
                        "sld": sld,
                        "previous_category": current_cat,
                        "new_category": self.target_rare_class,
                        "reason": reason,
                    })

        output_df["category"] = output_df["id"].map(pred_map)
        return output_df

    def get_disambiguation_report(self) -> pd.DataFrame:
        """Returns structured DataFrame of all disambiguated samples."""
        return pd.DataFrame(self.disambiguated_records)

    def reproduce_v2(
        self,
        sub1_path: str = "official/submission_TIFIS_TIFIS.csv",
        predict_path: str = "official/predict.csv",
        output_path: Optional[str] = "official/submission_TIFIS_TIFIS_v2.csv",
    ) -> pd.DataFrame:
        """Deterministically reproduces official Submission v2 (MD5: 1a1d5d83b8388d086e81151545868a0e)."""
        if sub1_path == "official/submission_TIFIS_TIFIS.csv" and not Path(sub1_path).exists():
            sub1_path = "official/TIFIS TIFIS-01.csv"
        sub1_df = pd.read_csv(sub1_path)
        predict_df = pd.read_csv(predict_path)

        v2_df = self.hunt_rare_classes(predict_df, sub1_df)

        if output_path is not None:
            export_submission(v2_df, output_path)

        return v2_df
