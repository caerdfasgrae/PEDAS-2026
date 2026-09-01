"""WHOIS Parser and Feature Extractor.

Extracts domain age, expiration period, and registrar metadata.
Supports both live WHOIS lookup and parsing pre-extracted WHOIS columns from PANDI datasets.
"""

from __future__ import annotations
from typing import Dict, Any, Union
from datetime import datetime, timezone
import tldextract


class WHOISFeatureExtractor:
    """Extracts WHOIS domain registration and lifecycle features."""

    def __init__(self, timeout: float = 3.0, use_cache: bool = True):
        self.timeout = timeout
        self.use_cache = use_cache
        self._cache: Dict[str, Dict[str, Any]] = {}

    def extract_from_live(self, url: str) -> Dict[str, Any]:
        """Performs live WHOIS query with fallback."""
        extracted = tldextract.extract(url)
        domain = extracted.registered_domain
        if not domain:
            return self._empty_whois_dict()

        if self.use_cache and domain in self._cache:
            return self._cache[domain]

        features = self._empty_whois_dict()

        try:
            import whois
            w = whois.whois(domain)
            if w and w.creation_date:
                features = self._parse_dates(
                    creation_date=w.creation_date,
                    expiration_date=w.expiration_date,
                    updated_date=w.updated_date,
                )
                features["has_whois_record"] = 1
                features["registrar_length"] = len(str(w.registrar or ""))
        except Exception:
            features = self._empty_whois_dict()

        if self.use_cache:
            self._cache[domain] = features

        return features

    def extract_from_dict(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts features when WHOIS columns are already provided in PANDI dataset."""
        creation_date = record.get("creation_date") or record.get("created_at") or record.get("domain_created")
        expiration_date = record.get("expiration_date") or record.get("expires_at") or record.get("domain_expires")
        updated_date = record.get("updated_date") or record.get("updated_at")

        if not creation_date:
            return self._empty_whois_dict()

        features = self._parse_dates(creation_date, expiration_date, updated_date)
        features["has_whois_record"] = 1
        features["registrar_length"] = len(str(record.get("registrar") or ""))
        return features

    def _parse_dates(
        self,
        creation_date: Union[datetime, list, str, None],
        expiration_date: Union[datetime, list, str, None],
        updated_date: Union[datetime, list, str, None],
    ) -> Dict[str, Any]:
        """Normalizes dates and computes age and expiration metrics."""
        now = datetime.now(timezone.utc)

        c_dt = self._to_utc_datetime(creation_date)
        e_dt = self._to_utc_datetime(expiration_date)
        u_dt = self._to_utc_datetime(updated_date)

        age_days = -1
        time_to_expire = -1
        time_since_update = -1

        if c_dt:
            age_days = max(0, (now - c_dt).days)
        if e_dt:
            time_to_expire = (e_dt - now).days
        if u_dt:
            time_since_update = max(0, (now - u_dt).days)

        is_new_domain = 1 if (0 <= age_days <= 30) else 0
        is_young_domain = 1 if (0 <= age_days <= 365) else 0

        return {
            "has_whois_record": 1 if c_dt else 0,
            "domain_age_days": age_days,
            "domain_time_to_expire_days": time_to_expire,
            "domain_time_since_update_days": time_since_update,
            "is_new_domain_30d": is_new_domain,
            "is_young_domain_365d": is_young_domain,
            "registrar_length": 0,
        }

    @staticmethod
    def _to_utc_datetime(dt_val: Any) -> datetime | None:
        """Converts various date representations into a UTC datetime."""
        if not dt_val:
            return None
        if isinstance(dt_val, list):
            dt_val = dt_val[0]
        if isinstance(dt_val, datetime):
            if dt_val.tzinfo is None:
                return dt_val.replace(tzinfo=timezone.utc)
            return dt_val.astimezone(timezone.utc)
        if isinstance(dt_val, str):
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d-%b-%Y", "%Y/%m/%d"):
                try:
                    parsed = datetime.strptime(dt_val.strip(), fmt)
                    return parsed.replace(tzinfo=timezone.utc)
                except ValueError:
                    continue
        return None

    @staticmethod
    def _empty_whois_dict() -> Dict[str, Any]:
        return {
            "has_whois_record": 0,
            "domain_age_days": -1,
            "domain_time_to_expire_days": -1,
            "domain_time_since_update_days": -1,
            "is_new_domain_30d": 0,
            "is_young_domain_365d": 0,
            "registrar_length": 0,
        }
