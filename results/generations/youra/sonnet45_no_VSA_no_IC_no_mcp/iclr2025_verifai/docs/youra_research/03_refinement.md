# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-25T07:30:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Independent-Controller Ablation)
- **Gap ID**: Gap 1
- **Gap Title**: Systematic Benchmark Coverage Taxonomy for Hypothesis Feasibility Assessment
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 10

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 10

**Convergence Reason**: All 6 personas participated; core claim established (syntax validity scoring in beam search); mechanism explained (4-step causal chain); testable predictions defined (P1: ≤40% syntax errors, P2: type errors not +5pp, P3: pass@1 maintained); novelty articulated (validity scoring dimension vs hard constraints or soft penalties); feasibility verified (Variant A computationally feasible ~2-4 hours); major criticisms addressed (α/β tuning via PoC grid search, beam width ablation, Variant B deferred)

### Key Insights

**From h-m1 Failure Analysis:**
- Syntax errors (64-68%) dominate CodeLlama-7B HumanEval failures vs type errors (20%)
- Soft logit penalties (-2.0) are too weak for meaningful constraint enforcement
- Targeting the wrong failure mode (type instead of syntax) leads to performance degradation
- Small-scale PoC gates prevent expensive full-run failures

**From Discussion:**
- Beam search allows exploration of multiple candidate paths (vs greedy sampling's committed single path)
- Validity scoring as a dimension (not hard constraint) balances correctness with generation fluency
- AST parsing is fast enough (~10-50ms per check) for real-time beam validation
- 5-problem PoC gate with α/β grid search validates hyperparameters before expensive full run

### Breakthrough Moments

1. **Dr. Nova's Reframing (Exchange 7):** Shifted from greedy sampling + penalty (h-m1's failed approach) to beam search with validity scoring as a separate dimension. This eliminated the "soft penalty magnitude debate" entirely by changing the generation strategy.

2. **Prof. Pax's Variant Distinction (Exchange 9):** Separated Variant A (simple parse-check validity) from Variant B (benchmark-derived learned features), clarifying that Variant A is immediately feasible while Variant B is a future enhancement.

3. **Prof. Vera's Experimental Design (Exchange 8):** Locked down precise testable predictions (≤40% syntax errors, ±5pp type errors, -2pp pass@1) with clear falsification conditions, ensuring rigorous experimental validation.

---

## Final Hypothesis

### Title
Syntax-Aware Beam Search with Validity Scoring for Code Generation

### Hypothesis ID
H-SyntaxBeam-v1

### Core Claim

Under code generation tasks on HumanEval benchmark with CodeLlama-7B, **if** we apply beam search (k=5) with combined scoring:

```
final_score = α * log_likelihood + β * syntax_validity_score
where α=0.7, β=0.3, and syntax_validity_score = 1 if ast.parse() succeeds else 0
```

**Then** syntax error rate will drop from 64-68% baseline to ≤40% (≥40% relative reduction),

**Because** beam search explores multiple candidate paths and validity scoring prunes syntactically invalid beams, preventing the model from committing to invalid paths early (which greedy sampling cannot recover from).

### Mechanism

**Four-Step Causal Chain:**

1. **Beam Exploration:** Beam search maintains k=5 candidate sequences instead of committing to a single path (greedy sampling limitation)
   - Falsifier: If beam search with α=1.0, β=0.0 (no validity scoring) does not outperform greedy, beam exploration alone is insufficient

2. **Combined Scoring:** At each generation step, each beam candidate scored by α * log_likelihood + β * syntax_validity_score
   - Falsifier: If validity_score computation introduces >100ms latency per beam step, computational cost becomes prohibitive

3. **Beam Pruning:** Syntactically invalid beams (validity_score=0) receive lower scores and are pruned over time
   - Falsifier: If valid beams consistently receive lower log_likelihood than invalid beams, β=0.3 weight is insufficient

4. **Validated Selection:** Final output selected from top-scoring beam, validated for syntax throughout generation
   - Falsifier: If top-scoring beam at completion still has syntax errors, validity scoring doesn't guarantee final validity

---

## Predictions

### P1: Syntax Error Reduction (PRIMARY)

**Statement:** Beam search (k=5) with α=0.7, β=0.3 scoring reduces syntax error rate from 64-68% baseline to ≤40% on HumanEval-164

**Test Method:** Generate code samples for all 164 HumanEval problems; parse each with ast.parse(); compute syntax error rate = (failed parses / total samples) × 100%

**Success Criterion:** Syntax error rate ≤40% (≥40% relative reduction)

**Falsification:** Syntax error rate >50% (less than 25% reduction is insufficient)

### P2: No Compensatory Type Error Increase

**Statement:** Type error rate does not increase by >5 percentage points compared to baseline

**Test Method:** Run Mypy type checker on all generated samples (reusing h-m1's evaluation pipeline); compute type error rate

**Success Criterion:** Type error rate ≤ baseline + 5pp

**Falsification:** Type error rate > baseline + 5pp indicates compensatory failure

### P3: Generation Quality Maintained

**Statement:** Pass@1 metric (correctness) is maintained within -2pp of baseline

**Test Method:** Execute generated code against HumanEval test cases; compute pass@1 = (problems with ≥1 correct sample / 164 total) × 100%

**Success Criterion:** Pass@1 ≥ baseline - 2pp

**Falsification:** Pass@1 < baseline - 5pp indicates unacceptable quality sacrifice

---

## Novelty

### Key Innovation

**Syntax validity as a beam search scoring dimension** for code generation — not a hard constraint (which blocks valid incomplete expressions) or soft penalty (which h-m1 showed is too weak), but an explicit scoring component that balances correctness with fluency.

### Differentiation from Prior Work

| Prior Work | Difference |
|------------|------------|
| **h-m1 (Type-Constrained Decoding)** | h-m1 targeted minority failure mode (type errors 20%) with soft logit penalties (-2.0) on greedy sampling. This work targets majority failure mode (syntax errors 64-68%) with beam search validity scoring. |
| **NeuroLogic Decoding, GeLM** | Prior constrained decoding focuses on semantic constraints or grammar-based generation. This work uses syntax validity (AST parse success) as lightweight scoring, not hard grammar constraints. |
| **SYNCHROMESH** | SYNCHROMESH uses formal grammars to guarantee syntax validity (hard constraint). This work uses validity scoring in beam search (soft guidance), allowing model likelihood to influence generation. |

### Impact Tier

**Medium-High** — Solid contribution addressing real problem (64-68% syntax errors) with principled approach. Not groundbreaking (beam search is standard), but generalizable pattern (validity scoring for structured output). Workshop/EMNLP Findings level.

---

## Experimental Design

### 5-Problem PoC Gate (Following h-m1's Lesson)

**Before Full HumanEval-164 Run:**

1. Select 5 representative problems:
   - Nested loops
   - List comprehensions
   - Recursion
   - Conditional logic
   - String manipulation

2. Test α/β combinations:
   - (0.5, 0.5)
   - (0.6, 0.4)
   - (0.7, 0.3)
   - (0.8, 0.2)

3. **Gate Success Criterion:** ≥1 α/β combination achieves <45% syntax error rate on 5-problem subset

4. **If Gate Fails:** STOP (like h-m1's CUDA OOM gate prevented expensive full run)

### Full HumanEval-164 Run (If Gate Passes)

**Configuration:**
- Model: CodeLlama-7B (same as h-m1 baseline)
- Benchmark: HumanEval-164 (same as h-m1 baseline)
- Beam width: k=5 (standard configuration)
- Scoring weights: Optimal α/β from PoC gate
- Temperature: 0.8
- Max tokens: 512

**Ablation Study:**
- Beam width k: Test k=3, 5, 10 to validate k=5 choice

**Baselines:**
- Greedy sampling (temperature=0.8) — syntax error rate 64-68%
- h-m1 type-constrained decoding (penalty_weight=-2.0) — syntax error rate 88% (WORSE)

---

## Limitations

### Known Limitations

1. **Variant A Simplicity:** Simple parse-check validity does not capture nuanced syntax correctness (semantically weird but syntactically valid code like `return None + None` scores high)

2. **Beam Width k=5 Arbitrary:** Standard choice but not empirically validated for this task (ablation study needed)

3. **α/β Hyperparameter Tuning:** Grid search over 4 combinations may not find global optimum (systematic but limited)

4. **Computational Cost:** ~2-4 hours for HumanEval-164 (5× slower than greedy sampling)

### Scope Boundaries

**Applies To:**
- Code generation tasks with well-defined syntax (Python, languages with AST parsers)
- Benchmarks where syntax errors are dominant (≥50% of failures)
- Small-to-medium models (7B parameters) where syntax guidance provides value

**Does NOT Apply To:**
- Semantic correctness (validity scoring only checks syntax, not logic)
- Large models (GPT-4, Claude) where base syntax accuracy is already high (>90%)
- Real-time applications where 2-4 hour generation time is prohibitive

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 personas participated; core claim, mechanism, predictions, novelty, feasibility established; criticisms addressed |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (PoC gate addresses α/β tuning, beam width, Variant A/B tradeoff) |

---

## Open Questions for Phase 2B+

1. What is the optimal α/β balance? (5-problem PoC grid search will answer)
2. What is the optimal beam width k? (Ablation study k=3,5,10 will answer)
3. Does Variant B (learned validity features) improve over Variant A (simple parse-check)?
4. Can this approach generalize to other code generation benchmarks (MBPP, CodeContests)?
5. Can this approach generalize to other structured output tasks (semantic parsing, SQL generation)?

---

*Phase 2A Complete — Ready for Phase 2B (Research Planning)*
