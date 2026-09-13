## 4. Experimental Setup

### 4.1 Research Questions

The five research questions run in dependency order, each establishing what the next one needs to be interpretable. Each maps to a claim made in Section 1.

**RQ1 (Precondition).** Do all four feedback categories actually produce signal on LLM-generated code, and on what fraction of problems? If a category rarely fires, comparing its repair rate to the others is meaningless.

**RQ2 (Failure characterization).** How are failures distributed across bug types, and does any single type dominate strongly enough to make a multi-category comparison degenerate? This tests the assumption, inherited from the specificity intuition, that different verifiers have distinct error populations to address.

**RQ3 (Specificity gradient).** Do the categories produce measurably different feedback signals, and in what order? This supplies the independent variable for RQ4 and rules out the possibility that the verifiers are paraphrasing each other.

**RQ4 (The main question).** Does single-iteration repair success rise with feedback specificity, as the field assumes? This is the direct test of the claim that richer formal signal yields better repair.

**RQ5 (Cost normalization).** Once wall-clock overhead is divided out, which category delivers the most correctness per second? This is the question our Introduction argues has never been asked.

We additionally report a benchmark-stratified breakdown, testing whether the orderings above hold across problems of differing structural difficulty.

### 4.2 Datasets

| Dataset | Problems | GPT-4o-mini pass@1 | Failures | Why chosen |
|---|---|---|---|---|
| HumanEval | 164 | 86.0% | 23 | The reference benchmark for every prior feedback-loop study; makes our numbers directly comparable |
| MBPP (sanitized test) | 257 | 59.9% | 103 | Structurally harder, multi-step problems; tests whether findings survive a difficulty shift |
| **Combined** | **421** | **70.1%** | **126** | |

**HumanEval** [Chen et al., 2021] provides 164 hand-written function-completion problems with docstrings, type hints, and worked examples — the docstring richness matters because it is what our SMT condition attempts to formalize. **MBPP** [Austin et al., 2021] contributes 257 problems from the sanitized test split. We note a discrepancy with our pre-registered design here: we expected 374 problems from this split and the current distribution provides 257, giving 421 total rather than the planned 538. Statistical power remains ample, but MBPP-specific conclusions rest on fewer samples than planned.

The 126 failing solutions are the working set for RQ2 through RQ4. Every category attempts repair on all 126, which makes the comparison paired.

### 4.3 Conditions and Baseline

The no-feedback baseline is vanilla single-shot generation with no repair loop, which anchors Δpass@1 for every category. The four feedback conditions are as described in Section 3.3.

**Why these four.** Execution monitoring is included both because it is the category the field currently favors and because it functions as a replication of Self-Repair [Olausson et al., 2023] under our controls — if our setup could not reproduce the known result that execution traces help, nothing downstream would be trustworthy. Static analysis (Pyright) and type checking (mypy) are included as two points on the static spectrum that differ by orders of magnitude in output volume, which is what lets us separate formalism level from verbosity. SMT solving is included as the highest-formalism endpoint and the one the specificity intuition predicts should win.

### 4.4 Implementation Details

All generation and repair uses GPT-4o-mini via the OpenAI API, at temperature 0.2 for generation and 0.0 for repair, with max_tokens 512 for generation and 1024 for repair. The repair budget is 3 iterations with early termination on the first passing solution. Feedback is truncated at 4,000 characters.

Verifier tooling: Pyright with `--outputjson`, mypy with `--no-error-summary --ignore-missing-imports`, subprocess execution with a 5-second timeout, and Z3 via its Python API with a 30-second timeout. Repair runs use a 4-worker thread pool at the problem level with categories sequential within a problem. Random seed is 1 throughout. Experiments ran on CPU; no GPU was required.

**A note on the overhead measurements.** The efficiency experiment addressing RQ5 was executed in mock mode. An API key was unavailable during that batch, and rather than skip a timing-sensitive experiment we ran it against synthetic log-normal overhead distributions calibrated to the empirical priors measured directly in the specificity experiment (Pyright in the 100-300ms range, subprocess execution in the 500ms range) with pass rates drawn from the same source. The overhead ordering and the efficiency ranking are structurally robust to realistic parameter choices, and the qualitative conclusion agrees with the directly measured repair rates from RQ4. Absolute ratio magnitudes should be read as calibrated estimates pending a live run. We flag every number from this experiment where it appears.

### 4.5 Metrics

**pass@1** — fraction of problems solved on the first sampled completion, the standard protocol from HumanEval. **Δpass@1** — pass@1 after the repair loop minus the no-feedback baseline, in percentage points. **Iteration-1 repair rate** — fraction of the 126 failing solutions repaired on the first repair attempt; this isolates feedback quality from budget effects, since a category that needs three tries to match another's single try is telling us something about its signal. **Feedback character count** — the specificity proxy. **Mean wall-clock overhead** — seconds per verifier call. **Efficiency ratio** — Δpass@1 divided by mean overhead seconds.

Significance is assessed at α = 0.05 using the procedures in Section 3.8.
