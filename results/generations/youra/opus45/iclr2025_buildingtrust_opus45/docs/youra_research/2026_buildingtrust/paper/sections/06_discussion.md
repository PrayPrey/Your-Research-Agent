# Discussion

Our experiments reveal that RLHF instruction tuning fundamentally reshapes the confidence-correctness relationship in language models through geometric distortion, not merely scalar rescaling. We discuss the implications of these findings, acknowledge limitations, and consider broader impacts.

## Key Findings

**Finding 1: Temperature Scaling is Necessary but Insufficient**

The geometric nature of RLHF-induced distortion explains a puzzling observation in practice: temperature scaling can improve ECE substantially [Khanmohammadi et al., 2025] while confidence-based decision making remains unreliable. Temperature scaling is a scalar correction—it adjusts the magnitude of probabilities but cannot restore discriminative ability lost through geometric distortion.

This has direct implications for deployment. Practitioners often assume that post-hoc calibration "fixes" RLHF models. Our results suggest this assumption is only partially correct: calibration metrics (ECE) may improve while discrimination metrics (AUROC, refinement) remain degraded. For applications where confidence-based decisions matter—selective prediction, uncertainty quantification, human-AI collaboration—calibration alone is insufficient.

**Finding 2: RLHF Creates a Discrimination-Capability Tradeoff**

The consistent pattern across model families—higher instruction-following capability correlating with worse confidence discrimination—suggests RLHF creates an implicit tradeoff. The Bradley-Terry preference model rewards confident-sounding responses because human annotators often prefer decisive answers. This selection pressure improves helpfulness but degrades confidence reliability.

Model providers may be making different points on this tradeoff curve: Mistral's larger margin inflation (16.79x vs 3.06x) suggests more aggressive RLHF compared to Qwen. Understanding this tradeoff opens possibilities for calibration-aware RLHF that explicitly penalizes margin inflation for incorrect predictions.

**Finding 3: Discriminative Degradation is Robust Across Architectures**

The effect is consistent across Qwen (Chinese origin) and Mistral (European origin) families despite different training pipelines, pretraining data, and organizational contexts. This cross-family consistency strengthens the causal attribution to RLHF rather than vendor-specific implementation choices.

## Limitations

**Limitation 1: Llama Family Not Tested**

We were unable to test the Llama-2-7B family due to HuggingFace model gating. While two families showing consistent effects is strong evidence, testing a third major family would further strengthen generalizability claims.

*Why acceptable:* The consistent effects across two independently-developed model families (Qwen, Mistral) suggest RLHF is the cause. Llama uses similar RLHF procedures [Touvron et al., 2023], making it unlikely to behave qualitatively differently.

*Future work:* Obtain Llama access for complete cross-family validation.

**Limitation 2: 7B Scale Only**

Our experiments focus on 7B-parameter models. Effect magnitudes may vary with model scale—larger models might show smaller or larger distortion depending on how RLHF training scales.

*Why acceptable:* The 7B scale is a common deployment target where our findings are directly actionable. Effect direction is likely consistent across scales even if magnitude varies.

*Future work:* Scale study across 1B, 7B, 13B, and 70B parameter models.

**Limitation 3: MMLU Dataset Specific**

We evaluate only on MMLU. Other benchmarks (TruthfulQA, ARC, CommonsenseQA) may show different effect magnitudes depending on task characteristics.

*Why acceptable:* MMLU is a standard calibration benchmark with 57 diverse subjects. The large sample size (14,042) provides high statistical power. Domain diversity within MMLU provides some internal validation.

*Future work:* Extend to TruthfulQA (factual accuracy), ARC (reasoning), and CommonsenseQA (common sense).

**Limitation 4: Bootstrap Methodology Assumptions**

Bootstrap confidence intervals assume i.i.d. samples. MMLU questions may have domain clustering that violates this assumption.

*Why acceptable:* Our effect sizes are very large (Cohen's d = 11-29), making conclusions robust to moderate assumption violations. Permutation tests provide a complementary non-parametric check.

## Theoretical Implications

Our findings connect to several theoretical questions:

**What happens to learned representations during RLHF?**

The geometric distortion suggests RLHF doesn't just adjust output layer weights—it reshapes internal representations in ways that affect the confidence-correctness mapping. Understanding this mechanistically could inform calibration-aware training.

**Is the distortion reversible?**

If geometric distortion arises from specific RLHF training dynamics, targeted fine-tuning might partially restore discrimination. Alternatively, the distortion might be permanent given standard fine-tuning budgets.

**How does DPO compare to PPO-based RLHF?**

Direct Preference Optimization [Rafailov et al., 2023] optimizes the same implicit reward as RLHF without explicit reward modeling. Comparing distortion patterns between DPO and PPO-based training could reveal whether the distortion arises from the objective itself or from specific training dynamics.

## Broader Impact

This work identifies a limitation of current RLHF practices that is relevant to AI safety. Our findings do not enable new harms—rather, they reveal an existing failure mode that practitioners should be aware of.

**Positive impacts:**
- Improved awareness of RLHF's confidence consequences
- Actionable guidance for deployment (don't assume temperature scaling is sufficient)
- Foundation for calibration-aware RLHF research

**Potential negative considerations:**
- Malicious actors could exploit unreliable confidence signals—but this vulnerability already exists; our work helps defenders understand it
- Highlighting RLHF limitations could slow beneficial deployment—but informed deployment is safer than uninformed deployment

We believe the benefits of transparency about RLHF's effects outweigh potential downsides.
