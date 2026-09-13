"""
Main Analysis Orchestrator for H-M-integrated Mechanism Validation
"""
import json
import yaml
import numpy as np
from pathlib import Path
from datetime import datetime

from config import AnalysisConfig
from data_loader import H_E1_ResultsLoader
from ranking_analyzer import PercentileRankingAnalyzer
from variance_analyzer import VarianceAnalyzer
from statistical_tests import MechanismTester
from gate_validator import GateValidator
from visualizer import MechanismVisualizer

def convert_to_serializable(obj):
    """Convert numpy types to native Python types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    return obj

def main():
    """Execute complete mechanism analysis workflow"""
    
    print("=" * 60)
    print("H-M-INTEGRATED MECHANISM ANALYSIS")
    print("=" * 60)
    print()
    
    # Create output directories
    Path(AnalysisConfig.OUTPUT_DIR).mkdir(exist_ok=True)
    Path(AnalysisConfig.FIGURE_DIR).mkdir(exist_ok=True)
    
    # Step 1: Load H-E1 results
    print("📊 Step 1: Loading H-E1 results...")
    loader = H_E1_ResultsLoader()
    data = loader.load_results()
    print(f"  ✅ Loaded data for {len(data)} models")
    print()
    
    # Step 2: Compute percentile rankings
    print("📈 Step 2: Computing percentile rankings...")
    ranking_analyzer = PercentileRankingAnalyzer(data)
    ranks = ranking_analyzer.compute_all_ranks()
    print(f"  ✅ Computed ranks for {len(AnalysisConfig.DIMENSIONS)} dimensions")
    print()
    
    # Step 3: Analyze variance
    print("📉 Step 3: Analyzing variance...")
    variance_analyzer = VarianceAnalyzer(data)
    m3_results = variance_analyzer.test_m3_clustering()
    print(f"  ✅ M3 clustering test: {'PASS' if m3_results['m3_passed'] else 'FAIL'}")
    print(f"     Mann-Whitney p-value: {m3_results['mannwhitneyu_pvalue']:.4f}")
    print()
    
    # Step 4: Run statistical tests (M1, M2, M3)
    print("🧪 Step 4: Running statistical tests...")
    tester = MechanismTester(data, ranks)
    mechanism_results = tester.test_all_mechanisms(m3_results)
    
    m1 = mechanism_results['m1']
    m2 = mechanism_results['m2']
    
    print(f"  M1 (Execution Dominance): {'PASS' if m1['m1_passed'] else 'FAIL'}")
    print(f"     Mean correctness rank: {m1['mean_rank']:.1f}% (threshold: ≤15%)")
    print()
    print(f"  M2 (Preference Balance): {'PASS' if m2['m2_passed'] else 'FAIL'}")
    print(f"     Mean rank across all dimensions: {m2['mean_rank']:.1f}% (threshold: ≤30%)")
    print()
    print(f"  M3 (Clustering Consistency): {'PASS' if m3_results['m3_passed'] else 'FAIL'}")
    print(f"     p-value: {m3_results['mannwhitneyu_pvalue']:.4f} (threshold: <0.05)")
    print()
    
    # Step 5: Validate gate (M1 AND M2)
    print("🚪 Step 5: Validating MUST_WORK gate...")
    validator = GateValidator(mechanism_results)
    gate_results = validator.evaluate_gate()
    
    print(f"  Gate Result: {gate_results['gate_result']}")
    print(f"  Gate Type: {gate_results['gate_type']}")
    
    if gate_results['gate_result'] == 'FAIL':
        print("\n  ❌ FAILURE REASONS:")
        for reason in gate_results['failure_reasons']:
            print(f"     - {reason}")
    else:
        print("  ✅ All required mechanisms validated!")
    print()
    
    # Step 6: Generate visualizations
    print("🎨 Step 6: Generating visualizations...")
    visualizer = MechanismVisualizer(data, ranks, mechanism_results, gate_results)
    visualizer.generate_all_plots()
    print()
    
    # Step 7: Save results
    print("💾 Step 7: Saving results...")
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'hypothesis_id': 'h-m-integrated',
        'gate_result': gate_results['gate_result'],
        'gate_type': gate_results['gate_type'],
        'mechanisms': {
            'm1': {
                'passed': convert_to_serializable(m1['m1_passed']),
                'mean_rank': convert_to_serializable(m1['mean_rank']),
                'threshold': convert_to_serializable(m1['threshold']),
                'execution_models': m1['execution_models'],
                'correctness_ranks': convert_to_serializable(m1['correctness_ranks'])
            },
            'm2': {
                'passed': convert_to_serializable(m2['m2_passed']),
                'mean_rank': convert_to_serializable(m2['mean_rank']),
                'threshold': convert_to_serializable(m2['threshold']),
                'preference_models': m2['preference_models']
            },
            'm3': {
                'passed': convert_to_serializable(m3_results['m3_passed']),
                'pvalue': convert_to_serializable(m3_results['mannwhitneyu_pvalue']),
                'threshold': convert_to_serializable(AnalysisConfig.M3_PVALUE_THRESHOLD),
                'intra_variances': convert_to_serializable(m3_results['intra_variances'])
            }
        },
        'diagnostics': convert_to_serializable(gate_results)
    }
    
    # Save as JSON
    results_file = Path(AnalysisConfig.OUTPUT_DIR) / 'mechanism_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"  ✅ Results saved to {results_file}")
    
    # Save ranks as CSV for reference
    import pandas as pd
    ranks_df = pd.DataFrame(ranks).T
    ranks_file = Path(AnalysisConfig.OUTPUT_DIR) / 'model_ranks.csv'
    ranks_df.to_csv(ranks_file)
    print(f"  ✅ Ranks saved to {ranks_file}")
    print()
    
    # Final summary
    print("=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"Gate Result: {gate_results['gate_result']}")
    print(f"M1: {'✅ PASS' if m1['m1_passed'] else '❌ FAIL'}")
    print(f"M2: {'✅ PASS' if m2['m2_passed'] else '❌ FAIL'}")
    print(f"M3: {'✅ PASS' if m3_results['m3_passed'] else '⚠️ FAIL (optional)'}")
    print("=" * 60)
    
    return 0 if gate_results['gate_result'] == 'PASS' else 1

if __name__ == '__main__':
    exit(main())
