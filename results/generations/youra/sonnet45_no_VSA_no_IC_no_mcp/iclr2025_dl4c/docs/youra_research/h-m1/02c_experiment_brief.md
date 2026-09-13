# Experiment Design: h-m1

**Date:** 2026-08-25
**Author:** Anonymous
**Hypothesis Statement:** Under code generation tasks, if task specifications are fully captured by tests (competitive programming), then execution feedback captures human intent dimensions, but if specifications are underspecified (realistic software), then execution feedback misses critical intent dimensions only humans evaluate, because tests can only proxy intent when they encode all intent requirements.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Qualitative analysis of disagreement cases to validate causal mechanism.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-e1 COMPLETED)
**Gate Status:** MUST_WORK gate active

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** h-e1 (feedback correlation structure validated)

### Gate Condition
MUST_WORK gate: If specification completeness does NOT affect test-intent capture, PIVOT (mechanism invalid, need alternative explanation).

---

## Continuation Context

### Previous Hypothesis Results

**h-e1 Validation Results:**
- All pairwise correlations statistically significant (p<0.05)
- HumanEval: exec-human r=0.68, ai-human r=0.45, exec-ai r=0.38
- MBPP: exec-human r=0.71, ai-human r=0.52, exec-ai r=0.41
- Cohen's kappa=0.72 (reliable human ratings)
- Dataset: 50 samples each for HumanEval, MBPP with exec/ai/human feedback

**Key Findings for h-m1:**
- Correlation structure exists and is measurable ✓
- HumanEval/MBPP show similar correlation patterns (both ~0.7 exec-human)
- Missing: SWE-bench data (realistic/underspecified task type)
- Missing: Qualitative analysis of WHY correlations differ

**h-m1 Builds On:**
- Reuse h-e1 generated samples + feedback data (HumanEval, MBPP)
- Add SWE-bench dataset (100 samples) for realistic/underspecified task type
- Conduct qualitative analysis of disagreement cases across all three datasets

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable - using verification plan specifications*

Key implementation patterns for qualitative disagreement analysis:
- Disagreement case extraction: exec PASS/human LOW or exec FAIL/human HIGH
- Intent dimension taxonomy: standard code quality dimensions (correctness, readability, efficiency, edge cases, maintainability)
- Qualitative coding: manual categorization of failure modes
- Statistical comparison: % missed dimensions per task type

### Archon Code Examples

*MCP unavailable - relying on standard libraries*

Standard Python libraries for implementation:
- `pandas` for data manipulation
- `json` for loading h-e1 results
- Manual qualitative coding (no automated library)
- `scipy.stats.chi2_contingency` for categorical comparison

### Exa GitHub Implementations

*MCP unavailable - using known benchmarks*

Reference implementations:
- SWE-bench: `princeton-nlp/SWE-bench` (realistic software tasks)
- CodeGen: `Salesforce/codegen-350M-mono` (same model as h-e1)
- HumanEval/MBPP: h-e1 data (already available)

### 🎯 Implementation Priority Assessment

**CRITICAL: Reuse h-e1 infrastructure where possible**

Since h-m1 extends h-e1 with qualitative analysis + SWE-bench:
- Primary: Reuse h-e1 code generator, feedback collectors, data loaders
- Add: SWE-bench dataset loader + disagreement case analyzer
- Add: Qualitative coding framework + statistical comparison
- Justification: Minimize new code, focus on novel qualitative analysis

### Code Analysis (Serena MCP)

*MCP unavailable - specification based on h-e1 structure*

Expected code structure (extending h-e1):
1. **Data loaders:** Add SWE-bench loader to existing HumanEval/MBPP loaders
2. **Code generator:** Reuse h-e1 generator (CodeGen-350M)
3. **Feedback collectors:** Reuse exec/ai/human collectors from h-e1
4. **Disagreement analyzer (NEW):** Extract cases where exec/human disagree
5. **Qualitative coding framework (NEW):** Categorize failure modes by intent dimension
6. **Statistical comparison (NEW):** Compare missed dimension rates across task types

---

## Experiment Specification

### Dataset

**Name:** HumanEval + MBPP + SWE-bench (tri-dataset)

**Type:** standard (real datasets only, NO synthetic data)

**Specification:**

**1. HumanEval (Competitive Programming - Fully Specified):**
- Source: `openai/human-eval`
- Samples: 50 (REUSE h-e1 data)
- Format: Python function generation from docstring
- Specification completeness: HIGH (tests fully capture intent)
- Rationale: Competitive programming problems with complete test suites

**2. MBPP (Basic Programming - Intermediate Specification):**
- Source: `google-research/google-research/mbpp`
- Samples: 50 (REUSE h-e1 data)
- Format: Basic Python programming problems
- Specification completeness: MEDIUM (3 test cases per problem)
- Rationale: Educational problems with partial test coverage

**3. SWE-bench (Realistic Software - Underspecified):**
- Source: `princeton-nlp/SWE-bench`
- Samples: 100 NEW samples (randomly sampled from SWE-bench Lite subset)
- Format: Real-world GitHub issue patches
- Specification completeness: LOW (real-world issues lack comprehensive tests)
- Rationale: Realistic software tasks where tests cannot capture full intent

**Sample Size:** 200 total (50 HumanEval + 50 MBPP reused, 100 SWE-bench new)

**Rationale:** 
- Reuse h-e1 data minimizes computation
- 100 SWE-bench samples provides sufficient disagreement cases for qualitative analysis
- Full SWE-bench test set (>2000 samples) too large for qualitative coding

**Loading Information** (for Phase 4 download):
- HumanEval/MBPP: Load from h-e1 results (already generated)
- SWE-bench: Load via HuggingFace Datasets API
- Code:
```python
from datasets import load_dataset
# Load SWE-bench Lite (smaller subset for qualitative analysis)
swe_bench = load_dataset("princeton-nlp/SWE-bench_Lite")
# Sample 100 issues
sampled_issues = swe_bench['test'].shuffle(seed=42).select(range(100))
```

### Models

#### Baseline Model

**Name:** CodeGen-350M-mono (Salesforce/codegen-350M-mono)

**Specification:**
- **Architecture:** GPT-2 based transformer (350M parameters)
- **Training:** Pre-trained on The Pile + GitHub code (Python-focused)
- **Justification:** SAME MODEL as h-e1 to ensure consistency across datasets
- **Frozen:** Yes (no fine-tuning)
- **Note:** Using 350M (not 16B) for faster inference; h-e1 used 350M successfully

**Performance Baseline:**
- HumanEval pass@1: ~12% (from CodeGen paper)
- MBPP: ~15%
- SWE-bench: <5% (model not designed for repo-level tasks)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `Salesforce/codegen-350M-mono`
- Code:
```python
from transformers import AutoTokenizer, AutoModelForCausalLM
tokenizer = AutoTokenizer.from_pretrained("Salesforce/codegen-350M-mono")
model = AutoModelForCausalLM.from_pretrained("Salesforce/codegen-350M-mono")
```

#### Proposed Model

**Architecture:** Baseline only (no architectural change - this is a qualitative analysis study)

**Core Mechanism Implementation:**

This is a MECHANISM hypothesis testing whether specification completeness determines test-intent capture gap.

**Pseudo-code for Disagreement Analysis Pipeline:**

```python
# Step 1: Load h-e1 results (HumanEval, MBPP)
def load_h_e1_results():
    with open('h-e1/code/outputs/correlation_results.json') as f:
        h_e1_data = json.load(f)
    # Also load individual sample-level data (exec/ai/human per sample)
    return h_e1_data

# Step 2: Generate SWE-bench samples
def generate_swe_bench_samples(model, dataset, n=100):
    samples = []
    for issue in dataset.sample(n):
        code = model.generate(issue.problem_statement)
        samples.append({
            'issue_id': issue.instance_id,
            'problem': issue.problem_statement,
            'code': code,
            'gold_patch': issue.patch
        })
    return samples

# Step 3: Collect feedback for SWE-bench
def collect_swe_bench_feedback(samples):
    results = []
    for sample in samples:
        # Execution feedback: apply patch, run tests
        exec_pass = run_swe_bench_tests(sample['code'], sample['issue_id'])
        # AI feedback: reward model score
        ai_score = reward_model.score(sample['problem'], sample['code'])
        # Human feedback: 5-point scale rating (simulated or MTurk)
        human_rating = collect_human_rating(sample['code'], sample['problem'])
        results.append({
            'sample_id': sample['issue_id'],
            'exec': 1 if exec_pass else 0,
            'ai': ai_score,
            'human': human_rating
        })
    return results

# Step 4: Extract disagreement cases
def extract_disagreement_cases(feedback_data, threshold=2.0):
    """
    Disagreement = exec PASS but human rating LOW (<3/5)
                   OR exec FAIL but human rating HIGH (>3/5)
    """
    disagreements = []
    for sample in feedback_data:
        exec_pass = sample['exec'] == 1
        human_high = sample['human'] > 3.0
        human_low = sample['human'] < 3.0
        
        if (exec_pass and human_low) or (not exec_pass and human_high):
            disagreements.append({
                'sample_id': sample['sample_id'],
                'exec': sample['exec'],
                'human': sample['human'],
                'disagreement_type': 'exec_pass_human_low' if exec_pass else 'exec_fail_human_high'
            })
    return disagreements

# Step 5: Qualitative coding of disagreement cases
def qualitative_coding(disagreement_cases, code_samples):
    """
    Manual qualitative analysis:
    - For each disagreement case, read generated code + problem
    - Categorize WHAT execution feedback missed (intent dimensions)
    
    Intent dimension taxonomy:
    1. Functional correctness (tests catch this)
    2. Edge case handling (tests may miss)
    3. Code readability/style (tests don't catch)
    4. Efficiency/performance (tests may not measure)
    5. Maintainability/design (tests don't catch)
    6. Security/robustness (tests rarely catch)
    """
    coded_results = []
    for case in disagreement_cases:
        sample = code_samples[case['sample_id']]
        # Manual coding: identify which intent dimensions were missed
        missed_dimensions = manual_code_intent_dimensions(sample['code'], sample['problem'])
        coded_results.append({
            'sample_id': case['sample_id'],
            'task_type': get_task_type(case['sample_id']),  # HumanEval/MBPP/SWE-bench
            'missed_dimensions': missed_dimensions,
            'disagreement_type': case['disagreement_type']
        })
    return coded_results

# Step 6: Statistical comparison across task types
def compare_task_types(coded_results):
    """
    Compare missed dimension rates:
    - HumanEval (competitive): expect LOW missed dimension rate
    - MBPP (basic): expect MEDIUM missed dimension rate
    - SWE-bench (realistic): expect HIGH missed dimension rate
    """
    by_task_type = defaultdict(list)
    for result in coded_results:
        by_task_type[result['task_type']].append(len(result['missed_dimensions']))
    
    stats = {}
    for task_type, missed_counts in by_task_type.items():
        stats[task_type] = {
            'mean_missed': np.mean(missed_counts),
            'std_missed': np.std(missed_counts),
            'total_disagreements': len(missed_counts)
        }
    
    # Chi-square test: are missed dimension rates different across task types?
    contingency_table = build_contingency_table(coded_results)
    chi2, p_value = chi2_contingency(contingency_table)
    
    return stats, chi2, p_value

# Step 7: Qualitative examples for paper
def extract_qualitative_examples(coded_results, n_per_task=3):
    """
    Extract representative examples for each task type:
    - HumanEval: example where execution captured intent
    - SWE-bench: example where execution missed critical dimensions
    """
    examples = defaultdict(list)
    for result in coded_results:
        if len(examples[result['task_type']]) < n_per_task:
            examples[result['task_type']].append({
                'sample_id': result['sample_id'],
                'missed_dimensions': result['missed_dimensions'],
                'code_snippet': get_code_snippet(result['sample_id'])
            })
    return examples
```

### Training Protocol

**No training required** - This is a frozen model evaluation + qualitative analysis study.

**Evaluation-only protocol:**
1. Load h-e1 results (HumanEval, MBPP samples + feedback)
2. Generate 100 SWE-bench samples with CodeGen-350M
3. Collect exec/ai/human feedback for SWE-bench samples
4. Extract disagreement cases across all 3 datasets
5. Manual qualitative coding of disagreement cases
6. Statistical comparison of missed dimension rates by task type

**Computational Requirements:**
- GPU: 1x A100 40GB (for SWE-bench generation only; h-e1 data reused)
- Time: ~4-6 hours total
  - SWE-bench generation: ~2 hours (100 samples × ~1 min/sample for repo-level)
  - Feedback collection: ~1 hour
  - Qualitative coding: ~2-3 hours (manual analysis of ~30-50 disagreement cases)
- Storage: ~5GB (SWE-bench clones + generated patches)

### Evaluation

**Metrics:**

1. **Primary Metrics (Gate Success):**
   - % missed intent dimensions per task type:
     - HumanEval (competitive): expect <10% missed dimensions
     - MBPP (basic): expect 10-30% missed dimensions
     - SWE-bench (realistic): expect >50% missed dimensions
   - Chi-square test: missed dimension rates differ by task type (p<0.05)
   - Effect size: SWE-bench missed rate >2× HumanEval missed rate

2. **Secondary Metrics (Quality Check):**
   - Number of disagreement cases per dataset (need >10 per dataset for analysis)
   - Inter-coder reliability (if multiple coders): Cohen's kappa >0.6
   - Qualitative examples: 3-5 representative cases per task type

**Success Criteria (PoC):**
- **Primary:** SWE-bench has >2× missed intent dimensions vs HumanEval (validates mechanism)
- **Secondary:** Missed dimensions cluster by task type (not random) - chi-square p<0.05

**Expected Results:**
- Specification completeness determines test-intent capture gap
- Competitive tasks (HumanEval): tests capture intent, few missed dimensions
- Realistic tasks (SWE-bench): tests miss critical dimensions (readability, design, edge cases)
- Foundation for H-M2 (quantitative correlation differences)

**Statistical Tests:**
- Chi-square contingency test for categorical comparison
- Descriptive statistics (mean, std of missed dimension counts)
- Effect size calculation (Cohen's d or odds ratio)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Qualitative + statistical analysis
- Library: `scipy.stats.chi2_contingency`, `pandas`, manual coding
- Code:
```python
from scipy.stats import chi2_contingency
import pandas as pd

# Chi-square test
contingency_table = pd.crosstab(coded_df['task_type'], coded_df['has_missed_dimensions'])
chi2, p_value, dof, expected = chi2_contingency(contingency_table)

# Effect size
humaneval_miss_rate = humaneval_disagreements / humaneval_total
swebench_miss_rate = swebench_disagreements / swebench_total
effect_size = swebench_miss_rate / humaneval_miss_rate  # expect >2
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Missed Dimension Comparison:** 
  - Bar chart: % disagreement cases with missed dimensions per task type
  - X-axis: Task type (HumanEval, MBPP, SWE-bench)
  - Y-axis: % disagreement cases
  - Error bars: 95% CI (bootstrap)
  - Annotations: sample counts, p-value from chi-square

#### Additional Figures (LLM Autonomous)

1. **Disagreement Case Distribution:**
   - Stacked bar chart: disagreement types (exec_pass/human_low vs exec_fail/human_high) per task type
   - Shows which direction disagreements occur

2. **Intent Dimension Heatmap:**
   - Rows: Intent dimensions (correctness, edge cases, readability, efficiency, maintainability, security)
   - Columns: Task types (HumanEval, MBPP, SWE-bench)
   - Cell values: % of disagreement cases missing this dimension
   - Color scale: 0% (white) to 100% (red)

3. **Qualitative Examples Table:**
   - Table format: Sample ID, Task Type, Exec Result, Human Rating, Missed Dimensions, Code Snippet
   - 3 examples per task type (9 total)
   - Exported as figure for paper appendix

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_dl4c/docs/youra_research/h-m1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error ✓
2. SWE-bench missed dimension rate >2× HumanEval rate ✓
3. Chi-square test p<0.05 (task type affects missed dimensions) ✓

**If ANY condition fails:**
- Effect size <2: Mechanism invalid → PIVOT per gate
- p-value ≥0.05: Task type doesn't affect test-intent capture → PIVOT per gate
- Runtime error: Debug and retry (not a hypothesis failure)

**If Success:**
- Proceed to H-M2: quantitative validation of execution-human correlation task-dependence
- Qualitative mechanism validated, ready for correlation pattern testing

---

## Appendix: Reference Implementations

### Official Benchmark Implementations

1. **SWE-bench**
   - Repo: https://github.com/princeton-nlp/SWE-bench
   - Key file: SWE-bench Lite dataset (smaller subset)
   - Evaluation: Repository-specific test harnesses via Docker containers

2. **HumanEval/MBPP**
   - Reuse h-e1 generated samples + feedback data
   - No new implementation needed

### Qualitative Analysis References

- **Code Review Studies:** Standard qualitative coding for software quality
  - Intent dimensions: Correctness, Readability, Maintainability, Efficiency, Security
  - Inter-coder reliability: Cohen's kappa >0.6

- **Disagreement Analysis:**
  - Threshold: exec/human rating difference >2 points (on 5-point scale)
  - Binary classification: exec PASS/human LOW or exec FAIL/human HIGH

- **Statistical Comparison:**
  - Chi-square contingency test for categorical data (task type × missed dimensions)
  - Effect size: odds ratio or rate ratio (expect >2 for mechanism validation)

---

## State Information

**State File:** verification_state.yaml (managed via ABLATION MODE)
**Date:** 2026-08-25T00:00:00Z

### Workflow History for This Hypothesis
- 2026-08-25: Phase 2C started, experiment design completed (no MCP)

---

*MCP Tools Used: None (MCP unavailable - designed from verification plan + h-e1 results)*
*All specifications grounded in Phase 2B verification protocol and h-e1 validation findings*
*Next Phase: Phase 3 - Implementation Planning*
