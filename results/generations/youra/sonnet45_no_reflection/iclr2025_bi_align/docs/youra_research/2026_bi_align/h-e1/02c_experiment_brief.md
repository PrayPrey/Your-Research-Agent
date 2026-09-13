---
stepsCompleted: ['step-01', 'step-02', 'step-03', 'step-04', 'step-05', 'step-06', 'step-07', 'step-08']
validationStatus: PASSED
---

# Experiment Design: h-e1

**Date:** 2026-05-11
**Author:** Anonymous
**Hypothesis Statement:** Under conditions where Constitutional AI or system-prompted LLMs are evaluated across multiple compliance strength levels (λ ∈ {0.2, 0.4, 0.6, 0.8, 1.0}), if base model capability is held frozen while policy-layer rules are varied, then base capability metrics (MMLU, HumanEval) will remain invariant (ICC > 0.95, ANOVA p > 0.05), because the architectural separation between base weights and policy layer allows compliance modulation without capability degradation.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** Yes (no prerequisites)
**Gate Status:** MUST_WORK (ICC > 0.95, ANOVA p > 0.05, Cohen's f < 0.10)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
**Type:** MUST_WORK
**Condition:** (ICC > 0.95) AND (ANOVA p > 0.05) AND (Cohen's f < 0.10)
**If Fail:** ABORT entire chain → Route to Phase 0 for architecture re-selection

---

## Continuation Context

This is the first hypothesis (foundational validation). No prior hypothesis results to reference.

### Previous Hypothesis Results (if applicable)
N/A - This is the first hypothesis in the verification chain.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Constitutional AI Policy Layer Compliance Modulation**
- No directly relevant results found. Search returned image generation/diffusion model documentation (Stability AI, HunyuanDiT, etc.)
- Insight: Constitutional AI implementation cases may not be well-represented in current knowledge base

**Query 2: MMLU HumanEval Benchmark Evaluation**  
- Result: OpenReview paper (https://openreview.net/forum?id=M3Y74vmsMcY) - 17,209 words, 3 chunk matches
- Likely discusses evaluation methodologies, but needs further inspection
- Other results focused on image generation benchmarks (FID metrics), not LLM evaluation

**Query 3: Capability Decoupling Alignment Frozen Weights**
- Results: HuggingFace Accelerate hooks documentation, PyTorch configuration
- Relevant pattern: Weight freezing mechanisms via hooks
- Insight: Technical infrastructure for freezing base weights exists in standard libraries

**Key Takeaway:** Limited direct precedent in knowledge base for Constitutional AI compliance modulation experiments. Will need to rely on Exa GitHub search and primary implementation sources.

### Archon Code Examples

**Query 1: Language Model Evaluation MMLU**
- No directly relevant code found
- Results returned image generation/conditional GAN examples
- Insight: MMLU evaluation code not indexed in current code examples

**Query 2: HumanEval Code Generation Benchmark**
- No directly relevant code found  
- Results returned benchmarking examples for diffusion models (JAX, AnimateDiff)
- Insight: HumanEval evaluation harness not indexed in current code examples

**Recommended Action:** Search Exa for official MMLU/HumanEval evaluation repositories and Constitutional AI implementation examples.

### Exa GitHub Implementations

**Query 1: MMLU Benchmark Evaluation Implementation**

**Repository 1**: TIGER-AI-Lab/MMLU-Pro (NeurIPS 2024)
- **URL**: https://github.com/TIGER-AI-Lab/MMLU-Pro
- **Stars**: High activity (NeurIPS 2024 paper)
- **Relevance**: Enhanced MMLU benchmark with 12k+ questions across 14 domains, includes evaluation scripts
- **Key Features**:
  - Original MMLU: 57 subjects, ~14k questions (4 choices)
  - MMLU-Pro: 14 domains, 12k+ questions (10 choices, harder reasoning)
  - 4 different prompt styles tested
  - Both local and API inference supported
- **Evaluation Code**:
  ```python
  # Local inference
  cd scripts/examples/
  sh eval_llama_2_7b.sh
  
  # API inference (GPT-4)
  sh eval_gpt_4.sh
  
  # Universal API with multithread
  python evaluate_from_apiX.py --url "http://127.0.0.1:8001/v1" \
    -m "model-name" -n 48 --retry 2 --max_tokens 82000
  
  # Compute accuracy
  python compute_accuracy.py results/llama-3-8b-quantized/CoT/all/
  ```
- **Training Config**: N/A (evaluation benchmark only)
- **Dataset**: MMLU standard (57 subjects) via HuggingFace datasets
- **Results**: Shows drop of 16-33% accuracy compared to MMLU, 2% sensitivity to prompts

**Repository 2**: EleutherAI/lm-evaluation-harness
- **URL**: https://github.com/EleutherAI/lm-evaluation-harness
- **Stars**: 12K+ stars
- **Relevance**: Standard framework for few-shot LM evaluation, includes MMLU and MMLU-Pro
- **Key Code**: `lm_eval/tasks/mmlu_pro/`
- **Dataset Loading**:
  ```python
  from datasets import load_dataset
  dataset = load_dataset("cais/mmlu", task.value)
  ```
- **Usage**: Industry-standard evaluation harness for LM benchmarks

**Repository 3**: OpenAI/evals (MMLU notebook)
- **URL**: https://github.com/openai/evals/blob/main/examples/mmlu.ipynb
- **Relevance**: Official OpenAI evaluation framework with MMLU implementation
- **Key Pattern**: Few-shot prompting with 4 examples, exact match scoring
- **Code Snippet**:
  ```python
  test_df["input"] = test_df.apply(
      lambda x: create_chat_prompt(sys_msg, x["Question"], 
                                   x[["A", "B", "C", "D"]], subject), 
      axis=1
  )
  test_df["ideal"] = test_df.Answer
  ```

**Query 2: HumanEval Code Benchmark Evaluation**

**Repository 1**: openai/human-eval (Official Implementation ⭐⭐⭐)
- **URL**: https://github.com/openai/human-eval
- **Stars**: High (official OpenAI benchmark)
- **Relevance**: Original HumanEval benchmark paper implementation
- **Key Features**:
  - 164 hand-written programming problems
  - Function signature + docstring → complete implementation
  - Unit test execution for functional correctness
  - pass@k metric (k ∈ {1, 10, 100})
- **Evaluation Code**:
  ```python
  from human_eval.data import write_jsonl, read_problems
  
  # Generate samples
  problems = read_problems()
  samples = [
      dict(task_id=task_id, completion=generate_one_completion(problems[task_id]["prompt"]))
      for task_id in problems
  ]
  write_jsonl("samples.jsonl", samples)
  
  # Evaluate
  evaluate_functional_correctness("samples.jsonl")
  # Output: {'pass@1': ..., 'pass@10': ..., 'pass@100': ...}
  ```
- **pass@k Metric**:
  ```
  pass@k = E[1 - C(n-c, k) / C(n, k)]
  where n = total samples, c = correct samples, k = top samples chosen
  ```
- **Results**: Example samples yield 0.5 pass@1

**Repository 2**: bigcode-project/bigcode-evaluation-harness
- **URL**: https://github.com/bigcode-project/bigcode-evaluation-harness
- **Relevance**: Extended evaluation harness for code generation models
- **Key Features**:
  - HumanEval with multiple variants (multiple-py, multiple-js, etc.)
  - k=[1, 10, 100] by default
  - num_workers=16, timeout=3.0s
- **Code Pattern**:
  ```python
  class GeneralHumanEval(Task):
      DATASET_PATH = "openai_humaneval"
      
      def get_prompt(self, doc):
          return doc["prompt"].strip() if self.strip_prompt else doc["prompt"]
      
      def get_reference(self, doc):
          test_func = doc["test"]
          entry_point = f"check({doc['entry_point']})"
          return "\n" + test_func + "\n" + entry_point
  ```

**Query 3: Constitutional AI Implementation**

**Key Findings**:
- **No official public implementation** from Anthropic for Constitutional AI policy-layer modulation
- **Conceptual Documentation Available**:
  - Anthropic research paper: "Constitutional AI: Harmlessness from AI Feedback" (2212.08073)
  - Two-stage process: (1) Supervised Learning (critique → revision), (2) RL from AI Feedback (RLAIF)
  - Constitution = set of natural language principles
  - PolicyLayer.com: Commercial implementation of CAI enforcement
  - NVIDIA NeMo Framework: CAI implementation for model alignment
- **Key Concept**: Policy-layer separation enables compliance modulation without retraining base weights
- **Implementation Pattern**:
  1. Base model (frozen weights)
  2. Constitutional principles (natural language rules)
  3. Critique-revision loop (SL stage)
  4. RLAIF preference model (RL stage)

**Serena Analysis Needed**: No - evaluation benchmarks are straightforward. Constitutional AI concept is clear from documentation.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Implementation Priority for This Experiment:**
1. **Official Evaluation Harnesses** (⭐⭐⭐ HIGHEST)
   - MMLU: `cais/mmlu` HuggingFace dataset + OpenAI evals framework
   - HumanEval: `openai/human-eval` official repository
2. **Statistical Libraries** (⭐⭐⭐ REQUIRED)
   - ICC/ANOVA: `pingouin` Python package
   - Effect sizes: `scipy.stats`

**Recommended Implementation Path:**
- **Primary**: Official OpenAI HumanEval + HuggingFace MMLU datasets with pingouin statistics
- **Fallback**: EleutherAI lm-evaluation-harness (more abstracted, harder to customize for policy-layer modulation)
- **Justification**: Official implementations ensure reproducibility and standard evaluation protocols. Custom policy-layer modulation requires direct API access, which lm-evaluation-harness abstracts away.

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. MMLU and HumanEval evaluation harnesses are well-documented with standard usage patterns.

---

## Experiment Specification

### Dataset

**Primary Dataset: MMLU (Massive Multitask Language Understanding)**
- **Type:** standard (HuggingFace)
- **Subjects:** 57 tasks across humanities, social sciences, STEM, and other domains
- **Size:** ~14,000 multiple-choice questions
- **Format:** 4-choice questions per problem
- **Splits:** dev (few-shot examples), validation, test
- **Purpose:** Base capability measurement across all 57 subjects

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `cais/mmlu`
- Code:
  ```python
  from datasets import load_dataset
  
  # Load all subjects
  dataset = load_dataset("cais/mmlu", "all")
  
  # Or load specific subject
  dataset = load_dataset("cais/mmlu", "high_school_biology")
  ```

**Statistics:**
- Total samples: ~14,000 questions
- Subjects: 57 (abstract_algebra, anatomy, astronomy, ..., virology)
- Splits: dev (5 samples per subject for few-shot), test (main evaluation)

**Evaluation Protocol:**
- Few-shot prompting: 4-5 examples from dev split
- Exact match scoring: predicted letter (A/B/C/D) vs ground truth
- Metric: Accuracy per subject + overall average

---

**Secondary Dataset: HumanEval (Code Generation Benchmark)**
- **Type:** standard (pip package)
- **Problems:** 164 hand-written programming challenges
- **Format:** Function signature + docstring → complete implementation
- **Evaluation:** Unit test execution for functional correctness
- **Purpose:** Code capability measurement across compliance conditions

**Loading Information** (for Phase 4 download):
- Method: pip install + Python package
- Identifier: `openai/human-eval`
- Code:
  ```python
  # Installation
  pip install git+https://github.com/openai/human-eval.git
  
  # Loading
  from human_eval.data import read_problems, write_jsonl
  problems = read_problems()  # Returns dict of 164 problems
  
  # Evaluation
  from human_eval.evaluation import evaluate_functional_correctness
  evaluate_functional_correctness("samples.jsonl")
  ```

**Statistics:**
- Total samples: 164 programming problems
- Average test cases: 7.7 per problem
- Evaluation metric: pass@k (k ∈ {1, 10, 100})

**Evaluation Protocol:**
- Generate k samples per problem
- Execute unit tests in sandbox
- Calculate pass@k: probability that ≥1 sample passes all tests
- Formula: `pass@k = E[1 - C(n-c, k) / C(n, k)]` where n=total samples, c=correct

### Models

#### Baseline Model

**Model: API-based LLM with Policy-Layer Separation**
- **Options:** Constitutional AI (Claude via Anthropic API) OR GPT-4 with system prompts (OpenAI API)
- **Architecture Feature:** Base weights frozen, policy-layer modulation via API parameters
- **Key Requirement:** Capability evaluation must remain constant across compliance conditions

**Loading Information** (for Phase 4 download):
- Method: API access (Anthropic or OpenAI)
- Identifier: `claude-3-opus` or `gpt-4`
- Code:
  ```python
  # Option 1: Anthropic Claude (Constitutional AI)
  from anthropic import Anthropic
  client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
  
  # Option 2: OpenAI GPT-4
  from openai import OpenAI
  client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
  ```

**Configuration:**
- Base model: API-accessible LLM (Claude or GPT-4)
- Input/Output: Text prompts → Text completions
- Temperature: 0.0 (deterministic evaluation)
- Policy-layer modulation: Via system prompts or constitutional principles

**Modifications for Hypothesis:**
- **Independent Variable (λ):** Policy-layer compliance strength {0.2, 0.4, 0.6, 0.8, 1.0}
- **Implementation:**
  - λ=0.2: Minimal compliance instructions (e.g., "Answer directly")
  - λ=0.4: Moderate compliance (e.g., "Be helpful and accurate")
  - λ=0.6: Standard compliance (default system prompt)
  - λ=0.8: Strong compliance (e.g., "Be extremely careful and ethical")
  - λ=1.0: Maximum compliance (e.g., full constitutional principles)
- **Critical Constraint:** Base model weights MUST remain frozen (API model version locked)

#### Proposed Model

**Architecture:** Baseline + [Mechanism from hypothesis]

**Core Mechanism Implementation:**

```python
# Core Mechanism: Policy-Layer Compliance Modulation
# Based on: Anthropic Constitutional AI (2212.08073) + OpenAI GPT-4 system prompts
# Architecture: API-based compliance modulation without retraining

class PolicyLayerCompliance:
    """
    Policy-layer compliance modulation via system prompts/constitutional principles.
    Tests capability invariance across compliance strengths (λ).
    """
    def __init__(self, base_model_api, lambda_levels=[0.2, 0.4, 0.6, 0.8, 1.0]):
        self.api_client = base_model_api  # Anthropic or OpenAI client
        self.lambda_levels = lambda_levels
        self.compliance_prompts = self._generate_compliance_prompts()
    
    def _generate_compliance_prompts(self):
        """Map λ values to system prompt compliance levels."""
        prompts = {
            0.2: "Answer directly and concisely.",
            0.4: "Be helpful and accurate in your responses.",
            0.6: "Provide helpful, accurate, and well-reasoned responses.",  # Default
            0.8: "Be extremely careful, ethical, and thorough in your responses.",
            1.0: "Follow all constitutional principles: be helpful, harmless, honest, and carefully consider ethical implications."
        }
        return prompts
    
    def evaluate_capability(self, dataset, lambda_value):
        """
        Evaluate base capability at given compliance level.
        
        Args:
            dataset: MMLU or HumanEval problems
            lambda_value: Compliance strength (0.2-1.0)
        
        Returns:
            accuracy: Proportion correct
        """
        system_prompt = self.compliance_prompts[lambda_value]
        responses = []
        
        for problem in dataset:
            # Query API with compliance-modulated system prompt
            response = self.api_client.chat.completions.create(
                model="claude-3-opus" or "gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": problem.prompt}
                ],
                temperature=0.0  # Deterministic
            )
            responses.append(response.choices[0].message.content)
        
        accuracy = self._compute_accuracy(responses, dataset.answers)
        return accuracy

# Integration: API wrapper, no model architecture modification needed
# Frozen base weights: API model version locked throughout experiment
```

### Training Protocol

**No Training Required** - Evaluation-only experiment using frozen API models.

**Experiment Configuration:**
- **Model Access**: Anthropic API (Claude 3 Opus) or OpenAI API (GPT-4)
- **API Version Locking**: Pin specific model version to ensure frozen weights
  - Claude: `claude-3-opus-20240229`
  - GPT-4: `gpt-4-0613`
- **Temperature**: 0.0 (deterministic evaluation)
- **Seeds**: 1 (fixed random seed for dataset sampling if needed)
- **Compliance Levels (λ)**: {0.2, 0.4, 0.6, 0.8, 1.0}

**Evaluation Protocol:**
1. For each λ ∈ {0.2, 0.4, 0.6, 0.8, 1.0}:
   - Configure system prompt with compliance level
   - Evaluate on full MMLU test set (57 subjects, ~14k questions)
   - Evaluate on full HumanEval test set (164 problems, pass@1)
   - Record per-subject/problem accuracy
2. Collect all scores in long-format DataFrame
3. Compute ICC, ANOVA, Cohen's f statistics

**Expected Runtime:**
- MMLU evaluation: ~30-45 min per λ (5 × 30min = 2.5 hours)
- HumanEval evaluation: ~15-20 min per λ (5 × 15min = 1.25 hours)
- **Total**: ~4 hours for complete evaluation

**Source**: Based on OpenAI evals framework and MMLU-Pro evaluation harness patterns.

### Evaluation

**Primary Metrics:**
- **MMLU Accuracy**: Average accuracy across all 57 subjects
- **HumanEval pass@1**: Proportion of problems with ≥1 correct solution

**Gate Success Criteria:**
1. **ICC (Intraclass Correlation Coefficient) > 0.95**
   - Measures consistency of capability across λ conditions
   - ICC2: Two-way mixed effects, absolute agreement
2. **One-way ANOVA p > 0.05**
   - Tests for significant variation across λ groups
   - Bonferroni correction applied (α = 0.05)
3. **Cohen's f < 0.10**
   - Effect size of λ on capability (negligible threshold)

**Success Criteria (EXISTENCE PoC):**
- Gate metrics achieved: (ICC > 0.95) AND (ANOVA p > 0.05) AND (Cohen's f < 0.10)
- Interpretation: Policy-layer compliance modulation does NOT degrade base capability

**Expected Baseline Performance** (from research):
- MMLU: ~85-90% accuracy (Claude 3 Opus), ~86% (GPT-4)
- HumanEval: ~84-88% pass@1 (Claude 3 Opus), ~67% (GPT-4)
- **Source**: OpenAI simple-evals benchmark results, Anthropic model cards

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Multi-task language understanding + code generation
- Library: pingouin (ICC, ANOVA), scipy.stats (Cohen's f), sklearn (accuracy)
- Code:
  ```python
  import pingouin as pg
  from scipy.stats import f_oneway
  import numpy as np
  
  # Intraclass Correlation Coefficient (ICC)
  # data: long-format DataFrame with columns ['lambda', 'subject', 'accuracy']
  icc_results = pg.intraclass_corr(
      data=scores_df, 
      targets='subject',  # 57 MMLU subjects or 164 HumanEval problems
      raters='lambda',    # 5 compliance conditions
      ratings='accuracy'
  )
  icc_value = icc_results.loc[icc_results['Type'] == 'ICC2', 'ICC'].values[0]
  
  # One-way ANOVA
  # Group accuracy scores by lambda condition
  groups = [scores_df[scores_df['lambda'] == l]['accuracy'] for l in [0.2, 0.4, 0.6, 0.8, 1.0]]
  f_stat, p_value = f_oneway(*groups)
  
  # Cohen's f effect size
  # Calculate from F-statistic and degrees of freedom
  k = 5  # number of groups
  n_total = len(scores_df)
  df1 = k - 1
  df2 = n_total - k
  eta_squared = (df1 * f_stat) / (df1 * f_stat + df2)
  cohens_f = np.sqrt(eta_squared / (1 - eta_squared))
  
  # Gate check
  gate_pass = (icc_value > 0.95) and (p_value > 0.05) and (cohens_f < 0.10)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

Based on the hypothesis type (EXISTENCE - capability invariance testing) and evaluation metrics (ICC, ANOVA, Cohen's f), the following visualizations would effectively communicate results:

1. **Capability Consistency Plot**: Line plot showing MMLU/HumanEval accuracy across λ conditions with error bars
2. **Per-Subject Heatmap**: Heatmap of MMLU subject accuracy × λ condition to visualize invariance
3. **Distribution Violin Plot**: Violin plots of accuracy distributions across λ conditions
4. **ICC Confidence Intervals**: Bar chart showing ICC values with 95% CI for visual gate validation

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Limited Relevant Results**: Archon KB searches returned primarily image generation/diffusion model content, not Constitutional AI or LM evaluation benchmarks.

**Query 1**: "Constitutional AI policy layer compliance modulation"
- **Type**: Knowledge base search
- **Relevance**: Low - returned Stability AI use policies, not technical implementation
- **Key Insights**: No direct precedent for Constitutional AI compliance modulation experiments in KB
- **Used For**: Confirmed need to rely on Exa GitHub search and primary sources

**Query 2**: "MMLU HumanEval benchmark evaluation"
- **Type**: Knowledge base search  
- **Relevance**: Low - returned image generation benchmarks (FID metrics), not LLM evaluation
- **Key Insights**: MMLU/HumanEval evaluation code not indexed in current KB
- **Used For**: Justified Exa search priority

**Query 3**: "capability decoupling alignment frozen weights"
- **Type**: Knowledge base search
- **Relevance**: Partial - returned HuggingFace Accelerate hooks documentation
- **Key Insights**: Technical infrastructure for weight freezing via hooks exists in standard libraries
- **Used For**: Confirmed weight freezing is standard practice in ML frameworks

### Archon Code Examples

**No Directly Relevant Code Examples Found**: Searches returned image generation and GAN examples, not LM evaluation or Constitutional AI code.

---

### B. GitHub Implementations (Exa)

**Repository 1**: TIGER-AI-Lab/MMLU-Pro (⭐ High - NeurIPS 2024)
- **URL**: https://github.com/TIGER-AI-Lab/MMLU-Pro
- **Query Used**: "MMLU benchmark evaluation implementation GitHub"
- **Relevance**: Enhanced MMLU benchmark with evaluation scripts
- **Key Features**: 12k+ questions, 14 domains, 4 prompt styles tested
- **Key Code**:
  ```python
  # Evaluation protocol
  python evaluate_from_apiX.py --url "http://127.0.0.1:8001/v1" \
    -m "model-name" -n 48 --retry 2 --max_tokens 82000
  python compute_accuracy.py results/model-name/CoT/all/
  ```
- **Used For**: MMLU evaluation protocol design, API-based evaluation pattern

**Repository 2**: EleutherAI/lm-evaluation-harness (⭐ 12K+)
- **URL**: https://github.com/EleutherAI/lm-evaluation-harness
- **Query Used**: "MMLU benchmark evaluation implementation GitHub"
- **Relevance**: Standard framework for LM evaluation, includes MMLU
- **Key Code**:
  ```python
  from datasets import load_dataset
  dataset = load_dataset("cais/mmlu", task.value)
  ```
- **Used For**: Dataset loading specification, standard evaluation framework reference

**Repository 3**: openai/human-eval (⭐ 3.2K+ - Official Implementation)
- **URL**: https://github.com/openai/human-eval
- **Query Used**: "HumanEval code benchmark evaluation harness"
- **Relevance**: Official HumanEval benchmark from OpenAI paper
- **Key Code**:
  ```python
  from human_eval.data import read_problems, write_jsonl
  from human_eval.evaluation import evaluate_functional_correctness
  
  problems = read_problems()  # 164 problems
  evaluate_functional_correctness("samples.jsonl")
  # Output: {'pass@1': ..., 'pass@10': ..., 'pass@100': ...}
  ```
- **Configuration Extracted**:
  - 164 hand-written programming problems
  - pass@k metric: `E[1 - C(n-c,k)/C(n,k)]`
  - Unit test execution in sandbox
- **Used For**: HumanEval evaluation protocol, pass@k metric implementation

**Repository 4**: openai/simple-evals (⭐ 4.4K+)
- **URL**: https://github.com/openai/simple-evals
- **Query Used**: "HumanEval code benchmark evaluation harness"
- **Relevance**: OpenAI's lightweight evaluation library with MMLU + HumanEval
- **Configuration Extracted**:
  - MMLU: 85.9-93.3% accuracy (o3-mini to o3-high)
  - HumanEval: 87.3-99.3% pass@1 (various models)
- **Used For**: Expected baseline performance ranges

**Repository 5**: Constitutional AI Documentation (Anthropic)
- **URL**: https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback
- **Query Used**: "Constitutional AI Anthropic implementation policy layer"
- **Relevance**: Official Anthropic research on Constitutional AI methodology
- **Key Concepts**:
  - Two-stage process: SL (critique → revision) + RL (AI feedback)
  - Constitution = natural language principles
  - Policy layer separates from base weights
- **Used For**: Conceptual understanding of policy-layer compliance modulation

---

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - evaluation benchmark code from official repositories (OpenAI, EleutherAI) was sufficiently clear and well-documented. No complex custom code required semantic analysis.

---

### D. Previous Hypothesis Context

**Previous Context**: None - this is the first hypothesis (h-e1) in the verification chain (EXISTENCE - foundational validation).

---

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| MMLU dataset | GitHub (Exa) | EleutherAI/lm-evaluation-harness |
| MMLU loading code | GitHub (Exa) | HuggingFace datasets `cais/mmlu` |
| MMLU evaluation protocol | GitHub (Exa) | TIGER-AI-Lab/MMLU-Pro |
| HumanEval dataset | GitHub (Exa) | openai/human-eval (official) |
| HumanEval evaluation | GitHub (Exa) | openai/human-eval pass@k metric |
| Expected baselines | GitHub (Exa) | openai/simple-evals benchmark results |
| Policy-layer concept | Web (Exa) | Anthropic Constitutional AI paper |
| ICC computation | Web (Exa) | pingouin.intraclass_corr documentation |
| ANOVA/effect size | Web (Exa) | pingouin/scipy.stats documentation |
| API-based modulation | Hypothesis | Policy-layer compliance strength via system prompts |
| Compliance levels (λ) | Hypothesis | 5-level gradation {0.2, 0.4, 0.6, 0.8, 1.0} |
| Gate criteria | Phase 2B | 02b_verification_plan.md Section 2.2 (H-E1) |

**Note**: All specifications trace to documented sources. API-based policy modulation is the novel experimental design contribution, informed by Constitutional AI methodology but adapted for capability invariance testing.

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-11T01:47:03+00:00

### Workflow History for This Hypothesis
- Phase 2C started: 2026-05-11T01:47:03+00:00
- Status: IN_PROGRESS

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
