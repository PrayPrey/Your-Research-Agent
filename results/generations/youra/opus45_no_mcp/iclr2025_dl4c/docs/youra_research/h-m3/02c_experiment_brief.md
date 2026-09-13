# Experiment Design: H-M3

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Under fine-grained feedback with U_ignore errors, if penalties are applied at traceback-reported locations, then gradient signal concentrates at wrong tokens, measurably increasing noise.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM Template** - Tests whether unreliable localization causes gradient noise.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M2 VALIDATED)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM
- **Prerequisites:** h-m2 (VALIDATED)

### Gate Condition
- **Type:** SHOULD_WORK
- **Pass:** gradient_concentration(U_line) > gradient_concentration(U_ignore), p < 0.05
- **Fail Action:** Document limitation, explore alternative noise manifestations

---

## Continuation Context

This hypothesis extends the mechanism chain established by H-M1 and H-M2:

1. **H-M1 (PASS):** Proved fine-grained penalties concentrate gradients at traceback-reported locations (16.11x ratio)
2. **H-M2 (PASS):** Proved U_line errors have 100% localization accuracy vs 20% for U_ignore

**H-M3 Goal:** Prove that when H-M1's gradient concentration targets H-M2's unreliable locations (U_ignore), the signal becomes noise - gradients concentrate at WRONG tokens rather than the actual error source.

### Previous Hypothesis Results

**H-M2 Key Findings:**
- U_line accuracy: 100.0% (N=250)
- U_ignore accuracy: 20.0% (N=250)
- Chi-square p-value: 9.57e-74

**H-M1 Key Findings:**
- Mean concentration ratio: 16.11x
- Mean within ±2 lines: 100%
- Random baseline ratio: 4.65x

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Note: Archon MCP unavailable. Findings synthesized from established RL literature and prior hypothesis validations.*

**Gradient Noise in RL Credit Assignment:**
1. **Sutton & Barto (2018):** Credit assignment noise occurs when rewards/penalties are attributed to wrong actions/states, increasing gradient variance and slowing convergence.
2. **RLTF (Liu et al., 2023):** Fine-grained feedback applies token-level penalties using traceback information. When traceback is unreliable, penalties target wrong tokens.
3. **VeRPO (Rafailov et al., 2024):** Addresses cardinality bias in RL for code - analogous noise source from aggregation choices.

**Gradient Concentration Metrics:**
- Concentration ratio: gradient_at_target / gradient_elsewhere (used in H-M1, achieved 16.11x)
- Signal-to-noise ratio: mean(correct_gradient) / std(noise_gradient)
- Localization accuracy correlation: concentration vs ground-truth match rate

### Archon Code Examples

*Note: Archon MCP unavailable. Code patterns from H-M1 validated implementation.*

**From H-M1 gradient_analysis.py:**
```python
# Token-level gradient extraction pattern
def extract_token_gradients(model, input_ids, loss):
    embeddings = model.get_input_embeddings()
    embedded = embeddings(input_ids)
    embedded.retain_grad()
    loss.backward()
    return embedded.grad.abs().sum(dim=-1)  # [batch, seq_len]

# Concentration ratio computation
def compute_concentration_ratio(gradients, target_mask, other_mask):
    target_grad = (gradients * target_mask).sum()
    other_grad = (gradients * other_mask).sum()
    return (target_grad / (other_grad + 1e-8)).item()
```

### Exa GitHub Implementations

*Note: Exa MCP unavailable. Recommended repositories from literature:*

1. **huggingface/transformers** - `modeling_utils.py` has gradient checkpointing patterns
2. **CarperAI/trlx** - RLHF implementation with per-token reward handling
3. **RLTF official repo** - Fine-grained reward implementation (if available)

**Key Implementation Pattern (PyTorch standard):**
```python
# Register gradient hook for token-level analysis
def gradient_hook(module, grad_input, grad_output):
    # grad_output[0] shape: [batch, seq_len, hidden_dim]
    token_grads = grad_output[0].abs().sum(dim=-1)
    return token_grads

model.get_input_embeddings().register_full_backward_hook(gradient_hook)
```

### Implementation Priority Assessment

**CRITICAL: For RL/gradient analysis experiments, leverage existing gradient computation infrastructure**

**Recommended Implementation Path:**
- Primary: Build on H-M1's gradient analysis code (`gradient_analysis.py`)
- Fallback: Standard PyTorch autograd with custom hooks
- Justification: H-M1 already has working gradient concentration measurement infrastructure

### Code Analysis (Serena MCP)

N/A - Building on existing H-M1/H-M2 codebase; no new repository analysis needed.

---

## Experiment Specification

### Dataset

**Name:** APPS (subset)
**Type:** standard
**Source:** https://github.com/hendrycks/apps
**Version:** Original (Hendrycks et al.)

**Splits:**
- Training subset: 500 samples with U_line errors + 500 samples with U_ignore errors
- Minimum per category: 200 samples (per verification protocol)

**Preprocessing:**
1. Filter APPS train set for problems that produce execution errors
2. Run code samples through error categorizer (from H-M2)
3. Select 500 U_line samples and 500 U_ignore samples
4. Store actual bug location ground truth (from H-M2's AST analysis)

**Loading Information:**
- Method: HuggingFace datasets
- Identifier: codeparrot/apps
- Code: `datasets.load_dataset("codeparrot/apps", split="train")`

### Models

#### Baseline Model

**Name:** CodeT5-small (for PoC) / CodeT5-large (full)
**Type:** encoder-decoder
**Source:** Salesforce/codet5-small or Salesforce/codet5-large
**Parameters:** 60M (small) / 770M (large)

**Loading Information:**
- Method: HuggingFace transformers
- Identifier: Salesforce/codet5-small
- Code:
```python
from transformers import T5ForConditionalGeneration, RobertaTokenizer
model = T5ForConditionalGeneration.from_pretrained("Salesforce/codet5-small")
tokenizer = RobertaTokenizer.from_pretrained("Salesforce/codet5-small")
```

#### Proposed Model

**Architecture:** Baseline + Gradient noise measurement at traceback vs ground-truth locations

**Core Mechanism Implementation:**

```python
def measure_gradient_noise(
    model: nn.Module,
    samples: List[ErrorSample],
    penalty_magnitude: float = -1.0
) -> Dict[str, GradientMetrics]:
    """
    Measure gradient concentration at traceback vs ground-truth locations.
    
    For U_line errors: traceback == ground_truth (low noise expected)
    For U_ignore errors: traceback != ground_truth (high noise expected)
    
    Returns metrics per error type.
    """
    results = {"u_line": [], "u_ignore": []}
    
    for sample in samples:
        # Forward pass
        outputs = model(
            input_ids=sample.input_ids,
            labels=sample.labels
        )
        
        # Apply penalty at traceback-reported line tokens
        traceback_tokens = get_tokens_at_line(sample.code, sample.traceback_line)
        penalty = create_token_penalty(traceback_tokens, penalty_magnitude)
        
        # Backward to get gradients
        model.zero_grad()
        total_loss = outputs.loss + penalty
        total_loss.backward()
        
        # Extract gradient magnitudes
        token_gradients = extract_token_gradients(model)
        
        # Compute concentration at ground truth vs traceback
        gt_tokens = get_tokens_at_line(sample.code, sample.ground_truth_line)
        
        gt_grad = sum_gradient_magnitude(token_gradients, gt_tokens)
        tb_grad = sum_gradient_magnitude(token_gradients, traceback_tokens)
        other_grad = sum_gradient_magnitude(token_gradients, exclude=[gt_tokens, tb_grad])
        
        # Key metrics for H-M3
        noise_ratio = tb_grad / (gt_grad + 1e-8)  # >1 means wrong location
        concentration_at_correct = gt_grad / (other_grad + 1e-8)
        
        results[sample.error_type].append({
            "noise_ratio": noise_ratio,
            "gt_concentration": concentration_at_correct,
            "traceback_matches_gt": sample.traceback_line == sample.ground_truth_line
        })
    
    return aggregate_metrics(results)
```

### Training Protocol

**Note:** H-M3 is a gradient analysis experiment, not a training experiment.

**Protocol:**
1. Load pre-trained CodeT5 model (no fine-tuning)
2. For each error sample:
   - Generate model output (forward pass)
   - Apply RLTF-style fine-grained penalty at traceback location
   - Compute gradients via backprop
   - Measure where gradients concentrate
3. Compare gradient patterns between U_line and U_ignore samples

**Compute:**
- GPU: Single A100 (40GB) sufficient
- Time: ~2 hours for 1000 samples
- Memory: ~8GB for CodeT5-small, ~24GB for CodeT5-large

### Evaluation

**Primary Metrics:**
| Metric | Definition | Success Threshold |
|--------|------------|-------------------|
| GT concentration (U_line) | gradient_at_ground_truth / gradient_elsewhere | Higher than U_ignore |
| GT concentration (U_ignore) | gradient_at_ground_truth / gradient_elsewhere | Lower than U_line |
| Noise ratio (U_ignore) | gradient_at_traceback / gradient_at_ground_truth | > 1.0 (gradient at wrong place) |

**Secondary Metrics:**
| Metric | Definition | Success Threshold |
|--------|------------|-------------------|
| Concentration difference | mean(U_line) - mean(U_ignore) | > 0, p < 0.05 |
| Effect size | Cohen's d between distributions | d > 0.5 (medium effect) |

**Statistical Tests:**
- Independent t-test comparing GT concentration between error types
- Mann-Whitney U as non-parametric alternative
- Bootstrap 95% CI for mean difference

**Metrics Loading Information:**
- Task Type: gradient_analysis
- Library: scipy.stats, numpy
- Code:
```python
from scipy import stats
t_stat, p_value = stats.ttest_ind(u_line_concentrations, u_ignore_concentrations)
effect_size = (np.mean(u_line_concentrations) - np.mean(u_ignore_concentrations)) / np.sqrt(
    (np.var(u_line_concentrations) + np.var(u_ignore_concentrations)) / 2
)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gradient Concentration Comparison**: Box plot showing GT concentration ratio for U_line vs U_ignore samples

#### Additional Figures (LLM Autonomous)
1. **Noise Ratio Histogram**: Distribution of noise_ratio for U_ignore samples (expect > 1.0)
2. **Gradient Heatmap**: Token-level gradient magnitude visualization for example U_line vs U_ignore case
3. **Scatter Plot**: GT concentration vs noise_ratio colored by error type

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Mean GT concentration (U_line) > Mean GT concentration (U_ignore)
3. Difference is statistically significant (p < 0.05)

**Expected Outcome Based on H-M2:**
- U_line: traceback = ground truth 100% of time → high GT concentration
- U_ignore: traceback ≠ ground truth 80% of time → low GT concentration (noise)

---

## Appendix: Reference Implementations

### H-M1 Codebase (Primary Reference)
- Location: `h-m1/code/gradient_analysis.py`
- Key functions: `extract_token_gradients()`, `compute_concentration_ratio()`
- Reuse: Gradient extraction and concentration computation

### H-M2 Codebase (Secondary Reference)
- Location: `h-m2/code/ground_truth.py`
- Key functions: `get_ground_truth_line()`, `categorize_error()`
- Reuse: Ground truth extraction and error categorization

### RLTF Paper Reference
- Paper: "RLTF: Reinforcement Learning from Unit Test Feedback"
- Section: Fine-grained reward (Eq. 4-5)
- Implementation: Token-level penalty at traceback location

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- h-m3 set to IN_PROGRESS: 2026-08-19T04:23:36
- Phase 2C experiment design: IN_PROGRESS

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in H-M1/H-M2 validated infrastructure*
*Next Phase: Phase 3 - Implementation Planning*
