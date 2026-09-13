# Paper Summary: Best Practices for ML Experimentation (Michelucci & Venturini 2025)

**arXiv ID:** 2511.21354  
**Authors:** U. Michelucci, F. Venturini  
**Citations:** 1

## Key Contributions
- Structured guide for ML experiments: reproducibility, fair comparison, transparent reporting
- Proposes Logarithmic Overfitting Ratio (LOR) + Composite Overfitting Score (COS)
- Step-by-step workflow from dataset prep → model evaluation

## Methodology
- Workflow stages: dataset preparation → train/val/test splitting → model training → evaluation → documentation
- New overfitting metrics accounting for instability

## Experiments & Results
- LOR and COS capture overfitting AND instability (not just train/test gap)
- Reproducibility requires: dataset versioning, seed control, environment documentation
- Fair comparison requires: standardized splits, consistent metrics, transparent reporting

## Potential Relevance
- **Gap 2:** Documentation elements needed for reproducibility (dataset version, seeds, environment)
- **Validation metrics:** LOR/COS show importance of multi-dimensional evaluation
- **Best practices:** Checklist applicable to repository design recommendations
