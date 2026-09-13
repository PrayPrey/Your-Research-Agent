# Experiment Design: H-M3

**Date:** 2026-03-27
**Author:** Anonymous
**Hypothesis Statement:** Projection-only LoRA can redistribute state energy toward slow eigenmodes (ΔE > 0.1 nats), effectively utilizing latent memory capacity without changing eigenvalues.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing Eigenmode Energy Redistribution (EUH)

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M2 VALIDATED)
**Gate Status:** SHOULD_WORK (G4)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M2 (Eigenvalue Preservation - VALIDATED)

### Gate Condition
- **Pass Condition:** ΔE > 0.1 nats (energy shift toward slow eigenmodes)
- **Fail Action:** PIVOT to MHSH (Memory Horizon Separation Hypothesis)
- **Interpretation:** If projection-only LoRA succeeds at long-range tasks AND shows energy redistribution, EUH is supported

---

## Continuation Context

This experiment builds directly on H-M2 findings:
- H-M2 proved that projection-only LoRA preserves eigenvalues (|ΔH_spec| = 0.0000%)
- A_log parameters remain frozen during training
- H_spec = 256.43 tokens (unchanged)

**Key Question for H-M3:** If eigenvalues are preserved, HOW does LoRA enable task adaptation? The hypothesis is that LoRA redistributes input energy toward slow eigenmodes (modes with |λ| close to 1) that have longer memory.

### Previous Hypothesis Results (if applicable)
**H-M2 Key Findings:**
- Eigenvalue correlation: 1.0000 (perfect preservation)
- A_log Max Diff: 0.0 (completely frozen)
- H_spec: 256.43 tokens pre and post training
- Validation Perplexity: 15.58
- LoRA targets: in_proj, x_proj only

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Eigenmode Energy Redistribution SSM**
- Limited direct results - eigenmode energy redistribution is a novel concept specific to this research
- No existing implementations in Archon KB for SSM eigenmode analysis

**Query 2: Mamba LoRA Fine-tuning**
- **Source:** HuggingFace PEFT Documentation (https://huggingface.co/docs/peft/conceptual_guides/adapter)
- **Key Insights:**
  - LoRA represents weight updates ΔW with low-rank decomposition: ΔW = BA where B ∈ R^(d×r), A ∈ R^(r×k)
  - Original weights remain frozen; only adapter matrices are trained
  - LoRA is orthogonal to other PEFT methods and preserves pretrained knowledge
  - AdaLoRA dynamically allocates rank based on importance scores (relevant for energy distribution)
  - X-LoRA uses dynamic gating to activate different adapters based on hidden states

**Query 3: State Space Model Energy Distribution**
- No direct matches for SSM energy analysis
- Related: Hidden state analysis patterns from attention processors

**Key Architectural Insight (AdaLoRA):**
- AdaLoRA uses SVD-like parameterization: ΔW = P × Λ × Q where Λ contains singular values
- Importance scoring based on contribution to model performance
- This provides a conceptual parallel: energy redistribution can be measured via singular value shifts

### Archon Code Examples

**Query 1: Mamba SSM Eigenvalue PyTorch**
- No direct code examples for SSM eigenvalue extraction
- General PyTorch device handling patterns available

**Query 2: LoRA Energy Distribution Hidden State**
- **Source:** HuggingFace Diffusers LoRA Examples
- **Pattern:** LoRA dimension matching is critical - query/key/value dimensions must align
- **Code Pattern (LoRA Attention):**
```python
# LoRA processor pattern from diffusers
d_attn = 16
rank = 4
lora_processor = LoRAAttnProcessor(hidden_size=d_attn, rank=rank)
# LoRA modifies hidden states through low-rank projection
```

**Relevance to H-M3:**
- LoRA modifies input/output projections without changing core parameters
- Energy redistribution must occur through changed projection weights
- Measurement approach: Compare eigenmode energy before/after LoRA training

### Exa GitHub Implementations

**Query 1: Mamba SSM Eigenvalue Analysis**

**Repository 1**: [state-spaces/mamba](https://github.com/state-spaces/mamba) (⭐ 17,733)
- **URL**: https://github.com/state-spaces/mamba
- **Relevance**: Official Mamba implementation by Gu & Dao - THE authoritative source
- **Architecture**: Mamba SSM with selective state spaces
- **Key Insight**: Contains A_log parameter implementation which we analyze for eigenvalues
- **License**: Apache 2.0

**Repository 2**: [AmeenAli/HiddenMambaAttn](https://github.com/AmeenAli/HiddenMambaAttn) (⭐ 231)
- **URL**: https://github.com/AmeenAli/HiddenMambaAttn
- **Relevance**: **HIGHLY RELEVANT** - Analyzes hidden state behavior in Mamba models
- **Paper**: "The Hidden Attention of Mamba Models" (ACL 2025)
- **Key Insight**: Shows SSMs can be viewed as attention-driven models; provides explainability methods for peering into Mamba's inner workings
- **Applicability**: Methods for analyzing internal state representations could be adapted for energy distribution analysis

**Repository 3**: [furiosa-ai/ssm-state-tuning](https://github.com/furiosa-ai/ssm-state-tuning) (⭐ 15)
- **URL**: https://github.com/furiosa-ai/ssm-state-tuning
- **Relevance**: **DIRECTLY RELEVANT** - State-based PEFT for SSMs
- **Paper**: "State-offset Tuning: State-based Parameter-Efficient Fine-Tuning for State Space Models" (ACL 2025)
- **Key Insight**: Studies PEFT methods on SSM-based models; benchmarks which modules are effective for fine-tuning
- **Finding**: Prompt-based methods perform differently on SSMs than Transformers

**Repository 4**: [yuhkalhic/SSMLoRA](https://github.com/yuhkalhic/ssmlora) (⭐ 10)
- **URL**: https://github.com/yuhkalhic/ssmlora
- **Relevance**: SSMLoRA - LoRA specifically designed for SSMs
- **Paper**: "SSMLoRA: Enhancing Low-Rank Adaptation with State Space Model" (NAACL 2025)
- **Key Insight**: SSM-specific LoRA enhancements

**Query 2: State Space Model PEFT**

**Key Paper Finding**: "Parameter-Efficient Fine-Tuning of State Space Models" (arXiv:2410.09016)
- Systematic study of PEFT on SSM-based models
- Key questions addressed: (i) How do existing PEFT methods perform on SSMs? (ii) Which modules are most effective?
- Finding: Prompt-based methods (e.g., prefix-tuning) behave differently on SSMs

**Serena Analysis Needed**: Yes - Complex eigenmode energy computation requires custom implementation

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Implementation | Rationale |
|----------|----------------|-----------|
| ⭐⭐⭐ HIGHEST | state-spaces/mamba (official) | Ground truth for Mamba architecture, A_log parameter access |
| ⭐⭐ HIGH | HuggingFace PEFT + Mamba | Proven LoRA integration from H-M2 experiments |
| ⭐ MEDIUM | HiddenMambaAttn analysis methods | Hidden state explainability techniques |
| ⭐ LOW | furiosa-ai/ssm-state-tuning | Reference for state-based PEFT approaches |

**Recommended Implementation Path:**
- Primary: Build on H-M2 codebase (state-spaces/mamba-1.4b-hf + PEFT) with custom energy measurement hooks
- Fallback: Use HiddenMambaAttn analysis methods adapted for eigenmode energy tracking
- Justification: H-M2 already validated LoRA on Mamba; we extend with energy measurement rather than rebuilding

### Code Analysis (Serena MCP)

**Analysis Source**: H-M2 validated codebase at `h-m2/code/`

**Code Structure (From H-M2)**:
- `MambaProbe`: Extracts A_log tensors from Mamba layers
- `LoRAAdapter`: Applies projection-only LoRA via PEFT
- `EigenvaluePreservationValidator`: Computes eigenvalue preservation metrics

**Key Code Pattern - Eigenvalue Extraction**:
```python
# From H-M2 model.py - reusable for H-M3
def extract_layer_A_log(self) -> List[Tensor]:
    """Return list of A_log tensors, one per layer."""
    a_logs = []
    for layer in self.model.backbone.layers:
        A_log = layer.mixer.A_log.detach().float()
        a_logs.append(A_log)
    return a_logs

# Discrete eigenvalue computation
# λ = exp(-exp(A_log))
eigenvalues = torch.exp(-torch.exp(a_log.float()))
```

**H-M3 Extension - Energy Redistribution Measurement**:
The key insight is that while eigenvalues remain fixed (H-M2 proved), the **energy distribution** across eigenmodes can change via projection matrices. We need to measure:

1. **Modal Energy**: For each eigenmode i, compute energy E_i = ||h_i||² where h_i is the component of hidden state in eigenmode i
2. **Slow Mode Fraction**: Fraction of total energy in slow modes (|λ| > 0.99)
3. **Energy Shift ΔE**: Change in slow mode fraction after LoRA training

**Core Mechanism for H-M3**:
```python
# Pseudo-code for eigenmode energy measurement
def compute_eigenmode_energy(model, input_ids):
    """Compute energy distribution across eigenmodes."""
    # Get hidden states from SSM computation
    with torch.no_grad():
        # Hook to capture SSM hidden states
        hidden_states = []  # [batch, seq, d_inner, d_state]

        # For each layer, decompose state into eigenmode components
        for layer_idx, state in enumerate(hidden_states):
            A_log = model.backbone.layers[layer_idx].mixer.A_log
            eigenvalues = torch.exp(-torch.exp(A_log))  # [d_inner, d_state]

            # State energy per mode: ||state[:,:,:,mode]||²
            mode_energy = (state ** 2).sum(dim=(0,1,2))  # [d_state]

            # Identify slow modes: |λ| > 0.99 (long memory)
            slow_mask = eigenvalues.abs() > 0.99
            slow_energy = mode_energy[slow_mask].sum()
            total_energy = mode_energy.sum()

            slow_fraction = slow_energy / total_energy

    return slow_fraction  # in nats: -log(1-slow_fraction)

# Gate metric: ΔE = slow_fraction_post - slow_fraction_pre > 0.1 nats
```

**Integration with H-M2 Codebase**:
- Reuse `MambaProbe` for model loading and A_log extraction
- Reuse `LoRAAdapter` for projection-only LoRA
- Add `EigenmodeEnergyAnalyzer` class for energy measurement
- Hook into SSM forward pass to capture hidden states

---

## Experiment Specification

### Dataset

**Name:** WikiText-103
**Type:** standard
**Source:** HuggingFace Datasets

**Justification for Dataset Selection:**
- **Phase 2A specified MQAR (synthetic)** - PROHIBITED by synthetic data policy
- **Replacement:** WikiText-103 (real, standard dataset)
- **Rationale:** H-M3 tests eigenmode energy redistribution, which can be measured on ANY language modeling task. WikiText-103 provides:
  1. Real natural language data (not synthetic)
  2. Consistency with H-M1 and H-M2 experiments (controlled comparison)
  3. Long sequences for memory-dependent language modeling
  4. Standard benchmark with established baselines

**Statistics:**
- Train: 103M tokens (28,591 articles)
- Validation: 218K tokens
- Test: 246K tokens
- Vocabulary: ~267K tokens

**Preprocessing:**
- Tokenizer: Mamba tokenizer (GPT-NeoX compatible)
- Sequence length: 256 tokens (matches H_spec from H-E1/H-M1)
- Chunking: Non-overlapping sequences

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets
- Identifier: `wikitext`, config: `wikitext-103-raw-v1`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("wikitext", "wikitext-103-raw-v1")
```

### Models

#### Baseline Model

**Architecture:** state-spaces/mamba-1.4b-hf
**Type:** Pretrained SSM (State Space Model)
**Source:** HuggingFace Hub

**Justification:**
- Same model as H-E1, H-M1, H-M2 (controlled comparison)
- 48 layers with accessible A_log parameters for eigenanalysis
- H_spec = 256.43 tokens (validated in H-E1)
- Eigenvalue preservation confirmed in H-M2

**Configuration:**
- Parameters: 1.4B total
- Layers: 48
- d_model: 2048
- d_state: 16
- Pretrained: Yes (HuggingFace Hub)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `state-spaces/mamba-1.4b-hf`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained(
    "state-spaces/mamba-1.4b-hf",
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("state-spaces/mamba-1.4b-hf")
```

#### Proposed Model

**Architecture:** Mamba-1.4B + Projection-Only LoRA + Eigenmode Energy Analyzer
**Integration Point:**
- LoRA applied to: `in_proj`, `x_proj` (projection matrices only)
- Energy analyzer: Hooks on SSM forward pass to capture hidden states
**Modification:** Add energy measurement hooks to track eigenmode activation patterns

**Core Mechanism Implementation:**

```python
# Core Mechanism: Eigenmode Energy Redistribution Analyzer
# Based on: H-M2 codebase (MambaProbe) + HiddenMambaAttn analysis methods

class EigenmodeEnergyAnalyzer:
    """
    Measures energy distribution across SSM eigenmodes.
    ΔE > 0.1 nats indicates significant redistribution toward slow modes.
    """
    def __init__(self, model, config):
        self.model = model
        self.config = config
        self.hooks = []
        self.hidden_states = []

    def register_hooks(self):
        """Register forward hooks on SSM layers to capture hidden states."""
        for layer in self.model.backbone.layers:
            hook = layer.mixer.register_forward_hook(self._capture_state)
            self.hooks.append(hook)

    def _capture_state(self, module, input, output):
        """Capture SSM hidden state for energy analysis."""
        # output contains processed hidden state
        self.hidden_states.append(output.detach())

    def compute_eigenmode_energy(self) -> dict:
        """Compute energy distribution across eigenmodes.

        Returns:
            dict with slow_mode_fraction, total_energy, per_layer_energy
        """
        results = {'per_layer': [], 'slow_fraction': 0.0}

        for layer_idx, layer in enumerate(self.model.backbone.layers):
            A_log = layer.mixer.A_log.detach().float()
            eigenvalues = torch.exp(-torch.exp(A_log))  # [d_inner, d_state]

            # Identify slow modes: |λ| > 0.99 (long memory retention)
            slow_mask = eigenvalues.abs() > 0.99

            if self.hidden_states:
                state = self.hidden_states[layer_idx]
                # Energy per mode = ||state component||²
                mode_energy = (state ** 2).sum(dim=(0, 1))  # [d_state]
                slow_energy = mode_energy[slow_mask.any(dim=0)].sum()
                total_energy = mode_energy.sum()
                slow_frac = (slow_energy / total_energy).item()
            else:
                slow_frac = slow_mask.float().mean().item()

            results['per_layer'].append(slow_frac)

        results['slow_fraction'] = sum(results['per_layer']) / len(results['per_layer'])
        return results

    def compute_delta_e(self, pre_energy: dict, post_energy: dict) -> float:
        """Compute energy shift ΔE in nats (KL-divergence approximation)."""
        pre_frac = pre_energy['slow_fraction']
        post_frac = post_energy['slow_fraction']
        # Approximate KL divergence for binary distribution
        delta_e = abs(post_frac - pre_frac)
        # Convert to nats: -log(1 - delta) approximation
        delta_e_nats = -math.log(1 - min(delta_e, 0.99))
        return delta_e_nats

# Integration with training loop:
# 1. Pre-training: analyzer.compute_eigenmode_energy() -> pre_energy
# 2. Apply LoRA, train on WikiText-103
# 3. Post-training: analyzer.compute_eigenmode_energy() -> post_energy
# 4. Compute: delta_e = analyzer.compute_delta_e(pre_energy, post_energy)
# 5. Gate: PASS if delta_e > 0.1 nats
```

### Training Protocol

**From Previous Hypothesis (H-M2):**
- **Optimizer**: AdamW
  - Parameters: lr=1e-4, weight_decay=0.01, betas=(0.9, 0.999)
- **Learning Rate**: 1e-4 (fixed, no schedule for PoC)
- **Batch Size**: 2 (effective: 16 with gradient accumulation 8)
- **Epochs**: 1 (PoC configuration - sufficient for energy redistribution measurement)
- **Loss**: Cross-entropy (language modeling)
- **Sequence Length**: 256 tokens (matches H_spec)
- **Training Sequences**: 500 (subsampled for PoC, statistically meaningful)

**LoRA Configuration** (reused from H-M2):
- Rank (r): 16
- Alpha: 32
- Target modules: `in_proj`, `x_proj` (projection-only)
- Dropout: 0.1

**Rationale**: Optimal configuration validated in H-M2; reusing for controlled experiment. Energy redistribution should be measurable even with minimal training.

**Seeds**: 1 (fixed at 42 for reproducibility)

### Evaluation

**Primary Metrics:**
1. **ΔE (Energy Shift)**: Change in slow-mode energy fraction (in nats)
   - Definition: KL-divergence approximation between pre/post eigenmode energy distributions
   - Gate threshold: ΔE > 0.1 nats

2. **Slow Mode Fraction**: Percentage of total state energy in slow modes (|λ| > 0.99)
   - Pre-training baseline: ~X% (to be measured)
   - Post-training: Should increase if EUH is correct

3. **Validation Perplexity**: Language modeling quality (sanity check)
   - Expected: ~15-20 (similar to H-M2)

**Success Criteria:**
- **GATE PASS**: ΔE > 0.1 nats (measurable energy shift toward slow eigenmodes)
- **Secondary**: Perplexity improves or stays stable (model not degraded)

**Interpretation:**
- ΔE > 0.1: EUH mechanism confirmed - LoRA redistributes energy to slow modes
- ΔE ≈ 0: Energy distribution unchanged - pivot to MHSH hypothesis

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Language Modeling + Eigenmode Analysis
- Library: Custom (based on H-M2 code) + torch for tensor operations
- Code:
```python
# Perplexity via HuggingFace
from transformers import Trainer
# Eigenmode energy via custom EigenmodeEnergyAnalyzer class
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: ΔE actual vs threshold (0.1 nats) bar chart with PASS/FAIL annotation

#### Additional Figures (LLM Autonomous)

1. **Eigenmode Energy Distribution (Pre vs Post)**
   - Histogram of energy per eigenmode before and after LoRA training
   - Overlay slow mode threshold (|λ| > 0.99)

2. **Per-Layer Slow Mode Fraction**
   - Bar chart showing slow_fraction for each of 48 layers
   - Pre-training vs post-training comparison

3. **Eigenvalue Spectrum with Energy Overlay**
   - Scatter plot: eigenvalue magnitude vs energy contribution
   - Color-code by slow/fast mode classification

4. **Training Loss Curve**
   - Cross-entropy loss over training steps
   - Sanity check for training stability

5. **Energy Shift Timeline (Optional)**
   - If checkpoints available: energy redistribution over training epochs

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. ΔE > 0.1 nats (measurable energy shift toward slow eigenmodes)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: HuggingFace PEFT Documentation
- **Type**: Technical documentation
- **URL**: https://huggingface.co/docs/peft/conceptual_guides/adapter
- **Query Used**: "Mamba LoRA fine-tuning eigenvalues memory"
- **Relevance**: Definitive guide on LoRA implementation and PEFT methods
- **Key Insights**:
  - LoRA represents weight updates as low-rank decomposition ΔW = BA
  - Original weights remain frozen; only adapters trained
  - AdaLoRA uses SVD-like importance scoring (parallel to energy distribution concept)
- **Used For**: Understanding LoRA mechanism, training protocol design

**Source A.2**: Long Range Arena Benchmark
- **Type**: Research benchmark
- **URL**: https://arxiv.org/abs/2011.04006
- **Query Used**: "long range dependency benchmark real dataset"
- **Relevance**: Standard benchmark for evaluating long-range sequence models
- **Used For**: Context for dataset selection rationale

### B. GitHub Implementations (Exa)

**Repository B.1**: [state-spaces/mamba](https://github.com/state-spaces/mamba) (⭐ 17,733)
- **URL**: https://github.com/state-spaces/mamba
- **Query Used**: "Mamba SSM state space model eigenvalue analysis PyTorch"
- **Relevance**: Official Mamba implementation - THE authoritative source
- **Key Code**: A_log parameter access pattern
- **Used For**: Model loading, eigenvalue extraction (A_log access)

**Repository B.2**: [AmeenAli/HiddenMambaAttn](https://github.com/AmeenAli/HiddenMambaAttn) (⭐ 231)
- **URL**: https://github.com/AmeenAli/HiddenMambaAttn
- **Query Used**: "SSM Mamba A matrix eigenvalue spectral analysis"
- **Paper**: "The Hidden Attention of Mamba Models" (ACL 2025)
- **Relevance**: Hidden state analysis methods for Mamba
- **Used For**: Conceptual basis for eigenmode energy analysis hooks

**Repository B.3**: [furiosa-ai/ssm-state-tuning](https://github.com/furiosa-ai/ssm-state-tuning) (⭐ 15)
- **URL**: https://github.com/furiosa-ai/ssm-state-tuning
- **Paper**: "State-offset Tuning" (ACL 2025)
- **Relevance**: State-based PEFT for SSMs
- **Used For**: Understanding SSM-specific fine-tuning patterns

**Repository B.4**: [microsoft/LoRA](https://github.com/microsoft/LoRA) (⭐ 13,367)
- **URL**: https://github.com/microsoft/LoRA
- **Query Used**: "LoRA energy distribution hidden state"
- **Relevance**: Original LoRA implementation
- **Used For**: LoRA theory and implementation patterns

### C. Code Analysis (Serena / Local Codebase)

**Analyzed Code**: H-M2 validated codebase (`h-m2/code/`)
- **Analysis Method**: Direct file reading (Serena project activation failed)
- **Files Analyzed**:
  - `model.py`: MambaProbe, LoRAAdapter, EigenvaluePreservationValidator
  - `evaluate.py`: Perplexity computation, figure generation
- **Key Findings**:
  - A_log extraction: `layer.mixer.A_log.detach().float()`
  - Eigenvalue computation: `λ = exp(-exp(A_log))`
  - LoRA targets: `in_proj`, `x_proj` only
- **Used For**: Core mechanism pseudo-code, energy analyzer design
- **Original Code Pattern**:
```python
# From H-M2 model.py
eigenvalues = torch.exp(-torch.exp(a_log.float()))
```
- **Our Derived Extension**:
```python
# Energy measurement
slow_mask = eigenvalues.abs() > 0.99
slow_energy = mode_energy[slow_mask].sum()
```

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report - H-M2
- **File**: `h-m2/04_validation.md`
- **Reused Components**:
  - Model: state-spaces/mamba-1.4b-hf (same)
  - Dataset: WikiText-103 (same)
  - LoRA config: r=16, alpha=32, targets=in_proj,x_proj
  - Training: AdamW, lr=1e-4, 1 epoch
- **Why Reused**: Enables controlled experiment - only energy measurement added
- **H-M2 Key Findings Applied**:
  - Eigenvalue correlation = 1.0000 (eigenvalues don't change)
  - A_log frozen during training
  - H_spec = 256.43 tokens

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Previous + Real Data Policy | H-M2 + WikiText-103 standard |
| Model architecture | GitHub | B.1 (state-spaces/mamba) |
| LoRA configuration | Previous + Archon | H-M2 + A.1 (PEFT docs) |
| Energy measurement | Code Analysis | C.1 (H-M2 + HiddenMambaAttn) |
| Pseudo-code | GitHub + Analysis | B.2, C.1 |
| Training protocol | Previous | H-M2 04_validation.md |
| Evaluation metrics | Phase 2B | 02b_verification_plan.md |
| Gate threshold (ΔE > 0.1) | Phase 2B | H-M3 specification |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-27T22:53:26Z

### Workflow History for This Hypothesis
- 2026-03-27T22:53:26Z: Hypothesis h-m3 set to IN_PROGRESS
- Phase 2C experiment design started

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
