#!/usr/bin/env python3
"""
H-E1 Inter-Rater Reliability Calculator
Compute Krippendorff's alpha for expert ratings.
"""
import sys
import json
import pandas as pd
import krippendorff
from pathlib import Path

class ReliabilityAnalyzer:
    def __init__(self, ratings_csv: str):
        self.df = pd.read_csv(ratings_csv)
        
    def compute_alpha(self, axis: str) -> float:
        """Compute Krippendorff's alpha for one axis"""
        # Pivot: rows=raters, cols=benchmarks
        pivot = self.df.pivot_table(
            index='rater_id',
            columns='benchmark_name',
            values=axis,
            aggfunc='mean'
        )
        
        # Convert to matrix format for krippendorff library
        reliability_data = pivot.values
        
        alpha = krippendorff.alpha(
            reliability_data=reliability_data,
            level_of_measurement='interval'
        )
        
        return alpha
    
    def compute_all_axes(self) -> dict:
        """Compute alpha for all compliance axes"""
        axes = ['data_realness', 'eval_automation', 'infra_readiness']
        results = {}
        
        for axis in axes:
            try:
                alpha = self.compute_alpha(axis)
                results[axis] = float(alpha)
            except Exception as e:
                print(f"Error computing alpha for {axis}: {e}", file=sys.stderr)
                results[axis] = None
        
        return results
    
    def flag_disagreements(self, threshold: float = 0.3) -> list:
        """Flag benchmarks with high rating variance"""
        disagreements = []
        
        for benchmark in self.df['benchmark_name'].unique():
            bench_df = self.df[self.df['benchmark_name'] == benchmark]
            
            for axis in ['data_realness', 'eval_automation', 'infra_readiness']:
                values = bench_df[axis].values
                variance = values.std()
                
                if variance > threshold:
                    disagreements.append({
                        'benchmark': benchmark,
                        'axis': axis,
                        'variance': float(variance),
                        'ratings': values.tolist()
                    })
        
        return disagreements

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Compute inter-rater reliability')
    parser.add_argument('--ratings', required=True, help='Path to ground_truth_labels.csv')
    parser.add_argument('--output', default='outputs/inter_rater_reliability.json', help='Output JSON path')
    args = parser.parse_args()
    
    analyzer = ReliabilityAnalyzer(args.ratings)
    
    results = {
        'reliability': analyzer.compute_all_axes(),
        'disagreements': analyzer.flag_disagreements(),
        'n_benchmarks': len(analyzer.df['benchmark_name'].unique()),
        'n_raters': len(analyzer.df['rater_id'].unique()),
        'total_ratings': len(analyzer.df)
    }
    
    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n=== Inter-Rater Reliability ===")
    for axis, alpha in results['reliability'].items():
        status = "PASS" if alpha and alpha >= 0.85 else "FAIL"
        print(f"{axis}: α={alpha:.3f} [{status}]")
    
    if results['disagreements']:
        print(f"\nWarning: {len(results['disagreements'])} disagreements detected (variance > 0.3)")
    
    # Check gate
    if results['reliability'] and all(alpha >= 0.85 for alpha in results['reliability'].values() if alpha is not None):
        print("\nReliability gate: PASS")
    else:
        print("\nReliability gate: FAIL")
        sys.exit(1)

if __name__ == '__main__':
    main()
