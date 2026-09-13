# Configuration: H-C1 (Transfer Gate Eval)

**Type:** CONDITION (inference-only) | **Format:** Python Dataclass

Applied: lm-eval-harness-standard-evaluation-pattern (unified HFLM eval across model configs)
Applied: gate-comparison-pattern (max(baselines) + threshold, reused from H-M2)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m2, VALIDATED) — checkpoints referenced by path only, no code import
**Status**: No h-c1 code exists yet (green-field for this hypothesis's modules). H-M2 checkpoint directory layout verified via `h-m2/03_architecture.md` (`train_variants.py` saves to `h-m2/code/checkpoints/{variant}_*`); no `h-m2/code/` directory present yet to inspect directly, so paths follow documented module contract.
**Config Files Found**: None for h-c1 (new). H-M2's `code/config.py` (`ModelVariant`, `VARIANTS`, `EvalConfig`) referenced for gate threshold consistency only — not imported (H-C1 does no training).
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-m2/03_config.md (EvalConfig) — threshold reused, not imported (no training in H-C1)
# gate_threshold_pp: float = 0.02  <- H-M2 EvalConfig, same value reused here for consistency
```

**Verified from**: `h-m2/03_config.md` `EvalConfig.gate_threshold_pp=0.02` — H-C1 reimplements this single value locally (no code dependency) since H-C1 is inference-only and does not import H-M1/H-M2 training modules.

---

## Configuration (Python Dataclasses)

### Model Registry

```python
from dataclasses import dataclass, field


@dataclass
class ModelsConfig:
    checkpoints: dict[str, str] = field(default_factory=lambda: {
        "B1": "meta-llama/Meta-Llama-3-8B-Instruct",
        "B2": "../h-m2/code/checkpoints/b2_helpfulness_only",
        "B3": "../h-m2/code/checkpoints/b3_quality_only",
        "T1": "../h-m2/code/checkpoints/t1_alpha0.2_beta0.8",
        "T2": "../h-m2/code/checkpoints/t2_alpha0.4_beta0.6",
        "T3": "../h-m2/code/checkpoints/t3_alpha0.6_beta0.4",
        "T4": "../h-m2/code/checkpoints/t4_alpha0.8_beta0.2",
    })
    baselines: tuple[str, ...] = ("B1", "B2", "B3")
    treatments: tuple[str, ...] = ("T1", "T2", "T3", "T4")
```

### Evaluation Config

```python
@dataclass
class EvalConfig:
    tasks: tuple[str, ...] = ("truthfulqa_mc1", "truthfulqa_mc2", "bbq")
    batch_size: str = "auto:4"          # NFR-2, GPU memory adaptive
    seed: int = 42                      # NFR-1
    num_fewshot: int = 0                # deterministic, no sampling (NFR-1)
    device: str = "cuda:0"              # NFR-3, single GPU
    ifeval_results_path: str = "../h-m2/code/outputs/ifeval_results.json"
    results_out_path: str = "results/safety_results.json"
    correlation_out_path: str = "results/correlation_analysis.json"
```

### Gate Config

```python
@dataclass
class GateConfig:
    threshold_pp: float = 0.02          # ≥2pp gate (FR-4), matches H-M2 EvalConfig value
    primary_metrics: tuple[str, ...] = ("truthfulqa_mc1", "bbq")  # FR-4: OR condition
```

---

## Task Configs [0/0 subtasks — all Low complexity]

## E-1: Config registry [Complexity: 3]

**Applied**: Standard PyTorch/HF defaults

`ModelsConfig`, `EvalConfig`, `GateConfig` above go directly into `h-c1/code/config.py`.

## E-2: Checkpoint validation [Complexity: 5]

**Applied**: fail-fast pattern (standard)

No new config — reads `ModelsConfig.checkpoints`; validation loop tries `AutoModelForCausalLM.from_pretrained(path)` per entry before eval loop starts.

## E-3: TruthfulQA eval [Complexity: 8]

**Applied**: lm-eval-harness HFLM pattern

Uses `EvalConfig.tasks[:2]`, `batch_size`, `num_fewshot=0`, `seed=42`.

## E-4: BBQ eval [Complexity: 9]

**Applied**: lm-eval-harness HFLM pattern (extended)

Uses `EvalConfig.tasks[2]` ("bbq"). Non-standard: `batch_size="auto:4"` retained despite 58k examples — auto-adaptive sizing handles longer runtime without a separate override field.

## E-5: Sequential eval orchestration [Complexity: 7]

**Applied**: sequential-load memory-safe pattern (NFR-3)

Iterates `ModelsConfig.checkpoints`, writes `EvalConfig.results_out_path`.

## E-6: Gate computation [Complexity: 5]

**Applied**: gate-comparison-pattern (reused from H-M2)

Uses `GateConfig.threshold_pp=0.02` and `GateConfig.primary_metrics` against `ModelsConfig.baselines`/`treatments`.

## E-7: Transfer correlation [Complexity: 7]

**Applied**: scipy.stats.pearsonr (standard)

Reads `EvalConfig.ifeval_results_path`, writes `EvalConfig.correlation_out_path`. No new config fields.

## E-8: Validation report [Complexity: 6]

**Applied**: standard markdown report generation

Consumes outputs of E-6/E-7; no new config.

## E-9: Failure-path breakdown [Complexity: 5]

**Applied**: conditional analysis (only runs if `gate_passed=False`)

No new config.
