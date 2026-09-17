"""Alternative and Competitive Portfolio Modules for PeDaS 2026.

Contains strictly isolated modules for:
1. DataCentricDenoiser: Training data de-noising & conflict resolution (Pasal 3.5 & Pasal 12.3).
2. RareClassHunter: Rare-class asymmetric upside maximization (Submisi 2).
3. AdaptiveHedgePipeline: Semi-supervised self-training domain adaptation (Submisi 3).
"""

from src.alternatives.data_centric_denoiser import DataCentricDenoiser
from src.alternatives.rare_class_hunter import RareClassHunter
from src.alternatives.adaptive_hedge_pipeline import AdaptiveHedgePipeline

__all__ = [
    "DataCentricDenoiser",
    "RareClassHunter",
    "AdaptiveHedgePipeline",
]
