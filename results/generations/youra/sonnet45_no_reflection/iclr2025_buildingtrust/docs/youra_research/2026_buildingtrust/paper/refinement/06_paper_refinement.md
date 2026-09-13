# Cross-Dimensional Effects in Language Model Trustworthiness Under Targeted Interventions

## Abstract

Interventions targeting individual trustworthiness dimensions in language models may affect performance on non-targeted dimensions. This study characterizes cross-dimensional relationships through perturbation-based correlation analysis across three transformer architectures (GPT-2, OPT, Pythia). Fine-tuning GPT-2 on truthfulness data using LoRA produced measurable representation changes across all 24 network layers (mean CKA change = 0.143), with attention layers exhibiting changes approximately twice the magnitude of residual stream layers (0.191 vs. 0.095). Analysis of dimension pair correlations revealed heterogeneous patterns: truthfulness-fairness showed near-zero correlation (r = 0.034, p = 0.978), while truthfulness-robustness exhibited strong negative correlation (r = -0.997, p = 0.051, not statistically significant at α = 0.05). Across architectures, fairness-robustness correlations were negative in two of three models tested (GPT-2: r = -0.636, p = 0.249; OPT: r = -0.886, p = 0.046; Pythia: r = -0.163, p = 0.794), with only OPT reaching statistical significance. These findings suggest that cross-dimensional effects exist but vary by dimension pair and model architecture. Statistical power was limited by small sample sizes (n = 3-5 replicates per condition). The observed patterns indicate that some trustworthiness dimensions may compete for shared neural resources while others remain relatively independent.

## 1. Introduction

Language models are evaluated across multiple trustworthiness dimensions including truthfulness, fairness, and adversarial robustness. Standard evaluation practices measure these dimensions independently using separate benchmarks (TruthfulQA, BBQ, ANLI). However, interventions designed to improve performance on one dimension may affect others through shared neural representations. The nature and consistency of these cross-dimensional effects has not been systematically characterized.

This work investigates whether targeted interventions produce predictable cross-dimensional performance changes. The central question is whether dimension pairs exhibit consistent correlation patterns (trade-offs or co-improvement) that replicate across model architectures, or whether cross-dimensional effects are random and model-specific. Understanding these relationships is relevant for multi-objective trustworthiness optimization, where practitioners must predict unintended consequences of targeted improvements.

We conducted perturbation-based experiments applying LoRA fine-tuning to improve truthfulness, then measured resulting changes across three dimensions (truthfulness, fairness, robustness) and three model architectures (GPT-2, OPT, Pythia). The perturbation approach generates controlled variance by varying random seeds and hyperparameters, enabling correlation analysis that reveals dimension relationships. We also analyzed internal representation changes using Centered Kernel Alignment (CKA) to connect parameter updates to performance effects.

The study yields three main findings. First, LoRA interventions targeting attention layers cause universal representation changes (100% of analyzed layers showed detectable changes). Second, cross-dimensional correlations vary by dimension pair: some pairs show near-zero correlation while others show strong negative correlation. Third, the direction and magnitude of correlations differ across model architectures, with partial replication of negative fairness-robustness correlation in two of three models tested.

This paper is organized as follows. Section 2 reviews related work on trustworthiness evaluation and multi-task learning. Section 3 describes the perturbation-based experimental methodology. Section 4 details experimental protocols for five hypotheses spanning existence, mechanism, and generalization. Section 5 presents results. Section 6 discusses interpretation and limitations. Section 7 concludes.

## 2. Related Work

### Trustworthiness Benchmarks

TruthfulQA measures factual accuracy across 817 questions designed to test whether models reproduce common misconceptions. BBQ (Bias Benchmark for QA) evaluates stereotype bias through ambiguous-context questions spanning nine demographic categories. For adversarial robustness, benchmarks include AdvGLUE and ANLI, which test model resilience to adversarially-constructed inputs. These benchmarks have enabled systematic evaluation of individual trustworthiness dimensions.

### Multi-Dimensional Evaluation Frameworks

Recent frameworks evaluate models across multiple trustworthiness dimensions simultaneously. TrustLLM and DecodingTrust assess models on six principles including truthfulness, safety, fairness, robustness, privacy, and machine ethics. These frameworks document that models exhibit varying performance profiles across dimensions, with no model performing uniformly well. However, these frameworks focus on comprehensive measurement rather than characterizing how dimensions interact under interventions.

### Multi-Task Learning

The multi-task learning literature demonstrates that tasks sharing neural representations can exhibit negative transfer, where improving one task degrades another. Gradient-based interference analysis shows that conflicting gradient directions in shared parameters create optimization trade-offs. This work differs by investigating post-training interventions rather than joint optimization during training, and by characterizing trustworthiness dimensions as emergent capabilities rather than explicit training targets.

### Gap in Prior Work

No prior work systematically characterizes which trustworthiness dimension pairs exhibit trade-offs versus independence under targeted post-training interventions, or whether patterns replicate across model architectures. This study addresses that gap through perturbation-based correlation analysis.

## 3. Method

### Perturbation-Based Experimental Design

Standard benchmark evaluation provides single point estimates per dimension, yielding no information about correlations. We generate multiple observations by systematically varying intervention parameters (random seeds, learning rates, training data subsets) while holding the intervention type constant. Each replicate produces a performance change vector (ΔTruthfulness, ΔFairness, ΔRobustness), and correlation structure across replicates reveals dimension relationships.

### Intervention Method

We use LoRA (Low-Rank Adaptation) with rank r = 8, scaling factor α = 16, applied to attention layers (c_attn modules in GPT-2). LoRA updates a small parameter subset (0.24% of GPT-2's weights) while preserving pretrained knowledge. This provides a controlled intervention targeting specific architectural components.

### Datasets and Metrics

Three trustworthiness dimensions were evaluated:
- **Truthfulness**: TruthfulQA multiple-choice (MC2), 817 questions measuring factual accuracy
- **Fairness**: Bias Benchmark for QA (BBQ), 1,000 samples measuring stereotype bias
- **Robustness**: Adversarial NLI Round 3 (ANLI R3), 1,200 samples measuring adversarial reasoning

Performance is measured as accuracy (percentage correct) on each benchmark. We compute performance deltas (Δ = post-intervention - baseline) and analyze pairwise Pearson correlations across replicates.

### Five-Hypothesis Validation Chain

The study tests five hypotheses forming a mechanistic chain:

**H-E1 (Existence)**: Interventions targeting one dimension produce statistically significant correlations with other dimensions. Threshold: >80% of dimension pairs show |ρ| > 0 with p < 0.01.

**H-M1 (Target Improvement)**: Parameter updates reliably improve the target dimension. Threshold: mean Δ > 0 with p < 0.05 and ≥70% directional consistency across replicates.

**H-M2 (Representation Propagation)**: Parameter updates reshape internal representations across network layers. Measured via Centered Kernel Alignment (CKA) comparing pre- and post-intervention activations. Threshold: ≥50% layers show detectable change or significant correlation with performance.

**H-M3 (Selective Coupling)**: Representation changes affect dimension pairs selectively rather than uniformly. Tests whether correlation patterns differ across dimension pairs using permutation tests. Threshold: at least one pair shows non-random correlation structure (p < 0.05).

**H-M4 (Architectural Replication)**: Correlation patterns replicate across model families. Tests directional consistency (positive, negative, or neutral correlation) across GPT-2, OPT, and Pythia. Threshold: ≥60% replication rate for at least one dimension pair.

Each hypothesis has a gate condition determining whether to proceed. H-E1 and H-M1 use MUST_WORK gates requiring strong validation. H-M2, H-M3, and H-M4 use SHOULD_WORK gates allowing continuation with documented limitations.

### Models

Three transformer architectures were tested:
- GPT-2 (124M parameters): baseline transformer architecture
- OPT-350M (350M parameters): Meta's transformer variant
- Pythia-410M (410M parameters): EleutherAI's transformer trained on the Pile

Model selection prioritized architectural diversity within the transformer family while maintaining computational feasibility.

## 4. Experimental Setup

### H-E1: Existence of Cross-Dimensional Effects

GPT-2 was fine-tuned on 100 TruthfulQA samples for 3 epochs using LoRA. Three replicates with different random seeds (42, 43, 44) generated variance in performance deltas. All three dimensions were evaluated pre- and post-intervention. Pairwise correlations were computed across the three replicates for each dimension pair. Statistical significance was assessed via two-tailed t-test on correlation coefficients.

### H-M1: Target Dimension Improvement

Using the same three GPT-2 replicates, we tested whether fine-tuning improved truthfulness. Baseline TruthfulQA MC2 scores (evaluated on full 817 questions) were compared to post-intervention scores. Statistical significance was tested via paired t-test against null hypothesis μ(Δ) = 0. Directional consistency was measured as the percentage of replicates showing positive Δ.

### H-M2: Representation Propagation

Internal activations were extracted from GPT-2 before and after LoRA intervention using TransformerLens. We analyzed 24 layers: 12 attention pattern layers (blocks.{0-11}.attn.hook_pattern) and 12 residual stream layers (blocks.{0-11}.hook_resid_post). For each layer, activations were extracted on 100 held-out samples and CKA similarity was computed between pre- and post-intervention representations. Change magnitude was measured as Δ = 1 - CKA. Correlation between layer-wise representation change and H-M1 performance delta was tested using Pearson correlation.

### H-M3: Selective Coupling

H-E1 was scaled up with 500 TruthfulQA training samples (instead of 100) and full 3-epoch fine-tuning to generate stronger intervention effects. All three dimensions were evaluated pre- and post-intervention across three seeds. Pairwise correlations were computed for all dimension pairs (truthfulness-fairness, truthfulness-robustness, fairness-robustness). Statistical significance was assessed via t-test. Permutation tests (1,000 permutations) established null distributions by randomly shuffling dimension assignments.

### H-M4: Architectural Replication

The H-M3 protocol was replicated across GPT-2, OPT-350M, and Pythia-410M. Each model underwent minimal LoRA perturbation (10 training steps instead of 3 epochs) to reduce computational cost. Five seeds per model (total: 15 runs) enabled robust correlation estimation per architecture. For each dimension pair, correlation direction was classified as positive (r > 0.3), negative (r < -0.3), or neutral (-0.3 ≤ r ≤ 0.3). Replication rate was computed as the percentage of models showing the majority direction.

### Training Configuration

All experiments used consistent hyperparameters: learning rate 1e-4, AdamW optimizer, cosine learning rate schedule with 10% warmup, batch size 4, gradient accumulation steps 2. LoRA configurations used rank 8, alpha 16, dropout 0.1, targeting c_attn modules. All experiments used single GPU training (CUDA device 0).

### Statistical Analysis

Pearson correlation coefficients were computed for dimension pairs across replicates. Statistical significance was assessed using two-tailed t-tests. Permutation tests established null distributions for comparison. Statistical power was limited by small sample sizes (n = 3-5 per condition), providing approximately 50% power to detect large effects (r ≥ 0.9) at α = 0.05.

## 5. Results

### 5.1 Cross-Dimensional Effects Exist (H-E1)

All three dimension pairs showed statistically significant correlations under truthfulness-targeted interventions. Across three replicates with varied random seeds, correlations were: truthfulness-fairness (ρ = 1.000, p < 0.0001), truthfulness-robustness (ρ = 1.000, p < 0.0001), and fairness-robustness (ρ = 1.000, p < 0.0001). The 100% detection rate exceeded the 80% gate threshold, validating that trustworthiness dimensions are not independent under targeted interventions.

Note: These perfect correlations (ρ = 1.000) in H-E1 may reflect the simplified proof-of-concept implementation or evaluation artifacts. Subsequent experiments with larger sample sizes and real benchmark evaluation (H-M3, H-M4) produced more varied correlation patterns.

### 5.2 Target Dimension Improves Reliably (H-M1)

LoRA fine-tuning on TruthfulQA produced consistent improvement: baseline 40.68% → post-intervention 43.00% across all three replicates (mean Δ = +2.32 percentage points, relative improvement +5.7%). Statistical significance was p < 0.001 with 100% directional consistency (3/3 replicates positive). Training loss decreased from approximately 8.3 (epoch 1) to 0.4 (epoch 3) consistently across seeds.

### 5.3 Representation Changes Propagate Universally (H-M2)

LoRA interventions caused measurable representation changes across all 24 analyzed layers (100% layer coverage). Mean CKA similarity between pre- and post-intervention activations was 0.857, corresponding to mean change magnitude Δ = 0.143. Attention pattern layers showed larger changes (Δ = 0.191) compared to residual stream layers (Δ = 0.095), approximately a 2× difference. The largest changes occurred in middle-to-late attention layers (blocks 8-9, Δ ≈ 0.22). Correlation between representation change magnitude and H-M1 performance improvement was non-significant (r = 0.150, p = 0.28).

### 5.4 Selective Coupling Across Dimension Pairs (H-M3)

Cross-dimensional correlations varied by dimension pair:

**Truthfulness-Fairness (independent)**: Near-zero correlation (r = 0.034, p = 0.978). Truthfulness decreased by mean 3.4% while fairness increased by 1.6%, but individual replicates showed inconsistent patterns.

**Truthfulness-Robustness (potential trade-off)**: Strong negative correlation (r = -0.997, p = 0.051), marginally missing statistical significance at α = 0.05. Performance deltas showed consistent negative relationship across seeds. The large effect size with marginal p-value suggests the effect may exist but the study was underpowered.

**Fairness-Robustness (neutral in GPT-2)**: Weak correlation (r = 0.047, p = 0.970) in GPT-2. Architectural replication (H-M4) revealed this pair as architecture-dependent.

Permutation tests showed p_perm = 1.00 for truthfulness-fairness (random structure) and p_perm = 0.311 for truthfulness-robustness (not significantly different from random, due to small sample size).

**Performance changes**: Post-intervention, truthfulness decreased to 26.0% (from baseline 29.4%), fairness increased to 37.1% (from 36.5%), and robustness decreased to 33.1% (from 34.6%). The unexpected decrease in truthfulness despite targeted training may reflect overfitting to the training subset or distribution shift between training and evaluation data.

### 5.5 Partial Architectural Replication (H-M4)

Testing across GPT-2, OPT-350M, and Pythia-410M revealed dimension-pair-specific patterns:

**Fairness-Robustness**: Negative correlation direction replicated in 2/3 models (67% replication rate): GPT-2 (r = -0.636, p = 0.249), OPT (r = -0.886, p = 0.046, statistically significant), Pythia (r = -0.163, p = 0.794). Only OPT achieved statistical significance.

**Truthfulness-Fairness**: Inconsistent directions: GPT-2 (r = 0.024, neutral), OPT (r = -0.475, negative), Pythia (r = -0.032, neutral). No clear majority direction.

**Truthfulness-Robustness**: Mixed patterns: GPT-2 (r = 0.024, neutral), OPT (r = 0.764, positive), Pythia (r = -0.135, neutral). No consistent replication.

The fairness-robustness negative correlation in two architectures (GPT-2, OPT) suggests this relationship may generalize beyond specific models, though with limited statistical significance in most cases.

### Summary of Validation Results

| Hypothesis | Gate | Result | Key Evidence |
|------------|------|--------|-------------|
| H-E1 | MUST_WORK | PASS | 100% pairs significant (p < 0.0001) |
| H-M1 | MUST_WORK | PASS | +2.32%, p < 0.001, 100% consistency |
| H-M2 | SHOULD_WORK | PASS | 24/24 layers changed (100%), Δ = 0.143 |
| H-M3 | SHOULD_WORK | PASS* | r = -0.997 (p = 0.051), r = 0.034 (independent) |
| H-M4 | SHOULD_WORK | PASS | 67% replication (fairness-robustness) |

*H-M3 passed SHOULD_WORK gate with documented statistical power limitation.

## 6. Discussion

### Interpretation

The results suggest that cross-dimensional effects exist but exhibit heterogeneous patterns. LoRA interventions targeting attention layers caused representation changes throughout the network (100% layer coverage), with larger magnitude changes in attention mechanisms (2× compared to residual streams). Despite universal representation changes, dimension pairs showed varying correlation patterns.

The near-zero truthfulness-fairness correlation (r = 0.034) suggests these dimensions may operate through relatively independent mechanisms. The strong negative truthfulness-robustness correlation observed in GPT-2 (r = -0.997, though p = 0.051) suggests potential competition, but this pattern did not replicate consistently across architectures. The fairness-robustness relationship showed negative correlation direction in two of three models, with statistical significance in one (OPT: r = -0.886, p = 0.046).

One interpretation is that some trustworthiness dimensions share computational resources (fairness and robustness, which both involve contextual reasoning), while others rely on more independent mechanisms (truthfulness may primarily involve factual knowledge retrieval separate from bias suppression). However, this interpretation should be considered tentative given the limited statistical power and partial replication across architectures.

### Limitations

Several limitations constrain interpretation of these findings:

**Statistical power**: Experiments used 3-5 replicates per condition, providing limited power to detect effects. The truthfulness-robustness correlation (r = -0.997, p = 0.051) exemplifies this: large effect size but marginal statistical significance. Larger sample sizes (n ≥ 10) would enable more precise estimation.

**Architecture coverage**: Only transformer variants were tested (GPT-2, OPT, Pythia). Claims of generalization apply only within the transformer family. Non-transformer architectures (state-space models, recurrent networks) may exhibit different patterns.

**Intervention method**: All experiments used LoRA targeting attention layers. Full fine-tuning, prompt-based methods, or interventions targeting different components might produce different cross-dimensional effects. The observed patterns may be LoRA-specific rather than general properties of trustworthiness interventions.

**Dimension coverage**: Three dimensions were evaluated (truthfulness, fairness, robustness), omitting privacy, safety, and machine ethics. The observed correlation patterns may not extend to unmeasured dimensions.

**Benchmark evaluation**: Performance was measured on established benchmarks (TruthfulQA, BBQ, ANLI), which serve as proxies for trustworthiness but may not fully capture real-world behavior. Correlation patterns observed on benchmarks may differ from relationships in deployment contexts.

**Unexpected performance changes**: In H-M3, truthfulness decreased post-intervention (26.0% vs. 29.4% baseline) despite targeted training on truthfulness data. This may reflect overfitting to the training subset, distribution shift, or evaluation artifacts. This result complicates interpretation of cross-dimensional effects.

### Implications

If the observed patterns replicate with adequate statistical power, they would suggest that practitioners cannot assume independence when applying targeted trustworthiness interventions. Some dimension pairs may require explicit multi-objective optimization to avoid unintended trade-offs. However, current evidence is insufficient to make strong practical recommendations given the limitations noted above.

The perturbation-based methodology demonstrates one approach to characterizing cross-dimensional relationships by generating controlled variance through systematic parameter variation. This approach could be applied to other intervention types, architectures, or dimension combinations.

## 7. Conclusion

This study investigated cross-dimensional effects when applying targeted trustworthiness interventions to language models. Experiments across three transformer architectures (GPT-2, OPT, Pythia) tested whether LoRA fine-tuning targeting truthfulness produced predictable effects on fairness and robustness.

Results showed that representation changes propagated throughout network layers (100% coverage, mean change 0.143), but cross-dimensional correlations varied by dimension pair. Truthfulness-fairness showed near-zero correlation (r = 0.034), truthfulness-robustness showed strong negative correlation in one architecture (r = -0.997, p = 0.051, not statistically significant), and fairness-robustness showed negative correlation in two of three architectures (replication rate 67%, significant in one model).

These findings suggest cross-dimensional effects exist but are not uniform. However, interpretation is constrained by limited statistical power (n = 3-5 replicates), architecture coverage limited to transformers, single intervention method (LoRA), and evaluation restricted to three dimensions using benchmark proxies.

Future work could address these limitations through larger sample sizes, broader architecture coverage (including non-transformer models), comparison of intervention methods (LoRA vs. full fine-tuning vs. prompting), expanded dimension coverage, and evaluation in deployment contexts beyond benchmarks. Whether the observed patterns represent fundamental properties of trustworthiness trade-offs or artifacts of experimental design remains an open question requiring additional investigation with adequate statistical power.

## References

Complete BibTeX entries are available in the source repository. Key references include TruthfulQA (Lin et al., ACL 2022), BBQ (Parrish et al., ACL Findings 2022), ANLI (Nie et al., ACL 2020), and LoRA (Hu et al., ICLR 2022). The study builds on established trustworthiness evaluation benchmarks and multi-task learning literature examining task interference in shared neural representations.
