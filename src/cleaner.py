"""Deterministic Data Cleaner for PeDaS 2026.

Ground-truth classes (9 canonical IDADX abuse categories):
1. online gambling
2. phishing
3. other
4. spam
5. malware
6. brand
7. fakeshop
8. violence
9. piiexposure
"""

import re
from urllib.parse import unquote
import pandas as pd

CANONICAL_CLASSES = [
    "online gambling",
    "phishing",
    "other",
    "spam",
    "malware",
    "brand",
    "fakeshop",
    "violence",
    "piiexposure",
]

TYPO_MAPPING = {
    "online gamblingg": "online gambling",
    "phishingg": "phishing",
    "otherr": "other",
    "malwaree": "malware",
    "spamm": "spam",
}


def clean_category(series: pd.Series) -> pd.Series:
    """Deterministic category normalizer.
    
    1. Strips leading/trailing whitespaces.
    2. Lowercases all characters.
    3. Maps known committee-injected typos (e.g. gamblingg, phishingg) to canonical classes.
    4. Asserts that all returned labels belong strictly to the 9 canonical classes.
    """
    clean = series.astype(str).str.strip().str.lower()
    clean = clean.replace(TYPO_MAPPING)
    
    invalid = set(clean.unique()) - set(CANONICAL_CLASSES)
    if invalid:
        raise ValueError(f"Encountered unexpected non-canonical classes: {invalid}")
    
    return clean


def clean_url(url: str) -> str:
    """Normalizes URL string:
    - Decodes URL-encoded parameters (e.g., %20 to space).
    - Removes synthetic noise patterns like 'item-\\d+' seen in workshop data.
    - Strips search engine operator prefixes like 'site:'.
    - Strips whitespace.
    """
    if pd.isna(url):
        return ""
    u = str(url).strip()
    u = unquote(u)
    if u.lower().startswith("site:"):
        u = u[5:].strip()
    u = re.sub(r"item-\d+", "", u, flags=re.IGNORECASE)
    return u


def clean_brand(brand: str) -> str:
    """Semantic cleaner for brand column:
    - Replaces '-' and empty strings with 'unknown_brand'.
    - Strips whitespace.
    """
    if pd.isna(brand):
        return "unknown_brand"
    b = str(brand).strip()
    if b in ["-", "", "nan", "None"]:
        return "unknown_brand"
    return b


def build_composite_text(df: pd.DataFrame) -> pd.Series:
    """Constructs multi-field composite text representation:
    'url {clean_url} brand {clean_brand} sld {sld} registrar {registrar}'
    
    Provides rich context for character n-gram and sub-word models.
    """
    url_clean = df["url"].apply(clean_url).astype(str).str.lower()
    brand_clean = df["brand"].apply(clean_brand).astype(str).str.lower()
    sld_clean = df["sld"].fillna("unknown_sld").astype(str).str.strip().str.lower()
    reg_clean = df["registrar"].fillna("unknown_registrar").astype(str).str.strip().str.lower()
    
    composite = (
        "url " + url_clean
        + " brand " + brand_clean
        + " sld " + sld_clean
        + " registrar " + reg_clean
    )
    return composite


def load_cleaned_datasets(
    train_path: str = "official/training.csv",
    predict_path: str = "official/predict.csv",
):
    """Loads and deterministically preprocesses both training and prediction datasets."""
    train_df = pd.read_csv(train_path)
    predict_df = pd.read_csv(predict_path)
    
    train_df["category_clean"] = clean_category(train_df["category"])
    train_df["composite_text"] = build_composite_text(train_df)
    
    predict_df["composite_text"] = build_composite_text(predict_df)
    
    return train_df, predict_df
