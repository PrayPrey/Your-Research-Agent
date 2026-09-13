# System Architecture: Fix-Impact-Ratio Measurement System

**Hypothesis:** h-e1  
**Type:** EXISTENCE (LIGHT tier, 15 task budget, 4-8 Epic range)  
**Generated:** 2026-08-28  
**Phase:** 3 — Implementation Planning

---

## Codebase Analysis (Serena)

**MCP Status:** Serena MCP not available in this session  
**Analysis Mode:** Green-field implementation (no existing codebase)

**Findings:**
- No existing debugging agent implementation to analyze
- No base hypothesis code to extend
- Starting fresh codebase per EXISTENCE hypothesis constraints

**Applied:** Green-field pattern from Archon KB — minimal infrastructure, focused on metric validation

---

## System Overview

### Architecture Pattern
**Applied:** Research Experiment Pattern (Archon KB: experiment-architecture-patterns)

```
┌──────────────────────────────────────────────────────────────┐
│                   Fix-Impact-Ratio System                     │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │   Dataset   │───▶│  Experiment │───▶│  Validation │      │
│  │  Pipeline   │    │   Runners   │    │   Analysis  │      │
│  └─────────────┘    └─────────────┘    └─────────────┘      │
│         │                  │                    │             │
│         ▼                  ▼                    ▼             │
│  data/codeforces/   results/h-e1/      04_validation.md      │
└──────────────────────────────────────────────────────────────┘
```

### Design Principles
**Applied:** EXISTENCE Hypothesis Pattern (Archon KB: light-tier-constraints)

1. **Minimal Infrastructure:** No complex orchestration (per LIGHT tier)
2. **Metric-First:** Focus on fix-impact-ratio computation
3. **Reproducible:** Fixed seeds, cached datasets, logged experiments
4. **Statistically Valid:** n=50 minimum, proper statistical tests

---

## Module Structure

### Core Modules

#### 1. Dataset Module (`src/dataset/`)
**Complexity: 8** (Module=2, Dependencies=2, Algorithm=2, Integration=2)

**Responsibilities:**
- Fetch Codeforces problems via API or CodeContests dataset
- Filter by rating, solve_count, test_case_count
- Validate ground truth solutions
- Cache to JSON format

**Key Files:**
- `fetcher.py`: API client for Codeforces/CodeContests
- `filter.py`: Problem filtering logic
- `validator.py`: Ground truth validation (run tests)
- `schema.py`: Data models (Problem, TestCase)

**Dependencies:**
- External: `requests`, `pandas`
- Internal: None

**Applied:** Data Pipeline Pattern (Archon KB: dataset-curation-patterns)

---

#### 2. Baseline Experiments Module (`src/baselines/`)
**Complexity: 10** (Module=3, Dependencies=2, Algorithm=3, Integration=2)

**Responsibilities:**
- Implement Random Sampling baseline
- Implement Sequential Trial-and-Error baseline
- Implement Zero-Shot baseline
- Track modifications and fix-impact-ratio

**Key Files:**
- `random_sampling.py`: Generate N solutions, pick best
- `sequential.py`: One-by-one test addressing
- `zeroshot.py`: Single-attempt generation
- `base_runner.py`: Abstract base for experiment execution

**Dependencies:**
- External: OpenAI API (`openai`)
- Internal: `src/metrics/`, `src/execution/`

**Applied:** Baseline Pattern (Archon KB: experiment-control-groups)

---

#### 3. Agent Experiments Module (`src/agents/`)
**Complexity: 14** (Module=4, Dependencies=3, Algorithm=5, Integration=2)

**Responsibilities:**
- Implement GPT-4 Baseline Agent (standard prompting)
- Implement GPT-4 + Memory Agent
- Implement GPT-4 + Explicit Prompting Agent
- Manage debugging loop and iteration tracking

**Key Files:**
- `gpt4_baseline.py`: Standard debugging prompt
- `gpt4_memory.py`: Memory module + debugging
- `gpt4_explicit.py`: Explicit error clustering prompt
- `memory.py`: Error pattern storage and retrieval
- `prompts.py`: Prompt templates

**Dependencies:**
- External: OpenAI API (`openai`)
- Internal: `src/metrics/`, `src/execution/`

**Applied:** Strategic Debugging Pattern (Archon KB: agent-architectures)

---

#### 4. Metrics Module (`src/metrics/`)
**Complexity: 6** (Module=2, Dependencies=1, Algorithm=2, Integration=1)

**Responsibilities:**
- Compute fix-impact-ratio per problem
- Compute secondary metrics (pass rate, iterations, high-impact proportion)
- Aggregate across problems (mean, std, median)

**Key Files:**
- `fix_impact_ratio.py`: Primary metric computation
- `secondary.py`: Pass rate, convergence, high-impact proportion
- `aggregation.py`: Statistical aggregation (mean, std, median)

**Dependencies:**
- External: `numpy`
- Internal: None

**Applied:** Metrics Framework Pattern (Archon KB: evaluation-metrics)

---

#### 5. Code Execution Module (`src/execution/`)
**Complexity: 9** (Module=3, Dependencies=2, Algorithm=2, Integration=2)

**Responsibilities:**
- Execute Python code against test cases
- Sandbox execution (timeout, resource limits)
- Capture outputs and errors
- Track test pass/fail status

**Key Files:**
- `sandbox.py`: Docker or subprocess execution
- `runner.py`: Test execution orchestration
- `result.py`: Test result data models

**Dependencies:**
- External: `docker` (optional) or `subprocess`
- Internal: `src/dataset/` (for test cases)

**Applied:** Code Execution Pattern (Archon KB: sandbox-execution)

---

#### 6. Statistical Analysis Module (`src/analysis/`)
**Complexity: 7** (Module=2, Dependencies=2, Algorithm=2, Integration=1)

**Responsibilities:**
- Mann-Whitney U test (agent vs baseline)
- Cohen's d effect size
- Pearson correlation (ratio vs pass rate)
- Confidence intervals

**Key Files:**
- `hypothesis_tests.py`: Mann-Whitney U implementation
- `effect_size.py`: Cohen's d computation
- `correlations.py`: Pearson r computation

**Dependencies:**
- External: `scipy`, `numpy`
- Internal: `src/metrics/` (for aggregated results)

**Applied:** Statistical Testing Pattern (Archon KB: hypothesis-validation)

---

#### 7. Validation Reporting Module (`src/reporting/`)
**Complexity: 5** (Module=2, Dependencies=2, Algorithm=0, Integration=1)

**Responsibilities:**
- Generate validation report (04_validation.md)
- Create visualizations (distributions, scatter plots)
- Assess gate status (PASS/FAIL)

**Key Files:**
- `report_generator.py`: Markdown report generation
- `visualizations.py`: Matplotlib charts
- `gate_assessment.py`: Success criteria verification

**Dependencies:**
- External: `matplotlib`, `pandas`
- Internal: `src/metrics/`, `src/analysis/`

**Applied:** Validation Reporting Pattern (Archon KB: result-documentation)

---

## File Organization

```
experiments/h-e1/
├── data/
│   └── codeforces_curated/
│       ├── problems.json           # Curated dataset (200 problems)
│       └── metadata.json           # Dataset statistics
│
├── src/
│   ├── dataset/
│   │   ├── fetcher.py              # API client
│   │   ├── filter.py               # Problem filtering
│   │   ├── validator.py            # Ground truth validation
│   │   └── schema.py               # Data models
│   │
│   ├── baselines/
│   │   ├── random_sampling.py      # Baseline 1
│   │   ├── sequential.py           # Baseline 2
│   │   ├── zeroshot.py             # Baseline 3
│   │   └── base_runner.py          # Abstract base
│   │
│   ├── agents/
│   │   ├── gpt4_baseline.py        # Agent A
│   │   ├── gpt4_memory.py          # Agent B
│   │   ├── gpt4_explicit.py        # Agent C
│   │   ├── memory.py               # Memory module
│   │   └── prompts.py              # Prompt templates
│   │
│   ├── metrics/
│   │   ├── fix_impact_ratio.py     # Primary metric
│   │   ├── secondary.py            # Secondary metrics
│   │   └── aggregation.py          # Aggregation logic
│   │
│   ├── execution/
│   │   ├── sandbox.py              # Code execution sandbox
│   │   ├── runner.py               # Test runner
│   │   └── result.py               # Result models
│   │
│   ├── analysis/
│   │   ├── hypothesis_tests.py     # Statistical tests
│   │   ├── effect_size.py          # Cohen's d
│   │   └── correlations.py         # Pearson r
│   │
│   └── reporting/
│       ├── report_generator.py     # 04_validation.md generator
│       ├── visualizations.py       # Charts
│       └── gate_assessment.py      # Gate verification
│
├── results/
│   └── h-e1/
│       ├── baseline_random.json
│       ├── baseline_sequential.json
│       ├── baseline_zeroshot.json
│       ├── agent_baseline.json
│       ├── agent_memory.json
│       ├── agent_explicit.json
│       ├── statistics.json
│       ├── 04_validation.md
│       └── figures/
│           ├── fix_impact_distribution.png
│           ├── agent_vs_baseline_scatter.png
│           └── convergence_curves.png
│
├── scripts/
│   ├── 01_prepare_dataset.py       # Run dataset pipeline
│   ├── 02_run_baselines.py         # Run all baselines
│   ├── 03_run_agents.py            # Run all agents
│   └── 04_generate_report.py       # Generate validation report
│
├── config/
│   ├── dataset_config.yaml         # Dataset parameters
│   ├── experiment_config.yaml      # Experiment parameters
│   └── api_keys.yaml               # OpenAI API key (git-ignored)
│
├── tests/
│   ├── test_dataset.py
│   ├── test_metrics.py
│   ├── test_execution.py
│   └── test_analysis.py
│
├── requirements.txt
└── README.md
```

---

## Epic Tasks (4-8 range for LIGHT tier)

### Epic 1: Dataset Curation Pipeline
**Complexity: 8**
- Implement Codeforces API fetcher
- Implement problem filtering logic
- Implement ground truth validator
- Cache dataset to JSON format
- **Breakdown:** Module=2 (fetcher, filter), Dependencies=2 (requests, pandas), Algorithm=2 (filtering logic), Integration=2 (cache I/O)

### Epic 2: Baseline Experiment Runners
**Complexity: 10**
- Implement Random Sampling baseline
- Implement Sequential Trial-and-Error baseline
- Implement Zero-Shot baseline
- Integrate with metrics and execution modules
- **Breakdown:** Module=3 (3 baselines), Dependencies=2 (OpenAI API), Algorithm=3 (sampling logic), Integration=2 (metrics/execution)

### Epic 3: Agent Experiment Runners
**Complexity: 14**
- Implement GPT-4 Baseline Agent
- Implement GPT-4 + Memory Agent
- Implement GPT-4 + Explicit Prompting Agent
- Implement memory module
- Integrate with metrics and execution modules
- **Breakdown:** Module=4 (3 agents + memory), Dependencies=3 (OpenAI API, memory storage), Algorithm=5 (debugging loop logic), Integration=2 (metrics/execution)

### Epic 4: Metrics and Statistical Analysis
**Complexity: 13** (Combined: Metrics=6 + Analysis=7)
- Implement fix-impact-ratio computation
- Implement secondary metrics (pass rate, convergence, high-impact proportion)
- Implement Mann-Whitney U test
- Implement Cohen's d effect size
- Implement Pearson correlation
- **Breakdown:** Module=4 (metrics + 3 analysis modules), Dependencies=3 (numpy, scipy), Algorithm=4 (statistical tests), Integration=2 (results aggregation)

### Epic 5: Code Execution Sandbox
**Complexity: 9**
- Implement sandbox execution (Docker or subprocess)
- Implement test runner orchestration
- Implement timeout and resource limits
- Capture outputs and errors
- **Breakdown:** Module=3 (sandbox, runner, result), Dependencies=2 (docker/subprocess), Algorithm=2 (timeout logic), Integration=2 (dataset integration)

### Epic 6: Validation Reporting
**Complexity: 5**
- Generate 04_validation.md report
- Create visualizations (distributions, scatter plots, convergence)
- Implement gate assessment logic
- **Breakdown:** Module=2 (report, viz), Dependencies=2 (matplotlib, pandas), Algorithm=0 (formatting only), Integration=1 (metrics/analysis)

---

## Total Complexity Budget

| Epic | Complexity |
|------|------------|
| Epic 1: Dataset Curation | 8 |
| Epic 2: Baseline Runners | 10 |
| Epic 3: Agent Runners | 14 |
| Epic 4: Metrics & Analysis | 13 |
| Epic 5: Code Execution | 9 |
| Epic 6: Validation Reporting | 5 |
| **Total** | **59** |

**Epics Count:** 6 (within 4-8 range for LIGHT tier ✓)  
**Total Complexity:** 59 (reasonable for LIGHT tier focus)

---

## External Dependencies

### Python Libraries
- `openai`: GPT-4 API access
- `requests`: Codeforces API client
- `pandas`: Dataset manipulation
- `numpy`: Numerical computations
- `scipy`: Statistical tests
- `matplotlib`: Visualizations
- `docker` (optional): Sandbox execution

### External APIs
- OpenAI API (GPT-4 Turbo)
- Codeforces API (or CodeContests dataset from Kaggle/HuggingFace)

### Environment Requirements
- Python 3.9+
- OpenAI API key (stored in `config/api_keys.yaml`, git-ignored)
- Docker (optional, for sandbox execution)

---

## Integration Points

### Dataset → Baselines/Agents
- Baselines and agents consume problems from `data/codeforces_curated/problems.json`
- Each experiment runner iterates over problems and tracks metrics

### Experiments → Metrics
- All experiment runners call `src/metrics/fix_impact_ratio.py` after each modification
- Results saved to `results/h-e1/{experiment_name}.json`

### Metrics → Analysis
- `src/analysis/` reads aggregated metrics from experiment JSON files
- Computes statistical tests and correlations

### Analysis → Reporting
- `src/reporting/` reads analysis results and generates 04_validation.md
- Visualizations saved to `results/h-e1/figures/`

---

## Data Flow Diagram

```
┌──────────────┐
│ Codeforces   │
│ API          │
└──────┬───────┘
       │ fetch
       ▼
┌──────────────┐      ┌─────────────┐
│ Dataset      │─────▶│ Baselines   │
│ Pipeline     │      │ (3 runners) │
└──────┬───────┘      └──────┬──────┘
       │                     │ track metrics
       │                     ▼
       │              ┌──────────────┐      ┌─────────────┐
       └─────────────▶│ Agents       │─────▶│ Metrics     │
                      │ (3 runners)  │      │ Framework   │
                      └──────────────┘      └──────┬──────┘
                                                   │ aggregate
                                                   ▼
                                            ┌──────────────┐
                                            │ Statistical  │
                                            │ Analysis     │
                                            └──────┬───────┘
                                                   │ test
                                                   ▼
                                            ┌──────────────┐
                                            │ Validation   │
                                            │ Report       │
                                            └──────────────┘
```

---

## Risk Mitigation Architecture

### Risk 1: Test Case Quality
- **Mitigation:** Validator module runs ground truth against all tests
- **Fallback:** CodeContests dataset as backup (pre-curated)

### Risk 2: API Rate Limits
- **Mitigation:** Cache agent responses in `results/h-e1/{experiment}_cache.json`
- **Fallback:** Reduce problem set to 30 if budget constrained

### Risk 3: Code Execution Safety
- **Mitigation:** Sandbox module with timeout (10s per test) and resource limits
- **Fallback:** Use `subprocess` with `signal.alarm()` if Docker unavailable

---

## Applied Patterns Summary

| Pattern | Source | Application |
|---------|--------|-------------|
| Research Experiment Pattern | Archon KB | Overall architecture |
| LIGHT Tier Constraints | Archon KB | 15 task budget, minimal infrastructure |
| Data Pipeline Pattern | Archon KB | Dataset curation module |
| Baseline Pattern | Archon KB | Control group baselines |
| Strategic Debugging Pattern | Archon KB | Agent architectures |
| Metrics Framework Pattern | Archon KB | Fix-impact-ratio computation |
| Sandbox Execution Pattern | Archon KB | Code execution module |
| Statistical Testing Pattern | Archon KB | Hypothesis validation |
| Validation Reporting Pattern | Archon KB | Report generation |

---

**End of Architecture Document**
