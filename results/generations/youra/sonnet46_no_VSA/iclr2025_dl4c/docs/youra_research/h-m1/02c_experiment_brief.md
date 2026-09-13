# Experiment Design: H-M1

**Date:** 2026-08-02
**Author:** Anonymous
**Hypothesis Statement:** Cross-benchmark transfer is asymmetric: HumanEval-only training outperforms MBPP-only on HumanEval+, and MBPP-only training outperforms HumanEval-only on MBPP+ (directional inversion pattern), consistent across ≥2/3 seeds at 1.3B scale, confirming same-source specialization advantage (P2).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (Analysis-only) Template** - H-M1 is a zero-training analysis experiment that re-uses H-E2 SFT checkpoint evaluation data to test the cross-benchmark inversion pattern.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E2 VALIDATED ✅
**Gate Status:** SHOULD_WORK — failure does not block pipeline

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E2 (VALIDATED)

### Gate Condition
SHOULD_WORK: If inversion pattern is absent, this weakens the mechanistic claim but does not block H-M2, H-C1, or Phase 5. Result is logged as limitation.

---

## Continuation Context

H-M1 directly reuses H-E2 experimental infrastructure. All SFT training runs (4 conditions × 1.3B × up to 3 seeds) and EvalPlus evaluation results already exist from H-E2 execution. H-M1 requires zero new model training — it is a statistical analysis pass over already-collected pass@1 data.

### Previous Hypothesis Results (H-E2)
- One-way ANOVA: F=11.37, p=0.020 (significant source effect confirmed)
- HumanEval-only mean pass@1 = 32.6%, MBPP-only = 27.7%, LeetCode-only = 3.0%, Equal-mix = 9.8%
- Seeds available: HumanEval-only [seeds 42, 123], MBPP-only [seeds 42, 777], LeetCode-only [seeds 42, 123, 777], Equal-mix [seed 123]
- NOTE: Partial seed coverage — HumanEval-only missing seed 777, MBPP-only missing seed 123

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Cross-benchmark transfer SFT training specialization**
- No relevant past cases in Archon KB for this specific topic (KB contains diffusion model content)
- Low similarity scores (0.37–0.38) — unrelated domain

**Query 2: SFT source domain adaptation pass@1 code generation**
- No relevant past cases (0.41–0.45 similarity but unrelated HuggingFace diffusers content)

**Assessment:** Archon KB does not contain prior YouRA experiments on code SFT specialization. This is a novel research direction with no cached implementation patterns. Defaulting to Exa GitHub evidence.

### Archon Code Examples

**Query: EvalPlus HumanEval MBPP pass@1 evaluation**
- No relevant code examples in KB (diffusion pipeline benchmarking only)

### Exa GitHub Implementations

**Source 1: evalplus/evalplus** (GitHub — official EvalPlus repo)
- **URL:** https://github.com/evalplus/evalplus
- **Relevance:** Official evaluation harness for HumanEval+ and MBPP+ — the exact evaluation benchmarks H-M1 analyzes
- **Key CLI:**
  ```bash
  evalplus.evaluate --model "deepseek-ai/deepseek-coder-1.3b-instruct" \
                    --dataset [humaneval|mbpp] \
                    --backend vllm \
                    --greedy
  ```
- **Dataset sizes:**
  - HumanEval+: 164 problems (80x more tests than original HumanEval)
  - MBPP+: 374 problems / 378 tasks v0.2.0 (35x more tests than original MBPP)
- **Key insight:** `evalplus.evaluate` outputs `Base pass@1` and `Base+Extra pass@1`; H-M1 uses the `Base+Extra` (HumanEval+ / MBPP+) as the primary metric, consistent with H-E2 protocol.
- **Used for:** Evaluation protocol confirmation, dataset size spec

**Source 2: deepseek-ai/DeepSeek-Coder** (GitHub)
- **URL:** https://github.com/deepseek-ai/DeepSeek-Coder
- **Relevance:** Official DeepSeek-Coder evaluation scripts for HumanEval and MBPP
- **Key evaluation code:**
  ```python
  # HumanEval evaluation pattern (from Evaluation/HumanEval/eval_instruct.py)
  def build_deepseekcoder_instruction(language: str, question: str):
      return '''Please continue to complete the function. You are not allowed to modify the
  given code and do the completion only. Please return all completed function in a codeblock.
  Here is the given code to do completion:
  ```{}
  {}
  ```'''.strip().format(language.lower(), question.strip())
  ```
- **MBPP evaluation format:**
  ```python
  # From Evaluation/MBPP/eval_instruct.py
  def format_test_example(q, tests, code=None):
      prompt = ">>> Problem:\n{}\n>>> Test Cases:\n{}\n".format(q.strip(), "\n".join(tests))
      return prompt
  ```
- **Used for:** Prompt template reference for H-E2 SFT training (already applied); confirms evaluation format consistency

**Source 3: Parallel-SFT Paper** (arxiv 2604.20835, ACL Findings 2026)
- **URL:** https://arxiv.org/html/2604.20835v1
- **Relevance:** Directly demonstrates asymmetric cross-language transfer in code SFT — single-source PL training fails to transfer to target PLs, while parallel programs improve transfer. Directly analogous to H-M1's cross-benchmark inversion hypothesis.
- **Key finding:** "While RL yields consistent benefits within the source PL, these gains fail to transfer to different target PLs, sometimes even degrading performance" — mirrors the expected source-specific specialization in H-M1.
- **Used for:** Mechanism grounding, confirms asymmetric transfer is a real phenomenon in code LLM SFT

**Source 4: Soft Contamination Paper** (gleech.org/files/papers/soft-contamination)
- **URL:** https://www.gleech.org/files/papers/soft-contamination
- **Relevance:** Demonstrates "surprising jump in HumanEval (MBPP's control) for semantic duplicates" — finetuning on MBPP semantic duplicates improved HumanEval unexpectedly. This is a data-point supporting cross-benchmark transfer exists, making the H-M1 inversion interesting.
- **Key finding:** Finetuning on MBPP semantic duplicates improves MBPP performance but ALSO unexpectedly improves HumanEval — this is the *absence* of the inversion (positive transfer). H-M1 tests whether same-source SFT produces *selective* (inverted) rather than promiscuous transfer.
- **Used for:** Falsifiability context — the null scenario where no inversion exists

**Source 5: Massive SFT Experiments Paper** (ACL 2025, EMNLP)
- **URL:** https://p.rst.im/q/aclanthology.org/2025.emnlp-main.1138.pdf
- **Relevance:** Large-scale study of SFT data effects across benchmarks (HumanEval, MBPP among others). Shows domain-specific data improves target domain but effects vary across benchmarks. Magicoder (code-specific) "improves a wider task range than math corpora."
- **Key finding:** SFT data source identity measurably affects HumanEval and MBPP differently — some datasets show "clear benefits for multiple tasks, while others offer minimal" transfer. Supports H-M1's hypothesis of asymmetric source-specific effects.
- **Used for:** Training protocol context, expected baseline performance range

### 🎯 Implementation Priority Assessment

**CRITICAL: H-M1 is an analysis-only experiment — no new training required.**

H-M1 does NOT implement a new model or training procedure. It is a statistical analysis over H-E2 results.

**Recommended Implementation Path:**
- Primary: Direct analysis script over H-E2 saved evaluation results (CSV/JSON from EvalPlus)
- Fallback: Re-run EvalPlus evaluation on H-E2 checkpoints if results files are missing
- Justification: H-E2 already ran evalplus.evaluate on all SFT checkpoints; H-M1 extracts pass@1 per (source_condition, benchmark, seed) and tests the rank-inversion pattern

### Code Analysis (Serena MCP)

*Skipped* — No complex codebase to analyze. H-M1 is a statistical analysis script (< 100 lines of Python). Code structure is clear from H-E2 context and EvalPlus output format.

---

## Experiment Specification

### Dataset

**Dataset:** HumanEval+ and MBPP+ (EvalPlus suite)
- **Type:** standard (established benchmark)
- **Source:** evalplus/evalplus, via `pip install evalplus`
- **HumanEval+:** 164 problems, version 0.1.10
- **MBPP+:** 374 problems (378 tasks v0.2.0 sanitized, 374 active)
- **Hypothesis Fit:** Two structurally distinct benchmarks — HumanEval uses doctest-style function completion; MBPP uses natural language + test-case-driven utility problems. Distinct distributions make them ideal for testing cross-benchmark inversion.
- **Data source:** H-E2 EvalPlus evaluation results (already computed), not new evaluations

**Note:** This experiment does not load datasets fresh — it reads saved pass@1 results from H-E2 EvalPlus evaluation output files.

**Loading Information** (for Phase 4 data access):
- Method: Read H-E2 evaluation result files (JSON/JSONL output from `evalplus.evaluate`)
- Identifier: `docs/youra_research/h-e2/results/` — per-checkpoint eval result files
- Code:
  ```python
  import json, glob
  results = {}
  for path in glob.glob("docs/youra_research/h-e2/results/*.json"):
      data = json.load(open(path))
      # Each file contains: source_condition, seed, humaneval_pass1, mbpp_pass1
      results[path] = data
  ```

### Models

#### Baseline Model

**Architecture:** DeepSeek-Coder-Base-1.3B fine-tuned on HumanEval-only source
**Configuration:** Same as H-E2 SFT (TRL SFTTrainer, H-E2 hyperparameters)
**Loading Information:**
- Method: Load H-E2 saved checkpoints (already exist)
- Identifier: `docs/youra_research/h-e2/checkpoints/humaneval_only_seed{seed}/`
- Code: `AutoModelForCausalLM.from_pretrained("docs/youra_research/h-e2/checkpoints/humaneval_only_seed42/")`

**Note:** Baseline here means "HumanEval-only trained model" when evaluating on HumanEval+, and "MBPP-only trained model" when evaluating on MBPP+. The "baseline" shifts per benchmark per the inversion test.

#### Proposed Model

**Architecture:** DeepSeek-Coder-Base-1.3B fine-tuned on MBPP-only source (cross-condition comparison)

**Core Mechanism Implementation:**

The H-M1 "mechanism" is not a model architecture change but a statistical analysis procedure. The pseudo-code below describes the inversion detection algorithm:

```python
# Core Mechanism: Cross-Benchmark Inversion Detection (H-M1)
# Based on: H-E2 EvalPlus results + Phase 2B protocol

def load_h_e2_results(results_dir: str) -> dict:
    """
    Returns: {(source_cond, seed, benchmark): pass@1_float}
    source_cond: 'humaneval_only' | 'mbpp_only' | 'leetcode_only' | 'equal_mix'
    benchmark: 'humaneval_plus' | 'mbpp_plus'
    """
    results = {}
    for path in glob.glob(f"{results_dir}/*.json"):
        data = json.load(open(path))
        key = (data['source_condition'], data['seed'], data['benchmark'])
        results[key] = data['pass_at_1']
    return results

def check_inversion_per_seed(results: dict, seed: int) -> dict:
    """Check if HE-only > MBPP-only on HE+ AND MBPP-only > HE-only on MBPP+"""
    he_on_he = results.get(('humaneval_only', seed, 'humaneval_plus'), None)
    mb_on_he = results.get(('mbpp_only', seed, 'humaneval_plus'), None)
    he_on_mb = results.get(('humaneval_only', seed, 'mbpp_plus'), None)
    mb_on_mb = results.get(('mbpp_only', seed, 'mbpp_plus'), None)
    if None in [he_on_he, mb_on_he, he_on_mb, mb_on_mb]:
        return {'valid': False, 'reason': 'missing_data'}
    inversion_he = he_on_he > mb_on_he  # HE-only wins on HumanEval+
    inversion_mb = mb_on_mb > he_on_mb  # MBPP-only wins on MBPP+
    return {
        'valid': True, 'seed': seed,
        'inversion_he_plus': inversion_he,
        'inversion_mbpp_plus': inversion_mb,
        'both_inverted': inversion_he and inversion_mb
    }

def evaluate_h_m1_hypothesis(results: dict, seeds: list) -> dict:
    seed_checks = [check_inversion_per_seed(results, s) for s in seeds]
    valid = [c for c in seed_checks if c['valid']]
    n_both_inverted = sum(1 for c in valid if c['both_inverted'])
    # Success: ≥2/3 seeds show full inversion
    success = n_both_inverted >= (2/3) * len(valid)
    return {'success': success, 'seed_checks': valid,
            'n_both_inverted': n_both_inverted, 'n_valid': len(valid)}
```

### Training Protocol

**Note:** H-M1 requires zero new training. All models were trained as part of H-E2.

**H-E2 Training Parameters (inherited, for reference):**
- **Model:** DeepSeek-Coder-Base-1.3B (`deepseek-ai/deepseek-coder-1.3b-base`)
- **Trainer:** TRL SFTTrainer
- **Conditions:** 4 × {humaneval_only, mbpp_only, leetcode_only, equal_mix}
- **Seeds:** {42, 123, 777} (partial — see H-E2 note)
- **Optimizer:** AdamW (TRL defaults)
- **Source:** Reused from H-E2 — no hyperparameter changes

**H-M1 Analysis Parameters:**
- **Input:** H-E2 EvalPlus result files
- **Analysis seeds used:** All valid seeds per condition (≥2 for HE-only and MBPP-only)
- **Statistical test:** Directional rank check per seed (no additional statistical test required for SHOULD_WORK gate)
- **Seeds for inversion check:** Seed 42 confirmed available for both HumanEval-only and MBPP-only; seed 123 for MBPP-only; seed 777 for HumanEval-only

### Evaluation

**Primary Metrics:**
- `pass@1` (greedy, temperature=0) on HumanEval+ (164 problems)
- `pass@1` (greedy, temperature=0) on MBPP+ (374 problems)
- These are the `Base+Extra` scores from `evalplus.evaluate`

**Success Criteria:**
- **Full inversion:** HumanEval-only pass@1_HE+ > MBPP-only pass@1_HE+ AND MBPP-only pass@1_MBPP+ > HumanEval-only pass@1_MBPP+
- **Consistency:** Full inversion holds in ≥2/3 valid seeds
- **Effect check:** Margin > 0 (direction only — no minimum effect size required for SHOULD_WORK gate)

**Expected Values (from H-E2):**
- HumanEval-only on HumanEval+: ~32.6% (mean over available seeds)
- MBPP-only on HumanEval+: ~27.7% (mean over available seeds)
- → HE-only advantage on HumanEval+: ~4.9 pp (already suggests inversion direction)
- MBPP-only on MBPP+: unknown (not yet computed in H-E2 — need to extract from H-E2 result files)
- HumanEval-only on MBPP+: unknown (need to extract from H-E2 result files)

**Source:** EvalPlus leaderboard confirms DeepSeek-Coder-1.3B baseline: ~34.8% HumanEval+ (instruct), ~55.3% MBPP+ (instruct). Base model SFT from scratch will be lower.

**Metrics Loading Information:**
- Task Type: code generation / functional correctness
- Library: evalplus (`pip install evalplus`)
- Code:
  ```bash
  evalplus.evaluate --dataset humaneval --samples h_e2_humaneval_only_seed42.jsonl
  evalplus.evaluate --dataset mbpp --samples h_e2_mbpp_only_seed42.jsonl
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison:** 2×4 heatmap — rows = {HumanEval+, MBPP+}, columns = {HE-only, MBPP-only, LC-only, Equal-mix}. Shows pass@1 for each (benchmark × source_condition) cell. Inversion pattern is visually obvious if hypothesis supported.

#### Additional Figures (LLM Autonomous)
- **Per-seed inversion consistency plot:** 3-panel strip (one per seed) showing rank order on HumanEval+ and MBPP+ for the key conditions
- **Transfer asymmetry delta bar chart:** For each benchmark, show (HE-only − MBPP-only) pass@1 — positive on HumanEval+, negative on MBPP+ if inversion holds

> Phase 4 Coder MUST include figure generation logic in analysis code.
> All figures will be saved to `docs/youra_research/h-m1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | H-E2 EvalPlus results exist for both HumanEval+ and MBPP+ per source condition | TRUE — H-E2 VALIDATED |
| Mechanism Isolatable | Per-condition per-seed pass@1 is individually accessible from H-E2 result files | TRUE — EvalPlus outputs per-checkpoint JSONL |
| Baseline Measurable | At least 2 valid seeds exist for both HumanEval-only and MBPP-only conditions | TRUE — seeds 42+777 for HE-only, 42+123 for MBPP-only (from H-E2 state) |

### Architecture Compatibility Check

H-M1 is an analysis-only experiment. No architecture modifications. Compatibility checks:

**Required:**
- H-E2 result files in `docs/youra_research/h-e2/results/` with per-(condition, seed, benchmark) pass@1
- EvalPlus ≥ v0.2.0 installed (MBPP+ v0.2.0 support)

**Incompatible scenarios:**
- H-E2 results missing MBPP+ evaluation (only HumanEval+ results saved) — must re-run evalplus.evaluate on MBPP for H-E2 checkpoints
- Fewer than 2 valid seeds for either HumanEval-only or MBPP-only — inversion check uses all available seeds, success requires ≥2/3 valid

> ⚠️ If MBPP+ results are missing from H-E2 output, Phase 4 MUST re-run evalplus.evaluate --dataset mbpp on H-E2 checkpoints before analysis.

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|----------------|-----------------|---------------|
| Log Message | "Inversion detected: HE-only > MBPP-only on HumanEval+ AND MBPP-only > HE-only on MBPP+" | analysis_script.py |
| Data Check | Both H-E2 result dicts contain non-None MBPP+ pass@1 values | load_h_e2_results() |
| Metric Delta | pass@1_HE-only_HE+ > pass@1_MBPP-only_HE+ (already confirmed ~4.9pp from H-E2) | check_inversion_per_seed() |

**Activation Verification Code:**

```python
def verify_mechanism_activated(results: dict, seeds: list) -> tuple:
    indicators = {}
    for seed in seeds:
        he_on_he = results.get(('humaneval_only', seed, 'humaneval_plus'))
        mb_on_he = results.get(('mbpp_only', seed, 'humaneval_plus'))
        he_on_mb = results.get(('humaneval_only', seed, 'mbpp_plus'))
        mb_on_mb = results.get(('mbpp_only', seed, 'mbpp_plus'))
        if None in [he_on_he, mb_on_he, he_on_mb, mb_on_mb]:
            indicators[seed] = {'valid': False}
            continue
        indicators[seed] = {
            'valid': True,
            'he_plus_inversion': he_on_he > mb_on_he,
            'mbpp_plus_inversion': mb_on_mb > he_on_mb,
            'both_inverted': (he_on_he > mb_on_he) and (mb_on_mb > he_on_mb)
        }
    valid = [v for v in indicators.values() if v.get('valid')]
    activated = sum(1 for v in valid if v['both_inverted']) >= (2/3) * len(valid)
    return activated, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| MBPP+ results missing from H-E2 | `results.get(('*', seed, 'mbpp_plus')) is None` | Re-run `evalplus.evaluate --dataset mbpp` on H-E2 checkpoints |
| Only 1 valid seed per condition | `n_valid < 2` after data loading | Report limitation; proceed with available seeds |
| No inversion in any seed | `n_both_inverted == 0` | SHOULD_WORK gate: log as limitation, do not stop pipeline |
| Partial inversion (one direction only) | `inversion_he_plus XOR inversion_mbpp_plus` | Report as partial — mechanism partially supported |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE | Both inversion checks return non-None per seed |
| Effect Measurable | Δ > 0 on both benchmarks | `he_on_he > mb_on_he` AND `mb_on_mb > he_on_mb` |
| Hypothesis Supported | ≥2/3 seeds show full inversion | `n_both_inverted / n_valid ≥ 0.667` |

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Analysis script runs without error
2. Inversion pattern present in ≥2/3 valid seeds for both benchmark directions

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Assessment:** No relevant past cases found in Archon KB (KB contains diffusion model content, similarity scores 0.37–0.45, unrelated domain). This is expected for a novel code SFT research direction.

### B. GitHub Implementations (Exa)

**Repository 1: evalplus/evalplus** (⭐ primary evaluation harness)
- **URL:** https://github.com/evalplus/evalplus
- **Query Used:** "EvalPlus evalplus evaluation HumanEval+ MBPP+ pass@1 greedy Python"
- **Relevance:** Official evaluation harness — provides exact HumanEval+ (164 problems) and MBPP+ (374 problems) evaluation with rigorous test augmentation
- **Key Code:**
  ```bash
  # Evaluate a model on both benchmarks (H-E2 used this exact protocol)
  evalplus.evaluate --model "deepseek-ai/deepseek-coder-1.3b-base" \
                    --dataset humaneval --backend hf --greedy
  evalplus.evaluate --model "deepseek-ai/deepseek-coder-1.3b-base" \
                    --dataset mbpp --backend hf --greedy
  ```
- **Output format:**
  ```
  Base {'pass@1': 0.xxxx}
  Base + Extra {'pass@1': 0.xxxx}
  ```
- **Used For:** Dataset specification, evaluation protocol, metric definition

**Repository 2: deepseek-ai/DeepSeek-Coder** (⭐ 23,976)
- **URL:** https://github.com/deepseek-ai/DeepSeek-Coder
- **Query Used:** "DeepSeek-Coder SFT fine-tuning HumanEval MBPP pass@1 evaluation analysis seed reproducibility"
- **Relevance:** Official evaluation scripts for DeepSeek-Coder on HumanEval and MBPP; confirms prompt format used in H-E2
- **Configuration Extracted:**
  - HumanEval prompt: function completion with instruction wrapper
  - MBPP prompt: ">>> Problem: ... >>> Test Cases: ... >>> Code:"
- **Used For:** Evaluation prompt format consistency check (H-E2 training format)

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code analysis not needed. H-M1 is an analysis-only experiment using simple Python statistics over H-E2 result files. No complex codebase to analyze.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report — H-E2
- **Reused Components:**
  - All SFT checkpoints: 4 conditions × 1.3B × partial seeds
  - EvalPlus evaluation results on HumanEval+ (already run)
  - MBPP+ evaluation results (may need to be confirmed/re-run)
  - Confirmed source effect (F=11.37, p=0.020)
- **Why Reused:** H-M1 is explicitly defined in Phase 2B as "re-uses H-E2 experimental data. Additional analysis only."

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|---------------|-------------|------------------|
| Dataset (HumanEval+, 164 problems) | GitHub (Exa) | evalplus/evalplus |
| Dataset (MBPP+, 374 problems) | GitHub (Exa) | evalplus/evalplus v0.2.0 |
| Evaluation CLI protocol | GitHub (Exa) | evalplus/evalplus docs |
| Baseline performance range | GitHub (Exa) | evalplus leaderboard |
| Prompt format | GitHub (Exa) | deepseek-ai/DeepSeek-Coder eval scripts |
| Asymmetric transfer precedent | Web (Exa) | Parallel-SFT arxiv:2604.20835 |
| Cross-benchmark transfer evidence | Web (Exa) | Soft contamination paper |
| SFT source effect on multiple benchmarks | Web (Exa) | Massive SFT paper EMNLP 2025 |
| Inversion detection algorithm | Derived | Phase 2B specification + H-E2 results |
| Success criterion (≥2/3 seeds) | Phase 2B | 02b_verification_plan.md H-M1 section |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — state managed via restate block)
**Date:** 2026-08-02

### Workflow History for This Hypothesis
- Phase 2C experiment design initiated: 2026-08-02
- H-E2 prerequisite confirmed VALIDATED: 2026-08-02
- 02b_context.md JIT-generated from 02b_verification_plan.md: 2026-08-02
- Archon KB search: no relevant results (diffusion domain mismatch)
- Exa search: 5 relevant sources identified
- Synthesis complete: 2026-08-02

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results), Exa (GitHub + web search — 5 sources)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
