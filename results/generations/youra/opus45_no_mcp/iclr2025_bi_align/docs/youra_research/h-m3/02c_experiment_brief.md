# Experiment Design: H-M3

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Under single scalar reward training, if models receive one combined signal for correctness and user-modeling, then they miss bidirectional adaptation nuance, because the training objective doesn't distinguish.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** - Testing whether single reward signal causes missing bidirectional nuance.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M2 (PASS - conflation_score=0.999)
**Gate Status:** SHOULD_WORK (pending validation)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M2 (COMPLETED, PASS)

### Gate Condition
**Type:** SHOULD_WORK
**Pass Condition:** Lower sensitivity to bidirectional features + evidence of representation conflation
**Threshold:** r(cluster, bidirectional_features) pattern OR representation separation < threshold

---

## Continuation Context

### Previous Hypothesis Results

**H-M1 Results (PASS):**
- Distribution overlap: 0.647
- Mean confidence diff: 0.018 (threshold <0.1)
- Cross-model consistency: 0.64-0.65 across Llama-7B, Llama-13B, Mistral-7B
- Finding: Models show similar confidence on correctness vs user-state-modeling tasks

**H-M2 Results (PASS):**
- Rate difference: 0.0010
- Conflation score: 0.999
- Finding: High-confidence patterns nearly identical across task types
- All thresholds pass: Annotators do not distinguish task types

**Established Chain:**
1. H-E1: Calibration inversion clusters exist (silhouette=0.6016)
2. H-M1: Models optimize for annotator approval (similar confidence on both types)
3. H-M2: Annotators conflate correctness with user-state-modeling (rate_diff=0.001)
4. **H-M3 (THIS):** Test if single reward signal misses bidirectional nuance

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** Archon MCP unavailable. Using web search findings.

**Query 1: Single Scalar Reward Limitations**
- Source: "Representation-Aware Advantage Estimation" (arXiv:2606.10528)
- Key finding: Most RLHF pipelines rely on single scalar reward from final hidden state
- This "compresses rich internal representations into a point estimate"
- Hidden states encode semantic and preference-aligned relationships that scalar ignores

**Query 2: Reward Conflation Research**
- Source: "Post-hoc Reward Calibration" (arXiv:2409.17407)
- Finding: PPO reward models biased toward high-confidence responses
- Calibration error can be reduced by calibrating reward models during training

**Query 3: Hidden State Analysis**
- Source: "Right Makes Might" (arXiv:2606.03234)
- Finding: Simple linear probe on hidden states predicts reward nearly as well as full RM
- Confirms hidden states encode correctness information that scalar rewards miss

### Archon Code Examples

**Note:** Using web search code repositories.

**Repository 1:** MOSS-RLHF (github.com/OpenLMLab/MOSS-RLHF)
- Complete PPO-max implementation with hidden state analysis
- Compatible with PyTorch 1.13.1
- Includes reward model training code

**Repository 2:** RLHF-Reward-Modeling (github.com/RLHFlow/RLHF-Reward-Modeling)
- Training reward/preference models for PPO/DPO
- Includes representation extraction utilities

### Exa GitHub Implementations

**Query: RLHF representation analysis**

**Repository 1:** rlhf-and-reward-modelling-alt
- URL: https://github.com/kartikmunjal/rlhf-and-reward-modelling-alt
- Full RLHF pipeline with 15 research extensions
- Includes reward signal design and hacking detection
- PyTorch FSDP support, scales 117M to 70B

**Repository 2:** Online_RLHF (NeurIPS 2025)
- URL: https://github.com/ZinYY/Online_RLHF
- One-pass reward modeling implementation
- Efficient online RLHF training

### 🎯 Implementation Priority Assessment

**CRITICAL: For this analysis experiment, we extend H-M1/H-M2 results**

**Recommended Implementation Path:**
- Primary: Extend H-M1 codebase with representation analysis
- Fallback: Build on MOSS-RLHF hidden state extraction
- Justification: Continuation experiment, controlled comparison with prior results

### Code Analysis (Serena MCP)

**Note:** Serena MCP not required for this analysis experiment. 
We extend H-M1/H-M2 code which has already been validated.

---

## Experiment Specification

### Dataset

**Name:** Combined RLHF Benchmarks (same as H-M1/H-M2)
**Type:** standard
**Source:** TruthfulQA (817 tasks) + ETHICS justice (~500 tasks) + HHH single-turn (~200 tasks)
**Total Samples:** 2212 tasks (from H-M1 results)
**Task Distribution:**
- Type A (Correctness): 1977 tasks (89.4%)
- Type B (User-State-Modeling): 235 tasks (10.6%)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets + lm-evaluation-harness
- Identifier: truthful_qa, hendrycks/ethics, Anthropic/hh-rlhf
- Code: 
```python
# Reuse H-M1 data loading (already cached)
from datasets import load_dataset
truthfulqa = load_dataset("truthful_qa", "multiple_choice")
ethics = load_dataset("hendrycks/ethics", "justice")
# Use cached classification from H-M1/H-M2
```

### Models

#### Baseline Model

**Architecture:** Llama-2-7B-Chat (primary), Llama-2-13B-Chat, Mistral-7B-Instruct
**Type:** Instruction-following LLM (RLHF-trained)
**Source:** meta-llama/Llama-2-7b-chat-hf, meta-llama/Llama-2-13b-chat-hf, mistralai/Mistral-7B-Instruct-v0.2

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: meta-llama/Llama-2-7b-chat-hf
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-chat-hf",
    torch_dtype=torch.float16,
    device_map="auto",
    output_hidden_states=True  # CRITICAL for representation analysis
)
```

#### Proposed Model

**Architecture:** Same models with hidden state extraction

**Core Mechanism Implementation:**

```python
# Core Mechanism: Bidirectional Feature Sensitivity Analysis
# Based on: H-M1/H-M2 confidence analysis + hidden state extraction

class BidirectionalSensitivityAnalyzer:
    """
    Analyze whether model representations distinguish bidirectional features.
    H-M3 tests: Do hidden states separate Type A vs Type B tasks?
    """
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        
    def extract_hidden_states(self, prompts: List[str]) -> torch.Tensor:
        """Extract last token hidden states for analysis."""
        inputs = self.tokenizer(prompts, return_tensors="pt", padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs, output_hidden_states=True)
        # Last layer, last token hidden state
        return outputs.hidden_states[-1][:, -1, :]  # (B, hidden_dim)
    
    def compute_representation_separation(
        self, 
        type_a_hidden: torch.Tensor,
        type_b_hidden: torch.Tensor
    ) -> Dict[str, float]:
        """
        Measure separation between Type A and Type B representations.
        Low separation = single reward signal misses bidirectional nuance.
        """
        # Cosine similarity within vs across types
        intra_a = F.cosine_similarity(type_a_hidden.unsqueeze(1), 
                                       type_a_hidden.unsqueeze(0), dim=-1)
        intra_b = F.cosine_similarity(type_b_hidden.unsqueeze(1),
                                       type_b_hidden.unsqueeze(0), dim=-1)
        inter = F.cosine_similarity(type_a_hidden.unsqueeze(1),
                                    type_b_hidden.unsqueeze(0), dim=-1)
        
        separation = (intra_a.mean() + intra_b.mean()) / 2 - inter.mean()
        return {"separation_score": separation.item()}
```

### Training Protocol

**Note:** This is an ANALYSIS experiment (no training required)

**Analysis Protocol:**
- **Step 1:** Load cached H-M1/H-M2 task classifications (Type A/B)
- **Step 2:** Extract hidden states for all 2212 tasks
- **Step 3:** Compute representation separation metrics
- **Step 4:** Test linear separability (SVM probe)
- **Step 5:** Compare with H-M1 confidence patterns

**Configuration:**
- Batch size: 8 (for hidden state extraction)
- Hidden layer: Last transformer layer
- Seeds: 1 (fixed for reproducibility)
- GPU: Single GPU with float16

### Evaluation

**Primary Metrics:**
- **Representation Separation Score:** Intra-type vs inter-type cosine similarity difference
- **Linear Probe Accuracy:** SVM classification of Type A vs Type B from hidden states
- **Sensitivity Index:** Gradient magnitude w.r.t. bidirectional features

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: analysis (representation comparison)
- Library: sklearn.svm, scipy.spatial
- Code:
```python
from sklearn.svm import LinearSVC
from sklearn.model_selection import cross_val_score
from scipy.spatial.distance import cosine

# Linear probe for separability
probe = LinearSVC()
probe_accuracy = cross_val_score(probe, hidden_states, task_types, cv=5).mean()
```

**Success Criteria:**
- **SHOULD_WORK Gate:** Evidence that models show lower sensitivity to bidirectional features
- **Pass:** separation_score < 0.1 OR probe_accuracy < 0.6 (representations conflated)
- **Fail:** separation_score > 0.3 AND probe_accuracy > 0.8 (representations distinct)

**Expected Results (from research):**
- Based on "Representation-Aware Advantage Estimation" findings
- Scalar reward compresses rich representations → expect low separation
- Hidden states likely encode SOME distinction, but weak (probe ~0.55-0.65)

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Separation score vs threshold bar chart

#### Additional Figures (LLM Autonomous)
- Hidden state t-SNE/UMAP with Type A/B coloring
- Probe accuracy per layer (if multi-layer analysis)
- Comparison with H-M1 confidence distributions

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** True - representation analysis requires hidden state extraction
- **mechanism_isolatable:** True - comparison between task types is isolated
- **baseline_measurable:** True - random separation baseline computable

### Architecture Compatibility
- Models must support `output_hidden_states=True`
- HuggingFace transformers API compatible (all 3 models confirmed)

### Activation Indicators
- **mechanism_log_message:** "Extracted {n} hidden states, computing separation..."
- **tensor_shape_change:** Hidden states shape (N, hidden_dim) where hidden_dim ~4096
- **metric_delta_expected:** Separation score 0.0-0.3 (low = supports hypothesis)

### Mechanism Verification Code
```python
def verify_mechanism():
    # Check hidden states extracted
    assert hidden_states.shape[1] == model.config.hidden_size
    
    # Check both task types present
    assert len(type_a_hidden) > 100 and len(type_b_hidden) > 50
    
    # Compute separation
    separation = compute_representation_separation(type_a_hidden, type_b_hidden)
    print(f"[MECHANISM VERIFIED] Separation score: {separation}")
    return separation
```

### Success Criteria
- **hypothesis_support_threshold:** separation_score < 0.1 OR probe_accuracy < 0.6
- **hypothesis_support_metric:** representation_separation_score

---

## 🔬 PoC Success Check

**Gate Condition (SHOULD_WORK):**
1. Code runs without error
2. Hidden states successfully extracted
3. Separation score computed
4. Evidence supports: single reward signal misses bidirectional nuance

**Pass Logic:**
```python
gate_pass = (separation_score < 0.1) or (probe_accuracy < 0.6)
# Low separation = representations conflated = hypothesis supported
```

---

## Appendix: Reference Implementations

### Research Papers
1. **Representation-Aware Advantage Estimation** (arXiv:2606.10528)
   - Key insight: Scalar rewards miss rich hidden state information
   - Relevance: Direct support for H-M3 hypothesis

2. **Post-hoc Reward Calibration** (arXiv:2409.17407)
   - Calibration methods for reward models
   - Relevance: Background on reward signal limitations

3. **Right Makes Might** (arXiv:2606.03234)
   - Linear probes on hidden states
   - Relevance: Methodology for representation analysis

### Code Repositories
1. **MOSS-RLHF** - https://github.com/OpenLMLab/MOSS-RLHF
   - PPO implementation with hidden state access
   
2. **RLHF-Reward-Modeling** - https://github.com/RLHFlow/RLHF-Reward-Modeling
   - Reward model training with representation analysis

3. **rlhf-and-reward-modelling-alt** - https://github.com/kartikmunjal/rlhf-and-reward-modelling-alt
   - Full pipeline with reward signal design extensions

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19T07:15:00+00:00

### Workflow History for This Hypothesis
- 2026-08-19: Hypothesis h-m3 set to IN_PROGRESS (External loop)
- 2026-08-19: Phase 2C experiment design initiated
- Prerequisites: H-M1 (PASS), H-M2 (PASS)

---

*MCP Tools Used: WebSearch (GitHub + arXiv)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
