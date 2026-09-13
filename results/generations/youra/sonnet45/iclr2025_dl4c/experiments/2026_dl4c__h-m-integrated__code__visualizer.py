"""
Visualization Generator for Mechanism Validation
"""
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict
from pathlib import Path
from config import AnalysisConfig

class MechanismVisualizer:
    """Generate mechanism validation plots"""
    
    def __init__(self, data: Dict[str, dict], ranks: Dict[str, Dict[str, float]], 
                 mechanism_results: dict, gate_results: dict):
        self.data = data
        self.ranks = ranks
        self.mechanism_results = mechanism_results
        self.gate_results = gate_results
        self.figure_dir = Path(AnalysisConfig.FIGURE_DIR)
        self.figure_dir.mkdir(exist_ok=True)
    
    def plot_dimension_rankings(self):
        """Plot 1: Dimension-wise rankings (bar chart)"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Prepare data
        models = list(self.ranks.keys())
        dimensions = AnalysisConfig.DIMENSIONS
        
        x = np.arange(len(models))
        width = 0.15
        
        for i, dim in enumerate(dimensions):
            ranks_for_dim = [self.ranks[m][dim] for m in models]
            ax.bar(x + i * width, ranks_for_dim, width, label=dim)
        
        ax.set_xlabel('Models')
        ax.set_ylabel('Percentile Rank (%)')
        ax.set_title('Dimension-wise Percentile Rankings')
        ax.set_xticks(x + width * 2)
        ax.set_xticklabels(models, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.figure_dir / 'dimension_rankings.png', dpi=150)
        plt.close()
    
    def plot_m1_execution_dominance(self):
        """Plot 2: M1 execution dominance (horizontal bar + threshold line)"""
        fig, ax = plt.subplots(figsize=(8, 5))
        
        m1 = self.mechanism_results['m1']
        models = m1['execution_models']
        ranks = m1['correctness_ranks']
        
        y_pos = np.arange(len(models))
        ax.barh(y_pos, ranks, color=['green' if r <= 15 else 'red' for r in ranks])
        ax.set_yticks(y_pos)
        ax.set_yticklabels(models)
        ax.set_xlabel('Correctness Percentile Rank (%)')
        ax.set_title(f'M1: Execution Model Correctness Dominance\n(Threshold: ≤15%, Mean: {m1["mean_rank"]:.1f}%)')
        ax.axvline(x=15, color='blue', linestyle='--', label='15% threshold')
        ax.legend()
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.figure_dir / 'm1_execution_dominance.png', dpi=150)
        plt.close()
    
    def plot_m2_preference_balance(self):
        """Plot 3: M2 preference balance (grouped bar or spider plot)"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        m2 = self.mechanism_results['m2']
        models = m2['preference_models']
        dimensions = AnalysisConfig.DIMENSIONS
        
        x = np.arange(len(models))
        width = 0.15
        
        for i, dim in enumerate(dimensions):
            ranks_for_dim = [self.ranks[m][dim] for m in models if m in self.ranks]
            if ranks_for_dim:
                ax.bar(x + i * width, ranks_for_dim, width, label=dim)
        
        ax.set_xlabel('Preference Models')
        ax.set_ylabel('Percentile Rank (%)')
        ax.set_title(f'M2: Preference Model Balance\n(Threshold: ≤30%, Mean: {m2["mean_rank"]:.1f}%)')
        ax.set_xticks(x + width * 2)
        ax.set_xticklabels(models, rotation=45, ha='right')
        ax.axhline(y=30, color='blue', linestyle='--', label='30% threshold')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.figure_dir / 'm2_preference_balance.png', dpi=150)
        plt.close()
    
    def plot_m3_variance_analysis(self):
        """Plot 4: M3 variance analysis (box plots)"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Group data by alignment method
        alignment_groups = {}
        for model, info in self.data.items():
            alignment_type = info['alignment_type']
            if alignment_type not in alignment_groups:
                alignment_groups[alignment_type] = []
            alignment_groups[alignment_type].append(info['correctness'])
        
        # Create box plots
        labels = list(alignment_groups.keys())
        data_to_plot = [alignment_groups[label] for label in labels]
        
        ax.boxplot(data_to_plot, labels=labels)
        ax.set_ylabel('Correctness Score')
        ax.set_title('M3: Within-Method Clustering Analysis')
        ax.grid(axis='y', alpha=0.3)
        
        # Add p-value annotation
        m3 = self.mechanism_results['m3']
        pvalue = m3['mannwhitneyu_pvalue']
        ax.text(0.5, 0.95, f"Mann-Whitney p-value: {pvalue:.4f}", 
                transform=ax.transAxes, ha='center', va='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig(self.figure_dir / 'm3_variance_analysis.png', dpi=150)
        plt.close()
    
    def plot_gate_metrics(self):
        """Plot 5: Gate metrics summary (status indicators)"""
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Prepare gate status data
        statuses = [
            ('M1: Execution\nDominance', self.gate_results['m1_status']),
            ('M2: Preference\nBalance', self.gate_results['m2_status']),
            ('M3: Clustering\nConsistency', self.gate_results['m3_status']),
            ('MUST_WORK\nGate', self.gate_results['gate_result'])
        ]
        
        y_pos = np.arange(len(statuses))
        colors = ['green' if status[1] == 'PASS' else 'red' for status in statuses]
        
        ax.barh(y_pos, [1] * len(statuses), color=colors, alpha=0.7)
        ax.set_yticks(y_pos)
        ax.set_yticklabels([s[0] for s in statuses])
        ax.set_xlim(0, 1)
        ax.set_xticks([])
        ax.set_title('Mechanism Validation Gate Results')
        
        # Add status labels
        for i, (_, status) in enumerate(statuses):
            ax.text(0.5, i, status, ha='center', va='center', 
                   fontweight='bold', fontsize=12, color='white')
        
        plt.tight_layout()
        plt.savefig(self.figure_dir / 'gate_metrics.png', dpi=150)
        plt.close()
    
    def generate_all_plots(self):
        """Generate all mechanism plots"""
        print("📊 Generating mechanism validation plots...")
        
        self.plot_dimension_rankings()
        print("  ✅ dimension_rankings.png")
        
        self.plot_m1_execution_dominance()
        print("  ✅ m1_execution_dominance.png")
        
        self.plot_m2_preference_balance()
        print("  ✅ m2_preference_balance.png")
        
        self.plot_m3_variance_analysis()
        print("  ✅ m3_variance_analysis.png")
        
        self.plot_gate_metrics()
        print("  ✅ gate_metrics.png")
        
        print(f"📁 All plots saved to {self.figure_dir}/")
