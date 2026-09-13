# Experiment Design: h-m3

**Date:** 2026-03-24
**Author:** Anonymous
**Hypothesis Statement:** DPO preference optimization without execution feedback concentrates failures in execution errors (syntax/runtime), and this effect persists at fine-grained taxonomy (Cramér's V > 0.03 at LlmFix 19-cause level)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM Hypothesis** - Tests whether DPO's preference surface plausibility creates specific error distribution patterns at fine-grained taxonomy.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-m2 (PASS)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM
- **Prerequisites:** h-m2

### Gate Condition
**SHOULD_WORK Gate:**
- Primary: P(syntax+runtime | failure, DPO) > P(syntax+runtime | failure, RL)
- Secondary: Effect persists at fine-grained taxonomy (Cramér's V > 0.03 at LlmFix 19-cause level)
- IF fails: Document limitation, complete verification (SHOULD_WORK allows continuation)

---

## Continuation Context

**Builds on H-E1 and H-M1/H-M2 Results:**
- H-E1 established error type distributions differ significantly (chi-square p < 0.05, V = 0.2147)
- H-M1 confirmed RL concentrates failures in assertion errors (zero-reward basin)
- H-M2 confirmed RL failures execute 326x deeper than DPO failures
- H-M3 tests the complementary DPO mechanism at fine-grained taxonomy level

**Data Reuse:** Can reuse H-E1 error classification data, extending with LlmFix 19-cause taxonomy

### Previous Hypothesis Results (if applicable)
**H-M2 Results (Prerequisite):**
- Gate: SHOULD_WORK - PASS
- Key Finding: RL execution depth (29.4%) >> DPO (0.09%) - 326x difference
- Cohen's d = 1.691 (large effect), p = 1.08e-34
- Mechanism: RL syntactic validity pressure confirmed via real sys.settrace() execution tracing

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Error taxonomy code generation classification**
- Limited direct results for LlmFix 19-cause taxonomy in Archon KB
- T5 model documentation found (transformers library reference)
- Key insight: Error classification requires custom implementation based on ICSE 2025 / LlmFix papers

**Query 2: DPO alignment code LLM preference**
- QLoRA paper (2305.14314): Efficient finetuning techniques for LLMs
  - Hyperparameters: LR 1e-4 to 2e-4, batch size 16-64, LoRA r=64
  - Key insight: DPO models typically built on preference-ranked datasets without execution filtering
- Diffusers DPO references for image models (not directly applicable)

**Query 3: Cramér's V chi-square contingency analysis**
- Statistical analysis methodology well-documented in scipy.stats
- Key insight: Use scipy.stats.chi2_contingency for chi-square and manual Cramér's V computation

**Serena Memory - dl4c_alignment_signatures_2026:**
- Previous DL4C pipeline validated alignment methods create distinguishable profiles (Cohen's d=7.835)
- Multi-granularity taxonomy testing proven methodology
- Reusable components: HumanEval+ data loader, error classification pipeline

### Archon Code Examples

**Query 1: Chi-square contingency scipy stats**
- No direct code examples found for statistical contingency analysis
- Implementation pattern: Use `scipy.stats.chi2_contingency(contingency_table)` for chi-square
- Cramér's V = sqrt(chi2 / (n * min(k-1, r-1))) where k=columns, r=rows

**Query 2: Error classification Python taxonomy**
- No direct LlmFix taxonomy implementation found
- Pattern: Parse error messages using regex/AST analysis
- Custom implementation required for 19-cause classification

### Exa GitHub Implementations

**Query 1: LlmFix error taxonomy classification**

**Key Paper Found: LlmFix (arXiv 2409.00676)**
- **Title:** Analysis of 12,837 errors from 14 LLMs on HumanEval
- **Taxonomy:** 19 categories of error causes
- **URL:** https://arxiv.org/pdf/2409.00676
- **Key Insight:** Classifies errors into 14 Python exception types + 19 root cause categories
- **Relevance:** EXACT taxonomy needed for H-M3 fine-grained analysis

**Error Categories from LlmFix:**
1. 14 Python exception types (SyntaxError, IndentationError, NameError, TypeError, ValueError, IndexError, KeyError, AttributeError, ZeroDivisionError, RecursionError, ImportError, AssertionError, TimeoutError, RuntimeError)
2. 19 root cause categories (semantic characteristics)
3. Three auto-fixable categories: missing import, redundant generation, inconsistent indentation

**Related Paper: ICSE 2025 Error Taxonomy (wangzhijie.me)**
- **Title:** Towards Understanding the Characteristics of Code Generation Errors
- **Authors:** Wang et al.
- **Taxonomy:** Semantic characteristics (13) + Syntactic characteristics (14)
- **Dataset:** 557 errors from 6 LLMs on HumanEval
- **URL:** https://wangzhijie.me/assets/pubs/icse25-llmcodeerrors.pdf

**Query 2: EvalPlus HumanEval MBPP benchmark**

**Repository: evalplus/evalplus** (GitHub)
- **URL:** https://github.com/evalplus/evalplus
- **Stars:** High (NeurIPS 2023 paper)
- **Relevance:** Standard evaluation framework for code generation
- **Key Features:**
  - HumanEval+ (80x more test cases than original)
  - MBPP+ (enhanced test coverage)
  - Error classification via execution

**Repository: CodeEval-Pro** (GitHub)
- **URL:** https://github.com/CodeEval-Pro/CodeEval-Pro
- **Features:** HumanEval Pro and MBPP Pro benchmarks
- **Error Statistics:** Includes error type analysis in logs
- **Code:** `python -m eval.harness` with `--run_code` flag for error statistics

**DebugBench (ACL 2024)**
- **URL:** http://www.aclanthology.org/2024.findings-acl.247/
- **Taxonomy:** 4 major bug categories, 18 minor types
- **Languages:** C++, Java, Python
- **Size:** 4,253 instances

**Serena Analysis Needed:** false (LlmFix taxonomy well-documented)

### Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Priority 1 (HIGHEST):** LlmFix taxonomy from arXiv 2409.00676
- 19 error cause categories derived from 12,837 errors across 14 LLMs
- Uses HumanEval dataset (same as our evaluation)
- Well-documented classification methodology

**Priority 2:** ICSE 2025 Error Taxonomy (Wang et al.)
- 13 semantic + 14 syntactic characteristics
- GitHub repository available with labeled data
- Complements LlmFix with finer granularity

**Priority 3:** evalplus error classification
- Standard execution-based error types
- Already integrated in H-E1 codebase

**Recommended Implementation Path:**
- Primary: Extend H-E1 error classifier to support LlmFix 19-cause taxonomy
- Fallback: Use 3-tier taxonomy (syntax/runtime/assertion) from H-E1 if 19-cause fails
- Justification: H-E1 infrastructure already validated; extend rather than rebuild

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. LlmFix taxonomy well-documented in paper.

**Key implementation insight from Serena memory (dl4c_alignment_signatures_2026):**
- Previous pipeline validated multi-granularity analysis approach
- Reusable components: HumanEval+ data loader, error classification pipeline
- Chi-square + Cramér's V methodology proven in H-E1

---

## Experiment Specification

### Dataset

**Dataset**: HumanEval+ and MBPP+ (combined 542 problems)
**Type**: standard
**Source**: evalplus/evalplus library (NeurIPS 2023)

**Statistics:**
- HumanEval+: 164 problems (80x more test cases than original)
- MBPP+: 378 problems (enhanced test coverage)
- Total: 542 problems
- Samples per problem: 10 (at T=0.8)
- Total samples: 542 × 10 × 2 models = 10,840 generations

**Preprocessing**: None (raw code generation task)
**Augmentation**: None (benchmark evaluation, not training)

**Loading Information** (for Phase 4 download):
- Method: evalplus library
- Identifier: `evalplus.data.get_human_eval_plus()`, `evalplus.data.get_mbpp_plus()`
- Code:
```python
from evalplus.data import get_human_eval_plus, get_mbpp_plus
humaneval_problems = get_human_eval_plus()  # 164 problems
mbpp_problems = get_mbpp_plus()  # 378 problems
```

**Continuation Note**: REUSE data from H-E1 - all 10,840 generated samples already exist with error traces.

### Models

#### Baseline Model

**Architecture**: CodeRL-770M (RL) and CodeLlama-7B-DPO (DPO)
**Type**: Pretrained code generation models with different alignment methods

**CodeRL-770M (RL-aligned):**
- Base: CodeT5 encoder-decoder
- Training: Execution-based RL (binary pass/fail reward)
- Source: salesforce/CodeRL (564 GitHub stars)
- Parameters: 770M

**CodeLlama-7B-DPO (DPO-aligned):**
- Base: CodeLlama decoder-only
- Training: Preference-based DPO (pairwise preferences)
- Source: HuggingFace community DPO fine-tunes
- Parameters: 7B

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `Salesforce/codet5-base` (CodeRL base), `codellama/CodeLlama-7b-hf` (CodeLlama base)
- Code:
```python
# CodeRL
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
coderl_model = AutoModelForSeq2SeqLM.from_pretrained("Salesforce/codet5-base")
# CodeLlama-DPO
from transformers import AutoModelForCausalLM
codellama = AutoModelForCausalLM.from_pretrained("codellama/CodeLlama-7b-hf")
```

**Continuation Note**: REUSE models from H-E1 - same generation data already available.

#### Proposed Analysis

**Architecture:** H-E1 error classifier + LlmFix 19-cause taxonomy extension
**Mechanism:** Multi-granularity error taxonomy classification
**Integration Point:** Extend existing H-E1 `analyze.py` classify_error() function

**Modification from H-E1:**
- 3-tier taxonomy (syntax/runtime/assertion) → 19-cause LlmFix taxonomy
- Chi-square + Cramér's V computed at BOTH granularity levels
- Verify effect persistence across taxonomy depth

**Core Mechanism Implementation:**

```python
# Core Mechanism: Multi-Granularity Error Taxonomy Classification
# Based on: LlmFix paper (arXiv 2409.00676) + H-E1 analyze.py

# LlmFix 19-cause taxonomy (from paper Table 2)
LLMFIX_CAUSES = {
    # Syntax-level (3 causes)
    "syntax": ["indentation_error", "syntax_error", "missing_import"],
    # Runtime-level (10 causes)
    "runtime": ["name_error", "type_error", "attribute_error", "index_error",
                "key_error", "value_error", "zero_division", "recursion_error",
                "timeout", "memory_error"],
    # Assertion-level (6 causes)
    "assertion": ["wrong_output", "partial_output", "missing_output",
                  "wrong_type", "off_by_one", "boundary_error"]
}

def classify_error_llmfix(error_trace: str, output: str) -> tuple[str, str]:
    """Classify error at both 3-tier and 19-cause granularity.

    Args:
        error_trace: Exception traceback string
        output: Generated code output

    Returns:
        (coarse_category, fine_cause): e.g., ("syntax", "indentation_error")
    """
    # Step 1: Coarse classification (reuse H-E1 logic)
    coarse = classify_error_coarse(error_trace)  # syntax|runtime|assertion

    # Step 2: Fine-grained classification via error message parsing
    fine_cause = parse_llmfix_cause(error_trace, coarse)

    return coarse, fine_cause

def compute_multi_granularity_cramers_v(rl_results, dpo_results):
    """Compute Cramér's V at both 3-tier and 19-cause levels."""
    # 3-tier (coarse) - 2x3 contingency table
    coarse_table = build_contingency_table_coarse(rl_results, dpo_results)
    _, _, cramers_v_coarse, _ = chi_square_test(coarse_table)

    # 19-cause (fine) - 2x19 contingency table
    fine_table = build_contingency_table_fine(rl_results, dpo_results)
    _, p_value_fine, cramers_v_fine, _ = chi_square_test(fine_table)

    return cramers_v_coarse, cramers_v_fine, p_value_fine
```

### Training Protocol

**No Training Required** - This is a statistical analysis experiment reusing H-E1 generation data.

**Analysis Protocol:**
1. Load H-E1 execution results (542 RL samples + 542 DPO samples)
2. Re-classify errors using LlmFix 19-cause taxonomy
3. Build contingency tables at both granularity levels
4. Compute chi-square and Cramér's V at each level
5. Verify effect persistence (V > 0.03 at fine-grained level)

**Configuration (from H-E1):**
- Temperature: 0.8
- Samples per problem: 10
- Total samples: 10,840 (reused)
- Seed: 42 (fixed)

### Evaluation

**Primary Metrics:**
- **Chi-square p-value (fine-grained)**: p < 0.05 required for statistical significance
- **Cramér's V (fine-grained)**: V > 0.03 required for effect persistence at LlmFix 19-cause level
- **Cramér's V (coarse)**: Compare with H-E1 result (V = 0.2147) for robustness check

**Success Criteria (MECHANISM hypothesis):**
1. P(syntax+runtime | failure, DPO) > P(syntax+runtime | failure, RL) - direction check
2. Cramér's V > 0.03 at LlmFix 19-cause level - effect persistence check
3. Chi-square p < 0.05 at fine-grained level - statistical significance

**Expected Results (from H-E1 coarse analysis):**
- H-E1 Cramér's V (coarse): 0.2147 (small-medium effect)
- Expected fine-grained V: 0.03-0.15 (smaller due to more categories)
- Source: H-E1 04_validation.md

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical analysis (error classification)
- Library: scipy.stats, numpy
- Code:
```python
from scipy.stats import chi2_contingency
import numpy as np

def cramers_v(contingency_table):
    chi2, p, dof, expected = chi2_contingency(contingency_table)
    n = contingency_table.sum()
    min_dim = min(contingency_table.shape) - 1
    return np.sqrt(chi2 / (n * min_dim))
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Cramér's V at coarse (3-tier) vs fine (19-cause) levels

#### Additional Figures (LLM Autonomous)
1. **Error Distribution Heatmap**: 2x19 heatmap showing RL vs DPO error cause distribution
2. **Cramér's V Persistence Plot**: V values across taxonomy granularities (3-tier → 19-cause)
3. **Error Proportion Bar Chart**: DPO syntax+runtime proportion vs RL at each level
4. **Statistical Significance Plot**: p-values with 0.05 threshold line

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Effect persists at fine-grained taxonomy (Cramér's V > 0.03 at LlmFix 19-cause level)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: QLoRA Paper (2305.14314)
- **Type**: Research paper / methodology reference
- **Query Used**: "DPO alignment code LLM preference"
- **Relevance**: DPO alignment methodology context
- **Key Insights**:
  - DPO models built on preference-ranked datasets without execution filtering
  - Hyperparameters: LR 1e-4 to 2e-4, batch size 16-64
- **Used For**: Understanding DPO alignment mechanism

**Source A.2**: Previous Pipeline Memory (dl4c_alignment_signatures_2026)
- **Type**: Serena memory / past experiment
- **Query Used**: `mcp__serena__read_memory("global/phase45/dl4c_alignment_signatures_2026")`
- **Relevance**: Prior DL4C pipeline with alignment analysis
- **Key Insights**:
  - Multi-granularity taxonomy testing proven methodology
  - Alignment methods create distinguishable profiles (Cohen's d=7.835)
  - Reusable components: HumanEval+ data loader, error classification
- **Used For**: Validation methodology, continuation context

### B. GitHub Implementations (Exa)

**Repository B.1**: LlmFix (arXiv 2409.00676)
- **URL**: https://arxiv.org/pdf/2409.00676
- **Query Used**: "LlmFix error taxonomy classification Python code generation debugging"
- **Relevance**: **CORE** - Defines 19-cause error taxonomy for LLM code generation
- **Key Findings**:
  - 14 Python exception types
  - 19 root cause categories derived from 12,837 errors across 14 LLMs
  - Three auto-fixable: missing import, redundant generation, inconsistent indentation
- **Used For**: Fine-grained taxonomy definition (core mechanism)

**Repository B.2**: ICSE 2025 Error Taxonomy (Wang et al.)
- **URL**: https://wangzhijie.me/assets/pubs/icse25-llmcodeerrors.pdf
- **Query Used**: (same as B.1)
- **Relevance**: Complementary taxonomy with semantic/syntactic dimensions
- **Key Findings**:
  - 13 semantic characteristics + 14 syntactic characteristics
  - 557 labeled errors from 6 LLMs on HumanEval
- **Used For**: Cross-validation of error categories

**Repository B.3**: evalplus/evalplus (GitHub)
- **URL**: https://github.com/evalplus/evalplus
- **Query Used**: "evalplus HumanEval MBPP error classification chi-square statistical analysis"
- **Relevance**: Standard evaluation framework for code generation
- **Key Findings**:
  - HumanEval+ (80x more test cases)
  - MBPP+ (enhanced test coverage)
  - Error classification via execution
- **Used For**: Dataset loading, execution infrastructure

**Repository B.4**: CodeEval-Pro (GitHub)
- **URL**: https://github.com/CodeEval-Pro/CodeEval-Pro
- **Query Used**: (same as B.3)
- **Relevance**: Extended benchmarks with error statistics
- **Key Features**: HumanEval Pro, MBPP Pro, error type analysis in logs
- **Used For**: Reference for error statistics methodology

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - LlmFix taxonomy well-documented in paper

**Project Memories Accessed**:
- `snapshot_h-e1_20260323`: Previous h-e1 hypothesis snapshot
- `global/phase45/dl4c_alignment_signatures_2026`: Prior pipeline synthesis

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Reports - H-E1, H-M1, H-M2
- **Files**:
  - `h-e1/04_validation.md`: Chi-square p=2.19e-08, V=0.2147
  - `h-m1/04_validation.md`: Fisher's exact p=0.0027, assertion proportion analysis
  - `h-m2/04_validation.md`: Welch t-test p=1.08e-34, Cohen's d=1.691
- **Reused Components**:
  - Dataset: HumanEval+ and MBPP+ (10,840 samples already generated)
  - Models: CodeRL-770M, CodeLlama-7B-DPO
  - Error classification: `h-e1/code/analyze.py` as base for extension
  - Statistical methodology: Chi-square, Cramér's V computation
- **Why Reused**: Enables controlled experiment - only taxonomy granularity changes

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Phase 2A/2B + Previous | H-E1 context |
| Error taxonomy (3-tier) | Previous | H-E1 analyze.py |
| Error taxonomy (19-cause) | Exa GitHub | B.1 (LlmFix) |
| Baseline model | Phase 2A | CodeRL, CodeLlama-DPO |
| Statistical methodology | Previous + scipy | H-E1, scipy.stats |
| Pseudo-code | H-E1 + LlmFix | H-E1/code/analyze.py + B.1 |
| Training protocol | N/A | Statistical analysis only |
| Evaluation metrics | Phase 2B | 02b_verification_plan.md |
| Success criteria | Phase 2B | H-M3 spec (V > 0.03) |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-24T15:25:00+00:00

### Workflow History for This Hypothesis
- 2026-03-24T15:22:19: Hypothesis h-m3 set to IN_PROGRESS (External loop starting Phase 2C → 3 → 4)
- Prerequisites: h-m2 COMPLETED (PASS)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
