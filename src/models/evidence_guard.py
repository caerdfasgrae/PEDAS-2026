"""Evidence Guard & Anti-False-Positive Filter for PeDaS 2026.

Ensures that rare class threshold shifts (e.g. fakeshop, violence, piiexposure)
never override samples that contain explicit high-confidence markers of
online gambling or phishing (e.g. slot, gacor, maxwin, login, verifikasi, bca).

Prevents heuristic hallucinations and protects majority class precision.
"""

import re
from urllib.parse import unquote
from typing import List, Tuple
import numpy as np
import pandas as pd


# High-confidence indicators for online gambling
RE_STRICT_GAMBLING = re.compile(
    r"(slot|gacor|maxwin|zeus|togel|pkv|depo|olympus|judi|casino|bet|pragmatic|jackpot|hoki|sbobet|scatter|toto|sensational|freebet|4d|poker|domino)",
    re.I,
)

# High-confidence indicators for phishing
RE_STRICT_PHISHING = re.compile(
    r"(login|signin|sign-in|verifikasi|otp|bca|bri|bni|mandiri|dana|ovo|gopay|hadiah|giveaway|bansos|kemensos|pulsa|claim|voucher|confirmaccount|2fa)",
    re.I,
)

# High-confidence indicators for malware
RE_STRICT_MALWARE = re.compile(
    r"(\.apk|\.exe|\.zip|\.rar|download|install|mediafire|dropbox|setup|payload)",
    re.I,
)


class EvidenceGuard:
    """Guards against false-positive overrides on minority classes.
    
    Checks raw URL content for unmistakable majority markers. If present, suppresses
    minority class threshold shifts and restores majority classification.
    """

    def __init__(self, class_names: List[str]):
        self.class_names = class_names
        self.gambling_idx = class_names.index("online gambling")
        self.phishing_idx = class_names.index("phishing")
        self.malware_idx = class_names.index("malware")

    def filter_predictions(
        self,
        pred_indices: np.ndarray,
        scores: np.ndarray,
        raw_urls: pd.Series,
    ) -> np.ndarray:
        """Applies evidence guard to predicted class indices.
        
        If a sample is predicted as a rare class (e.g. fakeshop, violence, piiexposure)
        but contains strict markers of gambling or phishing, forces the prediction
        to the legitimate majority class supported by evidence.
        """
        filtered = pred_indices.copy()
        
        rare_classes = {"fakeshop", "violence", "piiexposure"}
        rare_indices = {self.class_names.index(c) for c in rare_classes if c in self.class_names}
        
        for i, (pred_idx, url) in enumerate(zip(pred_indices, raw_urls)):
            if pred_idx in rare_indices:
                u = unquote(str(url)).lower()
                has_gambling = bool(RE_STRICT_GAMBLING.search(u))
                has_phishing = bool(RE_STRICT_PHISHING.search(u))
                has_malware = bool(RE_STRICT_MALWARE.search(u))
                
                if has_gambling:
                    filtered[i] = self.gambling_idx
                elif has_phishing:
                    filtered[i] = self.phishing_idx
                elif has_malware:
                    filtered[i] = self.malware_idx
                    
        return filtered
