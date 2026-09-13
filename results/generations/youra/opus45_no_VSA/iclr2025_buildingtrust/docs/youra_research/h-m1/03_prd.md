# Product Requirements Document: H-M1

**Date:** 2026-08-08
**Hypothesis:** PC1,residual correlates positively with Behavioral Stability Index (BSI) computed on independent datasets (ρ > 0, p < 0.05)
**Type:** MECHANISM
**Gate:** MUST_WORK

---

## 1. Objective

Validate that the latent trustworthiness factor (PC1,residual) discovered in H-E1 predicts behavioral stability across paraphrase detection tasks. This tests the GRC theory's causal claim: high PC1 models exhibit consistent behavior on semantically equivalent inputs.

## 2. Success Criteria

| Metric | Threshold | Required |
|--------|-----------|----------|
| Pearson ρ | > 0 | Yes |
| p-value | < 0.05 | Yes |
| Sample size | ≥ 30 models | Yes |
| 95% CI | Excludes 0 | Yes |

## 3. Scope

### In Scope
- Load PC1,residual scores from H-E1 (~100 models)
- Compute BSI on PAWS-Wiki test set (8,000 pairs)
- Compute BSI on QQP validation set (40,430 pairs)
- Calculate correlation between PC1 and BSI
- Generate scatter plot with regression line

### Out of Scope
- Training new models
- Fine-tuning on paraphrase tasks
- Modifying PC1 computation from H-E1

## 4. Data Requirements

### Input Data
1. **H-E1 Results**: `h-e1/results/pc1_scores.csv`
   - Columns: model_name, pc1_score, log_params, release_date
   
2. **PAWS-Wiki**: `google-research-datasets/paws` (labeled_final, test split)
   - 8,000 sentence pairs with paraphrase labels
   
3. **QQP**: `nyu-mll/glue` (qqp config, validation split)
   - 40,430 question pairs with duplicate labels

### Output Data
- `h-m1/results/bsi_scores.csv`: model_name, paws_acc, qqp_acc, bsi_score
- `h-m1/results/correlation_results.json`: rho, p_value, ci_lower, ci_upper
- `h-m1/figures/pc1_vs_bsi_scatter.png`: Correlation visualization

## 5. Technical Constraints

- Must use same model set as H-E1 (ensure PC1 validity)
- BSI computed independently of PC1 (no data leakage)
- All inference deterministic (seed=42)
- Max sequence length: 256 tokens

## 6. Dependencies

- H-E1 must be VALIDATED (confirmed: λ₁=2.277, p=0.001)
- HuggingFace datasets library
- scipy.stats for correlation

## 7. Deliverables

1. `03_prd.md` - This document
2. `03_architecture.md` - System architecture
3. `03_logic.md` - Core algorithm pseudo-code
4. `03_config.md` - Hyperparameters and settings
5. `03_tasks.yaml` - Implementation task breakdown

---

*Phase 3 Implementation Planning - H-M1*
