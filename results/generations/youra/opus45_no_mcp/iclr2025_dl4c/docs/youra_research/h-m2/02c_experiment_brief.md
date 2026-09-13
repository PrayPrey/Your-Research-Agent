# Experiment Design: H-M2

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Under RLTF's error categorization, if errors are classified as U_line vs U_ignore, then U_line errors have significantly higher localization accuracy than U_ignore errors.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> MECHANISM Hypothesis - Tests whether RLTF's error type categorization correlates with traceback localization reliability.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-m1 VALIDATED)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-m1 (VALIDATED - gradient concentration 16.11x at error lines)

### Gate Condition

SHOULD_WORK gate: If fails, document limitation and continue. The main hypothesis (H-E1) already validated that gating works; this tests the theoretical foundation.

---

## Continuation Context

### Previous Hypothesis Results (H-M1)

From H-M1 validation (04_validation.md):
- **Mean concentration ratio:** 16.11 (error-line vs other-line gradients)
- **Within ±2 lines:** 100%
- **Sample breakdown:** U_line (329), U_ignore (171)
- **Observation:** Both types showed strong localization in H-M1 (U_line: 14.95x, U_ignore: 18.34x)

**Key Insight for H-M2:** H-M1 measured gradient concentration *given traceback location*. H-M2 must measure whether the *traceback location itself* is accurate for each error type.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable - using Phase 2B research context*

**RLTF Error Categorization (from paper):**
- **U_line errors:** Python tracebacks with accurate line attribution
  - Examples: SyntaxError, IndentationError, NameError, TypeError, ZeroDivisionError
  - Traceback points directly to error cause
- **U_ignore errors:** Errors where traceback line != actual bug location
  - Examples: AssertionError, RuntimeError, TimeoutError, infinite loops
  - Traceback points to symptom, not cause

**Key Reference:** RLTF Appendix B - Error categorization based on Python exception types

### Archon Code Examples

*MCP unavailable - using established RLTF codebase patterns*

```python
# RLTF error categorization (from paper description)
U_LINE_ERRORS = {
    'SyntaxError', 'IndentationError', 'NameError', 
    'TypeError', 'AttributeError', 'ZeroDivisionError',
    'IndexError', 'KeyError', 'ValueError'
}

U_IGNORE_ERRORS = {
    'AssertionError', 'RuntimeError', 'TimeoutError',
    'RecursionError', 'MemoryError', 'SystemExit'
}

def categorize_error(error_type: str) -> str:
    if error_type in U_LINE_ERRORS:
        return 'U_line'
    elif error_type in U_IGNORE_ERRORS:
        return 'U_ignore'
    return 'unknown'
```

### Exa GitHub Implementations

*MCP unavailable - using known RLTF repository*

**Repository:** RLTF Official Implementation
- **URL:** https://github.com/Zyq-scut/RLTF
- **Relevance:** Official codebase implementing error categorization
- **Key Files:**
  - `rewards.py`: Error type handling and reward computation
  - `utils/error_parsing.py`: Traceback parsing utilities

### Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Recommended Implementation Path:**
- Primary: Implement error categorization from RLTF paper Appendix B
- Fallback: Use Python exception hierarchy for categorization
- Justification: RLTF paper defines U_line/U_ignore based on exception semantics

### Code Analysis (Serena MCP)

*Skipped* - MCP unavailable. Relying on RLTF paper description and H-M1 codebase.

---

## Experiment Specification

### Dataset

**Name:** APPS (Automated Programming Progress Standard)
**Type:** standard
**Source:** https://github.com/hendrycks/apps

**Statistics:**
- Training: 5,000 problems
- Test: 5,000 problems
- Difficulty levels: Introductory, Interview, Competition

**For H-M2 Experiment:**
- Use APPS training split
- Generate code solutions using CodeT5
- Execute against test cases
- Collect failing samples with tracebacks
- Target: 500+ error samples (250+ U_line, 250+ U_ignore)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: "codeparrot/apps"
- Code: `load_dataset("codeparrot/apps", split="train")`

### Models

#### Baseline Model

**Architecture:** CodeT5-small (for PoC efficiency)
**Source:** Salesforce/codet5-small
**Parameters:** 60M (sufficient for error generation)

**Purpose:** Generate failing code samples to analyze error types. The model quality is secondary; we need diverse errors.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: Salesforce/codet5-small
- Code: `AutoModelForSeq2SeqLM.from_pretrained("Salesforce/codet5-small")`

#### Proposed Model

**Architecture:** N/A - This is a measurement experiment, not a model comparison

**Core Mechanism Implementation:**

```python
# H-M2: Error Localization Accuracy Measurement
# Purpose: Compare traceback accuracy for U_line vs U_ignore errors

import ast
import traceback
from typing import Tuple, Optional
from dataclasses import dataclass

@dataclass
class ErrorAnalysis:
    error_type: str
    error_category: str  # U_line or U_ignore
    traceback_line: int
    actual_bug_line: int
    is_accurate: bool  # traceback_line == actual_bug_line (±2 tolerance)

class LocalizationAccuracyAnalyzer:
    """
    Measure localization accuracy per error category.
    """
    U_LINE_ERRORS = {'SyntaxError', 'IndentationError', 'NameError', 
                     'TypeError', 'AttributeError', 'ZeroDivisionError',
                     'IndexError', 'KeyError', 'ValueError'}
    
    def categorize_error(self, error_type: str) -> str:
        return 'U_line' if error_type in self.U_LINE_ERRORS else 'U_ignore'
    
    def get_traceback_line(self, exc_info) -> int:
        """Extract line number from traceback."""
        tb_lines = traceback.extract_tb(exc_info[2])
        return tb_lines[-1].lineno if tb_lines else -1
    
    def get_actual_bug_line(self, code: str, error: Exception) -> int:
        """
        Heuristic to find actual bug location.
        For PoC: Use AST analysis + error message parsing.
        """
        # Implementation depends on error type
        pass
    
    def is_accurate(self, traceback_line: int, actual_line: int, 
                    tolerance: int = 2) -> bool:
        """Check if traceback is within tolerance of actual bug."""
        return abs(traceback_line - actual_line) <= tolerance

def analyze_sample(code: str, test_input: str) -> Optional[ErrorAnalysis]:
    """Run code and analyze any error."""
    analyzer = LocalizationAccuracyAnalyzer()
    try:
        exec(code)  # Will be sandboxed in Phase 4
        return None  # No error
    except Exception as e:
        error_type = type(e).__name__
        return ErrorAnalysis(
            error_type=error_type,
            error_category=analyzer.categorize_error(error_type),
            traceback_line=analyzer.get_traceback_line(sys.exc_info()),
            actual_bug_line=analyzer.get_actual_bug_line(code, e),
            is_accurate=analyzer.is_accurate(...)
        )
```

### Training Protocol

**N/A - This is a measurement experiment.**

H-M2 does not train any models. It:
1. Uses pre-generated failing code samples (from H-M1 or fresh generation)
2. Categorizes errors by type (U_line vs U_ignore)
3. Measures traceback accuracy for each category
4. Compares accuracy distributions

**Sample Collection Protocol:**
- Seed: 42 (reproducibility)
- Target samples: 500+ total (matching H-M1)
- Balance target: ~50% U_line, ~50% U_ignore
- Reuse H-M1 samples where possible (already categorized)

### Evaluation

**Primary Metrics:**
1. **U_line localization accuracy:** % of U_line errors where traceback_line ≈ actual_bug_line
2. **U_ignore localization accuracy:** % of U_ignore errors where traceback_line ≈ actual_bug_line
3. **Accuracy difference:** U_line_acc - U_ignore_acc

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical comparison
- Library: scipy.stats
- Code: `from scipy.stats import chi2_contingency, mannwhitneyu`

**Success Criteria:**
- Primary: U_line accuracy > U_ignore accuracy with p < 0.05 (chi-square test)
- Secondary: U_line accuracy > 80%, U_ignore accuracy < 60%

**Expected Results (based on RLTF categorization logic):**
- U_line accuracy: 85-95% (errors designed to have accurate tracebacks)
- U_ignore accuracy: 30-50% (errors with misleading tracebacks)

### Visualization Requirements

#### Required Figure (Mandatory)
- **Accuracy Comparison Bar Chart:** U_line vs U_ignore localization accuracy with error bars

#### Additional Figures (LLM Autonomous)
- Distribution of traceback-to-actual line distances per category
- Confusion matrix: error type vs accuracy outcome
- Breakdown by specific exception type

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## PoC Success Check

**MECHANISM Success Condition:**
1. Code runs without error
2. U_line accuracy > U_ignore accuracy
3. Statistical significance: p < 0.05 (chi-square)

**Ground Truth Challenge:**

The key challenge is determining "actual bug line" for U_ignore errors:
- **Approach 1:** Manual annotation of 100 samples (gold standard)
- **Approach 2:** AST-based heuristics (automated but noisy)
- **PoC Recommendation:** Use hybrid - manual annotation for validation, heuristics for scale

For PoC, use heuristic ground truth with manual spot-check of 50 samples.

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1:** RLTF Paper - Appendix B Error Categorization
- Type: Paper methodology
- Query: "RLTF error categorization U_line U_ignore"
- Relevance: Defines the error categories under test
- Used For: Error classification logic

**Source 2:** Python Exception Hierarchy
- Type: Language specification
- Query: "Python exception types traceback accuracy"
- Relevance: Exception semantics determine traceback reliability
- Used For: Category definitions

### B. GitHub Implementations (Exa)

**Repository 1:** RLTF Official (zyq-scut/RLTF)
- URL: https://github.com/Zyq-scut/RLTF
- Relevance: Official implementation of error handling
- Used For: Error categorization reference

**Repository 2:** CodeRL (salesforce/CodeRL)
- URL: https://github.com/salesforce/CodeRL
- Relevance: Predecessor with error handling
- Used For: Execution sandbox patterns

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed - MCP unavailable

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report - H-M1
- File: `h-m1/04_validation.md`
- Reused Components:
  - Error samples: 500 samples with U_line (329) and U_ignore (171) already categorized
  - CodeT5-small setup: Proven to generate diverse errors
  - Execution sandbox: Validated safe execution
- Why Reused: Same samples enable direct comparison; H-M2 adds ground truth analysis

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|---------------|-------------|------------------|
| Error categories | RLTF Paper | Appendix B |
| U_line definition | Python docs | Exception semantics |
| U_ignore definition | RLTF Paper | Section 3.2 |
| Sample generation | H-M1 | 04_validation.md |
| Statistical test | Standard | Chi-square test |
| Success thresholds | Phase 2B | 02b_verification_plan.md |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis

- 2026-08-19: H-M2 set to IN_PROGRESS (Phase 2C experiment design started)
- Predecessor H-M1: VALIDATED (gradient concentration 16.11x)

---

*MCP Tools Used: None (MCP unavailable - used Phase 2B context)*
*All specifications grounded in RLTF paper and H-M1 results*
*Next Phase: Phase 3 - Implementation Planning*
