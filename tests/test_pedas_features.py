"""Unit tests for active feature engineering module (src/pedas_features.py)."""

import pytest
import numpy as np
import pandas as pd

from src.cleaner import clean_url, build_composite_text
from src.pedas_features import (
    DomainEnsembleExtractor,
    TfidfTextFeatureExtractor,
    extract_url_lexical_features,
    extract_domain_metadata_features,
)


def test_lexical_keyword_detection():
    # Test gambling keywords
    gambling_df = extract_url_lexical_features(pd.Series(["https://slot-gacor-maxwin.id/play", "http://hoki-zeus.id"]))
    assert gambling_df["has_gambling"].sum() == 2
    assert gambling_df["has_phishing"].sum() == 0

    # Test phishing keywords
    phishing_df = extract_url_lexical_features(pd.Series(["https://bca-klik-verifikasi-otp.id/login", "http://dana-hadiah.id"]))
    assert phishing_df["has_phishing"].sum() == 2
    assert phishing_df["has_gambling"].sum() == 0


def test_domain_ensemble_extractor_fit_transform():
    df = pd.DataFrame({
        "url": ["https://slot-gacor.id", "http://bca-login.id/user", "https://toko-sepatu.id"],
        "brand": ["unknown_brand", "bca", "unknown_brand"],
        "sld": ["id", "id", "id"],
        "registrar": ["pt digital registra indonesia", "unknown_registrar", "pt jc indonesia"],
        "ip": ["103.10.10.1", np.nan, "103.20.20.2"],
        "confidence_level": [100.0, 50.0, np.nan],
        "discovered": ["2026-09-15", "2026-09-10", "2026-09-01"],
        "registration_date": ["2026-09-01", "2026-08-01", "2025-01-01"],
    })
    
    extractor = DomainEnsembleExtractor()
    X = extractor.fit_transform(df)

    assert isinstance(X, pd.DataFrame)
    assert len(X) == 3
    assert not X.isna().any().any(), "Features should not contain any NaN values"
    assert "has_gambling" in X.columns
    assert "has_phishing" in X.columns
    assert "reg_pt digital registra indonesia" in X.columns


def test_tfidf_text_feature_extractor():
    texts = pd.Series([
        "url slot-gacor.id brand unknown_brand sld id registrar pt jc",
        "url bca-login.id brand bca sld id registrar unknown",
    ])
    tfidf = TfidfTextFeatureExtractor(ngram_range=(3, 4), max_features=100)
    X_tfidf = tfidf.fit_transform(texts)
    
    assert X_tfidf.shape[0] == 2
    assert X_tfidf.shape[1] > 0
