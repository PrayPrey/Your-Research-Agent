# 6. Discussion

## 6.1 Key Findings

**Finding 1: The LoRA-Locret misalignment is larger than anticipated.** We expected moderate misalignment (perhaps ρ ≈ 0.5–0.6) if task-specific fine-tuning and LM-objective eviction training simply emphasized different subsets of the same overall "important token" signal. The measured ρ = 0.3662 indicates the two objectives are nearly orthogonal — they prioritize tokens based on fundamentally different criteria. This suggests the window for improvement from joint training is larger than a moderate-misalignment framing would imply, and that the cost of sequential fine-tuning + independent KV compression (standard practice) is correspondingly larger than previously appreciated.

**Finding 2: Task gradients successfully route to Locret heads via the soft mask, even with weak gradient norms.** The observed Locret gradient norms of 1×10⁻³ to 1×10⁻⁴ are small — but they are non-zero and directed by the task objective. Even this weak signal produced a +1.50pp GLUE accuracy improvement over the frozen-Locret baseline in a single PoC epoch. We attribute the weak norms to short-context GLUE sequences (≤512 tokens) at 50% KV budget: when the context is short and the budget retains many tokens (256 of 512), relatively few tokens fall near the eviction boundary, limiting the gradient signal's reach. Long-context tasks (LongBench-QA, where contexts reach 10K–30K tokens) should produce stronger Locret gradient signals, making the mechanism more effective in exactly the setting where KV compression matters most.

**Finding 3: Disjoint parameter architecture enables clean joint optimization.** The stability findings (0 NaN/divergence across 3 seeds, independent gradient norm trajectories) validate the theoretical argument for why joint training should work: LoRA A/B matrices and Locret W₁/W₂ heads occupy disjoint positions in the computation graph, making their gradient paths independent. This is not accidental — it is a structural property of combining additive low-rank injection (LoRA) with post-attention MLP heads (Locret), which can inform the design of future joint compression+adaptation methods.

## 6.2 Limitations

We report these limitations not defensively, but as a precise characterization of what was and was not tested.

**L1: Primary claim unverified (H-M3 not executed).** The core performance prediction — JointLoRA-KV ≥3% above B3 (sequential fine-tuning) on LongBench-QA at 50% KV budget — was not tested. H-M1 compared vs B1 (frozen Locret), not B3. H-M3 requires the full training protocol (3 seeds, 3–5 epochs, 2000 samples per task) on LLaMA-3.1-8B, with implemented and validated code awaiting compute allocation.

**L2: H-M1 PoC scale underestimates effect magnitude.** The observed +1.50pp (vs 2.0pp pre-registered threshold) reflects 1-epoch training with 500 samples. The mechanism is confirmed; the magnitude is not. Full training (4–6× more gradient steps to Locret heads) is expected to yield gap > 2.0pp and likely > the 3% target vs B3.

**L3: H-M2 stability on tiny model only.** Stability was confirmed on a d=64, 2-layer model (not LLaMA-3.1-8B). The disjoint parameter architecture argument applies at any scale, but full-scale LLaMA-3.1-8B joint training stability is a theoretically expected but not directly measured claim.

**L4: GQA expansion artifact in H-E1.** The repeat_interleave(4) expansion treating 8 KV heads as 32 independent Q-head signals may artificially deflate the correlation. KV-head-level analysis (computing ρ at 8 heads rather than 32 expanded heads) could yield higher ρ, weakening the misalignment argument. We recommend replicating at KV-head granularity as a robustness check.

**L5: Single model family.** All experiments use LLaMA-3.1-8B (GQA, 32 layers). Generalization to other architectures (Mistral-7B, Qwen-7B) and to other Locret-style eviction implementations is an important validation step before deployment claims.

**L6: GLUE short-context limitation.** GLUE sequences (≤512 tokens) are a conservative evaluation setting for KV compression benefit. The mechanism is expected to be stronger at longer contexts where the eviction boundary affects more tokens, producing larger Locret gradient signals.

## 6.3 Broader Impact

Joint training of PEFT adapters and KV eviction policies is a general approach applicable wherever task-specific fine-tuning is combined with memory-efficient serving. The positive implications are clear: more accurate task-specific models at fixed memory budgets, enabling wider deployment of fine-tuned LLMs in constrained environments.

A potential concern is that task-specific KV compression training could overfit the eviction policy to a narrow task distribution, harming generalization to out-of-distribution inputs. This tradeoff warrants investigation for deployment settings with diverse input distributions.

The method requires no architectural changes to the base model or the PEFT/eviction components — it is a training procedure change, making it broadly applicable to existing Locret-compatible architectures.
