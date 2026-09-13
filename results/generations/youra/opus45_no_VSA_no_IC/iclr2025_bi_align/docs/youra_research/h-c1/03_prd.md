# Product Requirements Document: H-C1

## Executive Summary

H-C1 validates whether Mode 3 (Misaligned-Confident) concentrates in subjective prompts versus objective prompts. This condition hypothesis builds on h-e1's mode classification infrastructure to test if RM overconfidence correlates with prompt subjectivity.

**Hypothesis:** Mode 3 proportion is higher for subjective prompts (creative writing) than objective prompts (math/coding) with ratio > 1.5

**Gate:** SHOULD_WORK

---

## Problem Statement

H-E1 established that Mode 3 exists at 23.7% of samples. This hypothesis investigates whether Mode 3 distributes uniformly across prompt types or concentrates in specific categories. Understanding this distribution informs whether RM calibration issues are task-specific.

---

## Functional Requirements

### FR-1: Load H-E1 Results

**Priority:** P0 (Critical)

| Requirement | Description |
|-------------|-------------|
| FR-1.1 | Load `mode_distribution.json` from h-e1 |
| FR-1.2 | Load per-battle mode assignments |
| FR-1.3 | Verify Mode 3 exists in results (prerequisite check) |
| FR-1.4 | Inherit battle filtering from h-e1 |

### FR-2: Prompt Categorization

**Priority:** P0 (Critical)

| Requirement | Description |
|-------------|-------------|
| FR-2.1 | Extract prompts from all battles |
| FR-2.2 | Primary: Use Arena's built-in category tags |
| FR-2.3 | Fallback: Apply keyword-based heuristic classification |
| FR-2.4 | Classify as objective/subjective/ambiguous |
| FR-2.5 | Exclude ambiguous prompts from analysis |

**Categorization Mapping:**
- Subjective: `creative_writing`, `general` (partial)
- Objective: `coding`, `math`, `hard_prompts`

### FR-3: Stratified Mode Analysis

**Priority:** P0 (Critical)

| Requirement | Description |
|-------------|-------------|
| FR-3.1 | Compute Mode 3 proportion within objective prompts |
| FR-3.2 | Compute Mode 3 proportion within subjective prompts |
| FR-3.3 | Calculate ratio: `mode3_subjective / mode3_objective` |
| FR-3.4 | Require ≥500 battles per category minimum |

### FR-4: Statistical Testing

**Priority:** P0 (Critical)

| Requirement | Description |
|-------------|-------------|
| FR-4.1 | Two-proportion z-test for difference |
| FR-4.2 | 95% CI for ratio (log-transform method) |
| FR-4.3 | Effect size calculation (Cohen's h) |
| FR-4.4 | One-sided test: subjective > objective |

### FR-5: Output Generation

**Priority:** P1 (High)

| Requirement | Description |
|-------------|-------------|
| FR-5.1 | Generate `category_mode_distribution.json` |
| FR-5.2 | Generate `ratio_analysis.json` |
| FR-5.3 | Generate `prompt_categories.parquet` |
| FR-5.4 | Include all statistical metrics in output |

---

## Non-Functional Requirements

### NFR-1: Performance
- Total execution time: <10 minutes
- No GPU required (reuses h-e1 RM scores)

### NFR-2: Data Integrity
- All battles must retain h-e1 filtering criteria
- Category assignments must be deterministic and reproducible

### NFR-3: Statistical Rigor
- Minimum 500 samples per category
- Power > 0.99 at α=0.05 for detecting ratio 1.5

---

## Success Criteria

| Criterion | Threshold | Test |
|-----------|-----------|------|
| **Success** | Ratio > 1.5 | Two-proportion z-test, p < 0.05 |
| **Falsification** | Ratio < 1.0 | Same test, opposite direction |
| **Inconclusive** | 1.0 ≤ Ratio ≤ 1.5 | Effect exists but below threshold |

---

## Dependencies

### Prerequisite: H-E1 (VALIDATED)
- Mode classification infrastructure
- RM scores cache (`rm_scores.parquet`)
- Mode distribution results

### External Dependencies
- `lmsys/chatbot_arena_conversations` dataset
- scipy for statistical tests

---

## Data Specification

| Field | Value |
|-------|-------|
| Dataset | lmsys/chatbot_arena_conversations |
| Size | ~33K battles, subset by category |
| Expected Objective | ~8000 battles |
| Expected Subjective | ~6000 battles |
| Mode 3 Base Rate | ~20% (from h-e1) |

---

## Out of Scope

- New RM model training
- New battle collection
- Prompt rephrasing or modification
- Category boundary tuning beyond keyword fallback
