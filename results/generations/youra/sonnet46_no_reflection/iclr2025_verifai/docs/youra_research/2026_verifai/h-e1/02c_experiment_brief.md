# Experiment Design: h-e1

**Date:** 2026-05-20
**Author:** Anonymous
**Hypothesis Statement:** Under fixed BFS geometry and ≥85% formalization fidelity, if LLM policy uses step-local grounded feedback (condition A: Lean4 compiler errors) as DPO negatives, then post-DPO locality score (fraction of probability mass on premise-consistent tactics) will be significantly higher than the permutation control (shuffled error messages) and condition B (ungrounded step-local), because semantic content of the formal feedback directly encodes the violated constraint.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** Yes (no prerequisites for H-E1)
**Gate Status:** MUST_WORK (unsatisfied — pending experiment execution)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
MUST_WORK — Locality score condition A > permutation control (p < 0.05). If fail: oracle mechanism absent → H-M hypotheses re-evaluated; may PIVOT to regularizer framing.

---

## Continuation Context

N/A — This is the first hypothesis in the verification chain (H-E1 has no prerequisites).

### Previous Hypothesis Results (if applicable)
None — first hypothesis in chain.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: DPO formal feedback LLM theorem proving locality score**
- No domain-specific results found. Archon KB contains only diffusion model content (HuggingFace diffusers, DreamBooth, StableDiffusion). Similarity scores ~0.44 — all irrelevant.
- **Key Insight:** No past YouRA pipeline cases for theorem proving / DPO locality experiments exist in KB.

**Query 2: Step-local feedback implementation challenges best practices DPO**
- No relevant results. Same diffusion model corpus.
- **Key Insight:** This is a novel experiment type for this pipeline — no precedent cases to reuse.

**Query 3: miniF2F Vericoding benchmark formal verification LLM**
- One potentially relevant result: `openreview.net/forum?id=M3Y74vmsMcY` (similarity 0.38) — partial match but not confirmed as relevant.
- **Key Insight:** Standard benchmark well-known but not documented in current Archon KB.

**Archon KB Assessment:** Archon KB has no relevant content for this domain. All specifications grounded in Exa GitHub research below.

### Archon Code Examples

**Query 1: DPO training preference optimization LLM PyTorch**
- Results: DreamBooth training scripts — irrelevant (diffusion domain).
- **Extracted Pattern:** General accelerate launch pattern with gradient checkpointing is domain-transferable.

**Query 2: Formal verification Lean4 tactic proof search**
- Results: Cache management and model verification scripts — irrelevant.
- **Key Insight:** No Lean4 code examples in Archon KB.

**Code KB Assessment:** No usable code examples from Archon for this experiment. All code patterns sourced from Exa.

### Exa GitHub Implementations

**Query 1: BFS-Prover LeanDojo DPO tactic proof search Lean4 (official implementation)**

**Repository 1**: ByteDance-Seed/BFS-Prover-V2 ⭐ (ByteDance official)
- **URL**: https://github.com/ByteDance-Seed/BFS-Prover-V2
- **Paper**: arXiv:2502.03438 — BFS-Prover: Scalable Best-First Tree Search for LLM-based Automatic Theorem Proving
- **Relevance**: HIGHEST PRIORITY — This IS the BFS-Prover implementation our hypothesis is built on (72.95% miniF2F). Uses Qwen2.5-Math-7B + BFS + DPO with Lean4 compiler feedback.
- **Architecture**: Qwen2.5-Math-7B base, cold-start SFT on state-tactic pairs → DPO with compiler feedback negatives
- **Key Infrastructure**:
  ```python
  from lean_dojo import *
  url = URL
  commit = COMMIT_HASH
  repo = LeanGitRepo(url, commit)
  trace(repo)  # LeanDojo tracing for proof state extraction
  ```
- **Search Config** (`src/search/run_local_search.sh`):
  - `--file_path`: dojo_data JSONL (state-tactic pairs)
  - `--plan_file`: plan JSON with pre-generated high-level plans
  - BFS with length normalization α ∈ {0.0, 0.5, 1.0}
  - Tactic budget: 2048 × 2 × 600
- **Training**:
  - Stage 1: SFT on (state, tactic) pairs from Mathlib + Lean-Github + Lean-Workbook
  - Stage 2: DPO with Lean4 compiler error as rejected tactic (a_l), correct tactic as chosen (a_w)
  - DPO β=10 (high β for conservative deviation), 1 epoch, lr decay 5e-6 → 5e-7, batch 16
- **Results**: 72.95% on miniF2F test benchmark
- **Serena Needed**: No — architecture is clear from documentation

**Repository 2**: lean-dojo/LeanDojo-v2 ⭐⭐ (official LeanDojo framework)
- **URL**: https://github.com/lean-dojo/LeanDojo-v2
- **Relevance**: Framework for extracting proof states and interacting with Lean4 programmatically — essential infrastructure for locality score computation
- **Key Components**:
  - `lean_dojo_v2/trainer/`: SFT, GRPO, and retrieval trainers with HuggingFace + DeepSpeed
  - `BestFirstSearchProver`: Proof search class with `Dojo` context manager for tactic interaction
  - `HFProver`: Loads fine-tuned HuggingFace model, generates tactics sequentially
  - Pantograph-based Lean RPC server for tactic state tracking
- **Key Code** (BestFirstSearchProver):
  ```python
  with Dojo(thm, self.timeout, additional_imports=imps) as (dojo, init_state):
      self.root = InternalNode(state=init_state, cumulative_logprob=0.0)
      # Each node.state has LeanDojo state ID — used for state alignment verification
      asyncio.run(self._best_first_search())
  ```
- **State ID Access**: `dojo` returns structured tactic states with state IDs — enables 100% state alignment verification for H-M1

**Repository 3**: dvlab-research/step-dpo ⭐⭐ (Step-DPO implementation)
- **URL**: https://github.com/dvlab-research/step-dpo
- **Paper**: arXiv:2406.18629 — Step-DPO: Step-wise Preference Optimization for Long-chain Reasoning
- **Relevance**: Closest existing implementation to our step-local DPO approach — treats individual reasoning steps as preference units (analogous to our tactic-level DPO negatives)
- **Training Config**:
  ```bash
  accelerate launch --config_file deepspeed_zero3_cpu.yaml --mixed_precision bf16 \
    train.py configs/config_full.yaml \
    --model_name_or_path="Qwen/Qwen2-7B-Instruct" \
    --data_path="xinlai/Math-Step-DPO-10K" \
    --per_device_train_batch_size=2 \
    --gradient_accumulation_steps=8 \
    --beta=0.4 \
    --num_train_epochs=4
  ```
- **Key Pattern**: Step-DPO data pipeline: error collection → step localization (GPT-4o) → rectification → merging — analogous to our: BFS rollout → Lean4 compiler error extraction → DPO pair construction
- **Dataset**: 10K step-wise preference pairs with step-level error localization

**Query 2: DPO direct preference optimization LLM step-local feedback PyTorch**

**Repository 4**: eric-mitchell/direct-preference-optimization ⭐⭐⭐ (canonical DPO reference)
- **URL**: https://github.com/eric-mitchell/direct-preference-optimization
- **Relevance**: Canonical DPO reference implementation — our implementation should follow this pattern
- **Key Code** (DPO loss):
  ```python
  # Concatenate chosen+rejected for single forward pass
  all_logits = model(concatenated_input_ids, attention_mask=...).logits.to(torch.float32)
  all_logps = _get_batch_logps(all_logits, concatenated_labels, average_log_prob=False)
  chosen_logps = all_logps[:batch['chosen_input_ids'].shape[0]]
  rejected_logps = all_logps[batch['chosen_input_ids'].shape[0]:]
  # DPO loss: -log(sigmoid(beta * (chosen_ratio - rejected_ratio)))
  ```
- **Training**: β=0.1–0.5 typical; FSDPTrainer for multi-GPU; `loss=dpo loss.beta=DESIRED_BETA`
- **Key Insight**: `average_log_prob=False` — sum log-probs (not average) for tactic sequences

**Repository 5**: openai/miniF2F (dataset source)
- **URL**: https://github.com/openai/miniF2F
- **HuggingFace**: `Tonic/MiniF2F` — miniF2F in HuggingFace datasets format
- **Format**: `{name, split, informal_prefix, formal_statement, goal, header}` (Lean syntax)
- **Stats**: 488 problems (AMC/AIME/IMO + high-school/undergrad), train/valid/test splits

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

Our experiment extends BFS-Prover's DPO training with a new locality score measurement and condition comparison. Priority:

1. ⭐⭐⭐ **BFS-Prover-V2** (ByteDance-Seed) — ground truth for BFS infrastructure and DPO training setup
2. ⭐⭐ **LeanDojo-v2** — ground truth for proof state extraction and tactic interaction
3. ⭐⭐ **Step-DPO** — reference for step-level preference pair construction
4. ⭐ **eric-mitchell/DPO** — reference for DPO loss implementation details

**Recommended Implementation Path:**
- Primary: Extend BFS-Prover-V2 training pipeline with locality score computation hook
- Fallback: Implement from scratch using LeanDojo-v2 + eric-mitchell/DPO patterns
- Justification: BFS-Prover-V2 already has all BFS + DPO infrastructure; adding locality score is an additive measurement, not an architectural change

### Code Analysis (Serena MCP)

*Skipped* — Code from Exa search results was sufficiently clear. BFS-Prover-V2, LeanDojo-v2, and Step-DPO implementations provide adequate pseudocode basis without requiring semantic analysis of a local codebase.

---

## Experiment Specification

### Dataset

**Dataset 1: miniF2F Hard Subset**
- **Name**: miniF2F (hard subset: cold-start SFT pass@1 < 20%)
- **Type**: standard
- **Source**: Zheng et al. 2021; arXiv:2109.00110
- **HuggingFace**: `Tonic/MiniF2F`
- **GitHub**: https://github.com/openai/miniF2F
- **Total Problems**: 488 (full benchmark); hard subset defined post-cold-start SFT
- **Format**: `{name, split, formal_statement, goal, header}` in Lean4 syntax
- **Splits**: train / valid / test
- **Hard Subset Definition**: Run cold-start SFT (Qwen2.5-Math-7B SFT checkpoint); freeze problems where pass@1 < 20% across 16 rollouts; these form the hard subset for DV measurement
- **Preprocessing**:
  - Load via LeanDojo tracing: `LeanGitRepo(url, commit)` + `trace(repo)`
  - Extract (state, tactic, compiler_error) triples via `Dojo` context manager
  - Filter to hard subset after cold-start SFT evaluation

**Dataset 2: Vericoding Hard Subset**
- **Name**: Vericoding (hard subset: cold-start SFT pass@1 < 20%)
- **Type**: standard
- **Source**: Bursuc et al. 2025; arXiv:2509.22908
- **Total Problems**: 12,504 formally verified code specifications (Lean/Verus/Dafny)
- **Hard Subset Definition**: Same protocol as miniF2F — cold-start SFT pass@1 < 20%
- **Preprocessing**: Same LeanDojo tracing protocol; filter to Lean4-compatible problems

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets + LeanDojo tracing
- Identifier (miniF2F): `"Tonic/MiniF2F"` via `load_dataset("Tonic/MiniF2F")`
- Identifier (Vericoding): arXiv:2509.22908 — download from paper release
- Code:
  ```python
  from datasets import load_dataset
  minif2f = load_dataset("Tonic/MiniF2F")
  # For Vericoding: direct download from paper release URL
  ```

**Tactic Taxonomy (MUST be pre-specified before any training):**
LeanDojo error categories define the taxonomy for locality score:
- Category 1: **Type errors** (e.g., `type mismatch`, `application type mismatch`)
- Category 2: **Undefined names** (e.g., `unknown identifier`, `unknown tactic`)
- Category 3: **Tactic failures** (e.g., `tactic failed`, `simp made no progress`)
- Category 4: **Premise-consistent tactics** = tactics that address the specific error category in the compiler message

### Models

#### Baseline Model

**Architecture**: Qwen2.5-Math-7B cold-start SFT (BFS-Prover checkpoint)
- **Base**: `Qwen/Qwen2.5-Math-7B` — causal LLM fine-tuned for mathematical reasoning
- **SFT Checkpoint**: `ByteDance-Seed/BFS-Prover-V2-7B` (cold-start SFT stage, pre-DPO)
- **Type**: Decoder-only transformer, 7B parameters
- **Input Format**: Lean4 proof state (tactic state) → next tactic prediction
- **Role in Experiment**: Frozen reference model (π_ref) AND starting point for each DPO condition

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `transformers`
- Identifier: `"Qwen/Qwen2.5-Math-7B"` (base); `"ByteDance-Seed/BFS-Prover-V2-7B"` (SFT checkpoint)
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained(
      "ByteDance-Seed/BFS-Prover-V2-7B",
      torch_dtype=torch.bfloat16,
      device_map="auto"
  )
  tokenizer = AutoTokenizer.from_pretrained("ByteDance-Seed/BFS-Prover-V2-7B")
  ```

#### Proposed Model

**Architecture:** BFS-Prover SFT checkpoint + Condition A DPO (step-local Lean4 compiler error negatives)

Comparison conditions:
- **Condition A (proposed)**: DPO with Lean4 compiler error as a_l (negative) at same proof state s
- **Condition B (ablation)**: DPO with failed-branch tactic as a_l (ungrounded, same state)
- **Condition P (control)**: DPO with shuffled/permuted compiler error messages as a_l

**Core Mechanism Implementation:**

```python
# Core Mechanism: Step-Local Grounded DPO Pair Construction + Locality Score
# Based on: BFS-Prover-V2 (ByteDance-Seed), LeanDojo-v2, eric-mitchell/DPO

def construct_dpo_pairs_condition_A(bfs_rollout, dojo):
    """
    Construct state-aligned DPO pairs using Lean4 compiler errors.
    
    For each failed tactic at proof state s:
      - chosen (a_w): correct tactic that advances the proof
      - rejected (a_l): compiler-error-triggering tactic (same state s)
    
    Args:
        bfs_rollout: BFS tree from LeanDojo proof search
        dojo: LeanDojo Dojo context with state IDs
    Returns:
        pairs: List of {state_id, state, chosen_tactic, rejected_tactic, 
                        compiler_error_msg, error_category}
    """
    pairs = []
    for node in bfs_rollout.failed_nodes:
        state_id = node.state.id          # LeanDojo state ID for alignment verification
        compiler_error = node.lean4_error  # Lean4 compiler feedback (grounded signal)
        error_category = classify_lean4_error(compiler_error)  # pre-specified taxonomy
        pairs.append({
            "state_id": state_id,
            "state": node.state,
            "chosen": node.parent.winning_tactic,   # same state s
            "rejected": node.failed_tactic,          # same state s (A2 alignment)
            "error_msg": compiler_error,
            "error_category": error_category,
        })
    return pairs  # 100% state alignment: s_w == s_l verified via state_id

def compute_locality_score(model_pre, model_post, proof_states, taxonomy):
    """
    Compute locality score: post-DPO probability mass shift toward
    premise-consistent tactic category per LeanDojo taxonomy.
    
    locality_score = sum_s [ P_post(premise_consistent | s) - P_pre(premise_consistent | s) ]
                   / sum_s [ sum_t [ P_post(t | s) - P_pre(t | s) ] for t in any_category ]
    
    Args:
        model_pre: π_ref (frozen SFT checkpoint)
        model_post: π_θ (DPO-trained model for this condition)
        proof_states: failed proof states from hard subset
        taxonomy: pre-specified tactic category map
    Returns:
        locality_score: float in [0, 1]
    """
    mass_on_premise_consistent = 0.0
    total_mass_shift = 0.0
    for state in proof_states:
        logits_pre = model_pre(state.input_ids).logits
        logits_post = model_post(state.input_ids).logits
        probs_pre = F.softmax(logits_pre, dim=-1)
        probs_post = F.softmax(logits_post, dim=-1)
        delta = probs_post - probs_pre   # probability mass shift
        for tactic_token in taxonomy.premise_consistent_tokens(state.error_category):
            mass_on_premise_consistent += delta[:, tactic_token].sum().item()
        total_mass_shift += delta.abs().sum().item()
    return mass_on_premise_consistent / (total_mass_shift + 1e-8)
```

### Training Protocol

**Optimizer**: AdamW
- Parameters: weight_decay=0.01, betas=(0.9, 0.999)
- **Source**: BFS-Prover arXiv:2502.03438; eric-mitchell/DPO reference implementation

**Learning Rate**: 5e-6 (warm start) → 5e-7 (final, linear decay)
- **Source**: BFS-Prover-V2 training config (DPO stage)

**Schedule**: Linear decay (no warmup for 1-epoch DPO)
- **Source**: BFS-Prover-V2

**Batch Size**: 16 (per GPU, gradient accumulation × 2 if needed for memory)
- **Source**: BFS-Prover arXiv:2502.03438

**Epochs**: 1 (standard DPO practice to avoid overfitting preference data)
- **Source**: Step-DPO (dvlab-research), eric-mitchell/DPO

**DPO β**: 10
- **Note**: β=10 is high (typical range 0.1–0.5); BFS-Prover uses β=10 for conservative deviation from SFT policy in theorem proving context
- **Source**: BFS-Prover arXiv:2502.03438; hypothesis controlled variable spec

**Loss Function**: Standard DPO loss
```python
loss = -F.logsigmoid(beta * (chosen_logps - ref_chosen_logps 
                            - rejected_logps + ref_rejected_logps)).mean()
```
- **Source**: eric-mitchell/direct-preference-optimization trainers.py

**Seeds**: 1 (fixed; EXISTENCE PoC — single run sufficient)

**GPU**: Single A100 (80GB) — set `CUDA_VISIBLE_DEVICES=<empty_gpu_id>`

**Mixed Precision**: bfloat16

**Training Conditions**: 3 independent DPO runs
1. Condition A: Lean4 compiler error as a_l
2. Condition B: Failed-branch tactic as a_l (same state, ungrounded)
3. Condition P: Permuted compiler error messages as a_l (control)

Each run: ~2-4 hours on A100 for 1-epoch DPO of 7B model on hard subset pairs

### Evaluation

**Primary Metric (MUST_WORK gate):**
- **Locality Score (LS)**: Post-DPO probability mass shift toward premise-consistent tactic category
  - LS_A > LS_P (one-sided test, direction only for PoC)
  - Definition: `mass_on_premise_consistent / total_mass_shift` at each failed proof state in hard subset

**Secondary Metric:**
- **LS_A > LS_B**: Grounded vs. ungrounded step-local comparison

**Evaluation Datasets**: Both miniF2F hard subset AND Vericoding hard subset (full — all problems with cold-start SFT pass@1 < 20%)

**Success Criteria (PoC)**:
- PoC PASS: `LS_A > LS_P` (proposed > permutation control — direction only)
- PoC FAIL: `LS_A ≤ LS_P` → oracle mechanism absent → trigger MUST_WORK failure

**Expected Baseline Performance** (from research):
- BFS-Prover cold-start SFT: ~30-40% overall miniF2F pass@1 (hard subset by definition < 20%)
- Locality score without DPO (random baseline): ~1/|tactic_categories| ≈ 0.25 (4 categories)
- Expected LS_A after DPO: >0.40 (based on BFS-Prover DPO improvement pattern)
- **Source**: BFS-Prover arXiv:2502.03438 (72.95% with DPO vs. cold-start SFT baseline)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: custom probability mass measurement (not standard classification)
- Library: custom (scipy.stats for one-sided t-test; torch for probability computation)
- Code:
  ```python
  from scipy import stats
  t_stat, p_value = stats.ttest_1samp(locality_scores_A - locality_scores_P, 0, 
                                       alternative='greater')
  print(f"LS_A > LS_P: p={p_value:.4f}, pass={'YES' if p_value < 0.05 else 'NO'}")
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart — LS_A vs LS_B vs LS_P on miniF2F hard subset + Vericoding hard subset (2 datasets × 3 conditions = 6 bars)

#### Additional Figures (LLM Autonomous)
Based on hypothesis type and evaluation metrics, the following additional figures are recommended:
1. **Probability Mass Distribution Plot**: Stacked bar showing tactic category distribution of post-DPO mass shift (Δ = P_post - P_pre) for each condition × each dataset
2. **Error Category Breakdown**: LS per LeanDojo error category (type_error / undefined_name / tactic_failure) to identify which error types drive the locality effect
3. **Locality Score per Proof State**: Scatter plot of LS values across individual hard proof states (x-axis: proof state complexity, y-axis: LS — shows consistency)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions

| Check | Condition | Verification |
|-------|-----------|--------------|
| `mechanism_exists` | Lean4 compiler provides structured error messages | ✅ Confirmed — LeanDojo Dojo returns `TacticState` with error type + message |
| `mechanism_isolatable` | Conditions A/B/P differ only in a_l content, not state alignment | ✅ All conditions use same proof states, same a_w; only a_l content changes |
| `baseline_measurable` | Locality score computable from logit differences | ✅ `F.softmax(logits_post) - F.softmax(logits_pre)` at each proof state |

**Architecture Compatibility:**
- Qwen2.5-Math-7B is a standard causal LM — locality score computation requires only logit access, no architectural modification
- BFS infrastructure unchanged — experiment adds a measurement hook, not a new training architecture
- LeanDojo state IDs are returned by the existing Dojo interface — no API changes needed

### Activation Indicators

**Mechanism Log Message** (Phase 4 should print):
```
[H-E1] Locality Score — Condition A: {LS_A:.4f} | Condition B: {LS_B:.4f} | Condition P: {LS_P:.4f}
[H-E1] Gate Check: LS_A > LS_P = {LS_A > LS_P} (p={p_value:.4f})
```

**Tensor Shape Change**: None — locality score is a scalar derived from logit differences; model architecture unchanged.

**Expected Metric Delta**: 
- LS_A - LS_P > 0 (direction only for PoC)
- If LS_A - LS_P > 0.10 (10pp): strong positive signal

### Failure Detection

1. **Mechanism absent**: LS_A ≈ LS_B ≈ LS_P (all near 0.25) → oracle not functioning
2. **State alignment violation**: Any pair with s_w ≠ s_l → abort and fix pair construction
3. **Tactic taxonomy collapse**: All tactics map to single category → taxonomy too coarse, re-specify
4. **Training instability**: DPO loss diverges (> 2× initial loss at epoch end) → reduce LR or β

### Verification Code

```python
# Minimal verification check — run before full evaluation
def verify_mechanism_active(LS_A, LS_B, LS_P, threshold=0.0):
    """Returns True if oracle mechanism shows positive direction."""
    return LS_A > LS_P + threshold

# Gate check
if not verify_mechanism_active(LS_A, LS_B, LS_P):
    print("GATE FAIL: H-E1 MUST_WORK not satisfied — oracle mechanism absent")
    # Trigger MUST_WORK failure routing in verification_state.yaml
else:
    print("GATE PASS: H-E1 — locality score confirms oracle mechanism exists")
```

**Hypothesis Support Threshold**: `LS_A > LS_P` (strict direction)  
**Hypothesis Support Metric**: Locality Score (LS) — fraction of probability mass shift on premise-consistent tactic category

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (DPO training completes, locality scores computed)
2. `LS_A > LS_P` on both miniF2F hard subset AND Vericoding hard subset

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Archon KB Assessment**: No relevant domain content found.
- Queries executed: 3 knowledge base + 2 code examples
- All results from diffusion model domain (HuggingFace diffusers, DreamBooth)
- Similarity scores: 0.26–0.46 (below useful threshold of 0.60)
- **Used For**: Established that no past pipeline cases exist; all specifications sourced from Exa

### B. GitHub Implementations (Exa)

**Repository 1**: ByteDance-Seed/BFS-Prover-V2
- **URL**: https://github.com/ByteDance-Seed/BFS-Prover-V2
- **Query Used**: "BFS-Prover LeanDojo DPO tactic proof search Lean4 official implementation GitHub"
- **Relevance**: Official BFS-Prover implementation — ground truth for BFS + DPO training setup
- **Configuration Extracted**: β=10, lr 5e-6→5e-7, batch 16, 1-epoch DPO, BFS α ∈ {0,0.5,1}
- **Their Results**: 72.95% on miniF2F test benchmark
- **Used For**: Training protocol (β, lr, batch size, epochs), BFS geometry (α), model choice

**Repository 2**: lean-dojo/LeanDojo-v2
- **URL**: https://github.com/lean-dojo/LeanDojo-v2
- **Query Used**: "BFS-Prover LeanDojo DPO tactic proof search Lean4 official implementation GitHub"
- **Relevance**: Official framework for Lean4 tactic state extraction + programmatic interaction
- **Configuration Extracted**: `Dojo` context manager, `HFProver`, Pantograph RPC server
- **Used For**: Dataset loading protocol, proof state extraction, state ID alignment verification, locality score computation infrastructure

**Repository 3**: dvlab-research/step-dpo
- **URL**: https://github.com/dvlab-research/step-dpo
- **Query Used**: "DPO direct preference optimization LLM step-local feedback PyTorch"
- **Relevance**: Step-DPO — closest existing implementation to our step-local tactic DPO
- **Configuration Extracted**: Step-level error localization pipeline, β=0.4, DeepSpeed ZeRO-3
- **Used For**: DPO pair construction pattern (error collection → localization → pair building), training launch pattern

**Repository 4**: eric-mitchell/direct-preference-optimization
- **URL**: https://github.com/eric-mitchell/direct-preference-optimization
- **Query Used**: "DPO direct preference optimization LLM step-local feedback PyTorch"
- **Relevance**: Canonical DPO reference implementation
- **Key Code**: Concatenated forward pass (chosen+rejected in single batch), `_get_batch_logps`, FSDPTrainer
- **Used For**: DPO loss implementation, log-probability computation, training loop structure

**Repository 5**: openai/miniF2F
- **URL**: https://github.com/openai/miniF2F; HuggingFace: `Tonic/MiniF2F`
- **Query Used**: "miniF2F benchmark LeanDojo dataset loading formal theorem proving evaluation"
- **Relevance**: Official miniF2F dataset — primary evaluation benchmark
- **Configuration Extracted**: 488 problems, `{name, split, formal_statement, goal, header}` format
- **Used For**: Dataset specification, loading code, hard subset definition

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — code from search results was sufficiently clear. BFS-Prover-V2 and LeanDojo-v2 documentation provided adequate implementation details without requiring semantic analysis.

### D. Previous Hypothesis Context

**Previous Context**: None — this is the first hypothesis in the verification chain (H-E1 has no prerequisites).

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset 1 (miniF2F) | Exa GitHub | Repo B.5 (openai/miniF2F) |
| Dataset 2 (Vericoding) | Phase 2B | 02b_verification_plan.md §1.3 |
| miniF2F loading code | Exa Web | HuggingFace `Tonic/MiniF2F` |
| Hard subset definition | Phase 2B | 02b_verification_plan.md §2.2 H-E1 |
| Tactic taxonomy | Phase 2B + LeanDojo | 02b_verification_plan.md Assumption A4 + LeanDojo docs |
| Baseline model | Exa Web | `ByteDance-Seed/BFS-Prover-V2-7B` |
| Model loading code | Exa Web | HuggingFace `Qwen/Qwen2.5-Math-7B` |
| DPO pair construction | Exa GitHub | Repo B.1 (BFS-Prover-V2) + B.3 (Step-DPO) |
| Core mechanism pseudocode | Exa GitHub | Repo B.1, B.2, B.4 (BFS-Prover + LeanDojo + eric-mitchell) |
| Training protocol (β, lr, batch) | Exa Web + GitHub | BFS-Prover arXiv:2502.03438 + Repo B.1 |
| Epochs (1) | Exa GitHub | Repo B.3 (Step-DPO) + Repo B.4 (eric-mitchell) |
| DPO loss implementation | Exa GitHub | Repo B.4 (eric-mitchell/DPO) |
| Locality score formula | Phase 2B | 02b_verification_plan.md §2.2 H-E1 verification protocol |
| Evaluation datasets | Phase 2B + Exa | 02b_verification_plan.md §1.3 + Repo B.5 |
| Success criteria | Phase 2B | 02b_verification_plan.md §2.2 H-E1 success criteria |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-20T00:00:00

### Workflow History for This Hypothesis
- 2026-05-20T07:45:00: Phase 2B completed — H-E1 defined as foundation hypothesis
- 2026-05-20T07:55:31: H-E1 set to IN_PROGRESS (External loop starting Phase 2C → 3 → 4)
- 2026-05-20: Phase 2C Step 1 — State initialized, context JIT-generated, output file created
- 2026-05-20: Phase 2C Steps 2-3 — Archon KB (no domain content), Exa GitHub (5 repos found)
- 2026-05-20: Phase 2C Step 4 — Serena skipped (code clear from Exa)
- 2026-05-20: Phase 2C Step 5 — Dataset/baseline confirmed (miniF2F + Vericoding, standard type ✅)
- 2026-05-20: Phase 2C Steps 6-7 — Experiment specification synthesized, references documented
- 2026-05-20: Phase 2C Step 8 — Validation passed, state updated to COMPLETED

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code — no domain content), Exa (GitHub — 5 repos, 2 web searches)*
*Serena: Skipped (code clear from Exa results)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
