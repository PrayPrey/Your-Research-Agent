# Experimental Setup

We validate each system component through targeted experiments testing specific mechanistic claims. Experiments use proof-of-concept scale infrastructure with mock/simulated data to isolate mechanism feasibility from deployment complexity.

## Experimental Questions

1. **Q1 (h-e1):** Can load-time instrumentation track adoption with <10% overhead and ≥95% capture rate?
2. **Q2 (h-m1):** Do health metrics achieve ≥60% precision in identifying deprecation candidates?
3. **Q3 (h-m2):** Does context-aware inference achieve ≥70% accuracy on task-specific successors?
4. **Q4 (h-m3):** Can dependency graphs achieve ≥95% impact completeness for migration planning?
5. **Q5 (h-m4):** Does full telemetry stack maintain ≥95% capture with <10% overhead?

## Datasets and Baselines

**HuggingFace Datasets Hub Infrastructure:**
- **h-e1:** 100 benchmark dataset loads (MNIST, CIFAR-10, ImageNet subsets) to measure overhead
- **h-m1:** 1000-dataset simulation with synthetic health metrics (velocity, emergence, issue_ratio)
- **h-m2:** 50 synthetic validation cases with ground-truth task labels
- **h-m3:** Mock 4-node dependency graph (dataset → downstream models)
- **h-m4:** Integrated stack with 500 simulated user sessions

**Baselines:** No formal baselines exist (no prior dataset deprecation systems). Performance targets derived from software package manager requirements (NPM overhead benchmarks, PyPI deprecation warning thresholds).

**Mock Data Rationale:** Real HuggingFace API integration blocked by configuration errors and rate limits during PoC validation. Mock data isolates mechanism validation from external dependencies; generalization to real API data is future work.

## Evaluation Metrics

- **Overhead:** `(instrumented_time - baseline_time) / baseline_time × 100%`
- **Capture Rate:** `captured_events / total_events`
- **Precision:** `true_positives / (true_positives + false_positives)`
- **Recall:** `true_positives / (true_positives + false_negatives)`
- **Context Accuracy:** `correct_inferences / total_inferences`
- **Override Rate:** `user_overrides / total_recommendations`

Wilson confidence intervals (95% CI) computed for capture rate to validate statistical reliability.

## Experimental Protocol

Each sub-hypothesis follows gate protocol:
1. **Setup:** Load mock/simulated data matching experimental question
2. **Execution:** Run mechanism under test conditions
3. **Measurement:** Compute target metrics (overhead, precision, accuracy, etc.)
4. **Gate Check:** Pass if all metrics meet thresholds, otherwise FAIL

MUST_WORK gates (h-e1, h-m1, h-m2) are critical for system viability. SHOULD_WORK gates (h-m3, h-m4) validate supporting infrastructure but don't block Phase 6 progression.

## Reproducibility

Code, mock data generators, and evaluation scripts available at [repository TBD]. Simulated HuggingFace metadata uses patterns from literature (software package deprecation velocity distributions, GitHub issue accumulation rates). PoC scale chosen to validate mechanism feasibility; production validation requires deployment testing.
