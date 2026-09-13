# Per-Hypothesis Context: H-M2

*JIT-generated from 02b_verification_plan.md by Phase 2C step-01*
*Generated: 2026-08-21*

---

## Hypothesis Info

**ID:** H-M2
**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Statement:** GRPO training on variance-50 produces lower mean TRL frac_reward_zero_std than random-50 at training checkpoints (steps 10, 20, 50), confirming that variance profiling successfully identifies MBPP problems with nonzero GRPO gradient signal.

**Rationale:** Core mechanistic test. The mathematical identity σ=√(k(G-k))/G guarantees zero gradient for extreme-p_i problems. H-M2 verifies that profiling-based selection actually changes the per-step gradient information content during training.

**Variables:**
- Independent: Selection method (variance-50 vs random-50)
- Dependent: mean frac_reward_zero_std at training steps 10, 20, 50
- Controlled: G=4, use_vllm=False, generation_batch_size=4, lr=5e-7, same base model checkpoint

---

## Experimental Setup (from Phase 2A via Phase 2B)

**Dataset:**
- Name: MBPP (training split)
- Type: standard
- Source: google-research-datasets/mbpp (HuggingFace)
- Path: Training split (374 problems); two subsets: variance-50 and random-50
- Hypothesis Fit: MBPP binary execution reward is directly measured by frac_reward_zero_std; H-M1 confirmed heterogeneous variance distribution enabling meaningful subset selection

**Model:**
- Name: DeepSeek-Coder-7B-Instruct (v1.5)
- Type: Code LLM, instruction-tuned
- Source: deepseek-ai/deepseek-coder-7b-instruct-v1.5
- Hypothesis Fit: Confirmed functional in H-E1; same model used in profiling ensures variance_i values are valid priors for training behavior

---

## Success Criteria

**Primary (P2):** mean_frac_zero_std(variance-50) < mean_frac_zero_std(random-50) at ALL three checkpoints (10, 20, 50)
**Secondary:** Gap ≥ 5pp at checkpoint 10

**Failure Response:**
- IF fails at all checkpoints: PIVOT — proxy doesn't filter zero-gradient problems; explore online selection
- IF fails at some checkpoints: EXPLORE — document learning zone exhaustion dynamics

---

## Prerequisites

- H-E1: VALIDATED — MBPP variance distribution is non-degenerate for DeepSeek-Coder-7B
- H-M1: VALIDATED — Top-50 variance selection produces stable, meaningful ranking
- Top-50 problem IDs available from H-M1 output
- TRL GRPOTrainer functional in H-E1 environment

---

## Dependencies

- Source: Phase 2A Section 1.3 Step 2; Gradient Starvation arXiv:2605.07689
- Key reference: Mathematical identity σ=√(k(G-k))/G exact for binary rewards
