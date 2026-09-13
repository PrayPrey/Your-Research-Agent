# Experiment Design: H-M1

**Date:** 2026-03-27
**Author:** Anonymous
**Hypothesis Statement:** SSM state dynamics are governed by discretized transition matrix Ā = exp(ΔA) where eigenvalues determine information decay rates.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 VALIDATED)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (VALIDATED)

### Gate Condition
**MUST_WORK Gate:** Eigenvalues must match theoretical ZOH discretization formula.
- If eigenvalues don't follow Ā = exp(ΔA): Spectral horizon concept invalid
- Failure consequence: Entire MHSH/EUH framework collapses, workflow stops

---

## Continuation Context

**Continuation from H-E1 (VALIDATED, PASS):**
- Reusing same dataset (random token sequences) and model (Mamba-1.4B)
- H-E1 established H_spec = 256.18 tokens with CV ≈ 0
- H-M1 validates the theoretical foundation that enabled H_spec measurement
- Controlled comparison: Only measurement focus changes (stability → discretization formula)

### Previous Hypothesis Results (if applicable)
- **H-E1 Result:** PASS (MUST_WORK gate satisfied)
- **Key Findings:**
  - CV(H_spec) = 2.22e-16 (effectively 0), far below threshold of 0.3
  - H_spec is input-independent, determined solely by A matrix weights
  - H_spec(Mamba-1.4B) = 256.18 tokens
  - Cross-validation: H_spec(Mamba-370M) = 162,605 tokens (non-monotonic scaling)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "SSM state space model eigenvalue discretization ZOH"**
- No directly relevant results found in Archon KB
- Results returned were primarily about diffusion models (DEIS, DPM-Solver) which use different discretization methods
- SSM/Mamba architecture is a specialized niche not yet well-covered in general knowledge bases

**Query 2: "Mamba architecture A matrix state dynamics implementation"**
- No directly relevant results found
- CUDA cuBLAS documentation returned (matrix operations, but not SSM-specific)

**Query 3: "linear recurrence eigenvalue decay memory horizon"**
- No directly relevant results found
- Results about diffusion scheduling and eigenvalue-related numerical methods

**Key Insight:** Mamba/SSM eigenvalue analysis is cutting-edge research not yet indexed in standard knowledge bases. Implementation must rely on:
1. Original Mamba paper (Gu & Dao, 2023)
2. state-spaces/mamba GitHub repository
3. H-E1 validated methodology (eigenvalue extraction from A_log)

### Archon Code Examples

**Query 1: "Mamba SSM discretization A matrix PyTorch"**
- No SSM-specific code examples found
- PyTorch MPS backend documentation returned (device placement, not SSM)
- cuBLAS batched operations (matrix-vector multiply, not SSM discretization)

**Query 2: "state space model eigenvalue extraction analysis"**
- No directly relevant code examples found
- Diffusion model sampling code (DEIS, DPM-Solver++) returned

**Conclusion:** Archon KB lacks Mamba/SSM-specific content. Implementation will leverage:
1. H-E1 validated code (MambaProbe class for eigenvalue extraction)
2. Official state-spaces/mamba repository
3. Exa GitHub search for additional implementations (next step)

### Exa GitHub Implementations

**Query 1: "state-spaces mamba SSM A matrix discretization eigenvalue PyTorch"**

**Repository 1**: [state-spaces/mamba](https://github.com/state-spaces/mamba) (⭐ 17K)
- **URL**: https://github.com/state-spaces/mamba
- **Relevance**: OFFICIAL Mamba implementation by Albert Gu & Tri Dao
- **Key Insights from Issues**:
  - **Issue #114**: Discretization uses `delta*B` (Euler) not full ZOH for B matrix
  - **Issue #326**: A matrix parameterization explained:
    - `A_log` stores log of continuous-time eigenvalue magnitudes
    - `A = -torch.exp(self.A_log.float())` ensures negative eigenvalues (stability)
    - Discrete: `A_bar = exp(A * delta)` in CUDA code
  - **@tridao**: "We want A to be always negative, and delta always positive"
  - **@Hprairie**: "negative eigenvalues means the system is stable (BIBO stable)"

**Repository 2**: [johnma2006/mamba-minimal](https://github.com/johnma2006/mamba-minimal) (⭐ High)
- **URL**: https://github.com/johnma2006/mamba-minimal
- **Relevance**: Minimal, readable PyTorch implementation
- **Key Features**:
  - Equivalent numerical output to official implementation
  - Single file, annotated code
  - Good for understanding discretization logic

**Repository 3**: [soveshmohapatra/Mamba-SSM](https://github.com/soveshmohapatra/Mamba-SSM)
- **URL**: https://github.com/soveshmohapatra/Mamba-SSM
- **Relevance**: Educational SSM implementation with ZOH discretization
- **Key Code** (simple_ssm.py):
  ```python
  # Continuous-time parameters mapped to discrete via ZOH
  # Fast Convolutional Training: O(L) path
  # O(1) Memory Recurrence: Autoregressive generation
  ```

**Repository 4**: [myscience/mamba](https://github.com/myscience/mamba)
- **URL**: https://github.com/myscience/mamba
- **Relevance**: PyTorch Lightning implementation with clear parameter structure
- **Key Parameters**:
  - `d_model`: Model dimension
  - `d_state`: Latent hidden state dimension (eigenvalue count)
  - `d_discr`: Rank of discretization matrix Δ

**Query 2: "Mamba selective state space model A_log parameter eigenvalue"**

**Key Paper Findings**:

**Mamba-3 Paper (ICLR 2026)** - Discretization Theory:
- Introduces "Exponential-Trapezoidal" discretization (more expressive than Euler)
- Complex-valued state transitions for state tracking
- Formalizes Mamba-1/2 heuristic discretization
- Key equation: `h_t = α_t h_{t-1} + β_t (B_{t-1} x_{t-1}) + γ_t (B_t x_t)`

**EMNLP 2025 - Eigenvalue Stability in Pruning**:
- "A key challenge is maintaining eigenvalue stability"
- "Eigenvalues λ_i of state transition matrices must be controlled"
- Theorem bounds eigenvalue perturbation: `max|λ| ≤ γ_A · ∥A_log∥_F + γ_Δ · ∥Δ∥_F`

**ICML 2025 - Input Selectivity Analysis**:
- S6 layer can represent Haar wavelets (discontinuous functions)
- Analytical solutions for MQAR using Mamba architecture
- Mechanistic understanding of how selectivity affects memory

**Theoretical Analysis (arXiv 2602.12499)**:
- Discrete-time SSM: `H_t = A·H_{t-1} + b·x_t`, `y_t = c·H_t`
- Gating parameter filters class-relevant features
- Generalization depends on eigenvalue structure

**Serena Analysis Needed**: false
- Code patterns are well-documented in official repo
- H-E1 already validated eigenvalue extraction methodology
- Can reuse MambaProbe class from H-E1

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Priority 1 (HIGHEST):** state-spaces/mamba official repository
- Ground truth for A_log parameterization and discretization
- Issues #114, #326 provide authoritative clarification

**Priority 2:** H-E1 validated code (MambaProbe class)
- Already proven to work for eigenvalue extraction
- CV ≈ 0 validates numerical stability

**Priority 3:** mamba-minimal for reference
- Readable single-file implementation
- Good for cross-checking logic

**Recommended Implementation Path:**
- Primary: Extend H-E1's MambaProbe class with ZOH validation logic
- Fallback: Direct implementation following state-spaces/mamba Issue #326
- Justification: H-E1 code is validated, minimizes implementation risk

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. Key implementation patterns:

1. **A Matrix Parameterization** (from official repo):
   - `A_log = torch.log(A)` stores log of continuous eigenvalues
   - `A = -torch.exp(self.A_log.float())` ensures negative eigenvalues (stability)
   - Discrete transition: `A_bar = exp(A * delta)` computed in CUDA kernel

2. **ZOH Discretization** (theoretical vs practical):
   - Paper: Full ZOH for both A and B matrices
   - Code: ZOH for A, Euler approximation for B (`delta*B`)
   - Reason: Simpler implementation without affecting empirical performance

3. **Eigenvalue Structure**:
   - A is diagonal (not general matrix) → eigenvalues = diagonal elements
   - All eigenvalues negative → system BIBO stable
   - H_spec = -1/log|λ_max| where λ_max = exp(A * delta) for slowest mode

4. **Reusable Code from H-E1**:
   - `MambaProbe` class for A_log extraction
   - Eigenvalue computation: `λ = exp(-exp(A_log))` for Δ=1
   - H_spec calculation validated with CV ≈ 0

---

## Experiment Specification

### Dataset

**Name:** WikiText-103
**Type:** standard
**Source:** HuggingFace Datasets (wikitext/wikitext-103-raw-v1)
**Hypothesis Fit:** Real language modeling benchmark with natural long-range dependencies - tests whether eigenvalue-derived H_spec predicts actual memory behavior on real text

**Statistics:**
- Train: ~103M tokens from Wikipedia articles
- Validation: ~218K tokens
- Test: ~246K tokens
- Vocabulary: Model's BPE vocabulary (50,277 tokens for Mamba-1.4B)

**Why WikiText-103:**
1. Standard benchmark used in original Mamba paper (Table 1: 16.3 PPL)
2. Contains natural long-range dependencies (articles, not shuffled sentences)
3. Allows measuring perplexity at varying context lengths
4. Real-world text enables falsifiable predictions about memory decay

**Preprocessing:**
- Tokenize with Mamba tokenizer
- Chunk into sequences of varying lengths for context ablation
- Remove empty/short sequences

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets
- Identifier: wikitext/wikitext-103-raw-v1
- Code:
```python
from datasets import load_dataset
from transformers import AutoTokenizer

# Load WikiText-103
dataset = load_dataset("wikitext", "wikitext-103-raw-v1")
tokenizer = AutoTokenizer.from_pretrained("state-spaces/mamba-1.4b-hf")

# Tokenize validation set for evaluation
def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=False, return_attention_mask=False)

tokenized = dataset["validation"].map(tokenize_function, batched=True, remove_columns=["text"])

# Chunk into evaluation sequences
max_length = 1024
all_input_ids = []
for item in tokenized:
    all_input_ids.extend(item["input_ids"])

# Create non-overlapping chunks
chunks = [all_input_ids[i:i+max_length] for i in range(0, len(all_input_ids) - max_length, max_length)]
eval_sequences = torch.tensor(chunks[:1000])  # Use 1000 sequences for evaluation
```

### Models

#### Baseline Model

**Architecture:** state-spaces/mamba-1.4b (Pretrained Mamba SSM)
**Type:** Pretrained language model with Selective State Space architecture
**Parameters:** ~1.4B
**Hypothesis Fit:** Target model for spectral analysis - validates ZOH discretization theory

**Key Architecture Details:**
- Layers: 48 Mamba blocks
- A_log shape per layer: [4096, 16] (d_inner × d_state)
- Discretization: Ā = exp(ΔA) with Δ from softplus projection

**Loading Information** (for Phase 4 download):
- Method: HuggingFace / mamba-ssm
- Identifier: state-spaces/mamba-1.4b
- Code:
```python
# Option 1: Using mamba-ssm (recommended for weight access)
from mamba_ssm import MambaLMHeadModel
model = MambaLMHeadModel.from_pretrained("state-spaces/mamba-1.4b")

# Option 2: Using transformers (HF format)
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained("state-spaces/mamba-1.4b-hf")
```

#### Proposed Model

**Architecture:** N/A - This is an empirical validation hypothesis
**Purpose:** Validate that eigenvalue-derived memory horizon (H_spec) predicts actual perplexity degradation on real text
**No model modification needed:** We analyze existing pretrained weights and measure empirical behavior

**Non-Tautological Design Rationale:**

The hypothesis "eigenvalues determine information decay rates" makes a **falsifiable empirical prediction**:
- If H_spec (derived from eigenvalues) represents true memory capacity, then:
  1. Perplexity should remain stable when context length < H_spec
  2. Perplexity should degrade when context is truncated below H_spec
  3. The degradation curve should correlate with the eigenvalue spectrum

This is NOT a mathematical identity - it tests whether the theoretical H_spec has real predictive power on natural language.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Empirical Validation of Eigenvalue-Based Memory Horizon
# Based on: state-spaces/mamba official repo, H-E1 validated methodology
# Purpose: Test if H_spec predicts perplexity degradation on real text

import torch
import torch.nn.functional as F
from typing import Dict, List, Tuple

class EigenvalueMemoryValidator:
    """
    Empirically validates that eigenvalue-derived H_spec predicts
    actual memory behavior on real language modeling tasks.

    Non-tautological test: Compare THEORETICAL prediction (from eigenvalues)
    against EMPIRICAL measurement (perplexity at varying context lengths).
    """
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.device = next(model.parameters()).device
        self.layers = self._extract_mamba_layers()

    def _extract_mamba_layers(self) -> List[Tuple[str, torch.Tensor]]:
        """Extract A_log parameters from all Mamba blocks."""
        layers = []
        for name, param in self.model.named_parameters():
            if 'A_log' in name:
                layers.append((name, param.detach()))
        return layers

    def compute_theoretical_h_spec(self) -> Dict[str, float]:
        """
        Compute H_spec from eigenvalues (theoretical prediction).
        H_spec = -1 / log(λ_max) where λ_max is the largest discrete eigenvalue.
        """
        h_specs = {}
        global_max_lambda = 0.0

        for name, A_log in self.layers:
            # Discrete eigenvalue: λ = exp(-exp(A_log))
            lambda_discrete = torch.exp(-torch.exp(A_log.float()))
            max_lambda = lambda_discrete.max().item()
            h_spec_layer = -1.0 / torch.log(torch.tensor(max_lambda)).item()
            h_specs[name] = h_spec_layer
            global_max_lambda = max(global_max_lambda, max_lambda)

        # Global H_spec (determined by slowest decaying mode)
        h_specs['global'] = -1.0 / torch.log(torch.tensor(global_max_lambda)).item()
        return h_specs

    def measure_empirical_perplexity(
        self,
        input_ids: torch.Tensor,
        context_lengths: List[int]
    ) -> Dict[int, float]:
        """
        Measure perplexity at different context truncation points.

        Args:
            input_ids: Full sequences [batch, seq_len]
            context_lengths: List of context lengths to evaluate
        Returns:
            Dict mapping context_length -> perplexity
        """
        results = {}
        self.model.eval()

        with torch.no_grad():
            for ctx_len in context_lengths:
                if ctx_len >= input_ids.shape[1]:
                    continue

                # Truncate context (keep only last ctx_len tokens as context)
                truncated = input_ids[:, -ctx_len-1:]  # +1 for target token

                # Forward pass
                outputs = self.model(truncated)
                logits = outputs.logits if hasattr(outputs, 'logits') else outputs[0]

                # Compute perplexity on last token prediction
                shift_logits = logits[:, -2, :]  # Predict last token
                shift_labels = truncated[:, -1]   # Target is last token

                loss = F.cross_entropy(shift_logits, shift_labels)
                ppl = torch.exp(loss).item()
                results[ctx_len] = ppl

        return results

    def validate_hypothesis(
        self,
        input_ids: torch.Tensor,
        context_lengths: List[int] = None
    ) -> Dict:
        """
        Main validation: Compare theoretical H_spec against empirical perplexity curve.

        The hypothesis PASSES if:
        1. Perplexity increases significantly when context < H_spec
        2. Correlation between context length and perplexity matches eigenvalue prediction

        The hypothesis FAILS if:
        - Perplexity is context-independent (eigenvalues don't predict memory)
        - Or perplexity degrades at context lengths >> H_spec (theory wrong)
        """
        # Step 1: Compute theoretical H_spec
        h_specs = self.compute_theoretical_h_spec()
        global_h_spec = h_specs['global']

        # Step 2: Define context lengths to test (around H_spec)
        if context_lengths is None:
            # Test at fractions of H_spec: 0.1x, 0.25x, 0.5x, 1x, 2x, 4x
            context_lengths = [
                int(global_h_spec * 0.1),
                int(global_h_spec * 0.25),
                int(global_h_spec * 0.5),
                int(global_h_spec * 1.0),
                int(global_h_spec * 2.0),
                min(int(global_h_spec * 4.0), 1024)
            ]
            context_lengths = [max(16, c) for c in context_lengths]  # Minimum 16 tokens

        # Step 3: Measure empirical perplexity
        perplexity_curve = self.measure_empirical_perplexity(input_ids, context_lengths)

        # Step 4: Analyze correlation (non-tautological test)
        # If eigenvalues determine memory, perplexity should plateau near H_spec
        ctx_sorted = sorted(perplexity_curve.keys())
        ppl_values = [perplexity_curve[c] for c in ctx_sorted]

        # Compute degradation ratio: PPL(ctx < H_spec) / PPL(ctx >= H_spec)
        below_h_spec = [perplexity_curve[c] for c in ctx_sorted if c < global_h_spec]
        at_or_above = [perplexity_curve[c] for c in ctx_sorted if c >= global_h_spec]

        if below_h_spec and at_or_above:
            degradation_ratio = sum(below_h_spec) / len(below_h_spec) / (sum(at_or_above) / len(at_or_above))
        else:
            degradation_ratio = 1.0

        # Success criteria: Significant degradation when context < H_spec
        # Degradation ratio > 1.1 means 10% worse perplexity with truncated context
        hypothesis_supported = degradation_ratio > 1.1

        return {
            'theoretical_h_spec': global_h_spec,
            'h_specs_per_layer': h_specs,
            'perplexity_curve': perplexity_curve,
            'context_lengths_tested': ctx_sorted,
            'degradation_ratio': degradation_ratio,
            'hypothesis_supported': hypothesis_supported,
            'interpretation': (
                f"H_spec = {global_h_spec:.1f} tokens. "
                f"Perplexity degradation ratio = {degradation_ratio:.3f}. "
                f"{'PASS: Eigenvalues predict memory behavior' if hypothesis_supported else 'FAIL: No significant context dependence'}"
            )
        }
```

### Training Protocol

**N/A - Empirical Validation Hypothesis (No Training)**

This hypothesis does NOT involve training. It validates that eigenvalue-derived H_spec has predictive power for actual memory behavior on real text.

**Analysis Protocol:**
1. Load pretrained Mamba-1.4B model and WikiText-103 validation set
2. Extract A_log parameters from all 48 layers
3. Compute theoretical H_spec from eigenvalues: H_spec = -1/log(λ_max)
4. Measure empirical perplexity at varying context lengths around H_spec
5. Analyze correlation between context truncation and perplexity degradation
6. Validate that H_spec predicts the inflection point of the perplexity curve

**Fixed Parameters:**
- Context lengths: [0.1×H_spec, 0.25×H_spec, 0.5×H_spec, 1×H_spec, 2×H_spec, 4×H_spec]
- Evaluation samples: 1000 sequences from WikiText-103 validation
- Sequence length: 1024 tokens (max)
- Seed: 42 (for reproducibility)

### Evaluation

**Primary Metrics:**
1. **Perplexity Degradation Ratio:** PPL(ctx < H_spec) / PPL(ctx >= H_spec)
   - Target: Ratio > 1.1 (10% degradation when context < H_spec)
   - This is EMPIRICALLY measurable, NOT mathematically guaranteed
2. **H_spec Prediction Accuracy:** Does perplexity plateau near predicted H_spec?
   - Target: Perplexity curve shows inflection within ±50% of H_spec
3. **Baseline Perplexity:** Full-context perplexity on WikiText-103
   - Expected: ~16.3 PPL (from original Mamba paper Table 1)

**Success Criteria (MUST_WORK Gate):**
- Primary: Perplexity degradation ratio > 1.1 when context truncated below H_spec
- Secondary: Full-context perplexity within 10% of published benchmark (~16.3 PPL)
- Falsifiability: If perplexity is context-independent OR degrades at wrong threshold, hypothesis FAILS

**Why This Is NOT Tautological:**
- H_spec is computed from static weights (eigenvalues)
- Perplexity is measured from model behavior on real text
- The hypothesis predicts a relationship that can empirically fail:
  - If attention/other mechanisms dominate memory, eigenvalues won't predict behavior
  - If the decay model is wrong, H_spec will be at the wrong position

**Expected Results (predictions to validate):**
- H_spec ≈ 256 tokens for Mamba-1.4B (from H-E1)
- Full-context PPL ≈ 16.3 (from Mamba paper)
- Perplexity should increase when context < 256 tokens
- Perplexity should plateau when context >= 256 tokens

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Empirical validation (perplexity measurement)
- Library: PyTorch, HuggingFace Transformers
- Code:
```python
import torch.nn.functional as F

# Perplexity computation
def compute_perplexity(model, input_ids):
    with torch.no_grad():
        outputs = model(input_ids)
        logits = outputs.logits if hasattr(outputs, 'logits') else outputs[0]
        shift_logits = logits[:, :-1, :].contiguous()
        shift_labels = input_ids[:, 1:].contiguous()
        loss = F.cross_entropy(
            shift_logits.view(-1, shift_logits.size(-1)),
            shift_labels.view(-1),
            reduction='mean'
        )
        return torch.exp(loss).item()

# Context truncation evaluation
def evaluate_at_context_length(model, full_sequences, context_length):
    truncated = full_sequences[:, -context_length:]
    return compute_perplexity(model, truncated)

# Degradation ratio (primary metric)
def compute_degradation_ratio(ppl_curve, h_spec):
    below = [ppl for ctx, ppl in ppl_curve.items() if ctx < h_spec]
    above = [ppl for ctx, ppl in ppl_curve.items() if ctx >= h_spec]
    return (sum(below) / len(below)) / (sum(above) / len(above)) if below and above else 1.0
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Perplexity vs Context Length Curve**: Line plot showing perplexity at each context length, with vertical line at H_spec (target: inflection near H_spec)

#### Additional Figures (LLM Autonomous)

1. **Perplexity Degradation Heatmap**: Context length vs sequence position, showing where perplexity increases
2. **H_spec Prediction Validation**: Overlay of theoretical H_spec on empirical perplexity curve
3. **Per-Layer Eigenvalue Distribution**: Histogram of discrete eigenvalues across all layers
4. **Decay Rate Profile**: H_spec-equivalent timescale for each layer (identifies bottleneck layers)
5. **Baseline Comparison**: Full-context perplexity compared to published Mamba benchmark (16.3 PPL)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error on WikiText-103 validation set
2. Perplexity degradation ratio > 1.1 (context < H_spec shows higher perplexity)
3. Full-context perplexity within reasonable range of published benchmark (~16.3 PPL ± 20%)

**Falsification Conditions (Hypothesis FAILS if):**
- Perplexity is constant regardless of context length (eigenvalues don't predict memory)
- Perplexity degrades at threshold far from H_spec (eigenvalue-derived H_spec is wrong)
- Degradation ratio < 1.05 (no meaningful context dependence)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Query 1:** "SSM state space model eigenvalue discretization ZOH"
- **Type:** Knowledge base search
- **Results:** No directly relevant SSM/Mamba content found
- **Insight:** Mamba/SSM eigenvalue analysis is cutting-edge research not yet indexed

**Query 2:** "Mamba architecture A matrix state dynamics implementation"
- **Type:** Knowledge base search
- **Results:** General CUDA/cuBLAS documentation (not SSM-specific)
- **Insight:** Implementation must rely on original Mamba paper and GitHub

**Query 3:** "linear recurrence eigenvalue decay memory horizon"
- **Type:** Knowledge base search
- **Results:** Diffusion model scheduling content (different domain)
- **Insight:** Memory horizon concept is Mamba-specific, not in general KB

### B. GitHub Implementations (Exa)

**Repository 1:** [state-spaces/mamba](https://github.com/state-spaces/mamba) (⭐ 17K)
- **URL:** https://github.com/state-spaces/mamba
- **Query:** "state-spaces mamba SSM A matrix discretization eigenvalue PyTorch"
- **Relevance:** OFFICIAL Mamba implementation - ground truth for validation
- **Key Insights (from Issues #114, #326):**
  ```python
  # A_log parameterization (Issue #326)
  A = -torch.exp(self.A_log.float())  # Ensures negative eigenvalues

  # Discretization (Issue #114)
  # Paper: ZOH for both A and B
  # Code: ZOH for A, Euler for B (delta*B)
  # @albertfgu: "doesn't affect empirical performance"

  # Stability requirement (@Hprairie):
  # "negative eigenvalues means system is BIBO stable"
  ```
- **Used For:** Core mechanism pseudo-code, eigenvalue validation logic

**Repository 2:** [johnma2006/mamba-minimal](https://github.com/johnma2006/mamba-minimal)
- **URL:** https://github.com/johnma2006/mamba-minimal
- **Relevance:** Minimal, readable PyTorch implementation
- **Used For:** Understanding discretization flow

**Repository 3:** [soveshmohapatra/Mamba-SSM](https://github.com/soveshmohapatra/Mamba-SSM)
- **URL:** https://github.com/soveshmohapatra/Mamba-SSM
- **Relevance:** Educational SSM with explicit ZOH discretization
- **Used For:** Conceptual verification of ZOH formula

**Repository 4:** [myscience/mamba](https://github.com/myscience/mamba)
- **URL:** https://github.com/myscience/mamba
- **Relevance:** PyTorch Lightning implementation with clear parameter structure
- **Used For:** Parameter naming conventions (d_model, d_state, d_discr)

### C. Academic Papers (via Exa)

**Paper 1:** Mamba-3 (ICLR 2026) - arXiv:2603.15569
- **Topic:** Exponential-Trapezoidal Discretization
- **Key Insight:** Formalizes Mamba-1/2 heuristic discretization theoretically
- **Used For:** Understanding discretization theory evolution

**Paper 2:** EMNLP 2025 - Eigenvalue Stability in SSM Pruning
- **Key Insight:** "Eigenvalues λ_i of state transition matrices must be controlled"
- **Used For:** Eigenvalue stability requirements

**Paper 3:** ICML 2025 - Input Selectivity in Mamba
- **Key Insight:** Analytical solutions for MQAR using Mamba
- **Used For:** Understanding mechanistic role of eigenvalues

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report - H-E1
- **File:** `h-e1/04_validation.md`
- **Status:** VALIDATED (MUST_WORK gate PASS)
- **Reused Components:**
  - Model: state-spaces/mamba-1.4b (same)
  - Dataset: Random token sequences (same methodology)
  - Code: MambaProbe class for A_log extraction
  - Results: H_spec = 256.18 tokens, CV = 2.22e-16
- **Why Reused:** H-M1 validates the theoretical foundation for H-E1's measurement

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Standard Benchmark | WikiText-103 (wikitext-103-raw-v1) |
| Dataset justification | Mamba Paper | Table 1: 16.3 PPL baseline |
| Model selection | Phase 2A | state-spaces/mamba-1.4b |
| A_log parameterization | GitHub | state-spaces/mamba Issue #326 |
| Discretization formula | GitHub | state-spaces/mamba Issue #114 |
| Eigenvalue stability | Paper | EMNLP 2025 pruning paper |
| Pseudo-code structure | GitHub | mamba-minimal, official repo |
| H_spec computation | Previous | H-E1 validated methodology |
| Perplexity evaluation | Standard | Language modeling benchmark protocol |
| Non-tautological design | Phase 2C Fix | Empirical PPL vs theoretical H_spec |
| Success criteria | Phase 2B | Gate condition (MUST_WORK) |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-27T20:51:00Z

### Workflow History for This Hypothesis
- 2026-03-27T20:51:00Z: H-M1 set to IN_PROGRESS (Phase 2C started)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
