"""Unit tests for PeDaS 2026 feature extraction and modeling framework."""

import pytest
import pandas as pd
from src.features.lexical import extract_lexical_features, calculate_shannon_entropy
from src.features.domain_brand import IndonesianBrandDetector
from src.features.extractor import PhishingFeatureExtractor
from src.models.metrics import calculate_classification_metrics


def test_shannon_entropy():
    # Empty string has 0 entropy
    assert calculate_shannon_entropy("") == 0.0
    # Single repeated char has 0 entropy
    assert calculate_shannon_entropy("aaaaaa") == 0.0
    # Random characters have higher entropy
    low_entropy = calculate_shannon_entropy("google")
    high_entropy = calculate_shannon_entropy("x8q9w2z1m5v7")
    assert high_entropy > low_entropy


def test_lexical_features_bca_phishing_vs_legit():
    # Sample from PANDI presentation slide 5
    phish_url = "http://bca-secure-login.id/verify"
    legit_url = "https://bank.klikbca.com"

    phish_feats = extract_lexical_features(phish_url)
    legit_feats = extract_lexical_features(legit_url)

    # Phishing uses HTTP, legit uses HTTPS
    assert phish_feats["is_https"] == 0
    assert legit_feats["is_https"] == 1

    # Phishing has hyphens in domain, legit does not
    assert phish_feats["hyphen_count_domain"] >= 2
    assert legit_feats["hyphen_count_domain"] == 0

    # Phishing has suspicious tokens ('secure', 'login', 'verify')
    assert phish_feats["suspicious_token_count"] >= 2
    assert phish_feats["has_suspicious_token"] == 1

    # Both recognize .id ecosystem
    assert phish_feats["is_id_tld"] == 1


def test_ip_address_host_detection():
    ip_url = "http://192.168.1.100:8080/bca/login.php"
    feats = extract_lexical_features(ip_url)
    assert feats["is_ip"] == 1
    assert feats["has_non_standard_port"] == 1


def test_indonesian_brand_detector():
    detector = IndonesianBrandDetector()

    # Legitimate BCA domain
    legit_res = detector.detect("https://bank.klikbca.com")
    assert legit_res["brand_in_domain"] == 1
    assert legit_res["is_unauthorized_brand_domain"] == 0
    assert legit_res["is_brand_combosquatting"] == 0

    # Phishing BCA combosquatting domain
    phish_res = detector.detect("http://bca-secure-login.id/verify")
    assert phish_res["brand_in_domain"] == 1
    assert phish_res["is_unauthorized_brand_domain"] == 1
    assert phish_res["is_brand_combosquatting"] == 1

    # Phishing DANA Kaget
    dana_phish = detector.detect("http://dana-kaget-saldo-gratis-100rb.biz.id/klaim")
    assert dana_phish["brand_in_domain"] == 1
    assert dana_phish["is_unauthorized_brand_domain"] == 1
    assert dana_phish["is_brand_combosquatting"] == 1

    # Neutral domain without brand
    neutral_res = detector.detect("https://pandi.id")
    assert neutral_res["is_unauthorized_brand_domain"] == 0


def test_phishing_feature_extractor_pipeline():
    extractor = PhishingFeatureExtractor(include_dns=False, include_whois=False)
    sample_url = "http://bca-secure-login.id/verify"
    single_res = extractor.extract_single(sample_url)

    assert isinstance(single_res, dict)
    assert "url_len" in single_res
    assert "brand_in_domain" in single_res
    assert "is_unauthorized_brand_domain" in single_res

    # Test DataFrame transformation
    df = pd.DataFrame({
        "url": [
            "http://bca-secure-login.id/verify",
            "https://bank.klikbca.com",
            "http://dana-kaget.web.id/klaim",
        ]
    })
    feature_df = extractor.transform(df, show_progress=False)

    assert len(feature_df) == 3
    assert not feature_df.isna().any().any(), "Transformed feature DataFrame must not have NaNs"


def test_classification_metrics():
    y_true = [1, 0, 1, 1, 0, 0]
    y_pred = [1, 0, 1, 0, 0, 1]
    metrics = calculate_classification_metrics(y_true, y_pred)

    assert "accuracy" in metrics
    assert "f1_macro" in metrics
    assert "f1_binary" in metrics
    assert "fpr" in metrics
    assert 0.0 <= metrics["accuracy"] <= 1.0
