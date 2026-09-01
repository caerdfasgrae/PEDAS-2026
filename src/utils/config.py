"""Configuration and project path resolver for PeDaS 2026."""

from pathlib import Path
import os
import yaml
from typing import Dict, Any

# Root Directory (robust against local vs Colab execution)
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parent.parent.parent

# Standard Directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
BENCHMARK_DATA_DIR = DATA_DIR / "benchmark"
CONFIG_DIR = PROJECT_ROOT / "config"
MODELS_DIR = PROJECT_ROOT / "models"
SRC_DIR = PROJECT_ROOT / "src"

# Deterministic Seed for Reproducibility (Crucial for Finalist Code Verification)
RANDOM_STATE = 42

# Ensure directories exist
for d in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, BENCHMARK_DATA_DIR, CONFIG_DIR, MODELS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Default Indonesian Brands Path
BRANDS_CONFIG_PATH = CONFIG_DIR / "indonesian_brands.yaml"


def load_yaml_config(path: Path = BRANDS_CONFIG_PATH) -> Dict[str, Any]:
    """Safely loads YAML configuration file."""
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def is_colab() -> bool:
    """Detects whether code is running in a Google Colab environment."""
    try:
        import google.colab
        return True
    except ImportError:
        return False
