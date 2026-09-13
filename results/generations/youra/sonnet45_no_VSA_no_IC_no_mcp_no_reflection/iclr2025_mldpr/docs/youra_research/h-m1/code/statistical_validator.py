from scipy import stats
import pandas as pd
from typing import Dict

class StatisticalValidator:
    def levene_test(self, pre_scores: pd.Series, post_scores: pd.Series) -> Dict[str, float]:
        stat, pvalue = stats.levene(pre_scores, post_scores)
        return {'stat': float(stat), 'pvalue': float(pvalue)}

    def validate_convergence(self, df: pd.DataFrame, convergence_date: str, benchmark: str) -> Dict:
        benchmark_df = df[df['benchmark'] == benchmark].copy()
        convergence_period = pd.Period(convergence_date, freq='M')

        pre = benchmark_df[benchmark_df['month'] < convergence_period]
        post = benchmark_df[benchmark_df['month'] >= convergence_period]

        if len(pre) < 2 or len(post) < 2:
            return {
                'pre_count': len(pre),
                'post_count': len(post),
                'stat': None,
                'pvalue': None,
                'significant': False
            }

        test_result = self.levene_test(pre['score'], post['score'])
        return {
            'pre_count': len(pre),
            'post_count': len(post),
            'stat': test_result['stat'],
            'pvalue': test_result['pvalue'],
            'significant': test_result['pvalue'] < 0.05
        }
