"""DNS and Network Feature Extractor.

Supports both live DNS queries (with caching and timeout safeguards) and
processing of pre-extracted DNS features provided in datasets (such as PANDI dns.id).
"""

from __future__ import annotations
from typing import Dict, Any
import tldextract


class DNSFeatureExtractor:
    """Extracts DNS record statistics and resolution status."""

    def __init__(self, timeout: float = 2.0, use_cache: bool = True):
        self.timeout = timeout
        self.use_cache = use_cache
        self._cache: Dict[str, Dict[str, Any]] = {}

    def extract_from_live(self, url: str) -> Dict[str, Any]:
        """Performs live DNS resolution with short timeout and robust fallbacks."""
        extracted = tldextract.extract(url)
        domain = extracted.registered_domain
        if not domain:
            return self._empty_dns_dict()

        if self.use_cache and domain in self._cache:
            return self._cache[domain]

        features = self._empty_dns_dict()

        try:
            import dns.resolver
            resolver = dns.resolver.Resolver()
            resolver.timeout = self.timeout
            resolver.lifetime = self.timeout

            # Check A record
            try:
                a_answers = resolver.resolve(domain, "A")
                features["dns_has_a"] = 1
                features["dns_ip_count"] = len(a_answers)
                features["dns_resolved_success"] = 1
            except Exception:
                pass

            # Check AAAA record (IPv6)
            try:
                resolver.resolve(domain, "AAAA")
                features["dns_has_aaaa"] = 1
            except Exception:
                pass

            # Check MX record (Legitimate business domains usually have email servers)
            try:
                mx_answers = resolver.resolve(domain, "MX")
                features["dns_has_mx"] = 1
                features["dns_mx_count"] = len(mx_answers)
            except Exception:
                pass

            # Check NS record
            try:
                ns_answers = resolver.resolve(domain, "NS")
                features["dns_has_ns"] = 1
                features["dns_ns_count"] = len(ns_answers)
            except Exception:
                pass

            # Check TXT record (SPF/Domain verification)
            try:
                txt_answers = resolver.resolve(domain, "TXT")
                features["dns_has_txt"] = 1
                features["dns_txt_count"] = len(txt_answers)
            except Exception:
                pass

        except ImportError:
            # Fallback if dnspython not installed
            features["dns_resolved_success"] = 0
        except Exception:
            features["dns_resolved_success"] = 0

        if self.use_cache:
            self._cache[domain] = features

        return features

    def extract_from_record_dict(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts features when DNS stats are already provided in tabular data (PANDI dataset format)."""
        return {
            "dns_has_a": int(bool(record.get("dns_a") or record.get("has_a"))),
            "dns_has_aaaa": int(bool(record.get("dns_aaaa") or record.get("has_aaaa"))),
            "dns_has_mx": int(bool(record.get("dns_mx") or record.get("has_mx"))),
            "dns_has_ns": int(bool(record.get("dns_ns") or record.get("has_ns"))),
            "dns_has_txt": int(bool(record.get("dns_txt") or record.get("has_txt"))),
            "dns_ip_count": int(record.get("ip_count", 0)),
            "dns_resolved_success": int(bool(record.get("dns_success", 0))),
        }

    @staticmethod
    def _empty_dns_dict() -> Dict[str, Any]:
        return {
            "dns_has_a": 0,
            "dns_has_aaaa": 0,
            "dns_has_mx": 0,
            "dns_has_ns": 0,
            "dns_has_txt": 0,
            "dns_ip_count": 0,
            "dns_mx_count": 0,
            "dns_ns_count": 0,
            "dns_txt_count": 0,
            "dns_resolved_success": 0,
        }
