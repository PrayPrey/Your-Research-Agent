# 6. Discussion

## 6.1 Key Findings and Their Interpretation

**Finding 1: The structural efficiency framework is validated end-to-end.**
The most secure contribution of this paper is the measurement framework itself.
All components execute correctly, produce interpretable metrics, and handle the
full statistical pipeline. This means researchers can immediately apply the
framework to their own GRPO/DPO checkpoint archives — the infrastructure cost
is already paid.

**Finding 2: The raw/proportion dissociation challenges the selective-reallocation mechanism.**
The most intellectually provocative preliminary result is the divergence between
GRPO's raw semantic edit distance advantage (+250% on PoC data) and its near-zero
SEP advantage (≈0.237 for both methods). These two metrics ask different questions:
raw edit distance asks "how much does the policy change structurally in absolute
terms?"; SEP asks "what fraction of all changes are structural?"

Three competing interpretations deserve investigation:

**(a) The mechanism claim (P2) is false even if the existence claim (P1) holds.**
GRPO may produce more aggressive code restructuring (more total edits, including
more semantic edits in absolute terms) without proportionally concentrating edits
on semantic nodes. This would mean execution reward increases structural activity
broadly, not selectively. Under this interpretation, raw semantic edit distance
per unit KL (structural efficiency, P1) may still be a useful metric, but the
selective-reallocation mechanism is not its explanation.

**(b) Checkpoint aliasing masks a real SEP difference.**
With $n_\text{eff} \approx 2$, the Mann-Whitney test has essentially no statistical
power. A corrected run with 10+ diverse checkpoints might reveal SEP_GRPO > SEP_DPO
with adequate power. The dry-run smoke test (3 pairs, n=10 problems) also showed
near-equality, but is itself underpowered. This interpretation cannot be ruled out
and motivates the corrected experimental protocol (Section 6.3).

**(c) Scale-level equilibration of SEP at 7B.**
At 7B parameter scale with the specific KL budget used, both methods may converge
to similar proportional distributions over node types, even when absolute edit
distances differ. This would be a scale-specific finding that motivates testing
at different model sizes (1.3B, 13B).

Distinguishing these interpretations requires a corrected run with real training
(≥10 GRPO checkpoints from ≥1000 training steps) and execution-oracle DPO pairs.
The framework is ready; the experiment needs to be run.

**Finding 3: Checkpoint aliasing is a previously undocumented methodological confound.**
This finding has value independent of any hypothesis about GRPO vs. DPO. Any
researcher running checkpoint-comparison analysis in RL fine-tuning — for code,
math, or general NLP — should add checkpoint diversity pre-flight checks to their
experimental pipeline. The confound is invisible from benchmark metrics alone and
can corrupt nominally large analyses (27 pairs → $n_\text{eff}$ = 2) without
triggering any explicit error.

## 6.2 Limitations

**L1: Synthetic data in h-e1 gate evaluation.**
The proof-of-concept (h-e1) used hand-crafted code completions with guaranteed
GRPO structural advantage (more CF+DF nodes engineered into GRPO completions).
The bootstrap CI [4.65, 8.73] and mean differential 6.50 are valid measurements
of the infrastructure's detection capability, but they cannot be cited as
empirical evidence that real GRPO training produces higher structural efficiency
than DPO. A real training run with ≥1000 steps and evalplus-based execution
evaluation is required.

*Why this does not invalidate the framework contribution:* The framework's value
is in providing the measurement tool, not in the specific numbers from the PoC.
The PoC demonstrates the plumbing works; real training will provide the data.

**L2: Underpowered SEP analysis (n_effective ≈ 2).**
The h-m1 SEP comparison is entirely underpowered. The Mann-Whitney test
(p = 0.4248) and the near-zero effect size (−0.0072) cannot be interpreted as
evidence for or against the mechanism hypothesis. We report these numbers for
transparency and document the aliasing root cause; they should not be cited as
empirical findings about GRPO vs. DPO behavior.

*Why this does not invalidate the paper:* The aliasing characterization is itself
a contribution. The dry-run smoke test (n=10 problems, 3 pairs) provides
weak corroborating evidence of near-equality, but requires confirmation.

**L3: Single base model and single programming language.**
All experiments use DeepSeek-Coder-7B-instruct-v1.5 on Python (HumanEval+/MBPP+).
The structural efficiency framework is designed to be model-agnostic and
language-agnostic (any AST-parseable language), but empirical generalization
across scales and languages has not been tested.

**L4: DPO preference pairs not execution-oracle labeled.**
The h-e1 DPO implementation used stub preference pairs (`return None` as
rejected completion) rather than genuine model-generated failed solutions
labeled by evalplus. Real execution-oracle DPO pairs require sampling model
outputs and labeling via execution. This means the DPO training condition in
the PoC is not representative of execution-oracle DPO as specified.

## 6.3 Corrected Experimental Protocol

For any team seeking to reproduce or extend this work with valid empirical results:

1. **Enforce checkpoint diversity:** `save_steps=100` for a 1000-step run yields
   10 GRPO checkpoints (steps 100–1000). Assert `len(unique_checkpoints) >= 10`
   before h-m1 analysis.
2. **Fix mock data:** Replace hard-coded GRPO code completions in `smoke_test_experiment.py`
   with real GRPOTrainer outputs evaluated by evalplus.
3. **Fix DPO pairs:** Implement `generate_dpo_pairs()` to sample model outputs
   and label via evalplus execution (passing = preferred, failing = rejected).
4. **Use KL tolerance = 0.05** (±5%) as specified, not 0.15. With 10+ checkpoints,
   sufficient pairs will be found even at stricter tolerance.
5. **Reduce scope:** Test the H-E1 → H-M1 chain before attempting H-M2–H-M4.
   Confirm real-training SEP direction before proceeding to mediation analysis.

## 6.4 Broader Impact

This work provides measurement infrastructure for understanding how alignment
methods change model behavior in code generation.

**Positive impacts:** The structural efficiency framework enables more principled
comparison of post-training methods — researchers can now ask not only "which
method scores higher?" but "which method induces richer structural learning per
unit of KL cost?" This has the potential to reduce benchmark-chasing and focus
the field on methods that genuinely improve structural code understanding.
The checkpoint aliasing finding will prevent silent data corruption in future
checkpoint-comparison studies across the RL fine-tuning literature.

**Potential risks and mitigations:** The structural efficiency metric could be
gamed if used as a direct training reward (reward shaping toward high SEP without
improving functional correctness). We recommend the metric be used exclusively
for post-hoc analysis, not as a training signal, until its relationship to
functional correctness and out-of-distribution generalization is empirically
established. The framework should not be used to make deployment decisions about
alignment methods until validated with real training runs.
