# Configuration Specification: h-e1

**Date:** 2026-04-20  
**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (PoC)  
**Configuration Agent:** Configuration Specialist

Applied: EXISTENCE minimal config pattern, hardcoded dict pattern

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** Green-field project - designing new config schema  
**Config Files Found:** None - new config  
**Pattern Used:** Hardcoded dict (EXISTENCE tier)

---

## A-6: Visualization [Complexity: 11, Budget: 2]

**Applied:** EXISTENCE minimal config - hardcoded visualization parameters

### Configuration (Hardcoded Dict)

```python
# code/visualization/visualizer.py

VISUALIZATION_CONFIG = {
    # Output settings
    "output_dir": "./figures",
    "dpi": 300,
    "format": "png",
    
    # Figure size (inches)
    "figsize": (10, 6),
    
    # Color scheme
    "colors": {
        "success": "#2ecc71",  # Green
        "timeout": "#e74c3c",  # Red
        "target": "#3498db",   # Blue
    },
    
    # Gate metrics plot
    "gate_plot": {
        "target_correlation": 0.3,
        "bar_width": 0.35,
        "show_pvalue": True,
    },
    
    # Scatter plot
    "scatter": {
        "alpha": 0.6,
        "marker_size": 50,
        "jitter": 0.02,  # Vertical jitter for binary outcomes
    },
    
    # Distribution plots
    "distribution": {
        "bins": 20,
        "alpha": 0.7,
        "kde": True,  # Kernel density estimation overlay
    },
    
    # Trajectory examples
    "trajectory": {
        "n_examples_per_class": 3,
        "linewidth": 2,
        "show_std_band": False,  # Disabled for EXISTENCE simplicity
    },
    
    # ROC curve
    "roc": {
        "linewidth": 2,
        "show_diagonal": True,
        "show_auc": True,
    },
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Implement gate metrics visualization | Bar chart comparing r, ρ against target (0.3) with p-values |
| C-6-2 | Implement supporting visualizations | Scatter, distributions, trajectory examples, ROC curve |

---

## Global Experiment Configuration

**Applied:** Standard PyTorch/NumPy reproducibility defaults

### Configuration (Hardcoded Dict)

```python
# code/config.py

EXPERIMENT_CONFIG = {
    # Dataset
    "repo_url": "https://github.com/leanprover-community/mathlib",
    "commit_hash": "d88406ff7d5d41304c2f94222ac7852ecb4c38f2",  # LeanDojo Benchmark default
    "sample_size": 100,
    "random_seed": 42,
    
    # Experiment execution
    "timeout_seconds": 300,
    "confidence_window": 15,
    
    # Gate condition
    "target_correlation": 0.3,
    "significance_level": 0.05,
    
    # Output paths
    "results_dir": "./results",
    "figures_dir": "./figures",
    
    # Logging
    "log_level": "INFO",
    "progress_interval": 10,  # Print progress every N theorems
}
```

---

## Configuration Usage

### Visualization Module

```python
# code/visualization/visualizer.py

class ExperimentVisualizer:
    def __init__(self, output_dir: str = None):
        self.config = VISUALIZATION_CONFIG
        self.output_dir = output_dir or self.config["output_dir"]
        os.makedirs(self.output_dir, exist_ok=True)
    
    def plot_gate_metrics(self, r: float, rho: float, p_r: float, p_rho: float):
        """Generate mandatory gate metrics comparison plot."""
        cfg = self.config["gate_plot"]
        target = cfg["target_correlation"]
        
        fig, ax = plt.subplots(figsize=self.config["figsize"])
        
        # Bar positions
        x = np.arange(2)
        width = cfg["bar_width"]
        
        # Plot bars
        ax.bar(x - width/2, [r, rho], width, label="Observed", color=self.config["colors"]["success"])
        ax.axhline(y=target, color=self.config["colors"]["target"], linestyle="--", label=f"Target (r={target})")
        
        # Labels
        ax.set_ylabel("Correlation Coefficient")
        ax.set_title("Gate Condition: Correlation Metrics")
        ax.set_xticks(x)
        ax.set_xticklabels(["Pearson r", "Spearman ρ"])
        ax.legend()
        
        # P-values as text
        if cfg["show_pvalue"]:
            ax.text(0, r + 0.02, f"p={p_r:.4f}", ha="center", fontsize=9)
            ax.text(1, rho + 0.02, f"p={p_rho:.4f}", ha="center", fontsize=9)
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/gate_metrics.png", dpi=self.config["dpi"], format=self.config["format"])
        plt.close()
    
    def plot_scatter(self, derivatives: np.ndarray, outcomes: np.ndarray):
        """Scatter plot: confidence derivative vs timeout outcome."""
        cfg = self.config["scatter"]
        
        fig, ax = plt.subplots(figsize=self.config["figsize"])
        
        # Add jitter to binary outcomes for visibility
        outcomes_jittered = outcomes + np.random.uniform(-cfg["jitter"], cfg["jitter"], size=len(outcomes))
        
        # Separate by outcome
        success_mask = outcomes == 0
        timeout_mask = outcomes == 1
        
        ax.scatter(derivatives[success_mask], outcomes_jittered[success_mask], 
                   c=self.config["colors"]["success"], label="Success", 
                   alpha=cfg["alpha"], s=cfg["marker_size"])
        ax.scatter(derivatives[timeout_mask], outcomes_jittered[timeout_mask], 
                   c=self.config["colors"]["timeout"], label="Timeout", 
                   alpha=cfg["alpha"], s=cfg["marker_size"])
        
        ax.set_xlabel("Confidence Derivative (Entropy Std Dev)")
        ax.set_ylabel("Outcome (0=Success, 1=Timeout)")
        ax.set_title("Confidence Derivative vs Timeout Outcome")
        ax.legend()
        ax.set_ylim(-0.2, 1.2)
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/scatter_plot.png", dpi=self.config["dpi"], format=self.config["format"])
        plt.close()
    
    def plot_distributions(self, derivatives: np.ndarray, outcomes: np.ndarray):
        """Distribution comparison: success vs timeout groups."""
        cfg = self.config["distribution"]
        
        fig, ax = plt.subplots(figsize=self.config["figsize"])
        
        success_derivatives = derivatives[outcomes == 0]
        timeout_derivatives = derivatives[outcomes == 1]
        
        ax.hist(success_derivatives, bins=cfg["bins"], alpha=cfg["alpha"], 
                color=self.config["colors"]["success"], label="Success", density=True)
        ax.hist(timeout_derivatives, bins=cfg["bins"], alpha=cfg["alpha"], 
                color=self.config["colors"]["timeout"], label="Timeout", density=True)
        
        # KDE overlay
        if cfg["kde"]:
            from scipy.stats import gaussian_kde
            if len(success_derivatives) > 1:
                kde_success = gaussian_kde(success_derivatives)
                x_range = np.linspace(derivatives.min(), derivatives.max(), 100)
                ax.plot(x_range, kde_success(x_range), color=self.config["colors"]["success"], linewidth=2)
            if len(timeout_derivatives) > 1:
                kde_timeout = gaussian_kde(timeout_derivatives)
                ax.plot(x_range, kde_timeout(x_range), color=self.config["colors"]["timeout"], linewidth=2)
        
        ax.set_xlabel("Confidence Derivative")
        ax.set_ylabel("Density")
        ax.set_title("Distribution of Confidence Derivatives by Outcome")
        ax.legend()
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/distributions.png", dpi=self.config["dpi"], format=self.config["format"])
        plt.close()
    
    def plot_trajectory_examples(self, trajectories: list, outcomes: list):
        """Plot entropy trajectories for example theorems."""
        cfg = self.config["trajectory"]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Select examples
        success_indices = [i for i, o in enumerate(outcomes) if o == 0][:cfg["n_examples_per_class"]]
        timeout_indices = [i for i, o in enumerate(outcomes) if o == 1][:cfg["n_examples_per_class"]]
        
        # Plot success trajectories
        for idx in success_indices:
            ax1.plot(trajectories[idx], linewidth=cfg["linewidth"], 
                    color=self.config["colors"]["success"], alpha=0.7)
        ax1.set_xlabel("Proof Step")
        ax1.set_ylabel("Entropy")
        ax1.set_title("Success Examples (Low Variance)")
        ax1.grid(True, alpha=0.3)
        
        # Plot timeout trajectories
        for idx in timeout_indices:
            ax2.plot(trajectories[idx], linewidth=cfg["linewidth"], 
                    color=self.config["colors"]["timeout"], alpha=0.7)
        ax2.set_xlabel("Proof Step")
        ax2.set_ylabel("Entropy")
        ax2.set_title("Timeout Examples (High Variance)")
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/trajectory_examples.png", dpi=self.config["dpi"], format=self.config["format"])
        plt.close()
    
    def plot_roc_curve(self, derivatives: np.ndarray, outcomes: np.ndarray):
        """ROC curve for binary classification."""
        from sklearn.metrics import roc_curve, auc
        
        cfg = self.config["roc"]
        
        fig, ax = plt.subplots(figsize=self.config["figsize"])
        
        fpr, tpr, _ = roc_curve(outcomes, derivatives)
        roc_auc = auc(fpr, tpr)
        
        ax.plot(fpr, tpr, color=self.config["colors"]["success"], 
                linewidth=cfg["linewidth"], 
                label=f"ROC Curve (AUC = {roc_auc:.3f})")
        
        if cfg["show_diagonal"]:
            ax.plot([0, 1], [0, 1], color="gray", linestyle="--", linewidth=1, label="Random Classifier")
        
        ax.set_xlabel("False Positive Rate")
        ax.set_ylabel("True Positive Rate")
        ax.set_title("ROC Curve: Confidence Derivative as Timeout Predictor")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/roc_curve.png", dpi=self.config["dpi"], format=self.config["format"])
        plt.close()
```

### Main Experiment Script

```python
# code/run_experiment.py

from config import EXPERIMENT_CONFIG

def main():
    cfg = EXPERIMENT_CONFIG
    
    # Set random seed
    np.random.seed(cfg["random_seed"])
    
    # Initialize components
    print(f"Starting experiment with config:")
    print(f"  Sample size: {cfg['sample_size']}")
    print(f"  Timeout: {cfg['timeout_seconds']}s")
    print(f"  Confidence window: {cfg['confidence_window']} steps")
    
    # Create output directories
    os.makedirs(cfg["results_dir"], exist_ok=True)
    os.makedirs(cfg["figures_dir"], exist_ok=True)
    
    # [Rest of experiment logic...]
```

---

## Rationale for Non-Standard Values

**commit_hash:** Using LeanDojo Benchmark default commit (d88406ff...) as verified in official repository.

**jitter:** 0.02 vertical jitter added to binary scatter plot for visibility of overlapping points.

**n_examples_per_class:** 3 examples per class balances visual clarity with information density.

---

## Self-Validation

### Quick Checks
- [x] ONE format only (hardcoded dict)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values (commit_hash, jitter, n_examples_per_class)
- [x] Subtask count within budget (2/2)
- [x] Total length < 400 lines
- [x] Codebase Analysis (Serena) section included

### Serena MCP Validation
- [x] Green-field project → Serena skip is acceptable (noted in Codebase Analysis)

### EXISTENCE Tier Compliance
- [x] Single fixed config (no hyperparameter grid)
- [x] Default values from standard practices
- [x] 1 seed (42)
- [x] Minimal configuration for PoC
- [x] No ablation configs
- [x] No multiple config options

---

*Configuration optimized for EXISTENCE (PoC) tier - minimal hardcoded settings for correlation visualization*
*Next Phase: Phase 4 - Implementation*
