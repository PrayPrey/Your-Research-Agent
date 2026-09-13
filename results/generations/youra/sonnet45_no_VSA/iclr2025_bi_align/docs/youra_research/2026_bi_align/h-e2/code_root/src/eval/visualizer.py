import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

class Visualizer:
    @staticmethod
    def plot_error_distribution(results: pd.DataFrame, save_path: str) -> None:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        cnn_errors = results[results['model'].isin([
            'resnet18', 'resnet34', 'resnet50', 'vgg16',
            'densenet121', 'mobilenet_v2', 'efficientnet_b0', 'shufflenet_v2_x1_0'
        ])]['relative_error']
        
        transformer_errors = results[~results['model'].isin([
            'resnet18', 'resnet34', 'resnet50', 'vgg16',
            'densenet121', 'mobilenet_v2', 'efficientnet_b0', 'shufflenet_v2_x1_0'
        ])]['relative_error']
        
        parts = ax.violinplot([cnn_errors, transformer_errors], showmeans=True, showmedians=True)
        ax.set_xticks([1, 2])
        ax.set_xticklabels(['CNN', 'Transformer'])
        ax.set_ylabel('Relative Error')
        ax.set_title('Error Distribution by Architecture Type')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
    
    @staticmethod
    def plot_predicted_vs_actual(results: pd.DataFrame, save_path: str) -> None:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.scatter(results['ground_truth_mb'], results['predicted_mb'], alpha=0.6)
        
        min_val = min(results['ground_truth_mb'].min(), results['predicted_mb'].min())
        max_val = max(results['ground_truth_mb'].max(), results['predicted_mb'].max())
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', label='Perfect prediction')
        
        from scipy.stats import pearsonr
        r, _ = pearsonr(results['ground_truth_mb'], results['predicted_mb'])
        ax.text(0.05, 0.95, f'R² = {r**2:.3f}', transform=ax.transAxes, 
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        ax.set_xlabel('Ground Truth Memory (MB)')
        ax.set_ylabel('Predicted Memory (MB)')
        ax.set_title('Predicted vs Actual Memory')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
    
    @staticmethod
    def plot_length_bin_analysis(results: pd.DataFrame, save_path: str) -> None:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.text(0.5, 0.5, 'Length bin analysis requires stratified_bin column', 
               transform=ax.transAxes, ha='center', va='center')
        
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
    
    @staticmethod
    def generate_summary_table(results: pd.DataFrame) -> str:
        cnn_results = results[results['model'].isin([
            'resnet18', 'resnet34', 'resnet50', 'vgg16',
            'densenet121', 'mobilenet_v2', 'efficientnet_b0', 'shufflenet_v2_x1_0'
        ])]
        
        transformer_results = results[~results['model'].isin(cnn_results['model'].unique())]
        
        summary = "# Results Summary\n\n"
        summary += "| Metric | CNN | Transformer | All |\n"
        summary += "|--------|-----|-------------|-----|\n"
        
        cnn_median = cnn_results['relative_error'].median() if len(cnn_results) > 0 else 0
        transformer_median = transformer_results['relative_error'].median() if len(transformer_results) > 0 else 0
        all_median = results['relative_error'].median()
        
        summary += f"| Median Error | {cnn_median:.3f} | {transformer_median:.3f} | {all_median:.3f} |\n"
        
        cnn_p95 = cnn_results['relative_error'].quantile(0.95) if len(cnn_results) > 0 else 0
        transformer_p95 = transformer_results['relative_error'].quantile(0.95) if len(transformer_results) > 0 else 0
        all_p95 = results['relative_error'].quantile(0.95)
        
        summary += f"| P95 Error | {cnn_p95:.3f} | {transformer_p95:.3f} | {all_p95:.3f} |\n"
        
        return summary
