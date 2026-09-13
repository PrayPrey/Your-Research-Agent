# Architecture: H-E1
# lean-auto Baseline Measurement on miniF2F

**Hypothesis ID**: h-e1  
**Type**: EXISTENCE (PoC)  
**Generated**: 2026-08-20  
**Author**: Architecture Agent

**Applied Pattern**: Python multiprocessing worker pool, subprocess timeout enforcement

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation (Lean 4 theorem proving harness)  
**Analyzed Path**: N/A  
**Findings**: No existing Lean evaluation code in repository. Archive contains unrelated Python test harness (HumanEval-style). New implementation required.

---

## System Overview

Parallel evaluation harness measuring lean-auto success rate on 244 miniF2F test problems with 300s timeout per problem.

**Components**:
- Problem Loader (parse Test.lean)
- Worker Pool (8 parallel processes)
- Timeout Handler (subprocess-level SIGTERM)
- Tactic Extractor (regex on trace logs)
- Result Aggregator (merge worker outputs)

**Data Flow**:
```
Test.lean → Loader → [Problem Queue] → Worker Pool (8x) → [Results] → Aggregator → CSV/JSON
                                              ↓
                                       Lean REPL (subprocess)
                                              ↓
                                       timeout/solved/error
```

---

## Module Specifications

### ProblemLoader (`src/loader.py`)

**Dependencies**: None

```python
class ProblemLoader:
    def __init__(self, test_file: str): ...
    def load_problems(self) -> list[dict]: ...
    def _parse_theorem(self, line: str) -> dict | None: ...
```

### WorkerPool (`src/worker.py`)

**Dependencies**: ProblemLoader, TimeoutHandler

```python
class Worker:
    def __init__(self, timeout: int = 300): ...
    def evaluate_problem(self, problem: dict) -> dict: ...
    def _create_lean_script(self, statement: str) -> str: ...

def run_worker_pool(problems: list[dict], n_workers: int = 8) -> list[dict]: ...
```

### TimeoutHandler (`src/timeout.py`)

**Dependencies**: None

```python
class TimeoutHandler:
    def __init__(self, timeout_sec: int): ...
    def run_subprocess(self, cmd: list[str], script: str) -> tuple[str, str, str]: ...
```

### TacticExtractor (`src/tactic_count.py`)

**Dependencies**: None

```python
class TacticExtractor:
    def extract_count(self, trace_log: str) -> int | None: ...
    def _count_atp_invocations(self, log: str) -> int: ...
```

### ResultAggregator (`src/aggregate.py`)

**Dependencies**: None

```python
class ResultAggregator:
    def merge_results(self, worker_outputs: list[list[dict]]) -> pd.DataFrame: ...
    def compute_metrics(self, df: pd.DataFrame) -> dict: ...
    def save_summary(self, metrics: dict, output_path: str): ...
```

### CheckpointManager (`src/checkpoint.py`)

**Dependencies**: None

```python
class CheckpointManager:
    def __init__(self, checkpoint_dir: str): ...
    def save(self, worker_id: int, results: list[dict]): ...
    def load(self, worker_id: int) -> list[dict]: ...
```

### Main Orchestrator (`src/main.py`)

**Dependencies**: All above modules

```python
def main(test_file: str, output_dir: str, n_workers: int = 8): ...
def run_pilot(n_problems: int = 20): ...
def run_full_evaluation(): ...
```

---

## Data Schemas

### Per-Problem Result

```json
{
  "problem_id": "test_001",
  "source": "AMC",
  "statement": "theorem test_001 : 2 + 2 = 4",
  "outcome": "solved",
  "wall_clock_time": 12.3,
  "tactic_count": 8,
  "proof_size": 156,
  "trace_log_path": "/logs/test_001_trace.txt"
}
```

### Checkpoint Format

```json
{
  "worker_id": 3,
  "problems_completed": 20,
  "timestamp": "2026-08-20T12:34:56Z",
  "results": [...]
}
```

### Final Summary

```json
{
  "hypothesis_id": "h-e1",
  "dataset": {"name": "miniF2F Test", "size": 244},
  "results": {
    "success_rate": 0.18,
    "ci_95": [0.14, 0.23],
    "solved_count": 44,
    "timeout_count": 195,
    "error_count": 5
  },
  "tactic_count": {
    "mean": 9.2,
    "median": 8.0,
    "std": 3.1,
    "range": [3, 18]
  },
  "execution": {
    "total_time_hours": 2.8,
    "mean_time_per_problem": 41.3
  }
}
```

---

## Technology Stack

**Core**:
- Python 3.10+ (multiprocessing, subprocess)
- Lean 4.15.0 (elan-managed)
- lean-auto (git@main, pinned SHA)
- miniF2F (google-deepmind fork, pinned SHA)

**Dependencies**:
- pandas (result aggregation)
- scipy (confidence intervals)
- Standard library: signal, subprocess, multiprocessing, json, re

**Infrastructure**:
- 64 CPU cores (8 workers × 8 cores)
- 128GB RAM (16GB per worker)
- 50GB disk (mathlib + logs)

---

## Deployment Considerations

### Resource Management

**Per-Worker Limits**:
- Memory: 16GB (mathlib can use 8-12GB)
- Timeout: 300s per problem + 10s grace
- Disk: 5GB for trace logs per worker

**Error Handling**:
- Infrastructure errors: Retry up to 3 times
- Type-check failures: Log as "error", continue
- OOM: Kill worker, restart with reduced parallelism

### Checkpointing Strategy

- Checkpoint every 10 problems per worker
- On crash: Resume from last checkpoint (skip completed problems)
- Total checkpoints: 8 workers × ~3 checkpoints = 24 files

### Reproducibility

**Version Pins**:
- Lean: 4.15.0 (exact, via elan)
- lean-auto: git SHA in setup script
- miniF2F: git SHA in setup script
- mathlib: version from miniF2F's lean-toolchain

**Artifacts**:
- Raw logs: compressed tar.gz (DVC/S3)
- Results CSV + summary.json: git-tracked
- Setup script with all git SHAs

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Infrastructure Setup | Install Lean 4.15.0, lean-auto, miniF2F, build mathlib | 12 | 3+4+3+2 |
| A-2 | Problem Loader | Parse Test.lean, extract 244 theorem statements | 6 | 2+2+2 |
| A-3 | Worker Pool | Multiprocessing pool with subprocess timeout | 14 | 4+4+3+3 |
| A-4 | Tactic Extractor | Parse trace logs for ATP invocation count | 8 | 3+2+3 |
| A-5 | Checkpoint System | Save/load worker progress every 10 problems | 9 | 3+3+3 |
| A-6 | Aggregator | Merge results, compute metrics, generate summary | 10 | 3+3+2+2 |
| A-7 | Pilot Run | Validate on N=20 problems | 7 | 2+2+3 |
| A-8 | Full Evaluation | Run on 244 problems, archive results | 11 | 3+4+4 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3], Medium(9-13): [A-1, A-6, A-8], Low(4-8): [A-2, A-4, A-5, A-7]

**Complexity Scoring**:
- Module_Size: lines of code (1-5)
- Dependencies: external/internal deps (1-5)
- Algorithm: trace parsing, timeout handling (1-5)
- Integration: multiprocessing coordination (1-5)

---

## Implementation Notes

### Critical Paths

**Path 1: Timeout Enforcement**
- OS-level subprocess timeout (not Lean internal)
- SIGTERM at 300s, SIGKILL at 310s
- Prevents runaway lean-auto processes

**Path 2: Tactic Count Extraction**
- Primary: Parse `[auto.native] Invoking` from trace logs
- Fallback: Count monomorphization steps if ATP logs missing
- Validate on pilot run (manual check 5 solved problems)

**Path 3: Worker Isolation**
- Each problem gets fresh Lean REPL subprocess
- Prevents cross-contamination (shared environment state)
- Memory leak mitigation (process exit cleans up)

### Known Risks

**Risk 1: High timeout rate (>80%)**
- Mitigation: Expected for 300s timeout, not a failure
- Baseline measurement, not optimization task

**Risk 2: Tactic count extraction unreliable**
- Mitigation: Validate on pilot, accept fallback proxy
- Affects H-C1 budget setting, but not H-E1 success

**Risk 3: Infrastructure errors (>5%)**
- Mitigation: Retry mechanism, robust error logging
- If >10% errors: STOP, debug before proceeding

---

## Success Criteria

**PoC Pass Conditions**:
1. All 244 problems evaluated (no missing data)
2. Error rate < 5% (< 12 problems)
3. Success rate in 10-25% range (gate condition)
4. Tactic count captured for ≥80% of solved problems

**Deliverables**:
- `results.csv` (244 rows, all outcomes)
- `summary.json` (aggregated metrics)
- `logs.tar.gz` (raw trace logs for debugging)
- Reproducibility README (git SHAs, setup script)

---

## File Structure

```
h-e1/
├── code/
│   ├── src/
│   │   ├── loader.py
│   │   ├── worker.py
│   │   ├── timeout.py
│   │   ├── tactic_count.py
│   │   ├── aggregate.py
│   │   ├── checkpoint.py
│   │   └── main.py
│   ├── setup.sh
│   └── requirements.txt
├── data/
│   ├── checkpoints/
│   ├── logs/
│   ├── results.csv
│   └── summary.json
└── docs/
    ├── 02c_experiment_brief.md
    ├── 03_architecture.md (this file)
    └── evaluation_protocol.md
```

---

*MCP Tools Used: Archon (Knowledge), Serena (Codebase Analysis)*  
*Pattern: Multiprocessing worker pool with subprocess timeout*  
*Next Phase: Phase 4 - Implementation*
