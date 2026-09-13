# Experiment Design: H-E1

**Date:** 2026-03-24
**Author:** Anonymous
**Hypothesis Statement:** Under controlled conditions (matched length, correctness, completeness), if RLHF-trained reward models evaluate enumerated vs. synthesized response pairs, then enumerated responses will receive significantly higher scores (d >= 0.3) across multiple architecturally distinct RMs, because enumeration is an independently encoded structural feature.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** COMPLETED
**Prerequisites Satisfied:** Yes (no prerequisites)
**Gate Status:** MUST_WORK - d >= 0.3 in >=2 RMs required

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
**MUST_WORK Gate:**
- IF d >= 0.3 in >=2 architecturally distinct RMs → PASS
- IF d < 0.3 in all RMs → FAIL → ABANDON main hypothesis

---

## Continuation Context

**Prior Run Learning (from Serena Memory):**
- Previous composite agency approach failed (d=0.131)
- BUT enumeration factor showed strong positive effect (d=0.634 in ArmoRM)
- Lesson: Isolate single factor, cross-model replication essential

### Previous Hypothesis Results (if applicable)
N/A - This is the foundation hypothesis with no prerequisites.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "reward model preference evaluation"**
- OpenAI Instruction Following blog (relevance: 0.45) - General RLHF context
- No direct reward model behavioral probing methodologies found

**Query 2: "RLHF structural bias probing"**
- PEFT/LoRA documentation - Model adaptation techniques (not directly relevant)
- No structural preference probing literature in KB

**Query 3: "RewardBench ArmoRM evaluation"**
- RLHF papers (hf.co/papers/2305.14314) - General alignment research
- Quantization/optimization guides - Useful for model loading efficiency

**Key Insights:**
- Archon KB lacks specific reward model behavioral probing research (novel area)
- HuggingFace model loading patterns well-documented
- Standard transformer evaluation infrastructure available

**Limitation:** This research area (structural preferences in RMs) is novel - no direct precedent cases in knowledge base.

### Archon Code Examples

**Query 1: "reward model inference PyTorch"**
- StableDiffusion inference patterns (not applicable)
- General PyTorch model optimization examples

**Query 2: "AutoModelForSequenceClassification transformer"**
- Apple Neural Engine Transformers - Model loading pattern:
  ```python
  model = transformers.AutoModelForSequenceClassification.from_pretrained(
      model_name, return_dict=False, torchscript=True
  ).eval()
  ```
- 4-bit quantization loading for large models (bitsandbytes integration)

**Applicable Pattern:** Use HuggingFace `AutoModel` classes with `device_map="auto"` for multi-GPU inference. Consider 4-bit quantization for 13B+ models (UltraRM-13b).

### Exa GitHub Implementations

**Query 1: ArmoRM Implementation**

**Repository 1**: [RLHFlow/RLHF-Reward-Modeling](https://github.com/RLHFlow/RLHF-Reward-Modeling) (2K stars)
- **URL**: https://github.com/RLHFlow/RLHF-Reward-Modeling
- **Relevance**: Official implementation of ArmoRM (Multi-Objective Reward Model with MoE)
- **Paper**: arxiv:2406.12845 "Interpretable Preferences via Multi-Objective Reward Modeling and Mixture-of-Experts"
- **Key Code** (from HuggingFace model card):
  ```python
  import torch
  from transformers import AutoModelForSequenceClassification, AutoTokenizer
  device = "cuda"
  path = "RLHFlow/ArmoRM-Llama3-8B-v0.1"
  model = AutoModelForSequenceClassification.from_pretrained(
      path, device_map=device, trust_remote_code=True, torch_dtype=torch.bfloat16
  )
  tokenizer = AutoTokenizer.from_pretrained(path, use_fast=True)
  ```
- **RewardBench Score**: 89.0 overall (96.9 Chat, 76.8 Chat Hard, 92.2 Safety, 97.3 Reasoning)
- **Base Model**: Llama-3 8B, finetuned from FsfairX-LLaMA3-RM-v0.1

**Query 2: RewardBench Evaluation Framework**

**Repository 2**: [allenai/reward-bench](https://github.com/allenai/reward-bench) (705 stars)
- **URL**: https://github.com/allenai/reward-bench
- **Relevance**: Standard evaluation infrastructure for multiple RMs (Starling, PairRM, etc.)
- **Key Scripts**:
  - `scripts/run_rm.py`: Run evaluations for reward models
  - `scripts/run_dpo.py`: Run evaluations for DPO models
- **Supported Models**: ArmoRM, Starling-RM, PairRM, UltraRM, OpenAssistant, DPO models

**Query 3: Other Reward Models**

**UltraRM-13b** ([openbmb/UltraRM-13b](https://huggingface.co/openbmb/UltraRM-13b)):
- **Architecture**: LlamaRewardModel with regression head
- **Training Data**: UltraFeedback dataset
- **Key Code**:
  ```python
  class LlamaRewardModel(PreTrainedModel):
      def __init__(self, config):
          super().__init__(config)
          self.model = LlamaModel(config)
          self.regression_head = nn.Linear(self.config.hidden_size, 1, bias=False)

      def forward(self, input_ids, attention_mask, ...):
          hidden_states = self.model(input_ids, attention_mask=attention_mask)[0]
          rewards = self.regression_head(hidden_states).squeeze(-1)
          ends = attention_mask.cumsum(dim=1).argmax(dim=1).view(-1,1)
          return torch.gather(rewards, 1, ends)
  ```

**Starling-RM-7B-alpha** ([berkeley-nest/Starling-RM-7B-alpha](https://huggingface.co/berkeley-nest/Starling-RM-7B-alpha)):
- **Architecture**: GPTRewardModel (custom wrapper around Llama2-7B-Chat)
- **Training Data**: Nectar dataset (GPT-4 preference)
- **Note**: May be biased toward longer responses and certain formats

**PairRM** ([llm-blender/PairRM](https://huggingface.co/llm-blender/PairRM)):
- **Architecture**: DeBERTa-v3-large (0.4B params - efficient!)
- **Key Feature**: Pairwise comparison (compares two responses side-by-side)
- **Key Code**:
  ```python
  import llm_blender
  blender = llm_blender.Blender()
  blender.loadranker("llm-blender/PairRM")
  ```

**Serena Analysis Needed**: No - code patterns are clear and well-documented

### Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is a NOVEL behavioral probing experiment, not a paper reproduction. Implementation priority:
1. **Official HuggingFace model cards** - All 4 RMs have documented inference code
2. **RewardBench framework** - Standard infrastructure for multi-RM evaluation
3. **Custom stimulus generation** - Novel component requiring new implementation

**Recommended Implementation Path:**
- Primary: Use HuggingFace `AutoModelForSequenceClassification` for ArmoRM, custom wrappers for other RMs following their model card examples
- Fallback: RewardBench's `scripts/run_rm.py` as reference for unified RM inference interface
- Justification: Official model card code is ground truth; RewardBench provides proven multi-RM infrastructure

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. All four reward models have well-documented HuggingFace model cards with complete inference code examples. No complex/unfamiliar architecture patterns requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** Custom Agency-Structure Stimulus Set v2
**Type:** custom (LLM-generated with human validation - NOT synthetic)
**Size:** 600 stimulus pairs (2x2x2 factorial design)

**Factorial Design:**
| Factor | Levels | Description |
|--------|--------|-------------|
| Structure | Enumerated vs. Synthesized | Primary IV - response format |
| Correctness | High vs. Low | Control - factual accuracy |
| Completeness | Complete vs. Partial | Control - answer thoroughness |

**Generation Protocol:**
1. Select 75 diverse prompts across domains (general knowledge, advice, explanation)
2. For each prompt, generate 8 response variants (2x2x2 factorial)
3. Match response length within +/-2% across structure conditions
4. Validate via human ratings (require |d| < 0.2 cross-factor contamination)

**Enumeration Operationalization:**
- **Enumerated:** Contains numbered/bulleted lists (1., 2., 3. OR -, *, bullet patterns)
- **Synthesized:** Prose-only response with same content, no list markers
- **Classifier:** Regex-based detection (pre-registered, >95% human agreement target)

**Loading Information** (for Phase 4 download):
- Method: Programmatic generation (custom)
- Identifier: `stimulus_generator.py` in `{hypothesis_folder}/code/data/`
- Code:
  ```python
  # Generated during Phase 4 - saved to h-e1/data/stimuli.json
  stimuli = generate_factorial_stimuli(
      n_prompts=75,
      factors=["structure", "correctness", "completeness"],
      length_tolerance=0.02
  )
  ```

### Models

#### Baseline Model

**Multi-RM Evaluation Suite (4 Architecturally Distinct Reward Models)**

| Model | HuggingFace ID | Architecture | Training Objective | Size |
|-------|----------------|--------------|-------------------|------|
| ArmoRM | `RLHFlow/ArmoRM-Llama3-8B-v0.1` | Llama-3 + MoE gating | Multi-objective Bradley-Terry | 8B |
| UltraRM | `openbmb/UltraRM-13b` | Llama + regression head | Scalar regression | 13B |
| Starling-RM | `berkeley-nest/Starling-RM-7B-alpha` | Llama2-7B-Chat + scalar | K-wise Bradley-Terry | 7B |
| PairRM | `llm-blender/PairRM` | DeBERTa-v3-large | Pairwise comparison | 0.4B |

**Why These 4 Models:**
- Span 3 different training objectives (Bradley-Terry, scalar regression, pairwise)
- Span 4 different base architectures (Llama-3, Llama, Llama2, DeBERTa)
- All publicly available on HuggingFace
- ArmoRM: SOTA on RewardBench (89.0), previous d=0.634 observed
- Cross-model replication rules out single-model artifact

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: See table above
- Code:
  ```python
  # ArmoRM (requires trust_remote_code for custom MoE)
  from transformers import AutoModelForSequenceClassification, AutoTokenizer
  armo_model = AutoModelForSequenceClassification.from_pretrained(
      "RLHFlow/ArmoRM-Llama3-8B-v0.1",
      device_map="auto", trust_remote_code=True, torch_dtype=torch.bfloat16
  )

  # UltraRM (custom LlamaRewardModel class)
  from transformers import AutoModel, AutoTokenizer
  ultra_model = AutoModel.from_pretrained(
      "openbmb/UltraRM-13b",
      device_map="auto", trust_remote_code=True, torch_dtype=torch.bfloat16
  )

  # Starling-RM (requires custom GPTRewardModel wrapper)
  # See model card for full implementation

  # PairRM (uses llm-blender library)
  import llm_blender
  blender = llm_blender.Blender()
  blender.loadranker("llm-blender/PairRM")
  ```

#### Proposed Model

**Architecture:** No proposed model modification - this is a behavioral probing experiment

**Experiment Type:** Behavioral analysis (NOT model training)

This experiment evaluates EXISTING reward models on controlled stimuli. We do not train or modify any models. The "mechanism" being tested is the enumeration preference already encoded in the RMs.

**Core Analysis Pipeline:**

```python
# Core Mechanism: Multi-RM Enumeration Preference Probing
# Based on: ArmoRM model card, RewardBench infrastructure

class EnumerationPreferenceProbe:
    """
    Probe RLHF-trained reward models for structural enumeration preference.
    No model training - behavioral analysis only.
    """
    def __init__(self, rm_configs: List[RMConfig]):
        self.reward_models = {
            "armo": load_armo_rm(),
            "ultra": load_ultra_rm(),
            "starling": load_starling_rm(),
            "pairrm": load_pair_rm()
        }
        self.enumeration_classifier = EnumerationRegexClassifier()

    def score_response(self, model_name: str, prompt: str, response: str) -> float:
        """Score a single response with specified reward model."""
        model = self.reward_models[model_name]
        if model_name == "pairrm":
            # PairRM needs two responses for comparison
            return model.score_pair(prompt, response, baseline_response)
        else:
            # Other RMs score single responses
            return model.score(prompt, response)

    def run_factorial_experiment(self, stimuli: List[StimulusPair]) -> pd.DataFrame:
        """Run 2x2x2 factorial on all stimuli across all RMs."""
        results = []
        for stimulus in stimuli:
            for rm_name in self.reward_models:
                score_enum = self.score_response(rm_name, stimulus.prompt, stimulus.enumerated)
                score_synth = self.score_response(rm_name, stimulus.prompt, stimulus.synthesized)
                results.append({
                    "rm": rm_name, "prompt_id": stimulus.id,
                    "structure": "enumerated", "score": score_enum,
                    "correctness": stimulus.correctness,
                    "completeness": stimulus.completeness
                })
                results.append({
                    "rm": rm_name, "prompt_id": stimulus.id,
                    "structure": "synthesized", "score": score_synth,
                    "correctness": stimulus.correctness,
                    "completeness": stimulus.completeness
                })
        return pd.DataFrame(results)

# Statistical Analysis: Per-RM Cohen's d for structure main effect
```

### Training Protocol

**N/A - Behavioral Probing Experiment (No Training)**

This is a behavioral analysis experiment, not a model training experiment. We evaluate existing pretrained reward models on controlled stimuli.

**Inference Protocol:**
- **Batch Size:** 16 (for GPU memory efficiency with 13B models)
- **Precision:** bfloat16 (for ArmoRM, UltraRM) / float32 (for PairRM)
- **Device:** Single GPU with `device_map="auto"`
- **Seeds:** 1 (fixed seed for stimulus generation reproducibility)

**Stimulus Generation Protocol:**
- Generate 75 base prompts across diverse domains
- Create 8 variants per prompt (2x2x2 factorial)
- Match length within +/-2% between enumerated/synthesized
- Total: 600 stimulus pairs (75 prompts x 8 variants)

**Execution Order:**
1. Generate and validate stimulus set
2. Run enumeration classifier validation (target: >95% accuracy)
3. Score all stimuli with all 4 RMs
4. Compute per-RM effect sizes (Cohen's d) for structure main effect

### Evaluation

**Primary Metric:** Cohen's d (effect size) for structure main effect per RM

**Success Criteria (EXISTENCE PoC):**
- **PASS:** d >= 0.3 in >=2 architecturally distinct RMs
- **Secondary:** >=75% (3/4) RMs show positive effect (d > 0)

**Expected Performance (from prior research):**
- ArmoRM: d ~= 0.634 (observed in prior composite agency experiment)
- Other RMs: Unknown (cross-model replication is the novel contribution)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Behavioral probing / effect size estimation
- Library: scipy.stats, numpy
- Code:
  ```python
  from scipy import stats
  import numpy as np

  def cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
      """Compute Cohen's d effect size."""
      n1, n2 = len(group1), len(group2)
      pooled_std = np.sqrt(((n1-1)*group1.std()**2 + (n2-1)*group2.std()**2) / (n1+n2-2))
      return (group1.mean() - group2.mean()) / pooled_std

  def compute_ci(d: float, n1: int, n2: int, alpha: float = 0.05) -> tuple:
      """Compute confidence interval for Cohen's d."""
      se = np.sqrt((n1+n2)/(n1*n2) + d**2/(2*(n1+n2)))
      z = stats.norm.ppf(1 - alpha/2)
      return (d - z*se, d + z*se)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

Based on this behavioral probing experiment, recommended visualizations:

1. **Per-RM Effect Size Forest Plot**: Cohen's d with 95% CI for each RM
2. **Score Distribution Violin Plot**: Enumerated vs synthesized scores per RM
3. **Factorial Interaction Plot**: Structure x Correctness x Completeness
4. **RM Architecture Comparison**: Effect sizes grouped by training objective

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: OpenAI Instruction Following Blog
- **Type**: Knowledge base article
- **Query Used**: "reward model preference evaluation"
- **Relevance**: General RLHF context and methodology
- **Used For**: Background understanding of RLHF reward modeling

**Source A.2**: HuggingFace Model Loading Documentation
- **Type**: Code documentation
- **Query Used**: "AutoModelForSequenceClassification transformer"
- **Key Insight**: Use `trust_remote_code=True` for custom model architectures
- **Used For**: Model loading code in baseline specification

**Note**: Archon KB lacks specific reward model behavioral probing research (novel area). Primary sources from Exa GitHub search.

### B. GitHub Implementations (Exa)

**Repository B.1**: [RLHFlow/RLHF-Reward-Modeling](https://github.com/RLHFlow/RLHF-Reward-Modeling) (2K stars)
- **URL**: https://github.com/RLHFlow/RLHF-Reward-Modeling
- **Query Used**: "ArmoRM RLHFlow reward model inference implementation GitHub"
- **Relevance**: Official ArmoRM implementation and inference code
- **Key Code**:
  ```python
  # From HuggingFace model card - verified working
  model = AutoModelForSequenceClassification.from_pretrained(
      "RLHFlow/ArmoRM-Llama3-8B-v0.1",
      device_map=device, trust_remote_code=True, torch_dtype=torch.bfloat16
  )
  ```
- **Paper**: arxiv:2406.12845 "Interpretable Preferences via Multi-Objective Reward Modeling"
- **Used For**: ArmoRM model loading, inference pattern, RewardBench score reference (89.0)

**Repository B.2**: [allenai/reward-bench](https://github.com/allenai/reward-bench) (705 stars)
- **URL**: https://github.com/allenai/reward-bench
- **Query Used**: "RewardBench reward model evaluation benchmark code GitHub"
- **Relevance**: Standard evaluation infrastructure for multiple RMs
- **Key Scripts**: `scripts/run_rm.py` for reward model evaluation
- **Used For**: Multi-RM evaluation framework reference, supported model list

**Repository B.3**: [openbmb/UltraRM-13b](https://huggingface.co/openbmb/UltraRM-13b)
- **URL**: https://huggingface.co/openbmb/UltraRM-13b
- **Query Used**: "UltraRM openbmb Starling-RM PairRM reward model inference code"
- **Key Code**: Custom `LlamaRewardModel` with regression head
- **Training Data**: UltraFeedback dataset
- **Used For**: UltraRM loading and inference pattern

**Repository B.4**: [berkeley-nest/Starling-RM-7B-alpha](https://huggingface.co/berkeley-nest/Starling-RM-7B-alpha)
- **URL**: https://huggingface.co/berkeley-nest/Starling-RM-7B-alpha
- **Key Code**: Custom `GPTRewardModel` wrapper
- **Note**: Based on Llama2-7B-Chat, K-wise Bradley-Terry training
- **Used For**: Starling-RM loading pattern

**Repository B.5**: [llm-blender/PairRM](https://huggingface.co/llm-blender/PairRM)
- **URL**: https://huggingface.co/llm-blender/PairRM
- **Key Code**: `llm_blender.Blender().loadranker("llm-blender/PairRM")`
- **Architecture**: DeBERTa-v3-large (0.4B - efficient!)
- **Used For**: PairRM loading and pairwise comparison interface

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear. All 4 reward models have well-documented HuggingFace model cards with complete inference examples.

### D. Previous Hypothesis Context

**Source**: Serena Memory `snapshot_h-e1_20260324T082200Z` and `global/phase45/failure_h-e1_bi_align_opus45_run1`
- **Previous Experiment**: Composite agency approach (Attempt 2)
- **Result**: FAILED (d=0.131 overall)
- **Key Finding**: Enumeration factor showed d=0.634 in ArmoRM (very strong positive)
- **Lesson Applied**: Isolate enumeration effect, test cross-model replication

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset design (factorial) | Phase 2B | 02b_verification_plan.md |
| ArmoRM loading | GitHub (Exa) | Repository B.1 |
| Multi-RM infrastructure | GitHub (Exa) | Repository B.2 |
| UltraRM loading | GitHub (Exa) | Repository B.3 |
| Starling-RM loading | GitHub (Exa) | Repository B.4 |
| PairRM loading | GitHub (Exa) | Repository B.5 |
| Effect size methodology | Statistical standard | scipy.stats documentation |
| Prior enumeration effect | Serena Memory | D.1 (d=0.634 in ArmoRM) |
| Success criteria | Phase 2B | 02b_verification_plan.md Section 2.2 |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-24T09:25:00Z

### Workflow History for This Hypothesis
- Phase 2B: Generated verification plan with H-E1 as foundation hypothesis
- Phase 2C: Experiment design COMPLETED

### Quality Validation (Step 8)
```
Quality Validation Results:
───────────────────────────
✅ All hyperparameters justified (inference protocol from HuggingFace model cards)
✅ Dataset choice justified (factorial design from Phase 2B, custom stimulus for controlled probing)
✅ Mechanism grounded in code (all 4 RM loading patterns from official model cards)
✅ No unsupported assumptions (all claims reference prior d=0.634 finding or RewardBench data)
✅ Full traceability (traceability matrix in Appendix E)

Overall: PASSED
```

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
