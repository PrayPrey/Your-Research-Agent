# Discussion

## 6.1 Why the Results Make Sense: Mechanistic Interpretation of H2

The H2 boundary shift finding is mechanistically consistent with what we know about RLHF and DPO training objectives. Consider what alignment training actually optimizes:

**PPO alignment** maximizes expected reward $r_\theta(x, y)$ subject to a KL divergence penalty $\beta \cdot D_{\text{KL}}(\pi_\text{RL} \| \pi_\text{SFT})$ to the SFT reference policy \cite{ouyang2022instructgpt, li2024rlhf}. The KL penalty constrains how far the aligned policy can deviate from the SFT policy — it acts as a regularizer against catastrophic shift. Despite this regularization, PPO produces the most extreme boundary shift in our study (1.4B-PPO: ρ = −0.324, 99.7% argmax redistribution). We hypothesize this reflects *reward hacking* in the Goodhart's Law sense \cite{coste2023reward_overoptimization}: the proxy reward (trained on HH preference data) is poorly aligned with MMLU factual accuracy, so PPO maximizes HH preferences by adopting logit patterns that diverge completely from the base model's factual knowledge encoding. The KL constraint prevents collapse but does not prevent the near-complete argmax redistribution we observe.

**DPO alignment** optimizes the log-probability ratio $\log(\pi_\theta(y_w | x) / \pi_\text{ref}(y_w | x)) - \log(\pi_\theta(y_l | x) / \pi_\text{ref}(y_l | x))$ directly, where $y_w$ and $y_l$ are preferred and dispreferred responses \cite{rafailov2023dpo}. DPO's training objective directly reshapes per-token log-probabilities at the token level — it can selectively increase probabilities of preferred continuations and decrease probabilities of dispreferred continuations, *without* any explicit KL penalty to constrain how much the argmax rankings change. The result is a form of H2 boundary shift that is more aggressive in magnitude (larger ΔReliability) than PPO, consistent with the unconstrained token-level optimization. Paradoxically, DPO's lower raw Spearman ρ values than PPO for some size/model combinations, yet larger ΔReliability, may reflect that DPO produces more *systematic* boundary shifts (same answer preferred across more items) while PPO's near-zero/negative ρ reflects more random-looking redistribution (1.4B-PPO: ρ = −0.324 suggests the alignment almost randomly redistributes).

**SFT alignment** — supervised fine-tuning on demonstration data — shows the mildest calibration degradation (smallest ΔReliability, highest ρ values among alignment types). SFT does not optimize any reward signal; it simply adapts the model's output format to match demonstration patterns. The boundary shift is smaller in magnitude (ρ = 0.75–0.84 across sizes) but still present, suggesting that even format adaptation partially reorganizes answer preferences.

## 6.2 Counter-Intuitive Findings and Their Implications

### DPO Produces Larger Calibration Degradation Than PPO

The empirical ordering DPO > PPO > SFT (in ΔReliability) reverses our original prediction (PPO ≥ DPO > SFT). The original prediction assumed that greater reward optimization pressure (PPO) would produce greater calibration degradation. Our results suggest this intuition is backwards when the mechanism is H2 rather than H1.

Under H1 (scale inflation), greater reward pressure would uniformly amplify confidence — PPO would naturally exceed DPO. Under H2 (boundary shift), the question is which training method most aggressively reorganizes answer preferences. DPO's token-level direct preference reshaping can directly invert log-probability rankings for specific answer tokens; PPO's sequence-level reward optimization with KL penalty must navigate the tension between maximizing reward and staying close to the SFT reference, which may actually *moderate* the argmax redistribution at the sequence level.

**Implication for alignment design:** This finding suggests that the KL divergence penalty in PPO provides an implicit (partial) calibration regularization that DPO lacks. If calibration preservation is a design goal, adding a calibration-aware regularization term to the DPO objective (analogous to PPO's KL penalty) may be warranted.

### PPO 1.4B: Near-Complete Argmax Redistribution

The 1.4B-PPO model changing its argmax for 99.7% of MMLU items (44/14,042 shared) with ρ = −0.324 is the most striking finding in our dataset. A negative Spearman ρ at the per-item level implies the aligned model's preference ordering is *inversely* correlated with the base model's — not just uncorrelated, but *reversed*.

Two explanations are plausible:

1. **Reward hacking on MMLU format (HIGH plausibility):** The HH preference data trains PPO to prefer patterns characteristic of helpful, harmless responses. For 4-shot MMLU continuation scoring, these patterns may systematically correspond to specific answer-position biases (e.g., preference for option B or C) or response-length patterns in the continuation probabilities. The 1.4B model, with its limited representational capacity, cannot simultaneously maintain MMLU factual associations and HH preference patterns — the HH patterns dominate.

2. **Catastrophic forgetting (MEDIUM plausibility):** PPO optimization may partially overwrite the factual associations encoded during pretraining, replacing them with HH-preference-aligned associations that are orthogonal to MMLU factual structure.

**Implication for LLM evaluation:** Standard benchmark evaluation of PPO-aligned models may be fundamentally unreliable at small model sizes: the model's apparent preferences on multiple-choice items may reflect HH-training biases rather than factual knowledge, making ECE and accuracy metrics misleading as measures of the model's "true" calibration.

### 6.9B-DPO Approaching H1 Threshold (ρ = 0.875)

The 6.9B-DPO model's Spearman ρ = 0.875 is the closest any alignment-base pair comes to the H1 threshold (ρ = 0.90) in our study. This near-threshold behavior suggests a potential mechanism transition at larger scales with soft alignment methods. At 6.9B parameters, the model's pretraining representations are sufficiently rich to partially resist the boundary shift imposed by DPO alignment — larger models may have stronger factual encoding that competes more effectively with the DPO alignment signal.

If this scale-mechanism relationship holds, applying our Spearman ρ diagnostic to LLaMA-2 7B and 13B DPO-aligned variants may reveal a crossing of the H1/H2 threshold, where larger models with softer alignment exhibit H1-type scale distortion rather than H2-type boundary shift. This directly motivates the cross-family experiments proposed in Section 6.5.

## 6.3 Connection to ATS and Calibration Correction

Our finding that H2 is the dominant mechanism provides a new interpretation for *why* ATS \cite{xie2024ats} succeeds. ATS learns a per-input temperature function from the model's hidden states: $\tau(x) = g(\mathbf{h}_x)$ where $\mathbf{h}_x$ is a hidden state representation. Post-ATS calibration is substantially better.

If the dominant mechanism were H1 (scale inflation), a simple temperature scaling function could correct it. But if the dominant mechanism is H2 (boundary shift), then the hidden-state temperature function must be learning something more subtle: either (a) it learns to identify inputs where the boundary shift is likely to be large and applies aggressive temperature modulation on those inputs, or (b) hidden-state representations encode information about whether the alignment-induced answer reordering is likely to be correct, allowing implicit boundary correction via confidence modulation.

Testing hypothesis (b) is possible by correlating per-item ATS temperature $\tau(x_i)$ with per-item Spearman ρ: if ATS temperatures are lower (more aggressive modulation) for items with larger ρ deviation from H1, this would directly support interpretation (b). This is an immediate future experiment that our mechanistic framework enables.

## 6.4 Limitations

### Limitation 1: Public Fallback Checkpoints (Risk R1)

The RLHFlow alignment checkpoints from Li et al. \cite{li2024rlhf} require HuggingFace authentication and were unavailable during our experiments. We used public fallback checkpoints (lomahony SFT, Leogrin DPO, usvsnsp PPO) trained on HH data with Pythia base models. These checkpoints approximate the Li et al. setup but have unknown equivalence in training duration, reward model architecture, and hyperparameters.

**Impact on conclusions:** The H2 mechanism finding (8/9 ρ < 0.85; 1.4B-PPO ρ = −0.324) is robust to checkpoint variation — it would require an implausibly consistent pattern of overtrained DPO checkpoints and undertrained PPO checkpoints across all three sizes to produce the observed H2 signature from an underlying H1 mechanism. The DPO > PPO ordering claim is more fragile and should be treated as a checkpoint-level observation requiring replication.

### Limitation 2: Single Model Family (Pythia 1.4B–6.9B)

All experiments use the Pythia model family. Calibration behavior under alignment may differ substantially for LLaMA-2-Chat, Mistral-Instruct, or Falcon-Instruct models. However, Pythia provides the cleanest available causal isolation: identical pretraining data and architecture across all alignment variants removes confounds present in cross-family comparisons.

### Limitation 3: Scale Range (1.4B–6.9B)

The potential H1/H2 mechanism transition signaled by 6.9B-DPO (ρ = 0.875) remains unresolved. No publicly available Pythia checkpoints exceed 12B parameters. Whether larger models (13B, 70B) exhibit H1-type scale distortion or continued H2-type boundary shift is an open question.

### Limitation 4: H-M4 (ATS Correction) Not Executed

We did not test whether ATS post-hoc correction can reduce ECE in models exhibiting H2-type boundary shift. This was the planned fifth sub-hypothesis; pipeline constraints prevented its execution. The correctability of H2-type miscalibration remains unverified experimentally.

## 6.5 Broader Implications

**For calibration correction:** Our finding that H2 is the dominant mechanism implies that temperature scaling and similar confidence-rescaling methods may be inadequate for aligned LLMs. Effective correction of H2-type boundary shift may require methods that can identify and partially reverse answer-preference reorganizations, such as retrieval-based correction, contrastive decoding against the base model, or boundary-aware post-training regularization.

**For LLM evaluation:** Models showing large H2 boundary shift (high % changed argmax) cannot be reliably evaluated using standard multiple-choice benchmarks as measures of factual knowledge — the alignment training has reorganized which answer is predicted, making ECE and accuracy measure alignment-preference patterns rather than factual calibration.

**For alignment design:** The DPO > PPO ordering suggests that the KL divergence penalty in PPO provides an implicit partial protection against calibration degradation that DPO lacks. Alignment practitioners optimizing for trustworthiness — not just helpfulness — should consider explicit calibration-preservation constraints in the alignment objective.
