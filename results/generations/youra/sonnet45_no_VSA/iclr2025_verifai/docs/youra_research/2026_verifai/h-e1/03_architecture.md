# System Architecture: H-E1 Verifier-Feedback-Driven Specification Synthesis

**Date:** 2026-07-11  
**Hypothesis:** H-E1 - LLMs utilize structured verifier feedback to iteratively refine formal specifications  
**PRD:** 03_prd.md  
**Experiment Brief:** 02c_experiment_brief.md  
**Architecture Type:** EXISTENCE (PoC) - Minimal 3-stage pipeline  

---

## Knowledge Base Application

Applied: General API client patterns, iterative refinement architecture  
Codebase Analysis (Serena): Green-field project - no existing code to analyze  
Project Type: green-field  
Status: New implementation from scratch  
Analyzed Path: N/A  
Findings: No existing verifier-in-loop patterns. Implementing based on AutoSpec+ (ACL 2026) reference architecture.

---

## System Context

### Core Hypothesis Test

**Question:** Can LLMs utilize structured verifier feedback (witness + obligation + dependency) to iteratively improve ACSL specifications?

**Mechanism:** Verifier-as-Teacher - Frama-C/WP provides pedagogical feedback that guides LLM refinement without human intervention.

**Success Criteria:**
- Iterative improvement: iteration N+1 > iteration N (proof discharge rate)
- Final proof discharge ≥50% on 5-10 programs
- Evidence of feedback utilization in LLM responses

### System Boundaries

**Input:** Unannotated C programs (5-10 from FM-Bench-Verified dataset)  
**Output:** ACSL-annotated C programs + iteration metrics + proof discharge rate  
**External Dependencies:**
- Anthropic API (Claude Opus 4.5)
- Frama-C 29.0 + WP plugin
- Why3 1.8.2 + Alt-Ergo 2.6.2 + Z3 4.15.2

**Out of Scope (PoC):**
- Proof-aware decomposition (AutoSpec+ Stage 1)
- Termination analysis (AutoSpec+ Stage 5)
- Multi-program dependencies
- Baseline comparisons (Phase 4 only)

---

## Module Structure

### 1. LLMClient (`src/llm_client.py`)

**Dependencies:** anthropic

```python
class LLMClient:
    def __init__(self, api_key: str, model: str = "claude-opus-4-5"): ...
    def generate_specification(self, c_code: str, temperature: float = 0.7) -> str: ...
    def refine_specification(self, c_code: str, current_spec: str, feedback: dict, iteration: int, temperature: float = 0.5) -> str: ...
    def _build_generation_prompt(self, c_code: str) -> str: ...
    def _build_refinement_prompt(self, c_code: str, spec: str, feedback: dict, iteration: int) -> str: ...
```

### 2. FramaCVerifier (`src/verifier.py`)

**Dependencies:** subprocess

```python
class FramaCVerifier:
    def __init__(self, timeout: int = 10, solvers: list = ["alt-ergo", "z3"]): ...
    def verify(self, annotated_c_file: str) -> VerificationResult: ...
    def _execute_frama_c(self, c_file: str) -> str: ...
    def _parse_output(self, raw_output: str) -> VerificationResult: ...

class VerificationResult:
    total_vcs: int
    proved_vcs: int
    failed_vcs: list[str]
    raw_output: str
    @property
    def discharge_rate(self) -> float: ...
    @property
    def all_proved(self) -> bool: ...
```

### 3. FeedbackParser (`src/feedback_parser.py`)

**Dependencies:** re, verifier

```python
class FeedbackParser:
    def extract_feedback(self, verification_result: VerificationResult) -> StructuredFeedback: ...
    def _extract_witness(self, failed_vc: str) -> dict: ...
    def _extract_obligation(self, failed_vc: str) -> dict: ...
    def _extract_dependency(self, failed_vc: str, raw_output: str) -> dict: ...
    def format_for_llm(self, feedback: StructuredFeedback) -> str: ...

class StructuredFeedback:
    witness: dict  # Dimension 1: counterexample values
    obligation: dict  # Dimension 2: failed proof obligation type/location
    dependency: dict  # Dimension 3: inter-specification dependencies
```

### 4. RefinementLoop (`src/refinement_loop.py`)

**Dependencies:** llm_client, verifier, feedback_parser

```python
class RefinementLoop:
    def __init__(self, llm: LLMClient, verifier: FramaCVerifier, parser: FeedbackParser, max_iterations: int = 10): ...
    def synthesize(self, c_program: str, program_id: str) -> SynthesisResult: ...
    def _check_convergence(self, history: list[float]) -> bool: ...
    def _log_iteration(self, iteration: int, result: VerificationResult, spec: str): ...

class SynthesisResult:
    final_spec: str
    iterations: int
    discharge_history: list[float]
    converged: bool
    feedback_utilization: dict
```

### 5. DatasetManager (`src/dataset.py`)

**Dependencies:** datasets

```python
class DatasetManager:
    def __init__(self, dataset_name: str = "fm-universe/FM-bench-verified"): ...
    def load_benchmark(self, num_programs: int = 10) -> list[Program]: ...
    def _extract_c_code(self, raw_data: dict) -> str: ...
    def _extract_gold_acsl(self, raw_data: dict) -> str: ...

class Program:
    id: str
    c_code: str
    gold_acsl: str
    properties: list[str]
```

### 6. MetricsTracker (`src/metrics.py`)

**Dependencies:** json

```python
class MetricsTracker:
    def __init__(self, output_dir: str): ...
    def track_iteration(self, program_id: str, iteration: int, discharge_rate: float, spec: str, feedback: dict): ...
    def track_program_completion(self, program_id: str, result: SynthesisResult): ...
    def aggregate_metrics(self) -> dict: ...
    def save_metrics(self, output_path: str): ...
```

### 7. Visualizer (`src/visualizer.py`)

**Dependencies:** matplotlib, seaborn

```python
class Visualizer:
    def __init__(self, output_dir: str): ...
    def plot_gate_metrics(self, target: float, actual_rates: dict): ...
    def plot_iteration_progress(self, iteration_data: dict): ...
    def plot_feedback_utilization(self, utilization_data: dict): ...
    def plot_convergence_histogram(self, convergence_data: list[int]): ...
```

### 8. ExperimentRunner (`src/main.py`)

**Dependencies:** All modules

```python
class ExperimentRunner:
    def __init__(self, config: dict): ...
    def run(self): ...
    def _process_program(self, program: Program) -> SynthesisResult: ...
    def _aggregate_results(self, results: list[SynthesisResult]) -> dict: ...
    def _generate_visualizations(self, results: list[SynthesisResult]): ...
```

---

## Data Flow

### End-to-End Pipeline

```
DatasetManager → ExperimentRunner → RefinementLoop
                                     ↓
                      [Initial Generation] LLMClient
                                     ↓
                      [Verification] FramaCVerifier
                                     ↓
                      [Feedback Extraction] FeedbackParser
                                     ↓
                      [Refinement] LLMClient (loop back to Verification)
                                     ↓
                      [Convergence Check] RefinementLoop
                                     ↓
              MetricsTracker → Visualizer → Results
```

### Iteration Data Flow

**Iteration 0 (Initial Generation):**
1. C code → LLMClient.generate_specification() → ACSL spec
2. ACSL spec → FramaCVerifier.verify() → VerificationResult
3. If all_proved: exit with success
4. Else: extract feedback, goto refinement

**Iteration N (Refinement):**
1. VerificationResult → FeedbackParser.extract_feedback() → StructuredFeedback
2. StructuredFeedback + current_spec → LLMClient.refine_specification() → refined_spec
3. refined_spec → FramaCVerifier.verify() → VerificationResult
4. Track metrics, check convergence
5. If converged or max_iter: exit
6. Else: loop

---

## File Organization

```
h-e1/
├── code/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── llm_client.py        # LLMClient
│   │   ├── verifier.py          # FramaCVerifier + VerificationResult
│   │   ├── feedback_parser.py   # FeedbackParser + StructuredFeedback
│   │   ├── refinement_loop.py   # RefinementLoop + SynthesisResult
│   │   ├── dataset.py           # DatasetManager + Program
│   │   ├── metrics.py           # MetricsTracker
│   │   ├── visualizer.py        # Visualizer
│   │   └── main.py              # ExperimentRunner
│   ├── config/
│   │   └── experiment_config.yaml  # Hyperparameters
│   ├── prompts/
│   │   ├── generation_prompt.txt
│   │   └── refinement_prompt_template.txt
│   ├── requirements.txt
│   └── run_experiment.py        # Entry point
├── data/
│   ├── benchmark/               # 5-10 selected programs
│   │   ├── program_001.c
│   │   └── ...
│   └── ground_truth/            # Gold ACSL (not used during synthesis)
│       ├── program_001_gold.c
│       └── ...
├── results/
│   ├── iteration_logs/          # Per-iteration specs + feedback
│   │   ├── program_001/
│   │   │   ├── iteration_0.json
│   │   │   ├── iteration_1.json
│   │   │   └── ...
│   │   └── ...
│   ├── metrics.json             # Aggregated metrics
│   └── experiment_log.md        # Human-readable log
├── figures/
│   ├── gate_metrics_comparison.png
│   ├── iteration_progress.png
│   ├── feedback_utilization.png
│   └── convergence_histogram.png
└── 04_validation.md             # Results report (Phase 4 output)
```

---

## API Boundaries

### Anthropic API Integration

**Authentication:**
```python
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
```

**Request Pattern:**
```python
message = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=4096,
    temperature=0.7,  # 0.7 initial, 0.5 refinement
    messages=[{"role": "user", "content": prompt}]
)
response_text = message.content[0].text
```

**Error Handling:**
- HTTP 429 (rate limit): Exponential backoff, retry 3x
- HTTP 500 (server error): Retry 3x, log failure
- Timeout: 60s per request, fail gracefully

**Rate Limiting:**
- 1 request/second (conservative)
- Track token usage per program

### Frama-C CLI Integration

**Command Structure:**
```bash
frama-c -wp \
  -wp-timeout 10 \
  -wp-prover alt-ergo,z3 \
  -wp-out <output_dir> \
  <annotated_c_file>
```

**Output Parsing:**
- STDOUT: Proof obligation results (Valid/Unknown/Timeout)
- Exit code: 0 (success), 1 (failure), 2 (error)
- Parse format: `Goal <name>: <status>` lines

**Error Handling:**
- Malformed ACSL: Catch syntax errors, log, retry with syntax fix prompt
- Verifier crash: Log error, mark program as failed, continue
- Timeout: 10s per VC, aggregate failed VCs

---

## Error Handling Strategy

### LLM Client Errors

| Error Type | Detection | Recovery |
|------------|-----------|----------|
| API timeout | anthropic.APITimeoutError | Retry 3x with exponential backoff |
| Rate limit | HTTP 429 | Wait 60s, retry |
| Invalid response | JSON parse failure | Re-prompt with format instruction |
| Empty response | len(content) == 0 | Retry with stronger prompt |

### Verifier Errors

| Error Type | Detection | Recovery |
|------------|-----------|----------|
| Syntax error | Exit code 2, "syntax" in stderr | Extract error, send to LLM for fix |
| Crash | Exit code 134 (SIGABRT) | Log, skip program |
| Timeout | No output after 10s | Kill process, mark VCs as timeout |
| Missing solvers | "prover not found" in stderr | Fail early with environment check |

### Convergence Failures

| Scenario | Detection | Handling |
|----------|-----------|----------|
| No improvement | 3 iterations with same rate | Early stop, log as non-convergent |
| Degradation | rate[N] < rate[N-1] | Continue (may recover), log warning |
| Max iterations | iteration == 10 | Stop, return best spec so far |

---

## Logging Architecture

### Iteration Tracking

**Per-Iteration Log (`results/iteration_logs/<program_id>/iteration_<N>.json`):**
```json
{
  "iteration": 0,
  "timestamp": "2026-07-11T10:00:00Z",
  "spec": "<annotated C code>",
  "verification_result": {
    "total_vcs": 5,
    "proved_vcs": 3,
    "discharge_rate": 60.0,
    "failed_vcs": ["postcondition_line_42", "loop_inv_line_25"]
  },
  "feedback": {
    "witness": {"x": 5, "y": -1},
    "obligation": {"type": "postcondition", "line": 42, "function": "binary_search"},
    "dependency": {"clause": "loop_inv depends on precondition"}
  },
  "llm_tokens": {"input": 1200, "output": 800}
}
```

### Experiment-Level Log (`results/experiment_log.md`)

**Human-Readable Summary:**
```markdown
# H-E1 Experiment Log
Date: 2026-07-11

## Program: binary_search (program_001)
- Initial discharge: 40% (2/5 VCs)
- Iteration 1: 60% (3/5 VCs) [+20%]
- Iteration 2: 80% (4/5 VCs) [+20%]
- Iteration 3: 100% (5/5 VCs) [+20%] ✓ CONVERGED
- Feedback dimensions used: witness (2x), obligation (3x), dependency (1x)

## Summary
- Programs completed: 10/10
- Converged: 6/10 (60%)
- Mean discharge rate: 72%
- Mean iterations: 4.2
```

### Token Usage Tracking

**Cumulative Log (`results/token_usage.json`):**
```json
{
  "total_input_tokens": 45000,
  "total_output_tokens": 32000,
  "estimated_cost": 0.42,
  "per_program_avg": 7700
}
```

---

## Data Persistence

### Checkpointing Strategy

**Checkpoint Frequency:** After each program completion

**Checkpoint Data (`results/checkpoint.json`):**
```json
{
  "last_completed_program": "program_005",
  "completed_programs": ["program_001", "program_002", ...],
  "pending_programs": ["program_006", "program_007", ...],
  "partial_results": {
    "program_006": {
      "iterations_completed": 3,
      "last_spec": "<partial spec>",
      "discharge_history": [40, 55, 60]
    }
  }
}
```

**Recovery Process:**
1. Load checkpoint.json
2. Skip completed programs
3. Resume partial programs from last iteration
4. Continue with pending programs

### Results Storage

**Final Metrics (`results/metrics.json`):**
```json
{
  "experiment_id": "h-e1-poc-2026-07-11",
  "hypothesis": "H-E1",
  "programs_total": 10,
  "programs_converged": 6,
  "mean_discharge_rate": 72.0,
  "median_discharge_rate": 75.0,
  "std_discharge_rate": 15.3,
  "mean_iterations": 4.2,
  "gate_target": 50.0,
  "gate_status": "PASS",
  "feedback_utilization": {
    "witness": 18,
    "obligation": 25,
    "dependency": 12
  }
}
```

---

## Configuration Management

### Experiment Config (`config/experiment_config.yaml`)

```yaml
# LLM Configuration
llm:
  model: "claude-opus-4-5"
  api_key_env: "ANTHROPIC_API_KEY"
  temperature:
    generation: 0.7
    refinement: 0.5
  max_tokens: 4096
  timeout_seconds: 60
  retry_attempts: 3

# Verifier Configuration
verifier:
  frama_c_path: "frama-c"
  timeout_per_vc: 10
  solvers: ["alt-ergo", "z3"]
  wp_model: "Typed"

# Refinement Loop
refinement:
  max_iterations: 10
  early_stop_threshold: 3  # iterations without improvement
  convergence_criterion: "all_proved"  # or "rate_threshold"

# Dataset
dataset:
  name: "fm-universe/FM-bench-verified"
  num_programs: 10
  seed: 42

# Paths
paths:
  data_dir: "data/benchmark"
  ground_truth_dir: "data/ground_truth"
  results_dir: "results"
  figures_dir: "figures"

# Gate Criteria
gate:
  target_discharge_rate: 50.0
  require_iterative_improvement: true
```

---

## Deployment Considerations

### Environment Setup

**System Requirements:**
- OS: Linux (Ubuntu 22.04+) or macOS
- Python: 3.10+
- OCaml: 4.14+ (for Frama-C)
- Memory: 8GB RAM
- Disk: 5GB

**Installation Steps:**

1. **Install Frama-C + Why3:**
```bash
# Install opam (OCaml package manager)
sudo apt-get install opam

# Initialize opam
opam init -y
opam switch create 4.14.0

# Install Frama-C
opam install frama-c

# Install Why3 + solvers
opam install why3
sudo apt-get install alt-ergo z3
```

2. **Python Environment:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **API Key Setup:**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Dependencies (`requirements.txt`)

```txt
anthropic>=0.18.0
datasets>=2.14.0
matplotlib>=3.7.0
seaborn>=0.12.0
pyyaml>=6.0
pytest>=7.4.0
```

### Pre-Flight Checks

**Validation Script (`code/preflight_check.py`):**
```python
def check_frama_c():
    """Verify Frama-C installation."""
    result = subprocess.run(["frama-c", "-version"], capture_output=True)
    assert "Frama-C 29.0" in result.stdout.decode()

def check_solvers():
    """Verify Alt-Ergo and Z3 installation."""
    assert subprocess.run(["alt-ergo", "--version"]).returncode == 0
    assert subprocess.run(["z3", "--version"]).returncode == 0

def check_api_key():
    """Verify Anthropic API key."""
    assert os.environ.get("ANTHROPIC_API_KEY") is not None

def check_dataset():
    """Verify dataset access."""
    from datasets import load_dataset
    dataset = load_dataset("fm-universe/FM-bench-verified")
    assert len(dataset) > 0
```

### Execution

**Run Command:**
```bash
cd code
python run_experiment.py --config config/experiment_config.yaml
```

**Expected Runtime:**
- 10 programs × 5 iterations avg × 30s LLM + 10s verification = ~30 minutes
- Max: 10 programs × 10 iterations × 40s = 1.1 hours

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Dataset Setup | Download FM-Bench, select 10 programs, extract C code + gold ACSL | 8 | datasets(2) + selection(2) + extraction(2) + validation(2) |
| A-2 | LLM Client | Implement Anthropic API wrapper with retry logic + prompt templates | 12 | API client(3) + retry(2) + prompts(4) + testing(3) |
| A-3 | Verifier Integration | Implement Frama-C CLI wrapper + output parser | 14 | CLI wrapper(4) + parser(4) + error handling(4) + testing(2) |
| A-4 | Feedback Parser | Extract 3 feedback dimensions from Frama-C output | 16 | witness extraction(6) + obligation parsing(5) + dependency inference(3) + formatting(2) |
| A-5 | Refinement Loop | Implement iterative refinement controller with convergence detection | 10 | loop logic(4) + convergence(3) + checkpointing(2) + logging(1) |
| A-6 | Metrics & Viz | Implement MetricsTracker + 4 required plots | 9 | metrics(3) + gate plot(2) + progress plot(2) + heatmap(1) + histogram(1) |
| A-7 | Experiment Runner | Orchestrate end-to-end pipeline + batch processing | 11 | orchestration(4) + batch(3) + error recovery(2) + results aggregation(2) |

**Distribution:**
- VeryHigh (18-20): []
- High (14-17): [A-3, A-4]
- Medium (9-13): [A-2, A-5, A-6, A-7]
- Low (4-8): [A-1]

**Total Complexity:** 80 points (7 tasks)

---

## Critical Design Decisions

### 1. Simplified 3-Stage Pipeline (vs AutoSpec+ 5-Stage)

**Decision:** Omit proof-aware decomposition (Stage 1) and termination analysis (Stage 5) for PoC.

**Rationale:**
- EXISTENCE hypothesis only tests feedback utilization, not optimization
- Call graph analysis adds complexity without testing core mechanism
- Termination is out of scope (functional correctness only)

**Trade-off:** Lower proof discharge rate than AutoSpec+, but sufficient to test hypothesis.

### 2. Sequential Processing (vs Parallel)

**Decision:** Process programs one at a time.

**Rationale:**
- API rate limits (1 req/s)
- Easier debugging and checkpointing
- Small benchmark (10 programs) doesn't benefit from parallelization

### 3. Heuristic Dependency Extraction (vs Graph Analysis)

**Decision:** Use pattern matching for dependency extraction instead of full WP dependency graph parsing.

**Rationale:**
- Frama-C WP dependency graph is complex to parse
- Pattern-based heuristics (e.g., "loop invariant fails when precondition strengthened") are sufficient for PoC
- Full graph analysis deferred to post-PoC if H-E1 succeeds

---

## Validation Strategy

### Unit Tests

**Test Coverage:**
- LLMClient: Mock API responses, test prompt generation
- FramaCVerifier: Test parser with known Frama-C outputs
- FeedbackParser: Test extraction with synthetic failed VCs
- RefinementLoop: Test convergence logic with mock results

### Integration Tests

**End-to-End Test:**
1. Single program (simple binary search)
2. Expected: Converges in ≤5 iterations
3. Verify: All VCs proved, metrics logged correctly

### Validation Criteria (Phase 4)

**Code Validation:**
- All tests pass
- Preflight checks pass on target environment
- No hardcoded paths/keys

**Experiment Validation:**
- Mean discharge rate ≥50%
- At least 1 program shows iterative improvement
- All 4 plots generated successfully

---

**Architecture Version:** 1.0  
**Status:** Ready for Phase 4 Implementation  
**Next Step:** Phase 4 Coder implements modules following this specification
