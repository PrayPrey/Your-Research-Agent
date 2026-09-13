# Experiment Brief: H-M3 Orthogonal Signals Enable Complementary Detection

**Hypothesis ID:** h-m3
**Type:** MECHANISM
**Gate:** MUST_WORK
**Generated:** 2026-08-28

---

## 1. Hypothesis Statement

**Under-If-Then-Because:**
Under closed-book QA conditions (TruthfulQA), if entropy and consistency capture different failure modes, then their correlation is low (r < 0.3) and discordant cases (where methods disagree) show differential predictive value.

**Success Criteria:**
- Primary: correlation(entropy, consistency) < 0.3
- Secondary: Discordant proportion > 0.15 AND winning-method AUROC > 0.6 per subset

**Failure Response:** EXPLORE — signals may be orthogonal only for subset of questions

---

## 2. Dataset Specification

| Attribute | Value |
|-----------|-------|
| **Name** | TruthfulQA |
| **Source** | HuggingFace: `truthfulqa/truthful_qa` |
| **Split** | generation (817 questions) |
| **Type** | standard |
| **Ground Truth** | best_answer vs incorrect_answers |

**Sample Size Justification:**
- Full TruthfulQA generation split: 817 questions
- Sufficient for correlation estimation with narrow CI
- 15% discordant = ~122 samples per subset (adequate for AUROC)

**Loading Information** (for Phase 4 download):
```python
from datasets import load_dataset
dataset = load_dataset("truthfulqa/truthful_qa", "generation")
```

---

## 3. Model Specification

| Attribute | Value |
|-----------|-------|
| **Name** | LLaMA-2-7B |
| **HuggingFace ID** | `meta-llama/Llama-2-7b-hf` |
| **Access** | Requires HF token with Meta approval |
| **Requirements** | ~14GB VRAM (fp16) |

**Loading Information** (for Phase 4 download):
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
```

---

## 4. Implementation Research Summary

### Archon Knowledge Base Findings

**[INFERRED]** Pattern 1: Signal Correlation Analysis
- Source: General statistical practice
- Key insight: Pearson r measures linear correlation; r < 0.3 indicates weak correlation
- Complementary: Spearman rho for monotonic relationship robustness

**[INFERRED]** Pattern 2: Discordant Case Analysis
- Source: Multi-classifier ensemble literature
- Key insight: Cases where classifiers disagree reveal complementary information
- Threshold: Rank difference > 50 percentile points = discordant

**[INFERRED]** Pattern 3: Subset AUROC Validation
- Source: SelfCheckGPT evaluation methodology
- Key insight: Evaluate method performance on subset where it "should" win
- Validation: If high-entropy-only subset shows entropy AUROC > 0.6, entropy captures unique signal

### Reference Implementations

**Repository**: potsawee/selfcheckgpt
- Consistency computation already implemented in H-M2
- Reuse consistency scores from H-M2 pipeline

**Repository**: oxford-AI-Language/LM-Polygraph
- Token entropy computation already implemented in H-M1
- Reuse entropy scores from H-M1 pipeline

---

## 5. Experimental Design

### 5.1 Prerequisites

**Required from H-M1:**
- Per-question token entropy scores (817 values)
- Entropy already correlated with incorrectness

**Required from H-M2:**
- Per-question consistency scores (817 values)
- Consistency already correlated with correctness

### 5.2 Variables

| Variable | Type | Values |
|----------|------|--------|
| Entropy scores | Input | From H-M1 |
| Consistency scores | Input | From H-M2 |
| Ground truth labels | Input | TruthfulQA correct/incorrect |
| Pearson r | Output | Correlation coefficient |
| Discordant proportion | Output | % with rank diff > 50 |
| Subset AUROCs | Output | AUROC per discordant subset |

### 5.3 Procedure

```
PROCEDURE OrthogonalityVerification:
    
    INPUT:
        entropy_scores: float[817]      # From H-M1
        consistency_scores: float[817]  # From H-M2
        labels: bool[817]               # Ground truth (True=correct)
    
    STEP 1 - Correlation Analysis:
        # Compute Pearson correlation
        r_pearson = pearsonr(entropy_scores, 1 - consistency_scores)
        # Note: 1 - consistency because high entropy = bad, low consistency = bad
        
        # Also compute Spearman for robustness
        r_spearman = spearmanr(entropy_scores, 1 - consistency_scores)
        
        # Check primary criterion
        IF r_pearson.statistic < 0.3:
            correlation_pass = True
        ELSE:
            correlation_pass = False
    
    STEP 2 - Rank Normalization:
        # Convert to percentile ranks [0, 1]
        entropy_rank = rankdata(entropy_scores) / len(entropy_scores)
        consistency_rank = rankdata(consistency_scores) / len(consistency_scores)
        
        # For consistency, invert so high rank = more suspicious
        consistency_rank_inv = 1 - consistency_rank
    
    STEP 3 - Discordant Case Identification:
        discordant_mask = []
        high_entropy_only = []  # Entropy flags, consistency doesn't
        high_inconsistency_only = []  # Consistency flags, entropy doesn't
        
        FOR i in range(817):
            rank_diff = abs(entropy_rank[i] - consistency_rank_inv[i])
            
            IF rank_diff > 0.5:  # 50 percentile point difference
                discordant_mask.append(True)
                
                IF entropy_rank[i] > consistency_rank_inv[i]:
                    high_entropy_only.append(i)
                ELSE:
                    high_inconsistency_only.append(i)
            ELSE:
                discordant_mask.append(False)
        
        discordant_proportion = sum(discordant_mask) / 817
    
    STEP 4 - Subset AUROC Analysis:
        # For high-entropy-only subset: does entropy predict well?
        IF len(high_entropy_only) >= 50:
            auroc_entropy_subset = roc_auc_score(
                labels[high_entropy_only],
                -entropy_scores[high_entropy_only]  # Negate: low entropy = correct
            )
        
        # For high-inconsistency-only subset: does consistency predict well?
        IF len(high_inconsistency_only) >= 50:
            auroc_consistency_subset = roc_auc_score(
                labels[high_inconsistency_only],
                consistency_scores[high_inconsistency_only]
            )
    
    STEP 5 - Success Evaluation:
        primary_pass = r_pearson.statistic < 0.3
        
        secondary_pass = (
            discordant_proportion > 0.15 AND
            auroc_entropy_subset > 0.6 AND
            auroc_consistency_subset > 0.6
        )
        
        RETURN {
            'correlation': r_pearson.statistic,
            'correlation_p': r_pearson.pvalue,
            'spearman_r': r_spearman.statistic,
            'discordant_proportion': discordant_proportion,
            'n_high_entropy_only': len(high_entropy_only),
            'n_high_inconsistency_only': len(high_inconsistency_only),
            'auroc_entropy_subset': auroc_entropy_subset,
            'auroc_consistency_subset': auroc_consistency_subset,
            'primary_pass': primary_pass,
            'secondary_pass': secondary_pass
        }
```

---

## 6. Statistical Analysis Plan

### 6.1 Primary Analysis

| Metric | Threshold | Test |
|--------|-----------|------|
| Pearson r | < 0.3 | Correlation coefficient |
| Spearman ρ | < 0.3 | Robustness check |

### 6.2 Secondary Analysis

| Metric | Threshold | Test |
|--------|-----------|------|
| Discordant proportion | > 0.15 | Simple count |
| Subset AUROC (entropy) | > 0.6 | ROC analysis |
| Subset AUROC (consistency) | > 0.6 | ROC analysis |

### 6.3 Visualization Plan

1. **Scatter Plot**: Entropy vs (1 - Consistency) with regression line
2. **Quadrant Plot**: Questions colored by ground truth, quadrants by median splits
3. **Subset ROC Curves**: ROC for each method on its "winning" subset

---

## 7. Expected Outputs

| Output | Format | Purpose |
|--------|--------|---------|
| `correlation_analysis.json` | JSON | r, p-value, spearman |
| `discordant_cases.csv` | CSV | Question IDs with discordant flags |
| `subset_auroc.json` | JSON | AUROC per subset |
| `scatter_entropy_consistency.png` | PNG | Correlation visualization |
| `quadrant_analysis.png` | PNG | Discordant case visualization |

---

## 8. Code Structure

```
h-m3/
├── orthogonality.py         # Main analysis script
├── config.yaml              # Thresholds and paths
└── results/
    ├── correlation_analysis.json
    ├── discordant_cases.csv
    ├── subset_auroc.json
    └── figures/
        ├── scatter_entropy_consistency.png
        └── quadrant_analysis.png
```

### 8.1 Implementation Skeleton

```python
# orthogonality.py
"""H-M3: Orthogonality verification between entropy and consistency signals."""

import json
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr, rankdata
from sklearn.metrics import roc_auc_score
import matplotlib.pyplot as plt

def load_scores(h_m1_results_path: str, h_m2_results_path: str) -> tuple:
    """Load entropy and consistency scores from H-M1 and H-M2."""
    with open(h_m1_results_path) as f:
        m1 = json.load(f)
    with open(h_m2_results_path) as f:
        m2 = json.load(f)
    
    entropy = np.array(m1['entropy_scores'])
    consistency = np.array(m2['consistency_scores'])
    labels = np.array(m1['labels'])  # Same labels
    
    return entropy, consistency, labels


def compute_correlation(entropy: np.ndarray, consistency: np.ndarray) -> dict:
    """Compute Pearson and Spearman correlation."""
    # Invert consistency so both signals point same direction (higher = more suspicious)
    inv_consistency = 1 - consistency
    
    r_pearson, p_pearson = pearsonr(entropy, inv_consistency)
    r_spearman, p_spearman = spearmanr(entropy, inv_consistency)
    
    return {
        'pearson_r': float(r_pearson),
        'pearson_p': float(p_pearson),
        'spearman_r': float(r_spearman),
        'spearman_p': float(p_spearman),
        'primary_pass': r_pearson < 0.3
    }


def identify_discordant(entropy: np.ndarray, consistency: np.ndarray) -> dict:
    """Identify discordant cases where methods disagree."""
    n = len(entropy)
    
    # Convert to percentile ranks
    e_rank = rankdata(entropy) / n
    c_rank_inv = 1 - rankdata(consistency) / n  # Invert: low consistency = high rank
    
    # Discordant = rank difference > 0.5
    rank_diff = np.abs(e_rank - c_rank_inv)
    discordant = rank_diff > 0.5
    
    high_entropy_only = (e_rank > c_rank_inv) & discordant
    high_inconsistency_only = (c_rank_inv > e_rank) & discordant
    
    return {
        'discordant_mask': discordant,
        'high_entropy_only': high_entropy_only,
        'high_inconsistency_only': high_inconsistency_only,
        'discordant_proportion': float(discordant.sum() / n),
        'n_discordant': int(discordant.sum())
    }


def compute_subset_auroc(entropy: np.ndarray, consistency: np.ndarray, 
                         labels: np.ndarray, disc: dict) -> dict:
    """Compute AUROC on discordant subsets."""
    results = {}
    
    # High-entropy-only subset
    mask_e = disc['high_entropy_only']
    if mask_e.sum() >= 50:
        # For AUROC: predict label=1 (correct), lower entropy = more likely correct
        results['auroc_entropy_subset'] = float(roc_auc_score(
            labels[mask_e], -entropy[mask_e]
        ))
        results['n_entropy_subset'] = int(mask_e.sum())
    
    # High-inconsistency-only subset
    mask_c = disc['high_inconsistency_only']
    if mask_c.sum() >= 50:
        # Higher consistency = more likely correct
        results['auroc_consistency_subset'] = float(roc_auc_score(
            labels[mask_c], consistency[mask_c]
        ))
        results['n_consistency_subset'] = int(mask_c.sum())
    
    return results


def plot_scatter(entropy: np.ndarray, consistency: np.ndarray, 
                 labels: np.ndarray, output_path: str):
    """Scatter plot of entropy vs 1-consistency."""
    plt.figure(figsize=(8, 6))
    colors = ['green' if l else 'red' for l in labels]
    plt.scatter(entropy, 1 - consistency, c=colors, alpha=0.5, s=20)
    plt.xlabel('Token Entropy (higher = more uncertain)')
    plt.ylabel('1 - Consistency (higher = more unstable)')
    plt.title('Entropy vs Inconsistency by Correctness')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()


def main():
    # Paths from H-M1 and H-M2
    entropy, consistency, labels = load_scores(
        '../h-m1/results/entropy_scores.json',
        '../h-m2/results/consistency_scores.json'
    )
    
    # Step 1: Correlation
    corr = compute_correlation(entropy, consistency)
    print(f"Pearson r: {corr['pearson_r']:.3f} (pass: {corr['primary_pass']})")
    
    # Step 2-3: Discordant cases
    disc = identify_discordant(entropy, consistency)
    print(f"Discordant proportion: {disc['discordant_proportion']:.2%}")
    
    # Step 4: Subset AUROC
    subset = compute_subset_auroc(entropy, consistency, labels, disc)
    
    # Combine results
    results = {**corr, **disc, **subset}
    results['secondary_pass'] = (
        disc['discordant_proportion'] > 0.15 and
        subset.get('auroc_entropy_subset', 0) > 0.6 and
        subset.get('auroc_consistency_subset', 0) > 0.6
    )
    
    # Save
    with open('results/correlation_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    plot_scatter(entropy, consistency, labels, 'results/figures/scatter_entropy_consistency.png')
    
    print(f"\n=== H-M3 RESULTS ===")
    print(f"Primary (r < 0.3): {'PASS' if corr['primary_pass'] else 'FAIL'}")
    print(f"Secondary: {'PASS' if results['secondary_pass'] else 'FAIL'}")


if __name__ == '__main__':
    main()
```

---

## 9. Resource Requirements

| Resource | Estimate |
|----------|----------|
| GPU hours | 0 (reuses H-M1/H-M2 outputs) |
| Compute | CPU only (correlation + AUROC) |
| Storage | ~1 MB (JSON + plots) |
| Dependencies | scipy, sklearn, matplotlib, numpy, pandas |

---

## 10. Success Criteria Summary

| Criterion | Threshold | Type |
|-----------|-----------|------|
| Pearson r | < 0.3 | Primary |
| Discordant proportion | > 0.15 | Secondary |
| Entropy subset AUROC | > 0.6 | Secondary |
| Consistency subset AUROC | > 0.6 | Secondary |

**Gate Decision:**
- PASS: r < 0.3 AND (discordant > 0.15 with winning-method AUROC > 0.6)
- FAIL: r >= 0.3 OR discordant <= 0.15
- EXPLORE: Weak orthogonality (0.3 <= r < 0.5) — analyze by question category

---

**Phase 2C Complete for H-M3** | Generated: 2026-08-28
