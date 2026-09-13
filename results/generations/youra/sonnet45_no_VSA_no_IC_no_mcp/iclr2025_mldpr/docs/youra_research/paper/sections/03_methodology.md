# Methodology

Our three-component system addresses distinct failure modes in current dataset deprecation practice: automated health metrics for candidate detection (failure mode 1), context-aware successor graphs for task-specific recommendations (failure mode 2), and load-time instrumentation for adoption tracking (failure mode 3). Each component targets a separate infrastructure gap; their synergistic integration enables formal deprecation mechanisms validated through five sub-hypothesis experiments.

## System Architecture

The system integrates three layers:

1. **Health Metrics Layer:** Computes deprecation signals from repository metadata (usage velocity, successor emergence, issue accumulation) without manual curator intervention

2. **Context-Aware Graph Layer:** Models task-conditional successor relationships (e.g., ImageNet → ImageNet-v2 for robustness vs ImageNet-21k for pretraining) inferred from dataset card citations and usage patterns

3. **Instrumentation Layer:** Wraps dataset loaders with SHA256-based content hashing and async telemetry queues to track adoption events with minimal overhead

Design rationale: Each component solves one failure mode independently but creates synergy through integration—health metrics surface candidates, context graphs personalize recommendations, instrumentation measures outcomes.

## Component 1: Automated Health Metrics

Health metrics adapt software package deprecation patterns (NPM, PyPI) to ML's usage-driven lifecycle. We compute weighted scores combining three signals:

- **Usage Velocity:** Download rate decline (velocity < 0.3 flags stagnation)
- **Successor Emergence:** Alternative dataset availability (emergence > 3 indicates replacements exist)
- **Issue Ratio:** Maintenance burden (high issue-to-download ratio signals abandonment)

**Weighted Score:** `score = 2.0 × velocity + 1.5 × emergence + 1.0 × issue_ratio`

Velocity weighted highest because declining usage is the strongest deprecation predictor; emergence captures successor availability; issue ratio indicates maintainer burden. Threshold ≥2.5 flags deprecation candidates.

**Design Decision:** Weighted scoring over binary rules provides tunable precision-recall tradeoff. Alternatives considered: uniform weights (lower precision), API-based metrics (blocked by integration complexity), maintainer-only annotations (doesn't scale to 60k+ datasets).

## Component 2: Context-Aware Successor Graphs

Successor graphs model task-conditional replacement paths rather than linear version succession. Edges represent deprecation relationships labeled by task context (e.g., `ImageNet --[robustness_eval]--> ImageNet-v2`, `ImageNet --[pretraining]--> ImageNet-21k`).

**Context Inference:** Pattern-based matching on Python import history and dataset card citations:
- Exact match: `from datasets import load_dataset("squad")` → task="question_answering"
- Substring: `"robustness"` in notebook → task="robustness_eval"
- Semantic similarity: Dataset card keywords match known task taxonomies

**Graph Construction:** NetworkX DiGraph with datasets as nodes, successor edges inferred from dataset card citations ("`recommended_successor: dataset_name`" fields). Users can override inferred context via explicit task parameter.

**Design Decision:** Pattern-based inference enables validation on synthetic data; defer embedding-based inference (LLMs) to production testing. Alternatives: manual annotation (doesn't scale), usage co-occurrence (requires longitudinal data unavailable at PoC scale).

## Component 3: Load-Time Instrumentation

Decorator-based wrapper for `datasets.load_dataset()` adds SHA256 content hashing and async telemetry logging:

```python
@instrumented_loader
def load_dataset(name, *args, **kwargs):
    # 1. Compute SHA256 hash (lazy caching)
    content_hash = compute_hash(name)
    # 2. Check deprecation status via health metrics
    if is_deprecated(name):
        successor = get_context_aware_successor(name, infer_context())
        warn(f"{name} deprecated. Recommended: {successor}")
    # 3. Log event to async queue (non-blocking)
    telemetry_queue.put({
        "dataset": name,
        "hash": content_hash,
        "successor_shown": successor,
        "timestamp": now()
    })
    # 4. Proceed with normal load
    return original_load_dataset(name, *args, **kwargs)
```

**Overhead Mitigation:** SHA256 hashing amortized via lazy evaluation (compute once, cache result); async queue writes prevent blocking I/O.

**Design Decision:** Decorator pattern enables drop-in replacement without API changes. Alternatives: monkey-patching (fragile), separate CLI tool (adoption barrier), server-side tracking (privacy concerns mitigated via client-side hashing with no user PII).

## Sub-Hypothesis Decomposition

We validate mechanisms through five sub-hypotheses with gate protocols:

- **h-e1 (MUST_WORK):** Instrumentation overhead <10%, capture rate ≥95%
- **h-m1 (MUST_WORK):** Health metrics precision ≥60%, recall ≥80%
- **h-m2 (MUST_WORK):** Context inference accuracy ≥70%, override rate <50%
- **h-m3 (SHOULD_WORK):** Dependency graph impact completeness ≥95%
- **h-m4 (SHOULD_WORK):** Full-stack telemetry capture ≥95%, overhead <10%

Gate categories (MUST_WORK vs SHOULD_WORK) prioritize critical components (detection, recommendation, measurement) over supporting infrastructure (dependency analysis).

## Implementation Scope

Proof-of-concept validation uses:
- **Mock data (h-m2, h-m3, h-m4):** Isolates mechanism validation from external dependencies
- **Simulated HuggingFace metadata (h-m1):** 1000-dataset corpus with synthetic health signals
- **PoC scale (h-e1):** 100 dataset loads to validate overhead/capture feasibility

Real HuggingFace API integration and production-scale testing are future work. Mock data enables controlled mechanism validation; generalization requires deployment testing.
