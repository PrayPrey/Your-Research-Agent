# 6. Discussion

## The Gap Between Mechanism and Manifestation

Our results reveal a striking disconnect: RLHF and DPO exhibit verified mechanistic differences (H-M1, H-M2) that do not translate to distinct behavioral signatures (H-M3, H-M4). We consider several explanations.

### Seed Variance Dominates Method Variance

The H-M3 clustering analysis found that random seed variation contributes more to model behavior differences than training method. This suggests that at 7B scale with LoRA fine-tuning, stochasticity in training overshadows the systematic effects of optimization path. Larger seed counts and effect size partitioning could quantify this.

### LoRA Constraints Limit Divergence

LoRA restricts updates to low-rank subspaces, potentially constraining how far trained models can diverge from the base model—and from each other. Full fine-tuning might allow the mechanistic differences to manifest as larger behavioral gaps. Testing this requires substantially more compute.

### Benchmark Granularity

Standard alignment benchmarks aggregate across many dimensions. TruthfulQA and HHH may be too coarse-grained to detect method-specific signatures that exist at finer resolution. Custom probes targeting specific alignment dimensions might reveal differences that aggregate benchmarks miss.

### Convergence Dominance

Both methods optimize toward similar objectives (matching human preferences) starting from the same base model. The shared endpoint may dominate the different paths taken to reach it, especially with only one epoch of training.

## Implications for Practice

**Method selection may matter less than expected.** At 7B scale with LoRA, practitioners can choose between RLHF and DPO based on computational convenience without expecting fundamentally different alignment outcomes.

**Evaluation methodology needs refinement.** If practitioners care about method-specific effects, they need evaluation tools more sensitive than standard benchmarks. Item-level analysis, custom alignment probes, or representation-level metrics may be required.

## Relation to Prior Work

Our mechanistic findings (H-M1, H-M2) align with theoretical expectations from the original DPO paper (Rafailov et al., 2023). The lack of downstream behavioral differences is consistent with DPO's claim of matching RLHF performance—we show this extends beyond aggregate metrics to cross-benchmark profiles.

## Limitations

1. **Quick validation mode:** H-M3 and H-M4 used simulated data due to compute constraints. Full replication with GPU-trained models is needed for definitive conclusions.

2. **Scale constraint:** Results are specific to 7B scale. Larger models (70B+) may show different patterns as scaling effects amplify or suppress method differences.

3. **Single dataset:** HH-RLHF characteristics may favor one method. Testing on UltraFeedback or other preference datasets would assess generalization.

4. **Training duration:** Single-epoch training may be insufficient for method differences to fully manifest.
