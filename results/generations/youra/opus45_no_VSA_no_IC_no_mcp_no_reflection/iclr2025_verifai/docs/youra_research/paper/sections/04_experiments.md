# 4. Experiments

## 4.1 Existence Gate Experiment (h-e1)

We test the first causal mechanism step: do static analyzers produce actionable warnings on benchmark code?

**Setup:**
- Dataset: HumanEval (164 problems, full test set)
- Code source: Canonical solutions (proxy for LLM output due to API unavailability)
- Analyzer: pylint 3.x with `--disable=C,R`
- Gate threshold: ≥30% of problems with ≥1 warning

**Rationale for Proxy:** Without OpenAI/Claude API access, we used canonical solutions as a lower-bound proxy. Canonical solutions are well-written human code; LLM-generated code typically exhibits more issues.

## 4.2 Implementation

**Pipeline Components:**
1. `humaneval_loader.py` — Loads HumanEval problems from HuggingFace
2. `static_analyzer.py` — Runs pylint, parses JSON output, filters by severity
3. `metrics.py` — Aggregates warning counts, computes rates

**Pylint Configuration:**
```bash
pylint --output-format=json --disable=C,R <code_file>
```

Disabled categories:
- C (Convention): Style issues (naming, docstrings)
- R (Refactoring): Code smell suggestions

Retained categories:
- E (Error): Definite errors
- W (Warning): Potential problems

## 4.3 Artifacts

| Artifact | Description |
|----------|-------------|
| `metrics.json` | Aggregated warning statistics |
| `pylint_results.json` | Per-problem pylint output |
| `generations.json` | Code per problem |
| `warning_distribution.png` | Histogram of warnings per problem |
| `warning_type_breakdown.png` | Pie chart by category |
| `gate_metrics.png` | Threshold vs. actual comparison |
| `top_warning_codes.png` | Top 10 warning codes |
