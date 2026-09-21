"""Rare Class Precision Hunter for PeDaS 2026.

Implements high-precision, explainable heuristic anchors for minority classes:
1. 'brand': PANDI Brand Protection & Trademark Squatting Monitoring pattern.
2. 'fakeshop': Fraudulent commercial storefront signatures.
3. 'violence': High-impact public safety / weapon threat signatures.
4. 'piiexposure': High-impact personal identity breach / leak signatures.

Fully auditable for final round jury defense (Juknis PeDaS 2026 Pasal 12 Butir 3).
"""

import re
from typing import Dict, List, Tuple, Any, Optional
from urllib.parse import unquote
import pandas as pd
import numpy as np


# Storefront intent keywords (excluding educational, government, and gambling terms)
RE_SHOP_INTENT = re.compile(
    r"\b(shop|toko|belanja|store|cart|checkout|katalog|olshop|fakeshop)\b",
    re.IGNORECASE,
)
RE_SHOP_EXCLUSIONS = re.compile(
    r"(workshop|tokoh|perpustakaan|perpus|jurnal|fakultas|baak|alumni|slot|judi|gacor|jackpot|cuaks|login|bca|dana|bri|mandiri)",
    re.IGNORECASE,
)

# PANDI Brand Protection Pattern (Bare root domain registered under commercial SLDs, clean, no cybercrime tokens)
RE_BRAND_ROOT = re.compile(
    r"^http://[a-zA-Z0-9\.\*]+\.(id|co\.id|biz\.id|my\.id|or\.id)/?$",
    re.IGNORECASE,
)
RE_CYBERCRIME_TOKENS = re.compile(
    r"(slot|gacor|judi|togel|maxwin|bet|casino|poker|login|signin|otp|apk|exe|payload|verifikasi)",
    re.IGNORECASE,
)

# Violence / Weapon / Terror tokens
RE_VIOLENCE_INTENT = re.compile(
    r"\b(senjata|senpi|pistol|teror|jihad|rakitan|bom|tawuran|pembunuhan|aniaya|begal)\b",
    re.IGNORECASE,
)
RE_VIOLENCE_EXCLUSIONS = re.compile(
    r"(eksekusi-riil|sita-eksekusi|analisis|polisi|kpknl)",
    re.IGNORECASE,
)

# PII Exposure / Data Breach tokens
RE_PII_INTENT = re.compile(
    r"\b(leak|databocor|data-bocor|breach|doxing|dump-ktp|nik-dump|database-bocor|jual-database)\b",
    re.IGNORECASE,
)


class RareClassHunter:
    """High-precision heuristic detector for rare and minority classes."""

    def __init__(
        self,
        enable_brand: bool = True,
        enable_fakeshop: bool = True,
        enable_violence: bool = False,
        enable_piiexposure: bool = False,
    ):
        self.enable_brand = enable_brand
        self.enable_fakeshop = enable_fakeshop
        self.enable_violence = enable_violence
        self.enable_piiexposure = enable_piiexposure

    def detect(
        self,
        df: pd.DataFrame,
        current_predictions: List[str],
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """Applies high-precision precision anchors to override or reinforce predictions."""
        refined_preds = list(current_predictions)
        audit_trail: List[Dict[str, Any]] = []

        for idx, row in df.reset_index(drop=True).iterrows():
            url_str = str(row.get("url", "")).strip()
            brand_val = str(row.get("brand", "")).strip().lower()
            current_p = current_predictions[idx]
            new_p = current_p
            rule_applied = None

            u_clean = unquote(url_str).lower()
            has_crime = bool(RE_CYBERCRIME_TOKENS.search(u_clean))

            # 1. Fakeshop Precision Anchor
            if self.enable_fakeshop and not has_crime:
                if RE_SHOP_INTENT.search(u_clean) and not RE_SHOP_EXCLUSIONS.search(u_clean):
                    if current_p not in ["phishing", "online gambling", "malware"]:
                        new_p = "fakeshop"
                        rule_applied = "RareHunter: High-Precision Storefront Lexical Anchor"

            # 2. Brand Protection Squatting Anchor
            if self.enable_brand and rule_applied is None:
                is_bare = bool(RE_BRAND_ROOT.match(url_str))
                is_brand_nan = brand_val in ["nan", "-", "none", ""]
                if is_bare and is_brand_nan and not has_crime:
                    # Bare clean domain under Indonesian TLD with no path and no cybercrime keywords
                    if current_p in ["other", "online gambling", "spam"]:
                        new_p = "brand"
                        rule_applied = "RareHunter: PANDI Brand Protection Squatting Anchor"

            # 3. Violence Precision Anchor (if enabled)
            if self.enable_violence and rule_applied is None:
                if RE_VIOLENCE_INTENT.search(u_clean) and not RE_VIOLENCE_EXCLUSIONS.search(u_clean):
                    new_p = "violence"
                    rule_applied = "RareHunter: Violence/Threat Lexical Anchor"

            # 4. PII Exposure Precision Anchor (if enabled)
            if self.enable_piiexposure and rule_applied is None:
                if RE_PII_INTENT.search(u_clean):
                    new_p = "piiexposure"
                    rule_applied = "RareHunter: PII Leak / Breach Lexical Anchor"

            if rule_applied is not None:
                refined_preds[idx] = new_p
                audit_trail.append({
                    "row_index": idx,
                    "url": url_str,
                    "previous_prediction": current_p,
                    "refined_prediction": new_p,
                    "rule": rule_applied,
                })

        return refined_preds, audit_trail
