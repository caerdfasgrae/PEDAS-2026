"""Lexical and Structural URL Feature Extraction Module.

Extracts statistical, structural, syntactic, and information-theoretic features
from raw URLs to distinguish phishing attempts from legitimate domains.
"""

from __future__ import annotations
import math
import re
from typing import Dict, Any
from urllib.parse import urlparse, parse_qs
import ipaddress
import tldextract


# Pre-compiled Regex Patterns for High Performance
IP_PATTERN = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
HEX_PATTERN = re.compile(r"%[0-9a-fA-F]{2}")

# Common Indonesian Phishing Keywords (Social Engineering / CTA)
DEFAULT_SUSPICIOUS_TOKENS = {
    "login", "masuk", "secure", "security", "verifikasi", "verification", "verify",
    "autentikasi", "auth", "validasi", "update", "perbarui", "aktivasi", "activate",
    "reaktivasi", "pemulihan", "recovery", "reset", "unblock", "buka-blokir", "blokir",
    "konfirmasi", "confirm", "otp", "pin", "password", "rekening", "hadiah", "reward",
    "undian", "gebyar", "pemenang", "winner", "klaim", "claim", "bansos", "bantuan",
    "subsidi", "prakerja", "pulsa", "kuota", "gratis", "free", "saldo", "kaget",
    "cashback", "voucher", "promo", "tarif", "kenaikan", "etle", "tilang", "undangan",
    "kurir", "resi", "surat-tilang"
}

# TLDs under PANDI (.id ecosystem)
REGULATED_ID_TLDS = {"go.id", "mil.id", "ac.id", "sch.id"}
COMMERCIAL_ID_TLDS = {"co.id", "net.id", "or.id", "org.id"}
CHEAP_ID_TLDS = {"my.id", "biz.id", "web.id"}


def calculate_shannon_entropy(text: str) -> float:
    """Calculates Shannon Entropy of a given string.
    
    Higher entropy indicates random/obfuscated strings (e.g. DGA domains or hash paths).
    """
    if not text:
        return 0.0
    probabilities = [text.count(char) / len(text) for char in set(text)]
    return -sum(p * math.log2(p) for p in probabilities)


def is_ip_host(hostname: str) -> int:
    """Checks if hostname is an IPv4 or IPv6 address."""
    if not hostname:
        return 0
    # Strip port if present
    host = hostname.split(":")[0].strip("[]")
    if IP_PATTERN.match(host):
        return 1
    try:
        ipaddress.ip_address(host)
        return 1
    except ValueError:
        return 0


def extract_lexical_features(url: str, suspicious_tokens: set[str] | None = None) -> Dict[str, Any]:
    """Extracts a comprehensive suite of lexical & structural features from a single URL.

    Args:
        url: The raw URL string (e.g. 'http://bca-secure-login.id/verify').
        suspicious_tokens: Optional custom set of suspicious keyword tokens.

    Returns:
        Dictionary of numeric and binary features.
    """
    if suspicious_tokens is None:
        suspicious_tokens = DEFAULT_SUSPICIOUS_TOKENS

    url_clean = str(url).strip()
    if not url_clean:
        return _empty_feature_dict()

    # Prepend scheme if missing for accurate urlparse parsing
    parsed_candidate = url_clean
    if not (url_clean.startswith("http://") or url_clean.startswith("https://")):
        parsed_candidate = "http://" + url_clean

    parsed = urlparse(parsed_candidate)
    netloc = parsed.netloc.lower()
    path = parsed.path
    query = parsed.query

    # Extract domain, subdomain, and suffix via tldextract
    extracted = tldextract.extract(url_clean)
    subdomain = extracted.subdomain.lower()
    domain = extracted.domain.lower()
    suffix = extracted.suffix.lower()
    fqdn = f"{domain}.{suffix}" if suffix else domain

    # 1. Length Metrics
    url_len = len(url_clean)
    netloc_len = len(netloc)
    domain_len = len(domain)
    path_len = len(path)
    query_len = len(query)

    # 2. Shannon Entropy
    url_entropy = calculate_shannon_entropy(url_clean)
    domain_entropy = calculate_shannon_entropy(domain)
    path_entropy = calculate_shannon_entropy(path)

    # 3. Character Counts & Ratios
    digits_count = sum(c.isdigit() for c in url_clean)
    letters_count = sum(c.isalpha() for c in url_clean)
    symbols_count = sum(not c.isalnum() for c in url_clean)

    digit_ratio = digits_count / url_len if url_len > 0 else 0.0
    letter_ratio = letters_count / url_len if url_len > 0 else 0.0
    symbol_ratio = symbols_count / url_len if url_len > 0 else 0.0

    domain_digits = sum(c.isdigit() for c in domain)
    domain_digit_ratio = domain_digits / domain_len if domain_len > 0 else 0.0

    # Specific Symbol Counts
    hyphen_count_url = url_clean.count("-")
    hyphen_count_domain = domain.count("-")
    hyphen_count_subdomain = subdomain.count("-")
    dot_count_url = url_clean.count(".")
    dot_count_netloc = netloc.count(".")
    underscore_count = url_clean.count("_")
    slash_count_url = url_clean.count("/")
    question_count = url_clean.count("?")
    equal_count = url_clean.count("=")
    ampersand_count = url_clean.count("&")

    # 4. Structural & Syntactic Flags
    is_https = 1 if parsed.scheme.lower() == "https" else 0
    has_ip = is_ip_host(netloc)
    has_at_symbol = 1 if "@" in url_clean else 0
    has_double_slash = 1 if "//" in path else 0
    has_hex = 1 if bool(HEX_PATTERN.search(url_clean)) else 0
    has_port = 1 if bool(parsed.port and parsed.port not in (80, 443)) else 0

    # Subdomain Analysis
    subdomain_parts = [s for s in subdomain.split(".") if s and s != "www"]
    subdomain_count = len(subdomain_parts)
    subdomain_entropy = calculate_shannon_entropy(subdomain)
    has_www = 1 if "www" in subdomain.split(".") else 0
    has_misplaced_www = 1 if ("www" in domain or "www" in path) and not has_www else 0

    # Path & Query Structure
    path_segments = [p for p in path.split("/") if p]
    path_depth = len(path_segments)
    path_to_url_ratio = path_len / url_len if url_len > 0 else 0.0
    query_params_count = len(parse_qs(query)) if query else 0

    # Sensitive / Malicious File Extension Detection (e.g. .apk banking malware, .php phishing gates)
    path_lower = path.lower()
    has_sensitive_ext = 1 if any(path_lower.endswith(ext) or f"{ext}?" in path_lower for ext in (".apk", ".php", ".exe", ".zip", ".bin", ".rar")) else 0

    # 5. Indonesian TLD Indicators (.id ecosystem)
    is_id_tld = 1 if suffix == "id" or suffix.endswith(".id") else 0
    is_regulated_tld = 1 if suffix in REGULATED_ID_TLDS else 0
    is_commercial_tld = 1 if suffix in COMMERCIAL_ID_TLDS else 0
    is_cheap_tld = 1 if suffix in CHEAP_ID_TLDS else 0
    is_idn = 1 if "xn--" in netloc else 0

    # 6. Suspicious Keyword & Social Engineering Analysis
    url_lower = url_clean.lower()
    tokens_in_url = re.split(r"[-_./?=&%]", url_lower)
    suspicious_count = sum(1 for token in tokens_in_url if token in suspicious_tokens)
    has_suspicious_token = 1 if suspicious_count > 0 else 0

    # Return structured features dictionary
    return {
        "url_len": url_len,
        "netloc_len": netloc_len,
        "domain_len": domain_len,
        "path_len": path_len,
        "query_len": query_len,
        "path_to_url_ratio": round(path_to_url_ratio, 4),
        "url_entropy": round(url_entropy, 4),
        "domain_entropy": round(domain_entropy, 4),
        "subdomain_entropy": round(subdomain_entropy, 4),
        "path_entropy": round(path_entropy, 4),
        "digit_count": digits_count,
        "digit_ratio": round(digit_ratio, 4),
        "letter_ratio": round(letter_ratio, 4),
        "symbol_ratio": round(symbol_ratio, 4),
        "domain_digit_ratio": round(domain_digit_ratio, 4),
        "hyphen_count_url": hyphen_count_url,
        "hyphen_count_domain": hyphen_count_domain,
        "hyphen_count_subdomain": hyphen_count_subdomain,
        "dot_count_url": dot_count_url,
        "dot_count_netloc": dot_count_netloc,
        "underscore_count": underscore_count,
        "slash_count_url": slash_count_url,
        "question_count": question_count,
        "equal_count": equal_count,
        "ampersand_count": ampersand_count,
        "is_https": is_https,
        "is_ip": has_ip,
        "is_idn": is_idn,
        "has_at_symbol": has_at_symbol,
        "has_double_slash_path": has_double_slash,
        "has_hex_encoding": has_hex,
        "has_non_standard_port": has_port,
        "has_sensitive_ext": has_sensitive_ext,
        "subdomain_count": subdomain_count,
        "has_www": has_www,
        "has_misplaced_www": has_misplaced_www,
        "path_depth": path_depth,
        "query_params_count": query_params_count,
        "is_id_tld": is_id_tld,
        "is_regulated_tld": is_regulated_tld,
        "is_commercial_tld": is_commercial_tld,
        "is_cheap_tld": is_cheap_tld,
        "suspicious_token_count": suspicious_count,
        "has_suspicious_token": has_suspicious_token,
    }


def _empty_feature_dict() -> Dict[str, Any]:
    """Returns default zeroed features for empty/corrupt URLs."""
    dummy_keys = [
        "url_len", "netloc_len", "domain_len", "path_len", "query_len",
        "path_to_url_ratio", "url_entropy", "domain_entropy", "subdomain_entropy",
        "path_entropy", "digit_count", "digit_ratio", "letter_ratio", "symbol_ratio",
        "domain_digit_ratio", "hyphen_count_url", "hyphen_count_domain",
        "hyphen_count_subdomain", "dot_count_url", "dot_count_netloc",
        "underscore_count", "slash_count_url", "question_count", "equal_count",
        "ampersand_count", "is_https", "is_ip", "is_idn", "has_at_symbol",
        "has_double_slash_path", "has_hex_encoding", "has_non_standard_port",
        "has_sensitive_ext", "subdomain_count", "has_www", "has_misplaced_www",
        "path_depth", "query_params_count", "is_id_tld", "is_regulated_tld",
        "is_commercial_tld", "is_cheap_tld", "suspicious_token_count",
        "has_suspicious_token"
    ]
    return {k: 0.0 if "entropy" in k or "ratio" in k else 0 for k in dummy_keys}
