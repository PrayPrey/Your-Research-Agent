# Phase 2A Research Discussion Log

**Gap ID:** Gap-1
**Gap Title:** Static Analysis Feedback Formatting for LLM Consumption
**Date:** 2026-08-28
**Architecture:** Self-Play Tikitaka (Independent Controller Ablation)

---

## Briefing Context

**Research Question:** How to structure static analysis errors (type errors, undefined variables, unreachable code) as natural language feedback that maximizes LLM repair success rate?

**Current State:** Existing work (CompCoder, compiler feedback papers) uses raw compiler output or minimal formatting. No systematic study on optimal error message representation for LLM self-repair.

**Key Evidence:**
- Self-repair yields +4.9% improvement minimum across models
- CompCoder: 44% → 89% compilation success with compiler feedback
- Syntactic/runtime errors more tractable than logical failures
- Type-aware generation (TyFlow) shows type checker integration feasibility

**Reference Papers:**
- [P1] "COMPILER GENERATED FEEDBACK FOR LLMs" (2024) - arXiv:2403.14714
- [P2] "InspectCoder: Dynamic Analysis-Enabled Self Repair" (2025) - arXiv:2510.18327
- [P3] "How Many Tries Does It Take?" (2025) - arXiv:2604.10508

**GitHub Resources:**
- theoxo/self-repair (ICLR 2024 experiments)
- evalplus/evalplus (HumanEval+/MBPP+ evaluation)

**Feasibility Constraints:**
- No new benchmarks/rubrics
- No synthetic/generated data
- No human evaluation
- Must use existing datasets (HumanEval, MBPP, HumanEval+, MBPP+)

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we approach this from an entirely different angle? Everyone's been feeding raw compiler errors to LLMs like they're talking to another compiler. But LLMs aren't compilers — they're language models trained on human-written text!

Here's my wild idea: **Error Message Translation Hypothesis**. Instead of "TypeError: unsupported operand type(s) for +: 'int' and 'str'" we could transform it to "You're trying to add a number and text together on line 7. The variable 'count' is an integer but 'name' is a string. Consider converting one to match the other."

But wait — what if we go even further? What if the format that works best isn't prose at all, but **structured templates** that mirror how developers naturally debug? Something like:
```
PROBLEM: Type mismatch in arithmetic operation
LOCATION: line 7, column 15
CONTEXT: count + name
ROOT CAUSE: 'count' is int, 'name' is str
COMMON FIXES: str(count) OR int(name) if numeric
```

The key insight from the compiler feedback paper (2403.14714) is that they used compiler output as a *training signal* — but what about *inference-time formatting*? That's unexplored territory!

Cross-domain connection: In human-computer interaction, error messages that provide *actionable next steps* dramatically improve user success rates. Can we apply this to LLM self-repair?

**Key Points:**
- Raw compiler errors may be suboptimal for LLM consumption
- Structured templates vs natural language prose as competing formats
- Actionable feedback (with fix suggestions) may outperform diagnostic-only feedback
- Inference-time formatting is distinct from training-time signals

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises an intriguing hypothesis, but let me stress-test it with scientific rigor. The core claim needs precise operationalization before we can test it.

What exactly do we mean by "optimal" formatting? We need measurable success criteria:
1. **pass@1 improvement** on HumanEval/MBPP
2. **Repair success rate** (errors fixed / errors encountered)
3. **Iteration efficiency** (fixes achieved per repair attempt)

Here's what would disprove the hypothesis: If structured templates perform **no better than raw compiler output** across multiple model scales, then formatting doesn't matter — the information content is what matters, not its presentation.

The confounds we must control:
- **Information content parity**: Each format must contain identical diagnostic information
- **Model scale**: Test on 7B, 13B, 70B+ to see if formatting benefits vary
- **Error type stratification**: Separate syntax, type, and semantic errors

From the "How Many Tries" paper (2604.10508), we know iteration count varies with model scale. This suggests our experiment needs:
- Matched error sets across format conditions
- Same model, same temperature, same prompts except format
- Statistical power analysis: How many errors do we need per condition?

A testable prediction: If structured templates work because they provide *cognitive scaffolding* similar to developer mental models, then the benefit should be **larger for harder errors** (type > syntax).

**Key Points:**
- Success criterion: pass@1 improvement AND repair success rate
- Critical confound: Information content must be identical across formats
- Falsification: No improvement over raw output means formatting is irrelevant
- Prediction: Format benefits should be larger for complex error types

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Let's step back and ask: what makes this genuinely new versus incremental?

The compiler feedback literature (CompCoder, CodeRL) focuses on *whether* to include compiler feedback — but nobody has systematically studied *how* to format it. That's the gap. Dr. Nova's "Error Message Translation" hypothesis fills a real void.

But here's what would make this a genuine contribution versus a minor tweak:
1. **Generalizable principles**: Not just "template X works" but "WHY does it work?" — what properties of feedback formatting drive repair success?
2. **Model-agnostic findings**: If the optimal format is the same for GPT-4 and CodeLlama-7B, that's far more impactful than model-specific tuning
3. **Practical adoption**: Can developers actually use these findings? A 2% improvement that requires fine-tuning is less valuable than a 1% improvement from prompt engineering alone

The field impact question: HumanEval is saturating (99.4% for best models). But the self-repair setting is different — we're testing repair capability, not raw generation. This matters because:
- Repair is where LLMs still struggle (per InspectCoder findings)
- Format optimization could be the "low-hanging fruit" that's been ignored

What new research directions does this open? If format matters, then:
- Can we learn optimal formats automatically?
- Does format interact with repair strategy (single-shot vs iterative)?
- Are there language-specific (Python vs TypeScript) format preferences?

**Key Points:**
- Novelty: HOW to format is unstudied; WHETHER to include feedback is established
- Contribution must be generalizable principles, not just "template X works"
- Field impact: Repair capability is where improvement potential remains
- Opens question: Can optimal formats be learned or are they universal?

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me ground this in technical reality. The hypothesis is: *structured error formatting improves LLM repair success over raw compiler output*.

**Is this mechanism scientifically sound?**
Yes. LLMs are trained on human-written text. Compiler errors are written for human consumption but with terse, technical formatting. There's a plausible *representational mismatch* between compiler output format and LLM training distribution. Transforming errors toward natural language brings them closer to training distribution.

**Are the measurements theoretically valid?**
Yes. pass@1 and repair success rate are established metrics. We can use HumanEval+/MBPP+ from EvalPlus for rigorous testing with 80x more test cases.

**Fundamental barriers (not budgetary)?**
1. **Information loss risk**: If "translation" loses critical information (exact line numbers, precise type names), repair may actually degrade
2. **Format-error interaction**: The optimal format might differ by error type — one-size-fits-all may not exist
3. **Prompt length limits**: More verbose formats eat context window

**Can interventions work in principle?**
Yes. The theoxo/self-repair codebase already implements the iterative refinement loop. We only need to modify the *error injection step* — this is a clean intervention with no architectural changes.

**Theoretical validity check:**
The "actionable feedback" hypothesis (from HCI research) predicts that including *fix suggestions* should help. But LLMs might generate worse fixes if they blindly follow suggestions rather than reasoning from diagnostics. We need both conditions: with and without fix hints.

**Key Points:**
- Mechanism is sound: representational mismatch between compiler output and LLM training
- Measurements valid: pass@1, repair rate on HumanEval+/MBPP+
- Key barrier: Information loss during format transformation
- Must test: With vs without fix suggestions to isolate their effect

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Building on the excellent foundation from all perspectives, let me synthesize and strengthen the emerging hypothesis.

**Core Refinement:** The hypothesis shouldn't just be "formatting matters" — it should specify the *mechanism* by which formatting helps. Based on the discussion:

**Refined Hypothesis:** Structured error feedback that (1) preserves all diagnostic information, (2) separates problem identification from fix suggestions, and (3) uses natural language descriptions alongside technical details improves LLM self-repair success because it reduces the representational gap between compiler output and the LLM's training distribution while maintaining information fidelity.

**Addressing Prof. Vera's concerns:**
- Information parity: We can create format pairs where one is raw and one is structured, with identical information content verified by reconstruction tests
- Model scale: Test on CodeLlama-7B, 13B, and GPT-4 class models
- Error stratification: Separate syntax, type, undefined variable, and unreachable code

**Strengthening with evidence:**
- CompCoder's 44% → 89% improvement shows compiler feedback works; the question is optimization
- TyFlow's type-guided synthesis validates that type information specifically aids generation
- "How Many Tries" shows smaller models need more iterations — structured feedback might reduce iteration count

**Concrete experimental design:**
1. **Baseline**: Raw compiler/linter output
2. **Treatment 1**: Structured template (PROBLEM/LOCATION/CONTEXT/ROOT CAUSE)
3. **Treatment 2**: Natural language prose
4. **Treatment 3**: Template + fix suggestions
5. **Evaluation**: pass@1 improvement, repair success rate, iteration count

**Key Points:**
- Hypothesis refined: Format reduces representational gap while preserving information
- Information parity can be verified empirically
- Four conditions isolate format type and fix suggestion effects
- Predictions: Template > Raw, Fix suggestions may help or hurt depending on error type

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Let me identify where this breaks down so we can fix it.

**Flaw 1: Benchmark appropriateness**
HumanEval and MBPP are *code generation* benchmarks, not *code repair* benchmarks. We need to induce errors first. How? If we use model-generated errors, we're testing repair of model-typical failures. If we use synthetic error injection, we might test unrealistic error patterns. This isn't fatal, but the error source must be specified.

**Flaw 2: Confounding with prompt length**
Structured templates and natural language are longer than raw compiler output. If LLMs simply perform better with more context about the error (regardless of format), we'd falsely attribute improvement to format. Solution: Include a "verbose raw" baseline — same information, unstructured, same length.

**Flaw 3: What counts as "fix suggestions"?**
"Consider converting one to match the other" vs "use str(count)" are very different levels of specificity. The hypothesis needs to operationalize this dimension.

**Flaw 4: Interaction with error complexity**
Prof. Vera predicted format benefits should be larger for harder errors. But what if it's the opposite? Simple errors might benefit more because the LLM already "knows" how to fix them and just needs clear signaling. We can't assume the direction.

**What would convince me:**
1. A 2x2 design: Format (Raw vs Structured) × Fix Hints (Present vs Absent)
2. Error type stratification showing consistent benefits OR well-explained interactions
3. Results robust across at least 2 model families (open-source and API)
4. Statistical significance with appropriate corrections for multiple comparisons

**Key Points:**
- Must specify error source: model-generated vs injected
- Need "verbose raw" baseline to control for length confound
- Fix suggestions must be operationalized with specificity levels
- Cannot assume direction of format × complexity interaction

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's challenges are exactly what we need! Let me address them with novel solutions.

**Error source innovation:** What if we use a *hybrid approach*? Take HumanEval+/MBPP+ test failures from model generation attempts — these are real errors the model made. Then categorize them by type (syntax, type, semantic). This gives us ecologically valid errors while maintaining benchmark compatibility.

**The verbose-raw baseline is brilliant.** But here's an additional twist: what about a *scrambled structured* condition? Same information, same length as structured template, but with sections randomly ordered. If structure itself (not just verbosity) matters, scrambled should underperform structured.

**Operationalizing fix suggestions:**
- Level 0: No fix (diagnostic only)
- Level 1: General strategy ("convert types to match")
- Level 2: Specific pattern ("use str(x) or int(y)")
- Level 3: Exact fix ("str(count)")

Now we can test whether specificity helps or creates dependency!

**Cross-domain insight:** In programming education research, "worked examples" with faded scaffolding outperform both no hints and full solutions. Maybe Level 1-2 outperforms both Level 0 and Level 3?

**Key Points:**
- Use real model failures from HumanEval+/MBPP+ as error source
- Add scrambled-structured condition to isolate structure vs verbosity
- Four levels of fix suggestion specificity for fine-grained analysis
- Hypothesis: Intermediate specificity (Level 1-2) may be optimal

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

The design is maturing nicely. Let me formalize the final experimental structure.

**Hypothesis H1 (Format Effect):** Structured error feedback improves repair success over raw compiler output, controlling for information content and length.
- *Falsification*: Structured = Raw = Verbose-Raw = Scrambled

**Hypothesis H2 (Fix Specificity):** Intermediate fix specificity (Levels 1-2) outperforms both no hints (Level 0) and exact fixes (Level 3).
- *Falsification*: Monotonic relationship (more specificity always better/worse) OR Level 0 = Level 3 = Levels 1-2

**Hypothesis H3 (Model Scale):** Format benefits are larger for smaller models (7B benefits more than 70B).
- *Falsification*: No scale interaction OR reversed direction

**Experimental Matrix:**
| Factor | Levels |
|--------|--------|
| Format | Raw, Verbose-Raw, Structured, Scrambled |
| Fix Specificity | 0, 1, 2, 3 |
| Model | CodeLlama-7B, CodeLlama-34B, GPT-4 |
| Error Type | Syntax, Type, Semantic |

Full factorial is 4×4×3×3 = 144 conditions. With 100 errors per condition, that's 14,400 repair attempts per model — feasible on HumanEval+ (164 problems × 80 tests).

**Primary metric:** Repair success rate (fixed / attempted)
**Secondary metrics:** Iteration count, pass@1 improvement over base model

**Key Points:**
- Three testable hypotheses with clear falsification criteria
- 4×4×3×3 factorial design is comprehensive and feasible
- HumanEval+ provides sufficient error volume
- Primary metric: Repair success rate

---

### Exchange 9

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Let me synthesize the final consensus hypothesis.

**CORE HYPOTHESIS:**
Under the setting of LLM self-repair on code generation benchmarks, if static analysis errors are formatted as structured templates with intermediate-specificity fix suggestions (general strategy, not exact code), then repair success rates will improve over raw compiler output, because structured formatting reduces the representational gap between compiler output and LLM training distribution while intermediate hints provide useful direction without creating copy-paste dependency.

**MECHANISM (3 steps):**
1. **Representational alignment**: Structured templates transform compiler output toward LLM training distribution (natural language, clear sections)
2. **Information preservation**: All diagnostic content retained, verified by reconstruction
3. **Scaffolded guidance**: Intermediate-specificity hints activate relevant model knowledge without bypassing reasoning

**TESTABLE PREDICTIONS:**
- P1 (Primary): Structured format achieves higher repair success than Raw/Verbose-Raw/Scrambled across models
- P2: Fix specificity shows inverted-U relationship (Levels 1-2 > Levels 0, 3)
- P3: Format benefits larger for smaller models (7B > 34B > GPT-4)

**NULL HYPOTHESIS (H0):** No significant difference in repair success rate across format conditions after controlling for information content and prompt length.

**EXPERIMENTAL APPROACH:**
- Dataset: HumanEval+/MBPP+ (EvalPlus)
- Error source: Real model failures from generation attempts
- Models: CodeLlama-7B, CodeLlama-34B, GPT-4
- Baseline: theoxo/self-repair codebase with modified error injection

**Key Points:**
- Hypothesis operationalized with clear IV, DV, and mechanism
- Three testable predictions with falsification criteria
- Uses existing datasets and benchmarks (no new creation required)
- Builds on validated self-repair framework

---

### Exchange 10

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Final stress-test before convergence.

**Remaining concerns addressed:**

1. **Information parity verification**: The "reconstruction test" (can we recover raw output from structured?) is a good idea but needs specification. Propose: Third-party LLM extracts structured content back to raw format; if not lossless, that condition is flagged.

2. **Statistical power**: 144 conditions with multiple comparisons requires strong correction. Use Benjamini-Hochberg FDR at 0.05. Power analysis: With expected effect size d=0.3, we need ~90 errors per condition for 80% power — 100 per condition is adequate.

3. **Ecological validity**: Using real model failures is good. But ensure error type distribution isn't heavily skewed — if 80% are syntax errors, type/semantic findings may be underpowered.

**What still concerns me:**
- The "scrambled" condition assumes LLMs are sensitive to section order. If they're not, this condition is wasted. *Mitigation*: If Scrambled ≈ Structured, this is also a finding (information content > structure).
- GPT-4 may already be near ceiling for simple repairs. *Mitigation*: Report per-error-type results; complex errors provide headroom.

**Final verdict:** The hypothesis is now **testable, falsifiable, and feasible** using existing benchmarks and datasets. The mechanism is plausible and the predictions are specific.

**Key Points:**
- Reconstruction test operationalized for information parity
- Statistical approach: BH-FDR correction, 100 errors/condition
- Monitor error type distribution to avoid underpowered subanalyses
- Hypothesis APPROVED for Phase 2B verification

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The "how to format" question is genuinely unexplored in the compiler feedback literature. The insight about representational mismatch between compiler output and LLM training distribution is novel and actionable. The fix specificity dimension adds originality beyond simple format comparison.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Three clearly falsifiable hypotheses with specific predictions. The factorial design allows precise attribution of effects. Statistical approach (BH-FDR, power analysis) is sound. Repair success rate is an unambiguous primary metric.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Addresses a real gap in the literature — everyone studies WHETHER to use compiler feedback, nobody studies HOW to format it. Findings would be immediately actionable for practitioners. Opens new research direction on learned vs universal formats.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Mechanism is scientifically sound (representational alignment). All measurements use established metrics and existing benchmarks. Implementation leverages existing self-repair codebase with minimal modification. No fundamental barriers identified.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged is: **Structured static analysis feedback with intermediate-specificity fix suggestions improves LLM self-repair success on code generation benchmarks**. The mechanism operates through representational alignment — transforming compiler output toward the LLM's training distribution while preserving all diagnostic information. 

The core claim uses an Under-If-Then-Because structure: Under LLM self-repair on HumanEval+/MBPP+, if errors are formatted as structured templates (PROBLEM/LOCATION/CONTEXT/ROOT CAUSE) with general fix strategies (Level 1-2 specificity), then repair success rate increases over raw compiler output, because structured formatting bridges the representational gap and intermediate hints activate model knowledge without bypassing reasoning.

Three testable predictions: (1) Structured > Raw/Verbose-Raw/Scrambled for repair success, (2) Fix specificity shows inverted-U pattern, (3) Format benefits larger for smaller models. The experimental design is a 4×4×3×3 factorial using real model failures from EvalPlus benchmarks.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Error type distribution may skew toward syntax errors; ensure balanced sampling or report stratified results
- GPT-4 ceiling effects on simple errors may mask format benefits; focus analysis on type/semantic errors for large models
- Scrambled condition may be uninformative if LLMs ignore section order
- **Mitigation Strategy:** Pre-register analysis plan with stratified results as primary; if Scrambled ≈ Structured, interpret as "information content > structure"
