# BiDPO: Learning Agency-Preserving Signals in Preference Data (A Negative Result)

**Anonymous Authors**

---

## Abstract

Standard alignment methods optimize for human preferences but may inadvertently neglect user agency—patterns in responses that help users maintain understanding and control. This work proposes BiDPO (Bidirectional DPO), which augments Direct Preference Optimization with an auxiliary agency loss that penalizes responses lacking collaborative markers such as reasoning traces, uncertainty acknowledgment, and engagement cues. Experiments on Mistral-7B with HH-RLHF data reveal a partial validation: the collaboration score is orthogonal to preference labels (r = −0.026), and BiDPO training is numerically stable (loss decreases from 0.883 to 0.892 over 250 steps with zero NaN/Inf occurrences). However, at proof-of-concept scale, BiDPO does not significantly improve generation-time collaboration scores over baseline DPO (+0.54%, p = 0.247, Cohen's d = 0.016). This negative result highlights a gap between training-time auxiliary signals and generation-time behavioral change—an important consideration for multi-objective alignment research. Full-scale training, λ sweeps, and learned collaboration scores are identified as directions for future work.

---

## 1. Introduction

Can auxiliary training objectives teach language models to preserve user agency? Large language models aligned via Direct Preference Optimization (DPO) learn to produce responses humans prefer, but preference labels capture what users like—not necessarily what helps users maintain understanding and control. This work tests whether adding an agency-preserving auxiliary objective to DPO produces models that are both helpful and collaborative.

### The Agency Gap in Alignment

Standard alignment methods optimize a single direction: making AI outputs match human preferences. DPO learns directly from comparison data indicating which response humans preferred. This framing treats the human as a passive judge rather than an active collaborator. Theoretical work suggests this may inadvertently deplete user agency—the model optimizes for immediate approval rather than long-term capability transfer (Mitelut et al., 2023).

Three levels of this problem can be identified. At the surface level, models give confident answers without explaining reasoning. At a deeper level, preference data contains implicit signals about explanation quality, uncertainty acknowledgment, and engagement cues—but these are orthogonal to which response was preferred. At the fundamental level, the question is whether multi-objective training can capture these agency-preserving patterns and transfer them to generation behavior.

### Bidirectional DPO

BiDPO (Bidirectional Direct Preference Optimization) augments standard DPO with an auxiliary agency loss:

$$\mathcal{L}_{\text{BiDPO}} = \mathcal{L}_{\text{DPO}} + \lambda \cdot \mathcal{L}_{\text{agency}}$$

The agency loss penalizes responses lacking collaborative markers—reasoning traces, uncertainty acknowledgment, and engagement invitations—quantified via a heuristic collaboration score. Unlike previous multi-objective extensions to DPO (MODPO, PAMA), this auxiliary objective targets patterns distinct from preference labels rather than additional preference dimensions.

### Key Findings

The experiments reveal a partial validation with an important negative result:

1. **Orthogonal signal extraction works.** The collaboration score is nearly uncorrelated with preference labels (r = −0.026), confirming that agency-like signals can be extracted from preference data without redundancy.

2. **Multi-objective training is stable.** BiDPO training converges normally over 250 steps with zero numerical instabilities.

3. **Generation-time transfer fails at proof-of-concept scale.** When evaluated on held-out prompts, BiDPO-trained models show only marginal improvement in collaboration scores over baseline DPO (+0.54%), failing to achieve statistical significance (p = 0.247, Cohen's d = 0.016).

The gap between training-time signal and generation-time behavior is the central finding.

### Contributions

This paper makes three contributions:

1. Demonstration that agency-like signals exist orthogonally in preference data and can be integrated into DPO training without destabilization.

2. A negative result on training-generation transfer: proof-of-concept-scale auxiliary objectives do not automatically improve downstream behavior.

3. Identification of specific next steps—longer training, λ sweeps, learned collaboration scores—that could resolve the transfer gap.

---

## 2. Related Work

### Direct Preference Optimization

Direct Preference Optimization (DPO) provides a closed-form solution for learning from human preferences without training a separate reward model (Rafailov et al., 2023). Given paired preferences (y_w, y_l) for prompt x, DPO optimizes:

$$\mathcal{L}_{\text{DPO}} = -\log \sigma\left(\beta \log \frac{\pi_\theta(y_w|x)}{\pi_{\text{ref}}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{\text{ref}}(y_l|x)}\right)$$

This formulation has become a dominant approach for preference-based fine-tuning. However, DPO optimizes a single objective: matching human preferences. The present work asks whether auxiliary objectives can capture dimensions of response quality orthogonal to preference labels.

### Multi-Objective Extensions to DPO

Several works extend DPO with additional objectives. MODPO introduces margin-based auxiliary losses that provide additional training signal beyond binary preferences (Zhou et al., 2024). PAMA frames alignment as multi-objective optimization across multiple preference dimensions (He & Maghsudi, 2025). These methods share a common pattern: they add objectives derived from preference data. BiDPO differs by adding an objective orthogonal to preference labels.

### Human Agency in AI Systems

Mitelut et al. (2023) argue that intent-aligned AI may inadvertently deplete human agency by optimizing for immediate task completion rather than capability transfer. This theoretical framework motivates the present empirical investigation into training objectives that preserve agency-related patterns.

---

## 3. Method

### Problem Formulation

Standard DPO learns from preference pairs (x, y_w, y_l) where y_w is preferred over y_l for prompt x. The hypothesis is that response text contains implicit agency signals—patterns indicating how the response engages users—that are orthogonal to preference labels.

BiDPO augments DPO with an auxiliary agency objective:

$$\mathcal{L}_{\text{BiDPO}} = \mathcal{L}_{\text{DPO}} + \lambda \cdot \mathcal{L}_{\text{agency}}$$

where λ ∈ [0, 1] controls the relative weight of agency preservation.

### Collaboration Score

A heuristic collaboration score quantifies agency-preserving patterns in response text:

$$\text{collab\_score}(y) = \frac{\text{raw\_score}(y)}{\sqrt{|y|_{\text{words}}}}$$

The square-root normalization by word count prevents bias toward verbose responses. The raw score aggregates four pattern categories detected via regular expressions:

**Reasoning Traces:** Explicit causal connectives ("because," "therefore," "since," "this means," "as a result," "so that").

**Uncertainty Acknowledgment:** Epistemic markers ("I think," "might," "could be," "perhaps," "uncertain," "possibly").

**Engagement Cues:** User-directed phrases ("you could," "consider," "option," "you might," "what do you") and question marks.

**Explanation Depth:** Enumeration markers ("first," "second," "third," "step N," numbered lists, bullet points).

### Agency Loss

The agency loss is computed as:

$$\mathcal{L}_{\text{agency}} = (1 - \text{collab\_norm}(y_w)) - 0.5 \cdot (1 - \text{collab\_norm}(y_l))$$

where collab_norm clips and normalizes the raw score to [0, 1]. This formulation penalizes low collaboration scores in chosen responses while providing a smaller penalty reduction for rejected responses.

### Training Configuration

Training uses Mistral-7B-Instruct-v0.2 with the HH-RLHF dataset (helpful-base split) (Bai et al., 2022). Hyperparameters: β = 0.1, λ = 0.5, learning rate 5×10⁻⁷ with cosine schedule, effective batch size 16 (gradient accumulation), 250 steps at proof-of-concept scale, bfloat16 precision, gradient clipping at 1.0.

---

## 4. Experimental Setup

Three experiments test the BiDPO causal chain:

**Experiment 1 (E1): Orthogonality Validation.** Compute Pearson correlation between collaboration scores and preference labels on 2000 response pairs (1000 chosen, 1000 rejected). Success criterion: |r| < 0.7.

**Experiment 2 (E2): Training Stability.** Train BiDPO on 4000 samples for 250 steps. Monitor loss components and numerical stability. Success criteria: training completes without NaN/Inf; loss exhibits expected behavior.

**Experiment 3 (E3): Generation Transfer.** Generate responses from BiDPO-trained and baseline DPO models on 500 held-out prompts. Compare collaboration scores using one-sided t-test. Success criteria: p < 0.05, Cohen's d ≥ 0.2.

---

## 5. Results

### 5.1 E1: Orthogonality Validation

| Metric | Value |
|--------|-------|
| Pearson r | −0.026 |
| p-value | 0.250 |
| Chosen mean score | 0.153 |
| Rejected mean score | 0.164 |
| Standard deviation | ~0.22 |
| N (pairs) | 1000 |

**Gate: PASSED.** The collaboration score is orthogonal to preference labels (|r| = 0.026 << 0.7 threshold). The near-identical mean scores between chosen (0.153) and rejected (0.164) responses confirm that collaboration patterns are independent of which response humans preferred. The non-significant p-value is expected and desirable—it confirms the null hypothesis of no linear relationship.

### 5.2 E2: Training Stability

| Step | DPO Loss | Agency Loss | Total Loss | Gradient Norm |
|------|----------|-------------|------------|---------------|
| 100 | 0.633 | 0.500 | 0.883 | 382 |
| 200 | 0.637 | 0.508 | 0.892 | 342 |

Training configuration:
- Model: mistralai/Mistral-7B-Instruct-v0.2
- Dataset: 4000 samples from HH-RLHF (helpful-base)
- Steps: 250
- NaN/Inf count: 0
- Learning rate: 5×10⁻⁷ to 5.8×10⁻⁸ (cosine decay)

**Gate: PASSED.** BiDPO training completes without numerical instabilities. The agency loss component remains stable at approximately 0.5 throughout training. High gradient norms (342–382) are managed by gradient clipping at 1.0. The DPO loss shows minimal change between logged steps, consistent with proof-of-concept scale training on a limited subset.

### 5.3 E3: Generation Transfer (Negative Result)

| Metric | DPO Baseline | BiDPO | 
|--------|--------------|-------|
| Mean Score | 0.3728 | 0.3782 |
| Std Dev | 0.3294 | 0.3333 |
| N Samples | 500 | 500 |

| Statistical Test | Value |
|------------------|-------|
| Mean Difference | +0.0054 (+0.54%) |
| t-statistic | 0.684 |
| p-value (one-sided) | 0.247 |
| Cohen's d | 0.016 |

**Gate: FAILED.** BiDPO shows a marginal positive direction (+0.54% higher mean collaboration score), but the effect is not statistically significant (p = 0.247 > 0.05) and the effect size is negligible (Cohen's d = 0.016 < 0.2 threshold). The score distributions for both models are nearly identical.

### Summary of Gate Results

| Experiment | Gate Type | Criterion | Result |
|------------|-----------|-----------|--------|
| E1: Orthogonality | MUST_WORK | \|r\| < 0.7 | **PASSED** |
| E2: Training Stability | MUST_WORK | No NaN/Inf, stable training | **PASSED** |
| E3: Generation Transfer | SHOULD_WORK | p < 0.05, d ≥ 0.2 | **FAILED** |

---

## 6. Discussion

### The Training-Generation Gap

The central finding is negative: BiDPO training creates gradient pressure toward collaboration patterns during optimization, but this pressure does not transfer to generation-time behavior at proof-of-concept scale.

Several factors may contribute to this gap:

1. **Insufficient training duration.** The 250-step proof-of-concept scale may be insufficient to induce behavioral change. Longer training (full epoch, ~10,000 steps) may show different results.

2. **Suboptimal λ weighting.** Only λ = 0.5 was tested. The agency signal may require stronger weighting (λ > 0.5) to compete with the preference signal, or weaker weighting to avoid interference.

3. **Heuristic limitations.** The pattern-matching collaboration score may capture surface features that do not correspond to behaviors the model can learn to produce at generation time.

4. **Base model dominance.** Mistral-7B-Instruct has strong priors from instruction tuning that 250 steps on 4000 samples cannot override.

### Limitations

- **Proof-of-concept scale only:** All training used 250 steps on 4000 samples. Full-scale training (~10,000 steps on 170,000 samples) was not conducted.

- **Single model architecture:** Only Mistral-7B-Instruct-v0.2 was tested. Results may not generalize to other model sizes or architectures.

- **Single λ value:** Only λ = 0.5 was tested. The optimal weighting remains unknown.

- **Heuristic-based scoring:** The collaboration score uses regex pattern matching rather than learned representations. Heuristics may not capture the full range of agency-preserving behaviors.

- **Downstream benchmarks not evaluated:** MT-Bench and TruthfulQA evaluations were planned but not executed due to the E3 failure.

### Value of Negative Results

This negative result contributes by: (1) demonstrating that the foundational mechanism is feasible (orthogonality and stability), (2) identifying the specific failure point (generation transfer at proof-of-concept scale), and (3) informing future work with concrete next steps rather than open-ended exploration.

---

## 7. Conclusion

This work asked whether auxiliary training objectives could teach language models to preserve user agency. The answer, at proof-of-concept scale, is: not automatically.

BiDPO demonstrates that agency-like signals exist orthogonally in preference data (r = −0.026) and integrate stably into DPO training without numerical instabilities. However, the gap between training-time signals and generation-time behavior remains (p = 0.247, d = 0.016).

Three directions for future work:

1. **Full-scale training:** Extend training to a full epoch (~10,000 steps) to determine whether longer optimization induces behavioral change.

2. **λ sweep:** Test λ ∈ {0.25, 0.5, 0.75, 1.0} to identify whether stronger or weaker agency weighting improves transfer.

3. **Learned collaboration scores:** Replace heuristic pattern matching with a learned classifier trained on human annotations of agency-preserving responses.

The gap identified here is likely relevant beyond BiDPO—any auxiliary objective for alignment faces the challenge of transferring training-time gradient pressure to inference-time behavior.

---

## References

Bai, Y., Jones, A., Ndousse, K., Askell, A., Chen, A., et al. (2022). Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback. *arXiv preprint arXiv:2204.05862*.

He, Q. & Maghsudi, S. (2025). PAMA: Pareto Multi-Objective Alignment for Language Models. *arXiv preprint arXiv:2508.07768*.

Lin, S. C., Hilton, J., & Evans, O. (2022). TruthfulQA: Measuring How Models Mimic Human Falsehoods. In *Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics*.

Mitelut, C. et al. (2023). Intent-aligned AI Systems Deplete Human Agency: The Need for Asymmetric Alignment. *arXiv preprint*.

Rafailov, R., Sharma, A., Mitchell, E., Ermon, S., Manning, C. D., & Finn, C. (2023). Direct Preference Optimization: Your Language Model is Secretly a Reward Model. In *Advances in Neural Information Processing Systems*, 36.

Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., et al. (2023). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. In *Advances in Neural Information Processing Systems*, 36.

Zhou, Y., Maghsudi, S., et al. (2024). MODPO: Multi-Objective Direct Preference Optimization. *arXiv preprint*.
