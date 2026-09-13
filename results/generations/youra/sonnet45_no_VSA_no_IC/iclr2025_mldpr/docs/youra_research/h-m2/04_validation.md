# Validation Report: h-m2

**Hypothesis ID:** h-m2  
**Type:** MECHANISM  
**Gate:** SHOULD_WORK  
**Result:** PASS  

---

## Executive Summary

**Gate Verdict:** PASS  
**Rationale:** All primary criteria met (validation=90.00%/82.68%, gradient=False)  

### Key Findings

- **preprocessing_code:** HF 61.0% vs UCI 0.0%, diff=61.0pp, p=0.0000
- **data_source_url:** HF 66.2% vs UCI 15.2%, diff=51.0pp, p=0.0000
- **collection_date:** HF 55.4% vs UCI 10.0%, diff=45.4pp, p=0.0000

**Validation:** Parsing accuracy 90.00%, Semantic accuracy 82.68%

---

## Statistical Results

### preprocessing_code

**Counts:**

| Platform | Present | Absent | Total | Presence Rate |
|----------|---------|--------|-------|---------------|
| HF | 4272 | 2728 | 7000 | 61.0% |
| OpenML | 0 | 2500 | 2500 | 0.0% |
| UCI | 0 | 500 | 500 | 0.0% |

**Primary Test (HF vs UCI):**

- Chi-squared: 706.49
- p-value: 0.0000
- Significant: Yes

**Effect Size:**

- HF rate: 61.0%
- UCI rate: 0.0%
- Difference: 61.0 percentage points
- Cohen's h: 1.793
- Substantial (≥30pp): Yes

**Gradient Test (3 platforms):**

- Chi-squared: 3196.33
- p-value: 0.0000
- Gradient valid (UCI < OpenML < HF): No

### data_source_url

**Counts:**

| Platform | Present | Absent | Total | Presence Rate |
|----------|---------|--------|-------|---------------|
| HF | 4632 | 2368 | 7000 | 66.2% |
| OpenML | 1012 | 1488 | 2500 | 40.5% |
| UCI | 76 | 424 | 500 | 15.2% |

**Primary Test (HF vs UCI):**

- Chi-squared: 516.66
- p-value: 0.0000
- Significant: Yes

**Effect Size:**

- HF rate: 66.2%
- UCI rate: 15.2%
- Difference: 51.0 percentage points
- Cohen's h: 1.099
- Substantial (≥30pp): Yes

**Gradient Test (3 platforms):**

- Chi-squared: 875.88
- p-value: 0.0000
- Gradient valid (UCI < OpenML < HF): Yes

### collection_date

**Counts:**

| Platform | Present | Absent | Total | Presence Rate |
|----------|---------|--------|-------|---------------|
| HF | 3879 | 3121 | 7000 | 55.4% |
| OpenML | 755 | 1745 | 2500 | 30.2% |
| UCI | 50 | 450 | 500 | 10.0% |

**Primary Test (HF vs UCI):**

- Chi-squared: 384.05
- p-value: 0.0000
- Significant: Yes

**Effect Size:**

- HF rate: 55.4%
- UCI rate: 10.0%
- Difference: 45.4 percentage points
- Cohen's h: 1.036
- Substantial (≥30pp): Yes

**Gradient Test (3 platforms):**

- Chi-squared: 757.20
- p-value: 0.0000
- Gradient valid (UCI < OpenML < HF): Yes

---

## Validation Results

**Parsing Accuracy:** 90.00% (threshold: 85.00%)  
**Semantic Accuracy:** 82.68% (threshold: 80.00%)  

---

## Gate Evaluation

**Result:** PASS  
**Rationale:** All primary criteria met (validation=90.00%/82.68%, gradient=False)  

**Primary Criteria:**

1. Direction confirmed (HF > UCI): ✓
2. Statistical significance (p < 0.05): ✓
3. Substantial effect (≥2/3 fields ≥30pp): ✓ (3/3)

**Secondary Criteria:**

- Gradient effect (UCI < OpenML < HF): ✗
- Parsing accuracy >85%: ✓
- Semantic validity >80%: ✓

