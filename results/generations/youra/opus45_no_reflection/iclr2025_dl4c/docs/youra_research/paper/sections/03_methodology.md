# Methodology

## Fidelity and Richness: An Orthogonal Framework

We decompose feedback quality into two independent dimensions:

**Signal Fidelity**: The probability that feedback is factually correct. Execution feedback achieves near-perfect fidelity—test pass/fail is deterministic ground truth. AI feedback has low fidelity; Self-Refine analysis shows ~39% correctness (100% minus 61% wrong fix rate).

**Semantic Richness**: The amount of explanatory content about *why* code is wrong. Execution feedback has minimal richness—"test failed" provides no explanation. AI feedback is maximally rich, describing algorithmic errors, variable misuse, and design flaws.

Prior work implicitly assumes a trade-off: choose high fidelity (execution) or high richness (AI). We observe these dimensions are orthogonal. A method can achieve high fidelity *and* high richness if we filter rich signals through a fidelity check.

## EVAF: Execution-Verified AI Feedback

EVAF treats execution as a verification layer for AI feedback. The mechanism operates in four steps:

**Step 1: AI Critique Generation.** Given a problem description $p$ and failing baseline code $c_{\text{fail}}$, an AI feedback model generates a critique and proposed fix:

$$\text{critique}, c_{\text{fix}} = \text{FeedbackModel}(p, c_{\text{fail}})$$

The critique explains what is wrong; $c_{\text{fix}}$ is the suggested correction.

**Step 2: Code Extraction.** The proposed fix is extracted from the AI response. We parse fenced code blocks (```python ... ```) to isolate executable code. If no valid code block exists, the suggestion is marked "no code extracted" and rejected.

**Step 3: Execution Gating.** The extracted fix is executed against the problem's unit tests in a sandboxed environment:

$$\text{result} = \text{ExecuteTests}(c_{\text{fix}}, \text{tests}_p)$$

Execution uses subprocess isolation with a 3.0-second timeout per test, preventing infinite loops and resource exhaustion.

**Step 4: Accept/Reject Decision.** If all tests pass, the AI suggestion is accepted:

$$
\text{accepted} = \begin{cases} 
\text{True} & \text{if result.all\_passed} \\
\text{False} & \text{otherwise}
\end{cases}
$$

Accepted suggestions constitute verified feedback: semantically rich (from AI) and correct (verified by execution).

## Accept Rate as Viability Indicator

The **accept rate**—fraction of AI suggestions passing verification—determines EVAF viability:

- **Accept rate < 10%**: Nearly all AI suggestions are wrong. EVAF degenerates to pure execution feedback with massive computational overhead.
- **Accept rate 20-60%**: AI provides substantive correct feedback. EVAF achieves meaningful filtering.
- **Accept rate > 90%**: AI is nearly always correct. Execution gating adds little value beyond direct AI feedback.

Our experiment targets demonstrating accept rate in the 20-60% range as a proof-of-concept.

## Implementation Architecture

We implement EVAF as seven Python modules:

**config.py**: Fixed configuration constants (model IDs, temperature, timeout, random seed). No runtime configuration—inference-only existence test.

**data.py**: Loads HumanEval via HuggingFace datasets. Extracts task ID, prompt, entry point, test code, and canonical solution for each of 164 problems.

**model.py**: Wraps two models:
- `BaselineModel`: CodeT5-770M (Salesforce/codet5-large), 770M parameter encoder-decoder for code generation.
- `FeedbackModel`: CodeLlama-7b-Instruct (codellama/CodeLlama-7b-Instruct-hf), 7B parameter decoder-only LLM for critique generation.

**gating.py**: Implements execution verification:
- `extract_code_from_response()`: Parses fenced code blocks from AI output.
- `run_unit_tests()`: Subprocess execution with timeout, returns pass/fail status and error messages.
- `evaf_gate()`: Orchestrates critique generation and verification.

**metrics.py**: Computes evaluation metrics:
- Accept rate: accepted / total suggestions
- Coverage: problems with extractable code / total problems
- Rejection breakdown: distribution of rejection reasons (no code, tests failed, timeout)

**visualize.py**: Generates three figures:
- Gate metrics bar chart with 20-60% target zone
- Accept rate histogram across problems
- Rejection reason pie chart

**train.py**: Pipeline orchestration:
1. Load HumanEval
2. Generate baseline code for all problems
3. Filter to problems where baseline fails
4. Run EVAF gating on each failing problem
5. Compute metrics and generate figures
6. Save results to JSON

## Experimental Design

This experiment is an **existence proof-of-concept**, not a comparative study. We aim to demonstrate:

1. EVAF is implementable with existing components
2. Accept rate falls in the viable 20-60% range

No training occurs. The pipeline runs inference only: baseline generation followed by EVAF gating. Success is defined by achieving measurable accept rate in the target range.

**Gate Condition (MUST_WORK)**: If accept rate falls outside 20-60%, the mechanism is not viable and subsequent hypothesis testing (comparative performance vs. baselines) should not proceed.
