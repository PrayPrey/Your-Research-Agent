"""Parse required fields (license, version) from platform metadata."""

import re
from typing import Dict

from config import LICENSE_KEYWORDS, VERSION_KEYWORDS


class RequiredFieldParser:
    """Parse license and version fields with platform-specific rules."""

    @staticmethod
    def is_license_present(record: Dict) -> bool:
        """
        Detect license field presence.

        Platform-specific rules:
        - HF: Non-empty, not 'unknown'/'other'
        - OpenML: Non-empty string
        - UCI: Contains license keywords, length >10
        """
        platform = record.get("platform", "")
        license_val = record.get("license")

        if license_val is None:
            return False

        license_str = str(license_val).strip()

        if not license_str:
            return False

        if platform == "HF":
            # Reject 'unknown' and 'other'
            return license_str.lower() not in ["unknown", "other"]

        elif platform == "OpenML":
            # Non-empty is sufficient (required field)
            return len(license_str) > 0

        elif platform == "UCI":
            # Keyword match (not enforced, descriptive text)
            if len(license_str) < 10:
                return False
            return any(kw.lower() in license_str.lower() for kw in LICENSE_KEYWORDS)

        return False

    @staticmethod
    def is_version_present(record: Dict) -> bool:
        """
        Detect version field presence.

        Platform-specific rules:
        - HF: Semantic version pattern (X.Y.Z)
        - OpenML: Non-null integer
        - UCI: Keyword or date pattern
        """
        platform = record.get("platform", "")
        version_val = record.get("version")

        if version_val is None:
            return False

        if platform == "HF":
            # Semantic version pattern
            version_str = str(version_val).strip()
            return bool(re.match(r"^\d+\.\d+\.\d+", version_str))

        elif platform == "OpenML":
            # Integer version (non-null)
            return isinstance(version_val, int) or (
                isinstance(version_val, str) and version_val.strip().isdigit()
            )

        elif platform == "UCI":
            # Keyword or date pattern
            version_str = str(version_val).strip()
            if len(version_str) < 5:
                return False

            # Check for keywords
            has_keyword = any(kw.lower() in version_str.lower() for kw in VERSION_KEYWORDS)

            # Check for date pattern (YYYY-MM-DD)
            has_date = bool(re.search(r"\d{4}-\d{2}-\d{2}", version_str))

            return has_keyword or has_date

        return False

    def parse_record(self, record: Dict) -> Dict:
        """Parse single record, return presence flags."""
        return {
            "dataset_id": record.get("id"),
            "platform": record.get("platform"),
            "license_present": self.is_license_present(record),
            "version_present": self.is_version_present(record),
        }

    def parse_all(self, records: list) -> list:
        """Parse all records."""
        return [self.parse_record(r) for r in records]
