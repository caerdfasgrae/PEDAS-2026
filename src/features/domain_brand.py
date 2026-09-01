"""Brand Impersonation, Typosquatting, and Combosquatting Feature Extractor.

Specifically designed for Indonesian cyberspace threats (Banks, E-Wallets, E-Commerce,
Government Portals) targeting the .id domain ecosystem.
"""

from __future__ import annotations
from typing import Dict, Any, List
from difflib import SequenceMatcher
import tldextract

from src.utils.config import load_yaml_config, BRANDS_CONFIG_PATH


class IndonesianBrandDetector:
    """Detects brand impersonation, typosquatting, and combosquatting for Indonesian brands."""

    def __init__(self, config_path=BRANDS_CONFIG_PATH):
        self.config = load_yaml_config(config_path)
        self.brands_data = self.config.get("brands", {})
        self._build_lookups()

    def _build_lookups(self):
        """Precomputes lookup structures for ultra-fast matching."""
        self.brand_keywords: Dict[str, str] = {}  # keyword -> brand_id
        self.official_domains: Dict[str, set] = {}  # brand_id -> set of official domains
        self.all_keywords: List[str] = []

        for category, brand_list in self.brands_data.items():
            for brand in brand_list:
                b_name = brand.get("name")
                officials = set(brand.get("official_domains", []))
                self.official_domains[b_name] = officials

                for kw in brand.get("keywords", []):
                    kw_lower = kw.lower()
                    self.brand_keywords[kw_lower] = b_name
                    self.all_keywords.append(kw_lower)

        # De-duplicate keywords
        self.all_keywords = list(set(self.all_keywords))

    def detect(self, url: str) -> Dict[str, Any]:
        """Extracts brand impersonation features for a given URL."""
        url_lower = str(url).strip().lower()
        extracted = tldextract.extract(url_lower)

        subdomain = extracted.subdomain
        domain = extracted.domain
        suffix = extracted.suffix
        fqdn = f"{domain}.{suffix}" if suffix else domain

        brand_in_domain = 0
        brand_in_subdomain = 0
        brand_in_path = 0
        is_unauthorized_brand_domain = 0
        max_similarity = 0.0
        detected_brand = "none"

        # Check official domains match first
        is_official = False
        for b_name, officials in self.official_domains.items():
            if fqdn in officials:
                is_official = True
                detected_brand = b_name
                break

        if is_official:
            # Legitimate official domain of the brand
            return {
                "brand_in_domain": 1,
                "brand_in_subdomain": 0,
                "brand_in_path": 0,
                "is_unauthorized_brand_domain": 0,
                "max_brand_similarity": 1.0,
                "is_brand_combosquatting": 0,
            }

        # Check brand presence in domain, subdomain, path
        domain_tokens = domain.replace("-", " ").replace("_", " ").split()
        subdomain_tokens = subdomain.replace("-", " ").replace(".", " ").split()

        for kw in self.all_keywords:
            brand_id = self.brand_keywords[kw]

            # 1. Exact or Substring match in domain
            if kw in domain:
                brand_in_domain = 1
                detected_brand = brand_id
                # If brand is in domain, but domain is NOT official -> unauthorized brand domain!
                if fqdn not in self.official_domains.get(brand_id, set()):
                    is_unauthorized_brand_domain = 1

            # 2. Subdomain check (e.g. bca.login-phishing.com)
            if kw in subdomain:
                brand_in_subdomain = 1
                if detected_brand == "none":
                    detected_brand = brand_id
                if fqdn not in self.official_domains.get(brand_id, set()):
                    is_unauthorized_brand_domain = 1

            # 3. Path check (e.g. attacker.id/bca/login)
            if kw in url_lower and not (kw in domain or kw in subdomain):
                brand_in_path = 1

            # 4. Fuzzy similarity for Typosquatting (Levenshtein / SequenceMatcher)
            # Only compare with domain label if domain length is close
            sim = SequenceMatcher(None, domain, kw).ratio()
            if sim > max_similarity:
                max_similarity = sim

        # Combosquatting detection: domain contains brand name plus other words with hyphens
        # e.g., 'bca-secure-login' contains 'bca' and hyphens
        is_combosquatting = 1 if (brand_in_domain and ("-" in domain or len(domain_tokens) > 1)) else 0

        return {
            "brand_in_domain": brand_in_domain,
            "brand_in_subdomain": brand_in_subdomain,
            "brand_in_path": brand_in_path,
            "is_unauthorized_brand_domain": is_unauthorized_brand_domain,
            "max_brand_similarity": round(max_similarity, 4),
            "is_brand_combosquatting": is_combosquatting,
        }


# Global instance for easy functional access
_brand_detector = None


def extract_brand_features(url: str) -> Dict[str, Any]:
    """Convenience function to extract brand spoofing features."""
    global _brand_detector
    if _brand_detector is None:
        _brand_detector = IndonesianBrandDetector()
    return _brand_detector.detect(url)
