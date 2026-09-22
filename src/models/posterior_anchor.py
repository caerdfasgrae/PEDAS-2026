"""Posterior-Based Rare-Class Anchor Policy for PeDaS 2026 (Jury-Defensible).

Replaces hardcoded row-index overrides (e.g. ``preds[1345] = "fakeshop"``) with an
auditable, evidence-driven policy. Every anchor decision records:

1. The model posterior P(y = c | x) for the target rare class.
2. A lexical evidence assessment derived from the raw URL tokens.
3. A decision: ACCEPT (posterior meets threshold), LEXICAL_ONLY (no posterior support,
   but explicit textual evidence present -> flagged as analyst prior, NOT model output),
   or REJECT.

This module does not silently relabel. If a candidate lacks posterior support, the
audit trail says so explicitly, which is what a final-round jury requires.

Design goals:
- Explainability: each decision carries the numbers that justify it.
- Non-destructive: returns both predictions and a full audit DataFrame.
- Deterministic: no randomness.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
import re
from urllib.parse import unquote

import numpy as np
import pandas as pd

from src.cleaner import CANONICAL_CLASSES


# Lexical evidence patterns for rare classes (used as a secondary, transparent signal).
LEXICAL_EVIDENCE: Dict[str, re.Pattern] = {
    "fakeshop": re.compile(
        r"(shop|toko|belanja|store|cart|checkout|katalog|olshop|belanja-online|online-shop)",
        re.IGNORECASE,
    ),
    "violence": re.compile(
        r"(senjata|senpi|pistol|teror|jihad|rakitan|bom|tawuran|pembunuhan|aniaya|begal)",
        re.IGNORECASE,
    ),
    "piiexposure": re.compile(
        r"(leak|databocor|data-bocor|breach|doxing|dump-ktp|nik-dump|database-bocor|jual-database)",
        re.IGNORECASE,
    ),
    "brand": re.compile(
        r"(^http[s]?://[a-z0-9\.\*]+\.(id|co\.id|biz\.id|my\.id|or\.id|ac\.id)/?$)",
        re.IGNORECASE,
    ),
}

# Majority-class veto markers: if present, a rare-class anchor must not override.
VETO = re.compile(
    r"(slot|gacor|maxwin|togel|casino|judi|bet|jackpot|"
    r"login|signin|verifikasi|otp|bca|bri|bni|mandiri|dana|ovo|gopay)",
    re.IGNORECASE,
)


@dataclass
class AnchorDecision:
    row_index: int
    id: str
    url: str
    target_class: str
    posterior: float
    posterior_rank: int
    threshold: float
    lexical_match: bool
    vetoed: bool
    decision: str
    rationale: str


class PosteriorAnchorPolicy:
    """Auditable rare-class anchoring based on calibrated posteriors + lexical evidence."""

    def __init__(
        self,
        posterior_threshold: float = 0.50,
        allow_lexical_only: bool = False,
    ):
        self.posterior_threshold = posterior_threshold
        self.allow_lexical_only = allow_lexical_only

    def _lexical_match(self, target: str, url: str) -> bool:
        pattern = LEXICAL_EVIDENCE.get(target)
        if pattern is None:
            return False
        u = unquote(str(url)).lower()
        return bool(pattern.search(u))

    def evaluate(
        self,
        predict_df: pd.DataFrame,
        probas: np.ndarray,
        candidates: List[Tuple[int, str]],
    ) -> List[AnchorDecision]:
        """Evaluates candidate (row_index, target_class) pairs and returns audit records."""
        decisions: List[AnchorDecision] = []
        for row_index, target in candidates:
            if row_index < 0 or row_index >= len(predict_df):
                continue
            if target not in CANONICAL_CLASSES:
                continue

            target_idx = CANONICAL_CLASSES.index(target)
            p = probas[row_index]
            posterior = float(p[target_idx])
            order = np.argsort(p)[::-1]
            rank = int(np.where(order == target_idx)[0][0]) + 1

            url = str(predict_df.iloc[row_index]["url"])
            lexical = self._lexical_match(target, url)
            vetoed = bool(VETO.search(unquote(url).lower()))
            argmax_class = CANONICAL_CLASSES[int(order[0])]

            if posterior >= self.posterior_threshold and not vetoed:
                decision = "ACCEPT"
                rationale = (
                    f"Posterior P({target}|x)={posterior:.4f} >= threshold "
                    f"{self.posterior_threshold:.2f} (argmax={argmax_class})."
                )
            elif lexical and not vetoed and self.allow_lexical_only:
                decision = "LEXICAL_ONLY"
                rationale = (
                    f"No posterior support (P({target}|x)={posterior:.4f}, argmax="
                    f"{argmax_class}), but explicit lexical evidence present. "
                    f"Applied as analyst prior, NOT model-derived."
                )
            else:
                decision = "REJECT"
                reasons = []
                if vetoed:
                    reasons.append("majority-class veto token present")
                if posterior < self.posterior_threshold:
                    reasons.append(
                        f"P({target}|x)={posterior:.4f} < threshold {self.posterior_threshold:.2f}"
                    )
                if not lexical:
                    reasons.append("no lexical evidence")
                rationale = "; ".join(reasons).capitalize() + "."

            decisions.append(AnchorDecision(
                row_index=row_index,
                id=str(predict_df.iloc[row_index].get("id", "")),
                url=url,
                target_class=target,
                posterior=posterior,
                posterior_rank=rank,
                threshold=self.posterior_threshold,
                lexical_match=lexical,
                vetoed=vetoed,
                decision=decision,
                rationale=rationale,
            ))
        return decisions

    def apply(
        self,
        predictions: List[str],
        decisions: List[AnchorDecision],
    ) -> List[str]:
        """Applies only ACCEPT / LEXICAL_ONLY decisions and returns new predictions."""
        out = list(predictions)
        for d in decisions:
            if d.decision in ("ACCEPT", "LEXICAL_ONLY"):
                out[d.row_index] = d.target_class
        return out

    @staticmethod
    def to_dataframe(decisions: List[AnchorDecision]) -> pd.DataFrame:
        return pd.DataFrame([asdict(d) for d in decisions])
