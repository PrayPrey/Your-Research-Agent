#!/usr/bin/env python3
"""
H-E1 Corpus Verification Engine
Check gate conditions: completeness ≥90%, alpha ≥0.85, coverage=100%
"""
import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

class CorpusVerifier:
    def __init__(self, corpus_dir: str, ratings_csv: str):
        self.corpus_dir = Path(corpus_dir)
        self.ratings_df = pd.read_csv(ratings_csv)
        
    def check_completeness(self) -> dict:
        """Check % benchmarks with all 3 sources"""
        benchmarks_dir = self.corpus_dir / 'benchmarks'
        
        if not benchmarks_dir.exists():
            return {'completeness': 0.0, 'complete': [], 'incomplete': []}
        
        benchmarks = [d for d in benchmarks_dir.iterdir() if d.is_dir()]
        complete = []
        incomplete = []
        
        for bench_dir in benchmarks:
            sources = {
                'paper': (bench_dir / 'paper.pdf').exists(),
                'readme': (bench_dir / 'README.md').exists(),
                'code': (bench_dir / 'eval_script.py').exists()
            }
            
            if all(sources.values()):
                complete.append(bench_dir.name)
            else:
                missing = [k for k, v in sources.items() if not v]
                incomplete.append({
                    'name': bench_dir.name,
                    'missing': missing
                })
        
        total = len(benchmarks)
        completeness = len(complete) / total if total > 0 else 0.0
        
        return {
            'completeness': completeness,
            'complete': complete,
            'incomplete': incomplete,
            'total_benchmarks': total
        }
    
    def check_label_coverage(self) -> dict:
        """Check if all benchmarks have ratings on all axes"""
        required_axes = ['data_realness', 'eval_automation', 'infra_readiness']
        benchmarks = self.ratings_df['benchmark_name'].unique()
        
        coverage_issues = []
        
        for benchmark in benchmarks:
            bench_ratings = self.ratings_df[self.ratings_df['benchmark_name'] == benchmark]
            
            for axis in required_axes:
                if bench_ratings[axis].isna().any() or len(bench_ratings[axis]) == 0:
                    coverage_issues.append({
                        'benchmark': benchmark,
                        'missing_axis': axis
                    })
        
        coverage = 1.0 if len(coverage_issues) == 0 else 0.0
        
        return {
            'coverage': coverage,
            'issues': coverage_issues,
            'rated_benchmarks': len(benchmarks)
        }
    
    def verify_gate_conditions(self, reliability_results: dict) -> dict:
        """Apply gate logic: completeness ≥90% AND α≥0.85 AND coverage=100%"""
        completeness_check = self.check_completeness()
        coverage_check = self.check_label_coverage()
        
        # Extract reliability scores
        reliability = reliability_results.get('reliability', {})
        
        # Check each condition
        checks = {
            'completeness': {
                'value': completeness_check['completeness'],
                'threshold': 0.9,
                'passed': completeness_check['completeness'] >= 0.9
            },
            'label_coverage': {
                'value': coverage_check['coverage'],
                'threshold': 1.0,
                'passed': coverage_check['coverage'] == 1.0
            },
            'reliability': {}
        }
        
        for axis, alpha in reliability.items():
            if alpha is not None:
                checks['reliability'][axis] = {
                    'value': alpha,
                    'threshold': 0.85,
                    'passed': alpha >= 0.85
                }
        
        # Overall decision
        all_passed = (
            checks['completeness']['passed'] and
            checks['label_coverage']['passed'] and
            all(v['passed'] for v in checks['reliability'].values())
        )
        
        return {
            'decision': 'PASS' if all_passed else 'FAIL',
            'checks': checks,
            'timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'details': {
                'completeness': completeness_check,
                'coverage': coverage_check,
                'reliability': reliability_results
            }
        }

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Verify corpus gate conditions')
    parser.add_argument('--corpus', required=True, help='Path to benchmark_metadata_corpus/')
    parser.add_argument('--ratings', required=True, help='Path to ground_truth_labels.csv')
    parser.add_argument('--reliability', required=True, help='Path to inter_rater_reliability.json')
    parser.add_argument('--output', default='outputs/verification_result.json', help='Output path')
    args = parser.parse_args()
    
    # Load reliability results
    with open(args.reliability) as f:
        reliability_results = json.load(f)
    
    verifier = CorpusVerifier(args.corpus, args.ratings)
    result = verifier.verify_gate_conditions(reliability_results)
    
    # Save result
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    # Print summary
    print("\n=== Verification Result ===")
    print(f"Decision: {result['decision']}")
    print(f"\nCompleteness: {result['checks']['completeness']['value']:.2%} (threshold: 90%)")
    print(f"Label Coverage: {result['checks']['label_coverage']['value']:.2%} (threshold: 100%)")
    
    print("\nReliability:")
    for axis, check in result['checks']['reliability'].items():
        print(f"  {axis}: α={check['value']:.3f} (threshold: 0.85)")
    
    if result['decision'] == 'FAIL':
        print("\nGATE FAILED - See verification_result.json for details")
        sys.exit(1)
    else:
        print("\nGATE PASSED - Corpus is valid")

if __name__ == '__main__':
    main()
