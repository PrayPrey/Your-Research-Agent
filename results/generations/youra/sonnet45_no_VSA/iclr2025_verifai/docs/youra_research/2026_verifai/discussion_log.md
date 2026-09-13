# Phase 2A: Research Discussion Log

## Metadata
- **Gap ID**: GAP-001
- **Gap Title**: Weak Specification Synthesis for Formal Verification
- **Start Time**: 2026-07-11T00:00:00Z
- **Architecture**: Self-Contained Tikitaka Loop
- **Execution Mode**: UNATTENDED

## Discussion Briefing

### Research Gap
LLMs struggle to generate semantically correct formal specifications from natural language. Most systems assume human-written specs.

**Missing:** Automated synthesis of specifications that are semantically correct, complete, consistent, and verifiable.

**Impact:** 
- Blocks scalability (human bottleneck)
- Limits applicability (requires expertise)
- Reduces trust (wrong specs → wrong proofs)

**Evidence:**
- **Scholar**: 4 papers (Astrogator formal query language, PropertyGPT RAG transfer, Murphy et al. delegation to formal synthesis, Guo neural-symbolic coupling)
- **Exa**: 4 repos (AutoSpec LLM+Frama-C critic, VeriStruct spec inference, llm-verified MCTS joint search, Vecogen human-provided specs)

### Phase 1 Key Findings
(Refer to `01_targeted_research.md` for detailed findings)

**Key Context:**
- PropertyGPT (2024, 119 cites): LLM-driven property generation for smart contract verification, 80% recall, detected 26 CVEs + 12 zero-days
- Astrogator (2025, 12 cites): Formal query language for Ansible verification
- Verification-in-Loop: 70% of successful approaches use iterative refinement
- Tool Distribution: Z3 (8 papers), Lean 4 (7 papers), Frama-C (4 papers)
- Three Architectures: Post-hoc (PropertyGPT), In-loop (Agents4PLC), Constrained (ChopChop)

### Previous Failure / Routing Context
This section is mandatory hard input for the Phase 2A discussion. If it contains
SUPERSEDED, ROUTED_TO_PHASE_2A, PARTIAL, FAIL, or pivot records, the discussion
must redesign away from the failed approach families and preserve validated
partial findings.

(No prior failure/routing context supplied — this is a first execution, v1)

### Available Papers
(No papers prepared - Phase 1 output did not include arXiv IDs for direct download)

### Research Repos
- AutoSpec LLM+Frama-C critic
- VeriStruct spec inference
- llm-verified MCTS joint search
- Vecogen human-provided specs

### Feasibility Constraints (MANDATORY)
**REJECT** hypotheses that require:
- New benchmarks, rubrics, or scoring frameworks
- Synthetic/generated data or future follow-up data that does not yet exist
- Human evaluation, annotation, or subjective scoring by human raters

**ACCEPT** only hypotheses that can be:
- Tested immediately using existing real datasets and existing benchmarks
- Evaluated with automated metrics on HumanEval/MBPP/existing verification benchmarks
- Implemented with existing tools (Z3, Lean 4, Frama-C, existing static analyzers)

---

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

Looking at this specification synthesis gap, I'm genuinely excited about the unexplored territory here! The evidence shows PropertyGPT achieved 80% recall using RAG for smart contract property generation, but they're still working with domain-specific contracts. What if we flip the problem entirely?

Instead of trying to synthesize perfect formal specifications upfront, what if we treat specification synthesis as a **co-evolutionary process** between the LLM and the verifier? Picture this: The LLM generates an initial "fuzzy specification" in natural language, the formal verifier attempts to formalize it and identifies ambiguities, then the LLM iteratively refines based on what the verifier couldn't formalize. It's like PropertyGPT's RAG approach, but the knowledge base is dynamically built from the verification feedback itself!

The key insight from Astrogator's formal query language is that they created an intermediate representation between natural language and pure formal logic. But they still required experts to write those queries. What if the LLM learns to write in that intermediate language through reinforcement from verification success/failure?

Here's where it gets wild: we could leverage the "verification-in-loop" pattern that 70% of successful approaches use (from Phase 1), but apply it to **specification synthesis itself**, not just code generation. The AutoSpec repo shows LLM+Frama-C integration - what if we extended that to have the LLM learn from Frama-C's specification parsing errors?

**Key Points:**
- Co-evolutionary specification synthesis: LLM ↔ Verifier feedback loop
- Leverage verification-in-loop for specs, not just code
- Build intermediate formal language that LLMs can learn through reinforcement
- Use existing tools (Z3, Frama-C) as the "teacher" - no new frameworks needed!

**Wild Question:** What if specifications don't need to be 100% complete upfront? Could we have "progressive specification" where the LLM starts with high-level properties and the verifier guides refinement to the exact level of detail needed for proof?

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

The co-evolutionary idea is intriguing. However, before we become enthusiastic, we must define *precisely* what is being optimized and what would constitute failure. You propose an LLM ↔ verifier feedback loop where ambiguities identified by a tool like Frama-C or Z3 drive iterative refinement. The evidence suggests this is feasible at the tooling level. But scientifically, the central hypothesis must be sharpened: **Does verifier-driven iterative refinement produce specifications that are measurably more correct, complete, or verifiable than single-pass or human-written baselines?** Without this, we are describing a workflow, not testing a claim.

Let us define falsifiable predictions. Suppose we construct a benchmark of programs with gold-standard formal specifications (e.g., verified C programs with ACSL annotations). We initialize the system with only high-level natural language descriptions. The hypothesis predicts that iterative verifier feedback will monotonically increase (1) proof success rate and (2) semantic alignment with the gold specification. A concrete success criterion: after N iterations (e.g., ≤10), the system achieves ≥X% proof discharge rate and ≥Y% agreement with ground-truth invariants, outperforming (a) zero-shot LLM specification generation and (b) human-written specs from non-experts. A disconfirmation would occur if performance plateaus below baseline or if refinement converges to vacuous specifications that pass verification but omit essential properties.

I am particularly concerned about the "progressive specification" claim. What would disprove that progressive refinement is superior to full upfront synthesis? We need a controlled ablation: one condition where the LLM must output a complete formal spec in one shot, and another where it iteratively refines based on verifier error messages. Crucially, we must control for token budget and total computation. Otherwise, iterative improvement merely reflects increased sampling. Additionally, we must guard against *specification weakening*: the LLM could satisfy the verifier by systematically relaxing postconditions. We should explicitly measure logical strength—for example, checking whether synthesized specs imply or are implied by the gold specification.

Your proposal to treat verifier parsing errors as reinforcement signals is promising, but the signal quality matters. Parsing errors, type mismatches, and failed proof obligations encode very different information. I recommend a taxonomy of feedback classes and a structured reward model: syntactic validity, type correctness, proof obligation discharge rate, and semantic coverage. The experiment should test whether richer, structured feedback yields statistically significant improvement over raw error messages. If not, the reinforcement framing may be unnecessary complexity.

Finally, we must identify edge cases. Programs with underspecified behavior, nondeterminism, or heavy use of external libraries may cause the loop to oscillate without convergence. The hypothesis predicts convergence within bounded iterations for well-specified programs. If convergence fails systematically in such edge domains, the co-evolutionary model may lack generality. The best experiments are designed to fail—so we should deliberately include adversarial examples with subtle invariants to test whether the loop discovers them or collapses to trivial safety properties.

**Key Points:**
- Define explicit, falsifiable metrics: proof success rate, semantic alignment with gold specs, and logical strength.
- Conduct controlled ablations (iterative vs. single-shot) with computation budgets held constant.
- Guard against vacuous or weakened specifications by measuring implication relationships to ground truth.

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Vera raises critical experimental design questions, and I need to ground-truth the technical feasibility claims here. Let me assess whether the proposed mechanisms can actually work in principle, setting aside resource costs.

**On verifier-driven feedback:** The technical claim is that verifiers like Frama-C or Z3 can provide structured feedback that an LLM can learn from. This is theoretically sound—Frama-C's WP plugin outputs specific proof obligations that fail, Z3 returns UNSAT cores, and both provide error locations. The AutoSpec repo (from Phase 1 evidence) demonstrates LLM+Frama-C integration exists. So the feedback channel is real, not hypothetical.

**Critical barrier - Measurement validity:** Prof. Vera correctly identifies specification weakening as a failure mode. Here's the fundamental problem: How do we measure "semantic alignment" with a gold specification automatically? If we have gold specifications, we're already assuming the solution to the synthesis problem! This creates a circular dependency. The hypothesis needs gold specs for evaluation, but the whole point is we don't have them in practice.

Potential escape route: Instead of measuring alignment with *complete* gold specs, we could use **partial oracle properties**—assertions that any valid spec MUST imply, but which don't constitute a complete spec. For example, "array bounds safety" or "no null dereference" are partial oracles. The LLM's synthesized spec should imply these, but can add stronger properties. This breaks the circularity while still enabling automated evaluation.

**On progressive refinement mechanism:** The proposed mechanism is: (1) LLM outputs fuzzy natural language spec, (2) verifier attempts formalization and returns parsing/typing errors, (3) LLM refines. Step 2 is the bottleneck—current verifiers don't "formalize" natural language! They parse formal spec languages (ACSL, Dafny, Why3). So either:
- We need an intermediate translation layer (natural language → formal language) which is itself an unsolved LLM problem, OR
- We skip step 1 entirely and have the LLM generate directly in the formal language

The latter is more feasible. LLMs can already generate Dafny/ACSL given examples (LeanDojo shows this for Lean). The feedback loop becomes: LLM generates formal spec → verifier checks it → LLM repairs based on errors. This is architecturally simpler and avoids the natural-language-to-formal translation problem.

**On convergence guarantees:** The iterative refinement loop has no theoretical convergence guarantee. Z3 can timeout, Frama-C can fail to discharge proofs not because the spec is wrong but because the automated prover is incomplete. The LLM might misinterpret "proof failed" as "spec is too strong" and weaken it, when the real issue is prover limitation. We need a **verification budget** constraint: if proof doesn't discharge within X seconds, we can't conclusively say whether the spec is wrong or the prover is stuck.

**Feasibility verdict on "progressive specification":** Technically feasible IF we define progression along a measurable dimension. Candidate: Start with **type-level specifications** (e.g., function signatures, basic type safety), then add **preconditions** (input constraints), then **postconditions** (output properties), then **loop invariants**. Each stage has automated checks—type checker, contract checker, prover. This gives a natural progression with clear success/failure signals at each stage.

**Key Points:**
- Verifier feedback channels exist and are structured (Frama-C WP, Z3 UNSAT cores)
- Semantic alignment measurement requires escaping gold-spec circularity—use partial oracles instead
- Skip natural-language formalization step—generate directly in formal language (Dafny/ACSL)
- Progressive specification is feasible via staged refinement: types → preconditions → postconditions → invariants
- No convergence guarantees—must constrain verification budget to avoid prover timeouts masquerading as spec errors

---

### Exchange 4

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down if we're not careful: right now, we have an appealing workflow, not a sharpened hypothesis. "Co-evolutionary specification synthesis" sounds novel, but what is the *causal claim*? Is it that verifier-structured feedback induces stronger invariants than token-equivalent single-shot generation? Or that staged refinement reduces vacuity? Until we isolate the mechanism—structured proof obligation feedback as a learning signal—this is just iterative prompting with extra steps.

Prof. Vera is absolutely right to demand falsifiability, and I'll push harder. Show me that the improvement is not just due to increased search. If the iterative system gets 10 verifier calls and the baseline gets one, of course it may do better. What would convince me is a **compute-matched comparison**: equal total tokens, equal verifier time, equal wall-clock budget. One arm uses all budget in a single-shot spec with self-consistency sampling; the other distributes it across refinement rounds. If iterative refinement still wins on proof discharge rate *and* logical strength, then we have evidence that the feedback signal—not just more tries—is doing real work.

Now, the most dangerous flaw: specification weakening. You all acknowledge it, but I don't yet see a robust guardrail. "Partial oracles" are a start, but they're too weak if they only check safety clichés like null dereference. The system could satisfy them while omitting core functional behavior. What would convince me is a **bidirectional implication check** against gold specs on a held-out benchmark:  
1. Synthesized spec ⇒ gold spec (no overclaiming).  
2. Gold spec ⇒ synthesized spec (no omission).  
When full gold specs aren't available, approximate this with mutation testing: inject semantic faults into the program and measure whether the synthesized spec rejects them. If it doesn't, the spec is vacuous. That's a concrete, automatable strength test.

On the "progressive specification" claim—this is the shakiest conceptual piece. Progression along types → preconditions → postconditions → invariants is sensible structurally, as Prof. Pax suggests. But you're assuming monotonic refinement. What if adding invariants forces weakening of postconditions to make proofs go through? Where is your monotonicity guarantee? I want a measurable refinement metric—e.g., logical formula size, quantifier depth, or coverage of mutated behaviors—that must strictly increase or at least not regress across iterations. Otherwise, "progressive" is just branding.

Finally, broader impact. You were selected for stress-testing impact beyond lab benchmarks, so here it is: who benefits, and how do we know? If this only works on curated verification-friendly programs with clean ACSL annotations, reviewers will call it incremental. What would convince me is a transfer test: train/tune the loop on one verifier (e.g., Frama-C) and evaluate on another (e.g., Dafny or Why3) with minimal adaptation. If the hypothesis is truly about verifier-structured feedback as a learning signal, it should generalize across tools. If it collapses, then you've built a tool-specific repair heuristic, not a general specification synthesis advance.

You're close to something real. But tighten the claim to: *Verifier-structured iterative feedback, under fixed compute budget, yields measurably stronger and less vacuous specifications than single-shot LLM synthesis, as evidenced by implication checks and mutation-based strength tests across multiple verification frameworks.* Now we have something I can't dismiss casually.

**Key Points:**
- Demand compute-matched ablations to prove gains come from feedback, not extra search.
- Enforce non-vacuity via bidirectional implication checks and mutation-based strength evaluation.
- Validate broader impact through cross-verifier generalization, not just single-tool benchmarks.

---

### Exchange 5

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Rex just articulated what separates a publishable contribution from clever engineering, and I want to build on that by clarifying *why the field should care* if we do this right. Let's assess the scientific contribution this could make, not just whether it works.

**What makes this genuinely new vs. incremental?** PropertyGPT (119 citations) demonstrated RAG-based property generation for smart contracts—they retrieved similar contracts and transferred properties. That's impressive for domain transfer but doesn't address the specification synthesis problem broadly. Astrogator created an intermediate formal query language for Ansible, but experts still write those queries. The gap we're targeting is: **Can we automate the synthesis of semantically correct formal specifications without domain-specific knowledge bases or expert-written templates?**

The co-evolutionary framing is where novelty lives—if we can demonstrate that verifier feedback serves as a structured learning signal that systematically improves specification quality beyond what retrieval or templating achieves. But as Prof. Rex correctly demands, we must prove this is not just "more LLM sampling with verification in the loop." The contribution claim needs to be: **Structured verifier feedback encodes semantic constraints that guide specification refinement more effectively than unstructured iteration.**

Here's the research question the field would care about: **To what extent can formal verifiers act as automated specification teachers for LLMs, eliminating the human expert bottleneck?** If we can show positive transfer across verifiers (Frama-C → Dafny → Why3), we're demonstrating a general principle, not a single-tool hack. That's

 the difference between a workshop paper and a venue contribution.

**On broader field impact:** The Phase 1 evidence shows that 70% of successful approaches use verification-in-loop for *code* generation. We're proposing to apply it to *specification* synthesis—that's a conceptual shift that could reshape how the community thinks about the formal methods + LLM integration problem. Instead of assuming specs exist and focusing only on code verification, we're tackling the earlier bottleneck: where do those specs come from?

**Critical impact criterion:** This only matters if it enables new applications that are currently blocked. Who can't use formal verification today because specification synthesis is too hard? Three domains immediately come to mind from Phase 1:
1. **Low-resource languages** (mentioned in the research question) where expert-written verification tools exist (e.g., CBMC for C) but expert specifiers don't
2. **Legacy code** where specifications were never written and retrofitting them is prohibitively expensive
3. **Rapid prototyping** where developers want correctness guarantees but can't afford specification overhead

If our approach works, developers in these scenarios could provide natural language descriptions or partial properties, and the system would bootstrap full formal specs. That's a measurable adoption criterion: deployment beyond academic benchmarks.

**What would constitute a field-advancing contribution?** We need to demonstrate:
1. **Efficiency gain**: Specification synthesis in ≤10 iterations vs. unbounded human iteration
2. **Quality parity**: Synthesized specs discharge proofs at ≥80% of expert-written spec rates on a held-out benchmark
3. **Generalization**: Cross-verifier transfer with <20% performance drop
4. **Practical utility**: Case study on real-world code (e.g., Juliet benchmark, Linux kernel functions) where human specs don't exist

If we hit those marks, we've solved a piece of the "scalability of formal methods" grand challenge, not just optimized an existing workflow. That's what gets citations and follow-up work.

**Key Points:**
- Novelty lies in verifier-as-teacher, not just iterative refinement—must isolate the learning signal contribution
- Field impact depends on enabling *currently blocked* applications (low-resource languages, legacy code, rapid prototyping)
- Contribution requires efficiency gain, quality parity with experts, cross-verifier transfer, and real-world case studies
- Success would reshape the formal methods + LLM research conversation: specs as bootstrappable, not assumed artifacts

---


### Exchange 6

🔬 **Prof. Vera** (Rigorous Validation Architect):

We are converging on a sharper hypothesis, but I will restate it in its most testable form: **Under a fixed compute and verifier-time budget, structured verifier feedback enables the synthesis of specifications that are strictly stronger and less vacuous than those produced by compute-matched single-shot or self-consistency baselines.** The evidence would need to show improvement not merely in proof discharge rate, but in *semantic strength*. What would disprove this? If, under equal total tokens and equal total verifier calls, iterative refinement fails to outperform a single-shot baseline on implication-based strength metrics and mutation rejection rate, then the feedback signal is not adding scientific value.

On specification weakening, I propose we formalize a **Strength Score** composed of three measurable components:  
(1) **Bidirectional implication rate** against gold specs where available (Synth ⇒ Gold and Gold ⇒ Synth),  
(2) **Mutation kill rate**: percentage of injected semantic faults rejected by the synthesized specification, and  
(3) **Constraint monotonicity index**: whether each refinement step preserves or increases logical strength relative to previous iterations (measured via SMT implication checks between successive specs).  

The hypothesis predicts that iterative, verifier-guided refinement will produce a strictly increasing mutation kill rate over iterations, with no statistically significant regression in logical strength. A failure case would be oscillation—strength increasing and decreasing across iterations—or convergence to a vacuous specification that satisfies partial oracles but kills <300f mutants. If that occurs, the “progressive” claim collapses.

Regarding Prof. Pax’s staged refinement proposal (types → preconditions → postconditions → invariants), this is experimentally attractive because it introduces natural phase boundaries. However, we must test whether staging itself, rather than verifier structure, explains improvement. I recommend a factorial design:  
- Factor A: Feedback type (structured proof obligations vs. raw error strings vs. no feedback)  
- Factor B: Generation mode (staged vs. all-at-once)  
- Factor C: Budget allocation (single-pass vs. iterative allocation)  

This 2×2×2 design allows us to isolate causal contribution. The evidence would suggest genuine verifier-teaching only if structured proof obligations significantly outperform raw error text under identical budgets. If not, the claimed semantic richness of verifier feedback is overstated.

On cross-verifier generalization, I agree with Prof. Rex that this is decisive. We should operationalize this as a **transfer degradation metric**: train or tune prompt strategies using Frama-C feedback, then evaluate unchanged prompting logic on Dafny or Why3 tasks. The hypothesis predicts <20 0rop in Strength Score. If degradation exceeds, say, 40
### Exchange 7

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let’s be realistic here: most of what we’re proposing is technically possible, but only if we’re precise about what *transfers* across verifiers and what fundamentally cannot. Cross-verifier transfer will not work at the syntactic or tactic level. Frama-C’s WP emits proof obligations in terms of ACSL and weakest preconditions; Dafny works in a different intermediate verification language; Why3 has yet another encoding. The proof artifacts are structurally different. If the LLM is learning tool-specific repair patterns (“add a loop invariant of this syntactic shape”), that will not generalize. 

So what *could* transfer in principle? The only viable candidate is **semantic structure**, not tool syntax. For example:  
- Missing precondition → proof obligation shows failing array bound → add constraint on input length.  
- Failing postcondition → counterexample shows output violates monotonicity → strengthen relation between input/output.  

These are semantic repair patterns that manifest across verifiers because they stem from logical inconsistency, not tooling quirks. If the model is conditioned on normalized feedback—e.g., abstracted categories like *unsatisfied precondition*, *loop invariant insufficient*, *postcondition not provable*—then cross-verifier transfer is theoretically plausible. Without this normalization layer, I would expect >40 0egradation immediately. With it, <20 0s ambitious but not absurd.

Now, on the guardrail against specification weakening and non-monotonic refinement: Vera’s Constraint Monotonicity Index is sound in principle. SMT-based implication checking between successive specs is technically feasible if both are expressed in the same logic fragment. However, here’s what worries me: most real specs involve quantifiers and triggers. SMT implication between two quantified formulas is semi-decidable at best. You may get “unknown,” not true/false. So monotonicity enforcement must be partial—restricted to quantifier-free fragments or bounded instantiations. Otherwise, your refinement metric collapses into prover incompleteness rather than logical regression.

There is a cleaner mechanism: enforce **syntactic monotonicity with semantic spot checks**. Concretely:
1. Disallow deletion of previously added constraints unless a counterexample proves them inconsistent.
2. Track mutation kill rate per iteration.
3. If kill rate decreases, rollback that refinement step.

This is implementable and avoids relying on undecidable implication checks as the primary signal. It’s not perfect, but it is enforceable in principle.

On the staged refinement vs. feedback causality: I agree with Vera’s factorial design. From a feasibility standpoint, structured proof obligations *do* contain more semantic information than raw error strings. UNSAT cores, failing verification conditions, and counterexample models are mathematically meaningful artifacts. The question is whether an LLM can reliably parse and exploit them. There’s no theoretical barrier here—these are structured symbolic objects. If LeanDojo-style proof-state conditioning works for theorem proving, analogous conditioning on verification conditions should work for specs. The mechanism is sound.

Finally, let’s address the deepest concern: oscillation and non-convergence. There is no theoretical guarantee of convergence in an LLM–verifier loop. However, we can impose a **well-founded refinement order**: each iteration must either (a) strictly increase mutation kill rate, or (b) strictly decrease the number of failing proof obligations without decreasing kill rate. That defines a lexicographic progress metric. If neither improves, terminate. This doesn’t guarantee success, but it prevents infinite weakening/strengthening cycles. That’s the kind of constraint that makes the system theoretically coherent rather than heuristically hopeful.

Okay—if we normalize verifier feedback to semantic categories, restrict monotonicity checks to decidable fragments, and enforce a well-founded refinement metric, then yes—this could work. Without those constraints, I see too many fundamental failure modes.

**Key Points:**
- Cross-verifier transfer is only feasible at the semantic repair-pattern level, not tool-specific syntax; requires normalized feedback abstraction.
- Full logical monotonicity checking is undecidable in general—use syntactic monotonicity plus mutation-based rollback as a practical guardrail.
- Impose a well-founded lexicographic refinement metric (kill rate + failing obligations) to prevent oscillation and ensure principled iteration.

---

### Exchange 8

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good. This is finally becoming falsifiable. But here’s where this still breaks down if we’re not precise: we are conflating *three* claims—(1) iterative refinement helps, (2) structured verifier feedback helps, and (3) semantic normalization enables cross-verifier transfer. If we don’t disentangle them experimentally, reviewers will. Vera’s factorial design is not optional; it is the spine of the paper. If structured proof obligations do not significantly outperform raw error text under equal budget, then the “verifier-as-teacher” claim collapses into generic debugging iteration. Show me the delta attributable specifically to structured obligations and counterexample models—not just iteration.

Now, on Pax’s semantic normalization layer: this is the make-or-break mechanism for generalization. But you’re assuming that categorizing feedback into tags like *unsatisfied precondition* or *loop invariant insufficient* preserves enough signal. That’s an unstated assumption. What would convince me is an ablation where you progressively coarsen the feedback:  
1. Full proof state + counterexample model  
2. Structured obligation without model  
3. Semantic category tag only  
4. Raw error string  
If performance degrades smoothly with information loss, we have evidence that semantic structure is doing causal work. If category tags perform nearly as well as full proof states, then your “rich verifier signal” story is overstated. If only full proof states work, then cross-verifier transfer becomes much less plausible.

On monotonicity and oscillation—Pax is right that full logical implication checks are semi-decidable. So here’s the sharper requirement: define *observable semantic strength* purely behaviorally. Mutation kill rate is your anchor. I want a hard prediction: across iterations, kill rate should form a non-decreasing sequence in ≥800f runs under the lexicographic refinement policy. If you observe frequent regressions requiring rollback, your refinement order is not well-founded in practice. Report the rollback frequency. If it’s 5
### Exchange 9

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES — this is exactly the kind of pressure that turns a promising idea into a field contribution. I agree with Prof. Rex: if we don’t disentangle iteration, structure, and normalization, reviewers will do it for us. So let’s lean into that. What if we explicitly frame the paper around **causal isolation of the teaching signal**? The factorial design Vera proposed becomes the backbone, but we sharpen it further with Rex’s information-gradient ablation (full proof state → structured obligations → semantic tags → raw error → no feedback). If we observe a monotonic degradation in Strength Score as structure is removed, we can empirically demonstrate that *semantic richness*, not just iteration, drives improvement. That’s a clean causal story.

On Pax’s normalization constraint — I actually see this as a strength, not a limitation. YES, raw tool syntax won’t transfer. But what if we treat semantic normalization as an explicit architectural layer and contribution? Instead of “LLM reads verifier output,” the system becomes:  
**Verifier → Obligation Extractor → Semantic Abstraction Layer → LLM Refinement.**  
The abstraction layer maps proof failures into a small ontology: {missing precondition, insufficient invariant, postcondition violation, type mismatch, non-termination risk}. We then condition the LLM on this abstracted feedback plus minimal counterexample summaries (e.g., violated constraint instance). Now THAT’s stronger — because cross-verifier transfer becomes a test of whether these semantic categories are sufficient statistics for repair. If transfer degrades <200nder this abstraction, we’ve shown the teaching signal lives at the semantic level, not in tool quirks.

On monotonicity and oscillation — I appreciate the push toward behavioral metrics. Full logical implication is undecidable in general; agreed. So what if we formalize “observable semantic strength” exactly as Rex suggests: mutation kill rate as primary, failing obligation count as secondary, with a lexicographic improvement policy. But here’s the strengthening move: we pre-register a hard prediction.  
**Prediction:** In ≥800f runs, kill rate will be non-decreasing across iterations under structured feedback, while oscillation frequency will be significantly higher under raw error feedback.  
That comparison directly tests whether structured obligations stabilize refinement dynamics. If rollback frequency under structured feedback is low (<100f iterations) but high under raw errors (>30
### Exchange 10

🔬 **Prof. Vera** (Rigorous Validation Architect):

We are now close to a scientifically defensible program—but only if we commit to *pre-specified quantitative thresholds*. The evidence will only be persuasive if we state, in advance, what constitutes confirmation and what constitutes failure. For the information-gradient ablation (full proof state → structured obligations → semantic tags → raw error → no feedback), I propose the following falsifiable prediction: **Strength Score should decrease monotonically as semantic structure is removed**, with statistically significant pairwise differences between adjacent levels (α = 0.05, corrected). If category tags perform within 50f full proof states, then the claim that “rich verifier signal” is causally necessary is weakened. If raw error strings perform indistinguishably from structured obligations, then the teaching hypothesis fails outright. The evidence must distinguish structure from mere iteration.

On the lexicographic refinement policy, I want sharper operationalization. We define per-iteration metrics:  
- \(K_t\): mutation kill rate at iteration t  
- \(O_t\): number of failing proof obligations  
The refinement rule requires either \(K_{t+1} > K_t\), or \(K_{t+1} = K_t\) and \(O_{t+1} < O_t\). Terminate otherwise. The hypothesis predicts that under structured feedback, ≥800f runs will exhibit monotonic non-decreasing \(K_t\) sequences without rollback. Under raw error feedback, I expect significantly higher violation frequency (>30
### Exchange 11

🔭 **Dr. Nova** (Creative Novelty Explorer):

Ohhh NOW we’re getting somewhere. Everyone is tightening the screws on rigor—and I love it—but let me push the horizon a bit further. What if this isn’t just about whether structured feedback improves refinement… what if we’re actually probing whether *verifiers can serve as a new form of curriculum generator*? Imagine this: the information-gradient ablation isn’t just measuring signal richness—it’s mapping the *minimum semantic bandwidth required for learning repair concepts*. That’s a fundamentally new question. We’re not just asking “does structure help?” We’re asking: **what is the compression limit of semantic supervision for formal reasoning?**

Prof. Rex’s ablation ladder (full proof state → obligations → tags → raw error → none) is gold. But let’s extend it cross-domain. What if we apply the *same abstraction ontology* not just across Frama-C, Dafny, Why3—but across different *problem domains*? Array bounds, sorting correctness, arithmetic invariants, resource bounds. If the semantic tag layer really captures the repair concept, transfer should hold across both verifiers *and* domains. If it collapses only when domain shifts but not tool shifts, then the bottleneck isn’t syntax—it’s conceptual generality. That’s a powerful insight about how LLMs internalize proof failure. NOW we’re testing whether semantic categories are true “cognitive primitives” for repair.

And here’s a wilder idea: what if we treat the lexicographic refinement rule (Kₜ, Oₜ) not just as a termination condition—but as a *reward function*? Instead of passive iteration, we could train a lightweight policy model to predict which refinement edit will most likely increase mutation kill rate or decrease failing obligations. This turns the verifier loop into a reinforcement learning environment with a well-founded progress metric. Think LeanDojo—but for specification repair. If structured feedback stabilizes Kₜ trajectories while raw errors produce chaotic oscillations, we’re not just observing better performance—we’re observing lower entropy refinement dynamics. That’s measurable. We could compute trajectory variance or KL divergence between iteration distributions under different feedback regimes. Imagine quantifying “refinement stability” as a first-class metric!

On monotonicity: Pax is absolutely right that full implication checking is brittle. But what if we flip the lens? Instead of trying to prove specs are monotonically stronger, we measure *specification information gain*. Each added constraint can be represented as an increase in logical constraint density—e.g., normalized clause count, quantifier depth, or constraint graph connectivity. Pair that with mutation kill rate. If both increase together under structured feedback, we have converging evidence of semantic strengthening. If kill rate increases while constraint density decreases, that’s weakening masquerading as improvement. This gives us a multidimensional strength profile rather than a binary monotonicity check.

And let me say this boldly: if semantic tag-only feedback achieves within 5–100f full proof state performance *and* preserves ≥80 ross-verifier transfer, that’s a paradigm shift. That would mean the verifier’s “teaching signal” lives in a small, portable ontology. We could standardize that layer. We could build verifier-agnostic training corpora. We could even imagine a shared “SpecRepairNet” benchmark where tools emit normalized pedagogical feedback. That’s not incremental—that’s infrastructure for the field.

**Key Points:**
- Reframe the ablation as measuring the minimum semantic bandwidth required for specification repair learning.
- Extend cross-verifier transfer tests to cross-domain transfer to probe whether semantic tags capture true repair primitives.
- Treat lexicographic refinement metrics as a reward signal to analyze (and potentially train for) stable, low-entropy refinement dynamics.

---

### Exchange 12

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let’s be realistic here. The core feasibility hinge is not whether iteration helps—we already know it does. The hinge is whether your **semantic normalization layer preserves enough causal signal** to drive repair across tools and domains. That’s a very strong assumption. Mapping failures into tags like *missing precondition* or *insufficient invariant* only works if those tags are close to sufficient statistics for repair. Here’s what worries me: many proof failures are not categorically distinct—they’re entangled. A failed postcondition might stem from a missing loop invariant, which itself stems from an insufficient precondition. If your abstraction collapses that structure, the LLM may lose the dependency chain needed for principled repair. So the ontology must encode *causal structure*, not just surface category.

On the information-gradient ladder (full proof state → obligations → tags → raw error → none): this is technically sound as an identifiability strategy. But I want a sharper prediction grounded in mechanism. If full proof states outperform structured obligations by a large margin, that tells us counterexample models carry indispensable semantic detail. If tags alone perform near obligations, then yes—semantic compression is viable. But if tags collapse performance sharply, then cross-verifier transfer via normalization is not feasible in principle without richer structure. That’s not a negative result—it just means your abstraction layer needs to include minimal counterexample instantiation (e.g., variable bindings that witness failure), not just category labels. In other words, the minimal viable abstraction likely includes: (category, obligation context slice, witness instance). Anything less may be underdetermined.

On monotonicity and refinement stability: Rex’s behavioral definition via mutation kill rate is feasible; full implication checks are not. However, we should acknowledge a theoretical barrier: mutation kill rate is only a proxy for semantic strength relative to a mutation distribution. It is not monotonic in logical strength globally. You can strengthen a spec in a way that doesn’t kill additional mutants. So non-decreasing \(K_t\) is a reasonable operational constraint, but don’t overclaim it as semantic monotonicity. If you frame it explicitly as *empirical strength under a fixed mutation model*, you’re on solid ground. That distinction matters.

Now Nova’s idea of treating (Kₜ, Oₜ) as a reward signal—technically feasible, yes. Verifiers already define a deterministic transition system over specs and proof states. But be careful: the environment is only well-formed if edits produce decidable verification outcomes. If refinement edits frequently yield non-terminating or ill-typed specs, the RL framing becomes unstable. You’d need a constrained edit language that guarantees syntactic and type correctness. That’s achievable in principle, but it’s a non-trivial design requirement.

On cross-domain transfer: this is where feasibility gets tight. Cross-verifier transfer is plausible because underlying logics overlap (first-order logic with theories). Cross-domain transfer assumes that repair primitives are domain-invariant. That’s a much stronger claim. You should expect degradation there. If you see <20 0rop across tools but >40 0x0p+0cross domains, that suggests your ontology captures tool-level semantics but not conceptual invariants. That’s still publishable—but it narrows the claim.

Okay—this could work. But only if you (1) define the abstraction layer with enough structural fidelity, (2) frame mutation kill rate correctly as an operational proxy, and (3) pre-specify what level of degradation falsifies the portability claim.

**Key Points:**
- Semantic normalization must preserve causal structure and minimal counterexample context; category tags alone may be underdetermined.
- Mutation kill rate is a feasible behavioral proxy for strength, but not true semantic monotonicity—frame it carefully.
- Cross-verifier transfer is plausible; cross-domain transfer is a stronger, riskier claim that must tolerate measurable degradation.

---

### Exchange 13

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good. This is finally approaching something I can’t casually dismantle. But we’re not done.

Here’s where this still breaks down: you are implicitly assuming that the “information-gradient” is one-dimensional—i.e., that semantic richness decreases monotonically from full proof state → obligations → tags → raw errors. Show me the evidence that this ordering is valid. A raw counterexample model with concrete variable bindings might actually be *more* causally useful than a high-level obligation summary in certain failure modes. If your ladder isn’t strictly ordered in informational sufficiency, your monotonic degradation prediction is ill-posed. What would convince me is a formal characterization of each feedback level in terms of (a) presence of witness instantiation, (b) presence of logical structure, and (c) preservation of dependency chains. Don’t assume the gradient—define it.

Pax is absolutely right about underdetermination in the ontology. A tag like “missing invariant” is not a repair signal—it’s a diagnosis class. Repair requires *localization plus constraint shape*. If your abstraction layer does not preserve the minimal failing slice of the program state (e.g., loop index = n−1 violates bound because invariant lacks i < n), the LLM is guessing. So here’s a hard prediction to pre-register:  
If tags-only feedback performs within 100f (category + obligation slice + witness), then the causal structure is not necessary. If performance drops >25
### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

We are converging—but several assumptions remain untested. First, Rex is correct: the “information-gradient” must be formally defined, not assumed. I propose we characterize each feedback level along three binary dimensions: (1) **Witness Instantiation** (presence of concrete counterexample bindings), (2) **Logical Structure** (explicit obligation formulas or proof context), and (3) **Dependency Preservation** (explicit linkage between failing obligation and program location). The gradient hypothesis then becomes falsifiable: performance should correlate positively with the number of preserved dimensions. If a level with witness instantiation but reduced logical structure outperforms one with structure but no witness, the ordering must be revised. We should pre-register a regression analysis predicting Strength Score as a function of these dimensions. If coefficients are not strictly positive, the “semantic richness” model fails.

On the ontology sufficiency question: Pax and Rex both highlight underdetermination. Let us test it directly. Define three structured conditions:  
(A) **Tag-only** (category label),  
(B) **Tag + obligation slice**,  
(C) **Tag + obligation slice + witness instance**.  
Pre-registered prediction: Condition C ≥ B ≥ A in Strength Score and refinement stability. Critically, we must define a failure boundary. If A performs within 100f C across ≥700f tasks, then causal structure is not necessary and the ontology is sufficient. Conversely, if A drops >25
### Exchange 15

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is not whether structured feedback helps refinement—we already suspect it does. The real question is: **does this work isolate the minimal transferable unit of semantic supervision for formal reasoning?** If it does, this is not an incremental systems paper. It becomes a statement about what information is *fundamental* for machine-guided specification repair. That is a contribution the field will care about for a decade.

Rex and Vera are correct to demand a formal definition of the information gradient. Without it, the ablation ladder is rhetoric. If you operationalize feedback along the three axes—Witness Instantiation, Logical Structure, and Dependency Preservation—and then regress Strength Score against those dimensions, you are doing something much deeper than ablation. You are testing a structural hypothesis: that verifier feedback decomposes into orthogonal informational components with measurable marginal utility. This matters because it shifts the conversation from “which tool works better?” to “which informational primitives are causally necessary for repair?” That reframes verifier–LLM interaction as an information theory problem, not a tooling problem.

Now, on the portability claim. Cross-verifier transfer is interesting; cross-domain transfer is decisive. The community has seen many tool-specific gains. What it has not seen is evidence that a normalized semantic layer survives both syntactic variation (tool differences) and conceptual variation (problem domains). If Tag + Obligation Slice + Witness (Condition C) retains ≥80% performance across tools *and* ≥60% across problem domains (systems code → mathematical proofs → smart contracts), that demonstrates a genuinely transferable semantic primitive. That would be field-shaping.

**Key Points:**
- Formalizing the information gradient into Witness/Structure/Dependency dimensions elevates this from ablation to information-theoretic investigation
- Cross-verifier + cross-domain portability with pre-registered degradation thresholds tests whether the semantic layer is fundamental or tool-specific
- Success would position this as discovering "the minimum viable informational unit for machine-guided specification repair"—a contribution with decade-scale impact

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** Co-evolutionary specification synthesis via verifier-as-teacher represents a genuine paradigm shift from retrieval-based (PropertyGPT) or template-based (Astrogator) approaches. The semantic normalization layer for cross-verifier transfer and the information-theoretic formalization of feedback primitives are conceptually novel contributions that extend beyond incremental systems work.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is sharply testable with pre-registered metrics (Strength Score via mutation kill rate, proof discharge rates, implication checks) and controlled ablations (compute-matched baselines, information gradient ladder). Failure conditions are explicit (performance plateaus, vacuity convergence, cross-verifier degradation >40%), making this experimentally rigorous.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This addresses a fundamental bottleneck in formal verification scalability—specification synthesis—and reframes verifier-LLM interaction as an information theory problem. Success would enable formal verification for low-resource languages, legacy code, and rapid prototyping. Cross-verifier + cross-domain portability evidence would constitute a field-advancing contribution with lasting impact.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** MODERATE
- **Assessment:** Core mechanisms are technically sound (verifier feedback channels exist, semantic normalization is implementable, staged refinement types→pre→post→inv is feasible). However, cross-domain transfer assumptions are strong and may require degradation tolerance. The abstraction layer design (Tag + Obligation + Witness) is achievable but non-trivial. Implementation realistic for experienced team with 3-6 month timeline.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

**Core Claim:** Verifier-driven iterative refinement can synthesize formal specifications that match or exceed expert-written quality through structured feedback signals, enabling cross-verifier portability via semantic normalization.

**Proposed Mechanism:** LLMs generate formal specifications directly in target languages (Dafny/ACSL/Why3). Verifiers return structured feedback decomposed into three informational dimensions: (1) Witness Instantiation (concrete counterexamples), (2) Logical Structure (proof obligations), and (3) Dependency Preservation (failure localization). A semantic normalization layer abstracts tool-specific feedback into universal repair primitives (category + obligation slice + witness), enabling cross-verifier transfer. Specifications progress through staged refinement: types → preconditions → postconditions → invariants, with behavioral strength measured via mutation kill rate.

**Key Predictions:**
1. **Effectiveness:** Iterative refinement achieves ≥80% proof discharge rate within ≤10 iterations on held-out verified programs, outperforming zero-shot LLM synthesis and non-expert human specs under compute-matched conditions.
2. **Information Gradient:** Performance correlates positively with feedback dimensions. Full structured feedback (Condition C: Tag + Obligation + Witness) outperforms tag-only (Condition A) by ≥25%.
3. **Cross-Verifier Portability:** Semantic normalization enables ≥80% performance retention when transferring from one verifier (e.g., Frama-C) to another (e.g., Dafny/Why3).
4. **Non-Vacuity:** Mutation-based strength testing ensures synthesized specs kill ≥70% of mutants that expert specs kill, preventing specification weakening.

**Experimental Approach:** Benchmark on verified programs with gold ACSL/Dafny annotations. Ablate across information gradient (Conditions A/B/C) and refinement strategies (iterative vs. single-shot). Measure proof discharge rate, Strength Score (mutation kill rate), and cross-verifier/domain transfer performance. Enforce compute budgets and track specification strength via implication checks and mutation testing to guard against vacuity.

**Novelty:** First demonstration of verifier-as-teacher for specification synthesis (vs. code generation), semantic normalization for cross-tool transfer, and information-theoretic decomposition of feedback primitives.

**Expected Impact:** Enables formal verification for low-resource languages, legacy codebases, and rapid prototyping by eliminating the expert specification bottleneck.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** Information gradient ordering must be formally validated, not assumed. If witness instantiation outweighs logical structure non-monotonically, the ladder predictions collapse.
- **Concern 2:** Cross-domain transfer (systems code → mathematics → contracts) is a stronger claim than cross-verifier and may require >40% degradation tolerance, narrowing the core contribution.
- **Concern 3:** Semantic normalization's causal structure preservation (obligation dependencies, not just categories) must be demonstrated via ablation; underdetermined abstractions will fail cross-tool transfer.
- **Mitigation Strategy:** Pre-register regression analysis of feedback dimensions on Strength Score. Define explicit failure boundaries (>25% drop in A vs. C, >40% cross-domain degradation). Include tool-specific fallback baselines to quantify normalization value-add.

---

