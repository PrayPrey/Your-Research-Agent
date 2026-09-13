# Product Requirements Document: H-C1
# Scale Attenuation of SFT Source Identity Effect (1.3B → 7B)

**Date:** 2026-08-02  
**Hypothesis:** H-C1 (CONDITION / SHOULD_WORK)  
**Prerequisite:** H-E2 VALIDATED (F=11.37, p=0.020, max effect 29.6 pp at 1.3B)  
**Phase:** 3 — Implementation Planning

---

## 1. Objective

Determine whether the SFT source-identity effect on pass@1 (confirmed at 1.3B in H-E2) is **attenuated at 7B scale** by training DeepSeek-Coder-7B-Base under the same 4 source conditions and comparing between-condition effect sizes (η²) across scales.

**Success criterion:** η²_7B < η²_1.3B for at least one benchmark (HumanEval+ or MBPP+).  
**Acceptable null:** η²_7B ≥ η²_1.3B → "source effect robust to scale" — informative for H-D1; does not block pipeline.

---

## 2. Scope

### In-Scope
- SFT training: 4 conditions × 3 seeds = **12 runs** at 7B scale
- Evaluation: HumanEval+ (164 tasks) and MBPP+ (378 tasks) via EvalPlus v0.3.1, greedy decoding
- Statistical analysis: one-way ANOVA + η² at 7B; comparison to H-E2 η² at 1.3B
- Figures: all required visualizations (η² bar chart, grouped pass@1, seed variance, scatter)
- Reuse of H-E2 datasets: post-dedup, token-equalized training sets for all 4 conditions

### Out-of-Scope
- Architectural changes to DeepSeek-Coder-7B-Base (no LoRA unless hardware forces it)
- New benchmark suites beyond HumanEval+ and MBPP+
- Hyperparameter search (same protocol as H-E2 for controlled comparison)
- Human evaluation

---

## 3. Source Conditions (Controlled Variables)

| Condition | Source | Post-dedup Train Size |
|-----------|--------|----------------------|
| humaneval_only | HumanEval train split | ~150 problems |
| mbpp_only | MBPP train split | ~374 problems |
| leetcode_only | LeetCode Python subset | token-budget matched |
| equal_mix | Equal parts of all 3 | token-budget matched |

**Token equalization:** All 4 conditions matched to same total training token count.  
**Dedup:** all-MiniLM-L6-v2 cosine similarity > 0.95 against test sets removed.  
**Protocol:** Identical to H-E2 — datasets reused directly.

---

## 4. Model

**Base:** `deepseek-ai/deepseek-coder-7b-base` (D=4096, L=32, H=32, 2T token pretraining)  
**Precision:** bfloat16  
**Hardware target:** 4× H100 (80GB each)  
**Fallback:** LoRA (r=16, α=32) if full fine-tuning exceeds VRAM — must be documented if used

---

## 5. Training Protocol (identical to H-E2)

| Parameter | Value |
|-----------|-------|
| Optimizer | AdamW (β1=0.9, β2=0.999, weight_decay=0.01) |
| Learning rate | 2e-5 |
| LR schedule | Cosine decay, warmup_ratio=0.03 |
| Effective batch | 32 (per_device=4, grad_accum=8) |
| Epochs | 3 |
| Max seq length | 2048 tokens |
| Precision | bfloat16 |
| Loss | Completion-only cross-entropy |
| Seeds | 42, 123, 777 |

**Framework:** TRL SFTTrainer (same as H-E2 for controlled comparison)  
**Flash Attention 2:** recommended (`attn_implementation="flash_attention_2"`) for 7B memory efficiency

---

## 6. Evaluation Protocol

**Tool:** EvalPlus v0.3.1  
**Decoding:** greedy (temperature=0, do_sample=False)  
**Benchmarks:**
- HumanEval+ (164 tasks, EvalPlus base+extra tests)
- MBPP+ (378 tasks, EvalPlus base+extra tests)

**Primary output per model run:** `{'humaneval': pass@1, 'mbpp': pass@1}`  
**Total evaluations:** 12 models × 2 benchmarks = 24 pass@1 values

---

## 7. Statistical Analysis

**H-E2 reference η²:** Estimated ~0.83 from F=11.37 on ANOVA at 1.3B (3 conditions with complete data)

**H-C1 analysis steps:**
1. One-way ANOVA: `pass@1 ~ source_condition` for each benchmark at 7B
2. Compute η² = SS_between / SS_total
3. Compare η²_7B vs η²_1.3B per benchmark
4. Compute Cohen's f = √(η²/(1-η²))
5. Pairwise effect sizes (absolute pp differences) per condition pair

**Gate evaluation:**  
- PASS: η²_7B < η²_1.3B for ≥1 benchmark  
- NULL (informative): η²_7B ≥ η²_1.3B for both benchmarks

---

## 8. Required Outputs

### Files
```
docs/youra_research/h-c1/
├── 03_prd.md                  (this file)
├── 03_architecture.md
├── 03_logic.md
├── 03_config.md
├── 03_tasks.yaml
└── figures/
    ├── eta_sq_comparison.png       # η²_7B vs η²_1.3B bar chart (MANDATORY)
    ├── pass1_by_condition_scale.png # grouped bar chart 4 conditions × 2 scales
    ├── seed_variance_7b.png         # box plots across 3 seeds at 7B
    └── scale_attenuation_scatter.png # x=η²_1.3B, y=η²_7B per benchmark
outputs/h-c1/
├── {condition}_seed{seed}/    # 12 model checkpoints
└── results.json               # all 24 pass@1 values + η² analysis
```

### Validation Report
`docs/youra_research/h-c1/04_validation.md` — produced in Phase 4, must include:
- All 24 pass@1 values (table)
- η² at 7B vs 1.3B comparison
- Gate verdict (PASS / NULL) with interpretation
- If LoRA used: document as limitation

---

## 9. Implementation Budget

**Tier:** LIGHT (controlled experiment, reuses H-E2 infrastructure)  
**Budget:** 15 tasks  
**Compute estimate:** 12 × ~2h on 4× H100 = ~24 compute-hours

---

## 10. Risk Register

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| OOM at 7B full fine-tune | Medium | Flash Attention 2; LoRA fallback (r=16, α=32) |
| EvalPlus timeout on 7B inference | Low | Batch size 1, greedy; use vLLM backend if needed |
| Incomplete seeds (repeat of H-E2 partial) | Low | All 12 runs explicitly sequenced with checkpoint verification |
| η² comparison invalid (different number of conditions) | None | Same 4 conditions at both scales |

---

## 11. Success / Failure Definition

| Outcome | η² comparison | Next step |
|---------|--------------|-----------|
| PASS (H-C1 supported) | η²_7B < η²_1.3B ≥1 benchmark | Proceed to H-D1 |
| NULL (H-C1 not supported) | η²_7B ≥ η²_1.3B both benchmarks | Document; proceed to H-D1 with "source effect scale-invariant" note |
| FAILED (incomplete data) | Missing ≥1 seed | Retry missing runs; do not gate on partial data |
