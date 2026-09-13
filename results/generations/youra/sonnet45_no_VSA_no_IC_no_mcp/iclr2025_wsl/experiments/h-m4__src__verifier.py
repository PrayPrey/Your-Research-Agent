"""Verification pipeline (KB + confound detection)."""

from typing import Dict, List, Tuple
import yaml


class VerificationPipeline:
    """Integrate KB lookup (h-m1) + confound detection (h-m3)."""

    def __init__(self, kb_path: str, confound_patterns: Dict[str, List[Dict]]):
        self.kb = self._load_kb(kb_path)
        self.confound_patterns = confound_patterns

    def _load_kb(self, kb_path: str) -> Dict:
        """Load h-m1 knowledge base."""
        with open(kb_path, 'r') as f:
            kb_data = yaml.safe_load(f)

        # Convert triples list to nested dict for fast lookup
        kb_dict = {}
        for triple in kb_data['triples']:
            dataset = triple['dataset']
            benchmark = triple['benchmark']
            metric = triple['metric']

            if dataset not in kb_dict:
                kb_dict[dataset] = {}
            if benchmark not in kb_dict[dataset]:
                kb_dict[dataset][benchmark] = set()
            kb_dict[dataset][benchmark].add(metric)

        return kb_dict

    def classify_hypothesis(self, hypothesis: Dict) -> Tuple[str, str]:
        """Classify hypothesis as testable or not.

        Returns: (classification, reason)
        """
        # Step 1: Check DBM exists
        dbm = hypothesis['expected_dbm']
        dbm_exists = self._check_dbm_exists(dbm)

        if not dbm_exists:
            return ("not-testable", f"No (D,B,M) triple: {dbm}")

        # Step 2: Check for confounds
        confound_flagged, confound_desc = self._flag_confounds(hypothesis['statement'])

        if confound_flagged:
            return ("not-testable", f"Confound detected: {confound_desc}")

        # Both checks pass
        return ("testable", f"(D,B,M) exists: {dbm}, no confounds")

    def _check_dbm_exists(self, dbm_triple: Dict) -> bool:
        """Check if (D,B,M) triple exists in KB."""
        dataset = dbm_triple['dataset']
        benchmark = dbm_triple['benchmark']
        metric = dbm_triple['metric']

        if dataset not in self.kb:
            return False
        if benchmark not in self.kb[dataset]:
            return False
        if metric not in self.kb[dataset][benchmark]:
            return False

        return True

    def _flag_confounds(self, hypothesis_text: str) -> Tuple[bool, str]:
        """Detect confounds using h-m3 patterns."""
        text_lower = hypothesis_text.lower()

        for domain, patterns in self.confound_patterns.items():
            for pattern in patterns:
                if self._match_keywords(text_lower, pattern["keywords"]):
                    return (True, pattern["description"])

        return (False, "")

    def _match_keywords(self, text: str, keywords: List[str]) -> bool:
        """Check if ALL keywords appear in text."""
        return all(kw.lower() in text for kw in keywords)
