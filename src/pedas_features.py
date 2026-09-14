"""Deterministic Feature Engineering Module for PeDaS 2026.

Extracts domain, lexical, and structural features tailored for Indonesian .id abuse detection.
"""

import re
from urllib.parse import urlparse, unquote
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from src.cleaner import clean_url, clean_brand


# Distinctive Indonesian abusive keyword regular expressions
RE_GAMBLING = re.compile(
    r"(slot|gacor|maxwin|zeus|togel|pkv|depo|olympus|judi|casino|bet|pragmatic|jackpot|hoki|sbobet|scatter|mahjong|sensational|wd|freebet)",
    re.I,
)
RE_PHISHING = re.compile(
    r"(login|signin|sign-in|verifikasi|otp|bca|bri|bni|mandiri|dana|ovo|gopay|hadiah|giveaway|bansos|kemensos|pulsa|claim|voucher|confirmaccount)",
    re.I,
)
RE_MALWARE = re.compile(
    r"(\.apk|\.exe|\.zip|\.rar|download|install|mediafire|dropbox|setup|payload)",
    re.I,
)
RE_SHOP = re.compile(
    r"(shop|toko|belanja|store|order|cart|produk|beli|fakeshop)",
    re.I,
)


def extract_url_lexical_features(urls: pd.Series) -> pd.DataFrame:
    """Extracts granular lexical and keyword counts from raw URL strings."""
    records = []
    for u in urls:
        raw_u = str(u) if pd.notna(u) else ""
        dec_u = unquote(raw_u).lower()
        
        parsed = urlparse(dec_u if "://" in dec_u else "http://" + dec_u)
        path = parsed.path
        query = parsed.query
        
        url_len = len(dec_u)
        path_len = len(path)
        query_len = len(query)
        
        num_dots = dec_u.count(".")
        num_hyphens = dec_u.count("-")
        num_slashes = dec_u.count("/")
        num_digits = sum(c.isdigit() for c in dec_u)
        digit_ratio = num_digits / max(1, url_len)
        has_query = 1 if query_len > 0 else 0
        
        # Keyword matches
        has_gambling = 1 if RE_GAMBLING.search(dec_u) else 0
        has_phishing = 1 if RE_PHISHING.search(dec_u) else 0
        has_malware = 1 if RE_MALWARE.search(dec_u) else 0
        # Prevent false positive explosion on gambling defacements
        has_shop = 1 if (RE_SHOP.search(dec_u) and has_gambling == 0 and "judi" not in dec_u) else 0
        
        records.append({
            "url_len": url_len,
            "path_len": path_len,
            "query_len": query_len,
            "num_dots": num_dots,
            "num_hyphens": num_hyphens,
            "num_slashes": num_slashes,
            "num_digits": num_digits,
            "digit_ratio": digit_ratio,
            "has_query": has_query,
            "has_gambling": has_gambling,
            "has_phishing": has_phishing,
            "has_malware": has_malware,
            "has_shop": has_shop,
        })
    
    return pd.DataFrame(records)


def extract_domain_metadata_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extracts categorical indicators and missingness flags."""
    brand_missing = df["brand"].apply(lambda b: 1 if clean_brand(b) == "unknown_brand" else 0)
    ip_missing = df["ip"].isna().astype(int)
    confidence = df["confidence_level"].fillna(0).astype(float)
    
    meta_df = pd.DataFrame({
        "brand_missing": brand_missing,
        "ip_missing": ip_missing,
        "confidence_level": confidence,
    })
    return meta_df


TOP_REGISTRARS = [
    "kementerian komunikasi dan informatika",
    "pt digital registra indonesia",
    "pt jagat informasi solusi (int)",
    "pt cloud hosting indonesia",
    "pt web commerce communications",
    "pt registrasi nama domain",
    "pt jc indonesia",
    "pt masterweb network",
    "pt web media technology indonesia",
    "pt rumahweb indonesia",
    "pt radnet digital indonesia",
    "pt ardh global indonesia",
    "pt jagoan hosting indonesia",
    "pt dewabisnis digital indonesia",
    "pt beon intermedia",
]


class DomainEnsembleExtractor:
    """Transformer for explainable domain, lexical, and structural features.
    
    Ensures 100% column alignment between training, validation, and test datasets.
    """
    
    def __init__(self, top_registrars=None):
        self.top_registrars = top_registrars or TOP_REGISTRARS
        self.feature_names_ = None
        
    def fit(self, df: pd.DataFrame, y=None):
        feats = self._extract_raw(df)
        self.feature_names_ = list(feats.columns)
        return self
        
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        feats = self._extract_raw(df)
        if self.feature_names_ is not None:
            feats = feats.reindex(columns=self.feature_names_, fill_value=0.0)
        return feats

    def fit_transform(self, df: pd.DataFrame, y=None) -> pd.DataFrame:
        return self.fit(df, y).transform(df)
        
    def _extract_raw(self, df: pd.DataFrame) -> pd.DataFrame:
        records = []
        disc_dt = pd.to_datetime(df["discovered"], errors="coerce")
        reg_dt = pd.to_datetime(df["registration_date"], errors="coerce")
        age_days_arr = (disc_dt - reg_dt).dt.days.fillna(0).values
        
        for i, (_, row) in enumerate(df.iterrows()):
            raw_u = str(row.get("url", ""))
            dec_u = clean_url(raw_u).lower().strip()
                
            has_http = 1 if dec_u.startswith("http://") else 0
            has_https = 1 if dec_u.startswith("https://") else 0
            has_no_scheme = 1 if (has_http == 0 and has_https == 0) else 0
            
            parsed = urlparse(dec_u if "://" in dec_u else "http://" + dec_u)
            host = parsed.netloc.lower()
            path = parsed.path.strip("/")
            query = parsed.query.strip()
            
            url_len = len(dec_u)
            path_len = len(path)
            query_len = len(query)
            host_len = len(host)
            
            num_dots = dec_u.count(".")
            num_hyphens = dec_u.count("-")
            num_slashes = dec_u.count("/")
            num_digits = sum(c.isdigit() for c in dec_u)
            num_asterisks = dec_u.count("*")
            
            digit_ratio = num_digits / max(1, url_len)
            asterisk_ratio = num_asterisks / max(1, url_len)
            
            has_query = 1 if query_len > 0 else 0
            has_path = 1 if path_len > 0 else 0
            is_pure_root = 1 if (path_len == 0 and query_len == 0) else 0
            is_masked_root = 1 if (is_pure_root == 1 and num_asterisks > 0) else 0
            
            # Keyword matches
            has_gambling = 1 if RE_GAMBLING.search(dec_u) else 0
            has_phishing = 1 if RE_PHISHING.search(dec_u) else 0
            has_malware = 1 if RE_MALWARE.search(dec_u) else 0
            
            # Brand signals
            cb = clean_brand(row.get("brand", ""))
            has_brand = 1 if cb != "unknown_brand" else 0
            b_lower = cb.lower()
            brand_is_judi = 1 if "judi" in b_lower else 0
            brand_is_tech_bank = 1 if any(t in b_lower for t in ["generic/spear phishing", "dana", "facebook", "telegram", "whatsapp", "garena", "tencent", "microsoft", "google", "bca", "bri", "mandiri", "coda payments", "instagram", "dhl", "fedex", "paypal", "crypto"]) else 0
            
            # IP signals
            raw_ip = str(row.get("ip", ""))
            ip_missing = 1 if pd.isna(row.get("ip")) or raw_ip in ["", "nan", "None"] else 0
            is_cf_ip = 1 if (raw_ip.startswith("104.") or raw_ip.startswith("172.67.")) else 0
            is_gov_ip = 1 if raw_ip.startswith("103.") else 0
            
            # Confidence level
            raw_conf = row.get("confidence_level")
            conf = 100.0 if pd.isna(raw_conf) else float(raw_conf)
            conf_clipped = min(100.0, max(0.0, conf)) / 100.0
            
            # Domain temporal age (positionally accessed, immune to slice index mismatch)
            cur_age = age_days_arr[i] if i < len(age_days_arr) else 0
            is_future_reg = 1 if cur_age < 0 else 0
            is_aged_domain = 1 if cur_age > 1000 else 0
            is_fresh_domain = 1 if (0 <= cur_age <= 180) else 0
            
            records.append({
                "url_len": url_len,
                "path_len": path_len,
                "query_len": query_len,
                "host_len": host_len,
                "num_dots": num_dots,
                "num_hyphens": num_hyphens,
                "num_slashes": num_slashes,
                "num_digits": num_digits,
                "num_asterisks": num_asterisks,
                "digit_ratio": digit_ratio,
                "asterisk_ratio": asterisk_ratio,
                "has_query": has_query,
                "has_path": has_path,
                "is_pure_root": is_pure_root,
                "is_masked_root": is_masked_root,
                "is_http": has_http,
                "is_https": has_https,
                "has_no_scheme": has_no_scheme,
                "has_gambling": has_gambling,
                "has_phishing": has_phishing,
                "has_malware": has_malware,
                "has_brand": has_brand,
                "brand_is_judi": brand_is_judi,
                "brand_is_tech_bank": brand_is_tech_bank,
                "ip_missing": ip_missing,
                "is_cf_ip": is_cf_ip,
                "is_gov_ip": is_gov_ip,
                "conf_clipped": conf_clipped,
                "is_future_reg": is_future_reg,
                "is_aged_domain": is_aged_domain,
                "is_fresh_domain": is_fresh_domain,
            })
            
        feats_df = pd.DataFrame(records, index=df.index)
        
        # Categorical one-hot features: SLD
        sld_clean = df["sld"].fillna("unknown_sld").astype(str).str.strip().str.lower()
        sld_ohe = pd.get_dummies(sld_clean, prefix="sld", dtype=float)
        
        # Normalized Registrar one-hot features
        norm_reg = df["registrar"].fillna("unknown_registrar").astype(str).str.strip().str.lower()
        reg_filtered = norm_reg.apply(lambda r: r if r in self.top_registrars else "other_registrar")
        reg_ohe = pd.get_dummies(reg_filtered, prefix="reg", dtype=float)
        
        combined = pd.concat([feats_df, sld_ohe, reg_ohe], axis=1)
        return combined


def extract_domain_ensemble_features(df: pd.DataFrame) -> pd.DataFrame:
    """Convenience function to extract domain ensemble features using default settings."""
    extractor = DomainEnsembleExtractor()
    return extractor.fit_transform(df)


class TfidfTextFeatureExtractor:
    """Character N-gram TF-IDF vectorizer over composite text."""
    
    def __init__(self, ngram_range=(3, 5), min_df=2, max_features=15000):
        self.vectorizer = TfidfVectorizer(
            analyzer="char",
            ngram_range=ngram_range,
            min_df=min_df,
            max_features=max_features,
            sublinear_tf=True,
        )
        
    def fit(self, texts: pd.Series):
        self.vectorizer.fit(texts)
        return self
        
    def transform(self, texts: pd.Series):
        return self.vectorizer.transform(texts)
        
    def fit_transform(self, texts: pd.Series):
        return self.vectorizer.fit_transform(texts)
