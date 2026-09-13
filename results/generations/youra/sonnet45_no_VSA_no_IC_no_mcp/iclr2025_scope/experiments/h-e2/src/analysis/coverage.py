import pandas as pd
from typing import Dict

class CoverageAnalyzer:
    """Compute coverage metrics and breakdowns."""

    def __init__(self, fetcher):
        self.fetcher = fetcher

    def measure_coverage(self, corpus: pd.DataFrame) -> Dict:
        """Compute coverage for entire corpus."""
        results = []
        for idx, row in corpus.iterrows():
            if idx % 20 == 0:
                print(f"Checking {idx+1}/{len(corpus)}: {row['dataset_name']}")
            check = self.fetcher.check_coverage(row['dataset_name'])
            results.append({
                "dataset_name": row['dataset_name'],
                "domain": row['domain'],
                "pwc": check['pwc'],
                "hf": check['hf'],
                "covered": check['covered']
            })

        results_df = pd.DataFrame(results)
        covered = results_df['covered'].sum()
        total = len(results_df)
        coverage_pct = (covered / total) * 100 if total > 0 else 0.0

        return {
            "coverage_pct": round(coverage_pct, 2),
            "covered": int(covered),
            "total": int(total),
            "results_df": results_df
        }

    def breakdown_by_domain(self, results: pd.DataFrame) -> Dict[str, float]:
        """Breakdown by NLP vs CV."""
        nlp = results[results['domain'] == 'NLP']
        cv = results[results['domain'] == 'CV']

        nlp_pct = (nlp['covered'].sum() / len(nlp)) * 100 if len(nlp) > 0 else 0.0
        cv_pct = (cv['covered'].sum() / len(cv)) * 100 if len(cv) > 0 else 0.0

        return {"nlp_pct": round(nlp_pct, 2), "cv_pct": round(cv_pct, 2)}

    def breakdown_by_source(self, results: pd.DataFrame) -> Dict[str, int]:
        """Breakdown by API source."""
        pwc_only = ((results['pwc'] == True) & (results['hf'] == False)).sum()
        hf_only = ((results['pwc'] == False) & (results['hf'] == True)).sum()
        both = ((results['pwc'] == True) & (results['hf'] == True)).sum()
        neither = ((results['pwc'] == False) & (results['hf'] == False)).sum()

        return {
            "pwc_only": int(pwc_only),
            "hf_only": int(hf_only),
            "both": int(both),
            "neither": int(neither)
        }
