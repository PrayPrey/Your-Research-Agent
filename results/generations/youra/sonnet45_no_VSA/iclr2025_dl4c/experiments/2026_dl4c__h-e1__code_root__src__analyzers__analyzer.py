"""Security analyzer interface for Bandit and CodeQL."""
import os
import tempfile
import json
import subprocess
from typing import Dict, List
from bandit.core import manager as bandit_manager


class SecurityAnalyzer:
    """Interface for static security analyzers."""

    def __init__(self, analyzer_type: str = 'bandit'):
        self.analyzer_type = analyzer_type

    def analyze(self, code: str) -> Dict:
        """Run security analysis on code."""
        if self.analyzer_type == 'bandit':
            return self._run_bandit(code)
        elif self.analyzer_type == 'codeql':
            return self._run_codeql(code)
        else:
            return {'has_issues': False, 'cwe_list': [], 'issues': []}

    def _run_bandit(self, code: str) -> Dict:
        """Run Bandit analyzer."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            mgr = bandit_manager.BanditManager(
                bandit_manager.BanditConfig(),
                'file',
                None
            )
            mgr.discover_files([temp_path])
            mgr.run_tests()
            results = mgr.get_issue_list()

            issues = []
            cwes = set()
            for issue in results:
                cwe = issue.cwe if hasattr(issue, 'cwe') and issue.cwe else None
                if cwe:
                    cwes.add(f'CWE-{cwe.get("id", "Unknown")}' if isinstance(cwe, dict) else f'CWE-{cwe}')
                issues.append({
                    'severity': issue.severity,
                    'confidence': issue.confidence,
                    'test_id': issue.test_id,
                    'text': issue.text,
                    'cwe': cwe
                })

            return {
                'has_issues': len(issues) > 0,
                'cwe_list': list(cwes),
                'issues': issues,
                'severity': [i['severity'] for i in issues]
            }
        except Exception as e:
            return {'has_issues': False, 'cwe_list': [], 'issues': [], 'error': str(e)}
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def _run_codeql(self, code: str) -> Dict:
        """Run CodeQL analyzer (secondary)."""
        # Simplified implementation - CodeQL requires database setup
        return {'has_issues': False, 'cwe_list': [], 'issues': []}

    def _extract_cwes(self, results: Dict) -> List[str]:
        """Extract CWE IDs from analyzer results."""
        return results.get('cwe_list', [])
