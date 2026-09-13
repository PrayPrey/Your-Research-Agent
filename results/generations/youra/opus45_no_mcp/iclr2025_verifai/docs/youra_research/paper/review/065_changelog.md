# Phase 6.5 Changelog

**Paper:** Orthogonality of Static and Execution Feedback in LLM Code Generation
**Review Period:** 2026-08-19

---

## Round 1 Changes

### FATAL-001: Corrected Behavioral Rate (Section 5.3)

**Before:**
```markdown
| Metric | Threshold | Result | Status |
|--------|-----------|--------|--------|
| Behavioral Rate | > 40% | **38.6%** | SOFT FAIL |

Of 324 static-clean problems, 125 fail execution (38.6%).
```

**After:**
```markdown
| Metric | Threshold | Result | Status |
|--------|-----------|--------|--------|
| Behavioral Rate | > 40% | **0.3%** | FAIL |

Of 326 static-clean problems, 1 fails execution (0.3%).

**Note:** This result invalidates H-M2. The experimental design using canonical solutions (which pass by construction) cannot properly test whether execution catches behavioral errors in LLM-generated code.
```

### MAJOR-001: Updated Ground Truth YAML

**File:** `065_ground_truth.yaml`

**Before:**
```yaml
- name: "behavioral_rate"
  value: 0.386
  status: "SOFT_FAIL"
```

**After:**
```yaml
- name: "behavioral_rate"
  value: 0.003
  status: "FAIL"
```

### MAJOR-002: Strengthened Limitation L1 (Section 6.2)

**Before:**
```markdown
**L1: Canonical Solutions.** We analyzed EvalPlus canonical solutions, not LLM-generated code. This limits behavioral rate findings but not orthogonality measurement.
```

**After:**
```markdown
**L1: Canonical Solutions Invalidate H-M2.** We analyzed EvalPlus canonical solutions, not LLM-generated code. Since canonical solutions are designed to pass tests, the behavioral rate (0.3%) reflects solution quality, not execution feedback capability. H-M2 (behavioral detection) cannot be evaluated with this experimental design. Proper validation requires actual LLM-generated code that may contain semantic errors while passing static analysis.
```

---

## Round 2 Changes

No changes required. R1 fixes verified correct.

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total issues found | 6 |
| FATAL issues | 1 |
| MAJOR issues | 2 |
| MINOR issues | 3 |
| Issues fixed | 3 |
| Issues for human review | 3 |
| Rounds completed | 2 |
| Final recommendation | ACCEPT_WITH_MINOR |

---

*Generated: 2026-08-19*
