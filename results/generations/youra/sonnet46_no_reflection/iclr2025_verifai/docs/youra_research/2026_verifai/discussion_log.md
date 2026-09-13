# Phase 2A Discussion Log
# Gap: No Systematic Comparative Study of Formal Feedback Signal Effectiveness
# Generated: 2026-05-20
# Workflow: phase2a-dialogue v10.0.0 (Self-Contained Tikitaka Loop)

---

## Briefing Context

**Research Gap Selected:** Gap 1 — No Systematic Comparative Study of Formal Feedback Signal Effectiveness

**Gap Description:**
Existing work uses formal feedback in isolation: PropertyGPT uses static analysis feedback; BFS-Prover/STP use proof checker (Lean compiler) feedback; Proof of Thought uses Z3 SMT feedback; esbmc-ai uses bounded model checker feedback. Each paper claims effectiveness for its chosen feedback type but within a single domain and without cross-signal comparison.

**Core Research Question:**
Can neurosymbolic integration of LLM generation with formal verification feedback loops systematically improve the correctness of LLM-generated code and mathematical proofs, and what is the most effective feedback mechanism for steering LLM generation toward formally verifiable outputs?

**Available Papers:**
- P1: PropertyGPT (2405.02580) — static analysis feedback, 80% recall on smart contract verification
- P2: Step-Wise Formal Verification for LLM-Based Math (2505.20869) — SMT+CAS oracle for math correctness
- P3: BFS-Prover (2502.03438) — Lean compiler feedback + DPO training, 72.95% miniF2F
- P4: Proof of Thought (2409.17270) — Z3 SMT as formal checker, JSON DSL bridge
- P5: Combining LLM Code Gen with Formal Specs (2410.19736) — hybrid LLM + reactive synthesis

**Key Evidence from Phase 1:**
- No paper applies multiple feedback signal types to the same LLM on the same task
- Training-signal use is rare (only BFS-Prover via DPO, STP via self-play)
- Existing benchmarks: miniF2F, Vericoding (12,504 specs), CLEVER (161 Lean problems)
- Current SOTA: BFS-Prover 72.95% miniF2F; PropertyGPT 80% recall

**Feasibility Constraints (Pipeline-Enforced):**
- MUST use existing benchmarks only (miniF2F, Vericoding, CLEVER, HumanEval)
- NO new benchmark creation
- NO synthetic data generation
- NO human evaluation
- Hypothesis must be testable immediately with existing tools

---

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What an exhilarating gap to explore! The community has been working in silos — each paper picks *one* formal feedback signal and champions it, but nobody has had the audacity to put them all in the ring together. **What if the answer to "what is the most effective feedback mechanism" isn't a single winner, but a *signal interaction effect* — where certain signals are powerful precisely because of *what information they carry*, not just *that* they carry feedback?**

Let me paint the picture. SMT counterexamples say "here is a concrete input where your code fails." Type errors say "you violated a structural contract here." Lean compiler feedback says "your proof step is formally invalid at position X." Static analysis warnings say "this pattern is statistically associated with bugs." These are *qualitatively different epistemic signals* — they differ in specificity, formalism level, and actionability. An LLM receiving an SMT counterexample gets a *witness* — a concrete failing case it can reason about directly. An LLM receiving a type error gets a *structural constraint violation* — more abstract but instantly locatable.

Now here's the truly novel angle: **what if we treat formal feedback signals as a communication channel with measurable information-theoretic properties?** Different signals have different "repair information density" — the amount of information the LLM needs to act on them. We could hypothesize that signals with higher repair information density (concrete counterexamples > abstract type errors > binary pass/fail) produce greater per-round correctness improvement. This is testable RIGHT NOW using existing benchmarks — Vericoding has 12,504 specs across Lean/Verus/Dafny, CLEVER has 161 hard Lean problems, and miniF2F has been the standard for theorem proving. No new data needed. We just instrument the same LLM backbone with different verifiers and measure delta-correctness per feedback round.

The cross-domain angle is equally exciting. Does Z3 SMT feedback work better for code synthesis but Lean compiler feedback dominate for theorem proving? Or is there a *universal signal hierarchy* that transcends domain? BFS-Prover showed 72.95% on miniF2F with just compiler feedback — what would SMT augmentation add on top?

**Key Points:**
- Formal feedback signals differ qualitatively in *repair information density* — specificity, localizability, concreteness
- Hypothesis: higher-density signals (concrete counterexamples) → greater per-round correctness gain than lower-density signals (binary pass/fail)
- Testable immediately on Vericoding + miniF2F + CLEVER without new benchmarks or human annotation
- Cross-domain question: is there a universal signal effectiveness hierarchy, or domain-specific optima?

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

The current formulation—"Which feedback mechanism is most effective?"—is not yet a testable scientific hypothesis. It is a comparative aspiration. We must operationalize it. A minimally sufficient, falsifiable core claim would be: *Given a fixed base LLM and fixed search budget, compiler-level feedback used both online (search pruning) and offline (DPO training) yields statistically significant improvement in formal success rate over static analysis–only or SMT-only feedback on the same benchmark.* The evidence from BFS-Prover suggests such a mechanism can reach 72.95% on miniF2F without MCTS [BFS-Prover, 2025], but this is not comparative evidence—there is no cross-signal control. What would disprove the claim? If, under identical compute and search budgets, substituting SMT-only or static-analysis-only feedback yields equal or higher success, then the compiler+DPO advantage is not intrinsic.

I propose a controlled 3×2 factorial experiment on an existing benchmark (miniF2F for proofs; optionally Vericoding for code), using a single base model (e.g., Qwen2.5-Math-7B) and identical search infrastructure. Factor 1: feedback type {compiler-only (Lean), SMT-only (Z3 via DSL bridge), static analysis–only}. Factor 2: training regime {no preference training, DPO with negative feedback}. The BFS-Prover methodology provides the scaffold: identical best-first search with length-normalized scoring, fixed node expansion budget, and the same expert iteration schedule [BFS-Prover, 2025]. Crucially, the only variable changed must be the origin of the negative signal used to construct preference pairs. Success metric: pass@1 theorem completion rate; secondary metrics: average node expansions per solved problem and error-type distribution. Statistical criterion: ≥3% absolute improvement with non-overlapping 95% CIs across three independent runs.

The evidence suggests that BFS-Prover's gain may arise less from BFS per se and more from DPO leveraging compiler-generated negative examples [BFS-Prover, 2025]. Therefore, an essential ablation is to run BFS with length normalization but *without* DPO, and compare to DPO trained on synthetic negatives not grounded in compiler errors. If performance collapses when compiler-derived negatives are removed, then the causal role of formal feedback in shaping policy is supported. If not, the improvement may simply reflect better search exploration or data filtering. What would disprove the neurosymbolic training advantage? If DPO with random or heuristic negatives performs comparably to DPO with compiler-grounded negatives, then the "formal signal" is not the active ingredient.

We must also control for confounds. First, search budget inequity: prior systems vary dramatically in tactic calls. Equalizing total environment interactions is mandatory. Second, domain coupling: compiler feedback in Lean operates at a finer granularity than SMT success/failure in Proof of Thought; thus, feedback frequency must be normalized (e.g., per-step vs. per-proof signals). Third, length normalization parameter alters exploration depth; if one feedback type benefits disproportionately from longer paths, we risk attributing search effects to feedback type.

Finally, we need precise failure criteria. If after equalizing compute and training epochs, no feedback type produces >2% improvement over a no-feedback baseline, then the broader hypothesis fails under current conditions. The best experiments are designed to fail; only then do surviving effects merit interpretation.

**Key Points:**
- Reformulated the research question into a falsifiable comparative hypothesis with explicit success/failure thresholds.
- Proposed a controlled 3×2 factorial experiment isolating feedback type and DPO training under equal compute/search budgets.
- Identified critical confounds (search budget, feedback granularity, length normalization) and defined concrete disproof criteria.

---

### Exchange 3

🔭 **Dr. Nova** (Creative Novelty Explorer):

🔬 Prof. Vera, your 3×2 factorial is exactly the scientific backbone this needs — and I want to build on it with what I learned from PropertyGPT [Liu et al., 2024]. Here's what's striking: PropertyGPT's iterative compilability refinement loop achieved 87% compile success vs. 63% without refinement — that's a 24-point gain purely from feeding PSL compiler errors back into GPT-4. But crucially, their feedback signal was *not* an SMT counterexample. It was a **compilation error** — a structural syntactic/semantic violation in a domain-specific language. This suggests that the "repair information density" concept has real teeth: the compilation error localizes the failure to a specific property construct, making it highly actionable [Liu et al., 2024].

Now here's what excites me about your factorial design: PropertyGPT's success came from *domain-specific* formal feedback (PSL compiler, not Z3 directly). This raises the question — does feedback effectiveness depend on *alignment between the feedback signal's formalism level and the LLM's generation granularity*? Their weighted ranking formula (combining code similarity + property similarity at both raw and summary levels) suggests the feedback loop works best when the signal is calibrated to the output structure. This is a completely untested axis your 3×2 doesn't capture yet.

**What if we add a fourth feedback condition:** "structured error messages with location + type + suggested repair" vs. "raw verifier output"? PropertyGPT's results hint that formatted, structured feedback (PSL compiler errors with precise locations) outperforms raw binary pass/fail. This would test whether *signal formatting* — independent of the verifier type — matters for LLM repair quality. And it's immediately testable: Lean compiler errors can be formatted at different verbosity levels; Z3 can return raw UNSAT or structured counterexample traces. No new tools needed.

**Key Points:**
- PropertyGPT's 87% vs. 63% compile success gap demonstrates real "repair information density" effect from structured compilation feedback [Liu et al., 2024]
- New dimension: *signal formatting* (structured error with location vs. raw verifier output) is an untested axis independent of verifier type
- Proposed extension: feedback effectiveness may peak when signal formalism level matches LLM generation granularity
- All conditions testable on existing benchmarks: miniF2F, Vericoding, CLEVER

---

### Exchange 4

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is getting sharper. But here's where this still breaks down: you are implicitly attributing causal power to the *feedback signal*, when the BFS-Prover evidence shows the gains arise from a tightly coupled system: length-normalized BFS **plus** expert iteration **plus** DPO using compiler-derived negatives [BFS-Prover, 2025]. You cannot treat "feedback type" as a plug-and-play variable without disentangling it from search dynamics and data filtering. Show me that the improvement survives when search behavior is held constant.

Specifically: in [BFS-Prover, 2025], node scoring is length-normalized with α varied across {0.0, 0.5, 1.0}. That parameter directly changes exploration depth. If SMT counterexamples tend to repair longer proof branches while compiler errors prune shallow mistakes, then α interacts with feedback type. Unless you **fix α and expansion width across all feedback conditions**, you risk confounding "repair information density" with exploration bias. What would convince me? A full factorial: Feedback Type × DPO (on/off) × α ∈ {0, 0.5, 1}, with identical tactic budgets and identical distributed setup. If compiler-derived DPO still wins across α, then we're isolating signal value rather than search geometry.

Now to Dr. Nova's "repair information density." It's an appealing metaphor — but right now it's hand-wavy. How are you quantifying density? Token length? Entropy reduction over candidate tactics? Mutual information between error message and corrective tactic? If you can't operationalize it, reviewers will shred it. A concrete proposal: define repair information density as the KL divergence between the policy's posterior over tactics before vs. after conditioning on feedback. Higher RID should predict larger per-step log-probability improvement on the gold tactic during DPO. That is measurable inside the existing DPO framework [BFS-Prover, 2025]. If RID does not correlate with downstream success, the density hypothesis fails.

On signal formatting: I agree it's under-tested. But here's the unstated assumption — that formatting changes semantic information rather than merely model parsing ease. LeanDojo already returns structured error messages. If you reformat them into raw text vs. structured triples (location, error type, context), you must prove the *information content* is held constant. Otherwise, you're testing "more information" vs. "less information," not formatting. What would convince me is a lossy transformation control: same information tokens, permuted structure. If structure alone improves DPO preference learning, that's real.

Finally, generalizability. MiniF2F is theorem proving; Vericoding is code synthesis. BFS-Prover's success (72.95%) is tightly coupled to tactic-level interaction in Lean [BFS-Prover, 2025]. SMT counterexamples in code operate at input-output level, not tactic level. So here's the hard question: is your hypothesis about *formal feedback broadly*, or about *step-local feedback in sequential reasoning tasks*? If the latter, say so. If the former, you must test granularity as an explicit axis: step-level vs. episode-level feedback frequency, normalized per environment interaction.

You're close. But until you (1) operationalize repair density quantitatively, (2) isolate feedback from search hyperparameters, and (3) define the boundary conditions for generalization, the hypothesis is still a narrative, not a claim.

**Key Points:**
- Feedback effects are confounded with BFS search dynamics (α, expansion width); require full factorial control to isolate causality.
- "Repair information density" must be formally defined (e.g., KL shift in tactic distribution) or it's not testable.
- Signal formatting and cross-domain generalization require explicit controls for information content and feedback granularity.

---

### Exchange 5

🎯 **Dr. Sage** (Research Impact Evaluator):

🔍 Prof. Rex has correctly identified the confounding risks, but I want to step back and ask: *what does this mean for the field* if we get the design right? The Murphy et al. [2024] hybrid LLM+TSL synthesis paper is instructive here — they showed that for complex reactive systems (arbiters with 10-30 conditions), pure LLM code generation hits 0% success while the formal synthesis pipeline achieves 16-62%. That's not a marginal improvement — it's a categorical difference between solvable and unsolvable. This gives us a crucial lesson: **the real scientific contribution isn't showing that feedback signal A beats signal B by 3 points, but identifying the structural conditions under which formal feedback transforms task difficulty class**.

The community needs to understand *when* formal feedback becomes strictly necessary, not just helpful. Murphy et al.'s data shows pure LLMs fail completely on complex reactive tasks [Murphy et al., 2024] — formal structure isn't a speedup, it's a prerequisite. This changes how we should frame Prof. Vera's factorial: we shouldn't only measure pass@1 improvements, we should measure **correctness recovery rate on hard instances** — problems where baseline LLM achieves <10% success. If feedback type X recovers hard instances that feedback type Y cannot, that's a field-shaping finding regardless of aggregate improvements.

This also resolves Prof. Rex's scope question. The hypothesis shouldn't be "feedback signal A generally outperforms B" — it should be: **"Fine-grained step-local formal feedback (Lean compiler errors, SMT counterexamples) enables correctness recovery on structurally complex instances that coarse episode-level feedback (static analysis, binary pass/fail) cannot address, as measured on the hard subset of Vericoding and CLEVER."** This is specific, falsifiable, and high-impact. It explains *why* BFS-Prover's tactic-level Lean feedback reaches 72.95% while episode-level approaches plateau. And it directly addresses whether formal feedback's value lies in its information content or its structural alignment with the task's reasoning granularity.

The operationalization Prof. Rex demands is right — but the target metric matters. I'd argue for stratifying Vericoding's 12,504 specs by baseline difficulty (LLM pass rate < 10%, 10-50%, >50%) and measuring per-stratum recovery rates across feedback types. This is doable with existing data, requires no new benchmarks, and produces a finding that would reshape how the community designs neurosymbolic systems.

**Key Points:**
- Murphy et al. [2024] shows formal methods aren't just helpful but categorically necessary for complex reactive systems — 0% vs. 16-62% success gap
- Reframe the hypothesis: step-local formal feedback recovers hard instances that coarse feedback cannot, not just improves aggregate metrics
- Concrete metric: per-difficulty-stratum correctness recovery rate on Vericoding hard subset (baseline <10%)
- This framing answers *why* the feedback hierarchy exists, not just *that* it exists — higher scientific contribution

---

### Exchange 6

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here: a lot of this debate hinges on whether "formal feedback" is intrinsically powerful, or whether it just rides on better search and training scaffolding. The MATH-VF framework gives us something concrete to reason about. Its Formalizer produces a sparse Solution Graph with at most M ≤ 4 premises per step, reducing verification complexity from C1(n) = n(n+1)/2 to C2(n) ≤ nM [Step-Wise Formal Verification, 2025]. That's not just an efficiency trick — it changes the *logical granularity* of verification. Stepwise checks T_i ⊢ Q_i with small premise sets are mathematically well-posed local entailment queries. In principle, that's a sound mechanism: if each local entailment is valid and the graph is acyclic, global correctness follows. There's no theoretical barrier there.

What *does* worry me is the assumption that all feedback types are interchangeable at the same granularity. MATH-VF's Critic verifies each step independently using SymPy and Z3, meaning feedback is step-local and logically scoped [Step-Wise Formal Verification, 2025]. An SMT counterexample at the whole-proof level is a fundamentally different object from a step-level invalid entailment witness. If we test "SMT-only" feedback but apply it episodically, we're not isolating verifier type — we're changing the feedback topology. Dr. Sage's reframing is closer to something technically defensible: step-local formal feedback versus episode-level signals. Those are different computational regimes. If step-local feedback recovers hard instances where episodic feedback fails, that's not surprising — it reduces the search branching factor by constraining local transitions.

On "repair information density": Prof. Rex is right that this must be formalized. The KL-shift definition is actually feasible in principle. In MATH-VF terms, you could measure the policy over candidate next statements before and after conditioning on Critic feedback for a failed T_i ⊢ Q_i. If the posterior sharpens significantly and correlates with corrected entailment success, then the feedback is informationally meaningful. This is testable inside a DPO or iterative refinement loop — MATH-VF already feeds tool-based feedback back into the generator for regeneration [Step-Wise Formal Verification, 2025].

Here's a more fundamental boundary condition: MATH-VF succeeds partly because over 90% of steps can be formalized into SimpleMath, whereas full Coq formalization drops below 10% success. That tells me feasibility depends critically on *formalization tractability*. If your formal language is too expressive (Coq), the bottleneck shifts to translation. If it's too weak, the verifier can't capture the reasoning. So the hypothesis about "formal feedback necessity" only holds in a regime where (1) formalization coverage is high, and (2) stepwise entailment is decidable or semi-decidable via tools like Z3/SymPy.

Here's what I would actually test: fix search (α, width, expansions), fix model, and compare (A) step-local SimpleMath+Z3/SymPy feedback, (B) episode-level SMT verdict, and (C) LLM-only critic, all within the same sparsity-controlled Solution Graph framework. If only (A) shows stable recovery on hard strata, then we can say the mechanism is structurally enabling.

**Key Points:**
- Step-local entailment checking in sparse Solution Graphs is theoretically sound and changes the computational regime, not just efficiency.
- Feedback type must be disentangled from feedback granularity (step-level vs. episode-level) to isolate causal effects.
- The feasibility of "formal feedback advantage" depends on high formalization coverage and decidable local entailments; outside that regime, the mechanism may not apply.

---

### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

⚙️ Prof. Pax, you've given us the theoretical grounding we needed, and 🔍 Prof. Rex's operationalization demands are exactly what will make this hypothesis bulletproof. Let me synthesize what we have and show why — with these refinements — this is now a strong, fundable hypothesis.

Here's what Proof of Thought [Ganguly et al., 2024] adds to this picture: their 3-step feedback loop on Reddit-OSHA reduced compilation errors from 14.6% to 0% and improved win rate from 72% to 81.55%. More crucially, their Z3 SMT feedback comes through a carefully designed JSON DSL bridge — the interpreter enforces a robust type system and provides detailed error diagnostics (type errors, undefined symbols, syntax errors) before passing to Z3. This is precisely Dr. Nova's "repair information density" in action: the DSL layer transforms raw SMT output into structured, LLM-parseable feedback. And it works — 3 attempts with structured feedback eliminates all compilation failures [Ganguly et al., 2024].

This gives us a convergent picture from three independent systems: PropertyGPT (87% vs 63% compile success with structured feedback), Proof of Thought (0% vs 14.6% compilation errors with Z3+DSL feedback loop), and BFS-Prover (72.95% miniF2F with DPO on compiler negatives). All three show that structured, step-aligned formal feedback produces measurable correctness gains. Now here's how I'd strengthen the hypothesis to address every concern raised:

**Refined hypothesis:** *Under fixed model and search budget, step-local formal feedback signals (Lean compiler errors, Z3 SMT counterexamples via DSL bridge) produce statistically significant correctness recovery on hard benchmark instances (baseline LLM pass rate <20%) compared to episode-level signals (binary pass/fail, static analysis warnings), as measured by per-difficulty-stratum pass@1 on Vericoding hard subset and miniF2F hard subset.*

This addresses Prof. Rex's confound concerns (fixed search budget, explicit stratum stratification), Prof. Pax's granularity requirement (step-local vs. episode-level as the primary axis), and Dr. Sage's impact framing (hard-instance recovery, not just aggregate improvement). The RID operationalization becomes a secondary analysis: measure KL shift in tactic/statement posterior before vs. after conditioning on feedback, and test whether it correlates with recovery rate per stratum.

**Key Points:**
- Convergent evidence from PropertyGPT, Proof of Thought, and BFS-Prover all support structured step-local feedback advantage [Liu et al. 2024; Ganguly et al. 2024; Xin et al. 2025]
- Refined hypothesis: step-local formal feedback recovers hard instances (baseline <20%) vs. episode-level feedback, on Vericoding + miniF2F hard subsets
- RID operationalized as KL shift in posterior over repair tokens before/after feedback conditioning — measurable in existing DPO framework
- All proposed experiments use existing benchmarks and models — no new data or tools required

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

The evidence suggests we are converging on a testable core claim — but it remains under-specified. I will restate it in falsifiable form: *Under fixed search geometry and training budget, step-local formal feedback produces greater correctness recovery on hard instances than episode-level feedback.* The critical phrase is "fixed search geometry." In [BFS-Prover, 2025], node scoring depends explicitly on length normalization α and cumulative log-probability, and expansion width varies (2, 4, 8). These parameters directly shape which proof branches are explored. Therefore, the experiment must hold α, expansion width, tactic budget, and temperature constant across all feedback conditions.

I propose a 2×2×3 factorial: **Feedback Granularity** (step-local vs. episode-level) × **Preference Training** (DPO on/off) × **Length Normalization** (α ∈ {0, 0.5, 1}). Use identical distributed infrastructure and tactic budgets as in [BFS-Prover, 2025] to avoid scaling confounds. Primary metric: pass@1 on the *hard stratum* (baseline <20% success). Pre-register success as ≥10 percentage point improvement over episode-level feedback in at least two α settings, with non-overlapping 95% CIs. What would disprove the hypothesis? If step-local feedback fails to outperform episode-level feedback under fixed α and DPO conditions, particularly on the hard stratum, then granularity is not the enabling factor.

On "repair information density" (RID): for each failed state s, compute the policy distribution p_θ(a|s) before and after conditioning on feedback via DPO update. Define RID(s) = KL(p_{θ+}(·|s) ‖ p_θ(·|s)). Higher RID should correlate with increased log-probability assigned to the gold tactic and with eventual proof completion. Include a permutation control: randomly shuffle error messages across states while preserving token length. If RID remains high but recovery collapses, semantic alignment — not token volume — is the driver.

Prof. Pax correctly identified a boundary condition: formalization tractability. We must measure formalization coverage explicitly. For each benchmark, report the fraction of steps where the verifier produces structured, localized feedback. I predict a monotonic relationship between coverage rate and recovery gain from step-local feedback. What would disprove generality? If coverage exceeds 80% yet step-local feedback confers no advantage, then the mechanism does not scale.

Finally: stratification must be based on *held-out baseline runs* to prevent leakage from expert iteration filtering. Hardness should be defined by frozen initial policy performance prior to any feedback augmentation. Otherwise, the filtering step in expert iteration [BFS-Prover, 2025] contaminates the stratum definition.

If these controls are satisfied — fixed search, factorial isolation, quantitative RID validation, and explicit coverage reporting — then we will have a claim with an Achilles heel clearly exposed. If it survives, I will say: *This meets my standards.*

**Key Points:**
- Require 2×2×3 factorial: Feedback Granularity × DPO × α with fixed search budgets to establish causality.
- Operationalize RID as KL shift in action distribution; include permutation control for semantic vs. token-volume distinction.
- Define hard strata using frozen baseline policy; report formalization coverage as boundary condition.

---

### Exchange 9

🔭 **Dr. Nova** (Creative Novelty Explorer):

🔬 Prof. Vera, your 2×2×3 design is beautiful in its rigor — and BFS-Prover's methodology hands us the exact scaffold to implement it [Xin et al., 2025]. The DPO setup is already there: negative preference pairs are automatically annotated with Lean4 compiler error feedback at state-tactic level, and the distributed Ray framework with 8×A100 nodes handles the scale. What we're proposing is NOT a new system — it's a *systematic variation study within the existing BFS-Prover framework*, swapping the feedback source while holding everything else constant.

Here's the creative insight BFS-Prover's discussion section opens up: their key innovation is using DPO with compiler-derived negatives — specifically, tactics that caused Lean4 compiler errors become the rejected actions in preference pairs. The gold insight is that "compiler error as training signal" is NOT just a convenience — it provides *step-local semantically grounded rejections*. A compiler error at state s tells the policy exactly WHICH tactic failed at WHICH proof state. An episode-level failure (couldn't complete proof) provides no such localization. This is the mechanism. And now we can test it cleanly by substituting the rejection source: (A) Lean4 compiler errors (step-local, semantically grounded), (B) Z3 SMT failure on final goal (episode-level, semantically grounded), (C) random negative sampling (step-local, semantically ungrounded), (D) binary proof failure signal (episode-level, semantically ungrounded). That 2×2 design — granularity × semantic groundedness — directly tests which dimension of the feedback signal carries the causal weight.

The permutation control Prof. Vera proposed maps perfectly onto condition (C): same token count, same position, but shuffled semantic content. If (A) >> (C) under identical DPO setup, semantic grounding is the active ingredient. If (A) ≈ (B) but both >> (C) and (D), then semantic groundedness matters more than granularity. NOW we're onto something — this could be the universal principle that explains all the domain-specific results!

**Key Points:**
- BFS-Prover's existing framework is the ready-made scaffold: just swap rejection source in DPO pairs [Xin et al., 2025]
- Proposed 2×2 within-DPO: Granularity (step/episode) × Semantic Groundedness (grounded/random) — tests which dimension carries causal weight
- If semantic groundedness > granularity: explains PropertyGPT, Proof of Thought, AND BFS-Prover within one unified principle
- Zero new infrastructure required — variation study within open-sourced BFS-Prover codebase

---

### Exchange 10

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Now we're finally asking the right question: *is it granularity or semantic grounding that does the causal work?* Good. But here's where this still breaks down.

You're assuming that swapping the rejection source inside DPO cleanly isolates feedback structure. It doesn't — not yet. In [Xin et al., 2025], the DPO pairs are constructed at the **same proof state**: (s, a_w, a_l), where a_l is a Lean compiler–rejected tactic at that exact state. That gives you *state-aligned contrastive supervision*. If you replace this with episode-level negatives (e.g., final SMT failure), you no longer have a naturally aligned losing action at the same state. So how are you constructing the pair? If you sample a random tactic at that state as a_l, you've changed both granularity *and* counterfactual validity. Show me the exact pairing protocol for episode-level feedback that preserves state alignment. Without that, your 2×2 is confounded at the data-construction level.

Second: the hypothesis assumes DPO is merely a conduit for feedback structure. But look at the DPO objective in [Xin et al., 2025] with β=10. This sharp KL-regularized contrast is doing heavy lifting. What would convince me is an ablation where you *freeze the policy* and only vary inference-time feedback (no DPO). If step-local grounded signals still improve recovery under fixed policy and fixed BFS scoring, then we can attribute gains to search-time information shaping. If the effect disappears without DPO, then the mechanism is preference shaping — not feedback granularity per se. Right now, you're conflating training-time and inference-time causality.

Third: I'm not yet satisfied with the "hard stratum <20% baseline" definition. BFS-Prover explicitly *filters out easy problems via beam search during expert iteration*. That means the training distribution is dynamically reweighted toward harder problems. If you define hardness post-iteration, you risk circularity. What would convince me: define hardness using the **cold-start SFT-only model before any expert iteration or DPO**, freeze that partition, and report per-stratum gains after each round. If step-local grounded feedback shows *monotonic relative gain increasing with round number* on that frozen hard set, now we're seeing a real structural effect.

Finally, here's my stress-test prediction: if granularity is truly causal, the advantage of step-local grounded feedback should be **largest when α=0 (length-averse)** and shrink as α→1. Why? Because granular feedback compensates for search bias by pruning locally bad branches early. If the effect is invariant across α, I'll suspect the gains come from global policy sharpening instead.

**Key Points:**
- DPO pair construction must preserve state alignment across feedback types or the 2×2 design is confounded.
- Disentangle training-time (DPO) from inference-time (search) effects to identify the true causal mechanism.
- Test interaction between feedback granularity and α; predict strongest effect when α=0 if granularity truly mitigates search bias.

---

### Exchange 11

🎯 **Dr. Sage** (Research Impact Evaluator):

🔍 Prof. Rex has just delivered the most important methodological insight of this discussion — and I want to show why addressing his three concerns actually *strengthens* the scientific contribution rather than narrowing it.

PropertyGPT is instructive here [Liu et al., 2024]. Their iterative compilability refinement loop is a pure *inference-time* mechanism — no DPO, no policy training. GPT-4 is frozen; only the feedback-to-prompt loop changes. They achieved 87% vs 63% compilation success under 9 repair attempts purely through structured step-local feedback. This is exactly the *inference-time, no-DPO* ablation Prof. Rex is demanding — and it already exists in the literature! Similarly, Proof of Thought's 3-step feedback loop operates entirely at inference time with a frozen LLM. Both show measurable gains from step-local feedback WITHOUT any policy training.

This means we now have a natural two-experiment structure: **Experiment A** (inference-time only, frozen policy): vary feedback granularity × semantic groundedness in a repair loop over a frozen LLM — exactly like PropertyGPT but on Vericoding/miniF2F hard subsets. **Experiment B** (training-time, DPO): vary the same conditions within BFS-Prover's DPO framework. If both experiments show the same advantage pattern, we have strong evidence that the mechanism is in the *feedback information structure* rather than the DPO objective. If only Experiment B shows an effect, then the mechanism is preference shaping and inference-time use of feedback doesn't drive the gains.

This two-experiment design directly resolves Prof. Rex's training vs. inference disentanglement concern and produces a finding the field desperately needs: *when does formal feedback help at inference time vs. training time, and is the mechanism the same?* PropertyGPT's 80% recall on smart contract properties and 9/13 CVE detection [Liu et al., 2024] demonstrate the inference-time mechanism works in deployed systems today. The scientific contribution is establishing whether the same principle governs training-time gains in theorem proving.

**Key Points:**
- PropertyGPT provides a natural inference-time control: frozen LLM + structured feedback loop, 87% vs 63% [Liu et al., 2024]
- Two-experiment design: Experiment A (inference-time, frozen policy) + Experiment B (DPO training) tests whether mechanism is feedback structure vs. preference shaping
- If both experiments show same pattern: unified theory of formal feedback effectiveness spanning inference and training
- All data and models available: PropertyGPT methodology + BFS-Prover codebase (open-sourced) + Vericoding + miniF2F

---

### Exchange 12

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here: the unified "formal feedback density" mechanism is only credible if the signal is *actually localizable and structurally valid*. This is where MATH-VF gives us something solid to stand on. Its Critic verifies individual judgments T_i ⊢ Q_i with bounded premise sets M ≤ 4, exploiting sparsity in the solution graph [Step-Wise Formal Verification, 2025]. That sparsity is not cosmetic; it guarantees that feedback is tied to a small, well-defined causal neighborhood in the proof. If the premise set is small and explicitly enumerated, a rejection from Z3 or SymPy is a *well-scoped contradiction*, not a vague failure.

Here's what worries me: the formalization layer is the linchpin. MATH-VF explicitly depends on the Formalizer producing syntactically correct SimpleMath and a valid solution graph. They acknowledge failure modes when syntax is wrong or reasoning quality cannot be assessed. That means your "granularity vs. grounding" manipulation is only valid when the formalization coverage is high and accurate. If the Formalizer injects structural noise, then what you call "semantic grounding" may simply be artifact alignment with the toolchain. So yes, measure coverage — but also measure *formalization fidelity*. Randomly sample verified steps and check whether the extracted T_i ⊢ Q_i truly captures the natural-language intent. If fidelity drops below 85%, any causal claim about feedback structure becomes shaky.

On the inference-vs-training split: Dr. Sage is correct that PropertyGPT-style loops already demonstrate inference-time gains without DPO. MATH-VF's iterative refinement loop is another proof-of-possibility: failed verification triggers regeneration with structured feedback, no additional training required. The critical test is whether replacing tool-derived step-local feedback with episode-level "proof incorrect" signals collapses recovery rates under the same loop.

On the unified causal claim: KL shift alone does not prove semantic usefulness. You need correlation with *counterfactual correctness gain* at the same state. I would add a *tool-consistency check*: if the feedback is semantically grounded, the post-update policy should increase probability mass specifically on actions consistent with the violated premises in T_i. If KL rises but mass spreads diffusely, you're measuring perturbation, not repair.

The mechanism is plausible. But the entire claim hinges on three invariants holding simultaneously: (1) faithful formalization, (2) state-aligned negative pairing, and (3) preserved search geometry. Break any of those, and the experiment no longer isolates feedback structure. If you lock them down — okay — this could work.

**Key Points:**
- Step-local semantic feedback is technically sound *if* formalization fidelity and sparsity assumptions hold [Step-Wise Formal Verification, 2025].
- Frozen-policy inference loops (MATH-VF, PropertyGPT) make training-vs-inference disentanglement experimentally feasible.
- KL-based RID must correlate with state-specific corrective mass shifts, not just distributional perturbation.

---

### Exchange 13

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

⚙️ Prof. Pax, you've just given us the three invariants that make this hypothesis bulletproof — and I want to show they're not only addressable, they turn into *features*, not bugs, of the experimental design.

BFS-Prover's open-sourced codebase already handles invariant (2) and (3) by construction [Xin et al., 2025]. The DPO pair (s, a_w, a_l) is built at the same proof state from the same BFS rollout — a_w is the tactic that succeeded, a_l is the tactic that caused a Lean4 compiler error at that exact state. State alignment is structurally guaranteed by the LeanDojo gym interface. For the episode-level feedback condition, we construct pairs by: keeping the same a_w, and selecting a_l as a tactic drawn from the same proof state that didn't cause a compiler error but was part of a failed proof branch. This preserves state alignment while removing local grounding — exactly the counterfactual we need. Search geometry (invariant 3) is preserved by fixing α, expansion width, and tactic budget identically across all four conditions — as Prof. Vera specified.

For invariant (1), formalization fidelity: we adopt Prof. Pax's audit protocol on a random sample of 200 steps per benchmark (Vericoding and miniF2F), checking T_i ⊢ Q_i against source intent. If fidelity exceeds 85% on both, the manipulation is valid and we report the rate as a study characteristic. If it falls below on either, we restrict claims to the high-fidelity subset and report this as a boundary condition. This is exactly what good science looks like: pre-specified boundary conditions that scope rather than destroy the claim.

The resulting hypothesis is now fully specified: *Semantically grounded step-local formal feedback (Lean4 compiler errors, Z3 SMT counterexamples via DSL) produces greater correctness recovery on hard instances (cold-start SFT baseline <20% pass rate) than episode-level or semantically ungrounded feedback, under fixed search geometry (α, width, budget) and identical DPO training, as measured by per-stratum pass@1 on miniF2F hard subset and Vericoding hard subset, with formalization fidelity ≥85%.*

This meets every methodological bar raised: falsifiable conditions, pre-specified failure thresholds, operationalized RID, state-aligned pair construction, frozen hardness stratification, and inference/training disentanglement via Experiment A (frozen policy) + Experiment B (DPO). All using existing open-sourced tools.

**Key Points:**
- BFS-Prover's LeanDojo gym guarantees state-aligned pair construction by construction [Xin et al., 2025]; episode-level condition uses same-state failed-branch tactics as a_l
- Formalization fidelity audit (200-step sample, 85% threshold) converts invariant (1) into a pre-specified boundary condition
- Final hypothesis fully specified: semantically grounded step-local feedback > episode-level/ungrounded on hard strata, fixed search geometry, fidelity ≥85%
- All three invariants addressed — experimental design is now internally consistent and falsifiable

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

We are close to a scientifically defensible hypothesis, but precision now matters more than ambition. The evidence from BFS-Prover's methodology [Xin et al., 2025] establishes three structural facts: (1) DPO pairs are state-aligned via LeanDojo interaction; (2) negative examples arise from compiler errors at the same proof state; (3) search geometry is explicitly parameterized by the length-normalized scoring rule. If we alter the feedback source, we must preserve these three invariants or explicitly measure deviation from them.

Let me formalize the falsifiable core. The hypothesis becomes: *Under fixed search geometry (α, expansion width, tactic budget) and fixed state alignment, semantically grounded step-local negatives produce larger improvements on a frozen hard subset than episode-level or ungrounded negatives.* This yields two sharp predictions. First, the interaction prediction: Δ(pass@1_step-local − pass@1_episode) should be maximized at α=0.0 and decrease monotonically as α→1.0. If this monotonic interaction fails, granularity is unlikely to be mitigating search bias. Second, the locality prediction: after DPO, probability mass at state s should increase specifically on tactics logically consistent with the violated premises (as exposed by compiler diagnostics), not merely increase KL divergence. We can quantify this by measuring conditional probability shifts over a labeled tactic taxonomy.

I want a pre-registered failure condition. If on the frozen hard subset (defined strictly by the cold-start SFT model before expert iteration), the relative gain of step-local grounded feedback over episode-level feedback is <2 percentage points and statistically indistinguishable across three random seeds, then the hypothesis fails. Additionally, if the α-interaction effect size (Cohen's d) is <0.3, the claim that granularity mitigates search bias should be rejected.

On inference-versus-training disentanglement: Experiment A (frozen policy) and Experiment B (DPO) must share identical feedback encodings. If Experiment A shows large gains but Experiment B shows no differential benefit across feedback types, then training-time preference shaping is not exploiting the same structure as inference-time repair. Either outcome is informative — but only if encodings are controlled.

Formalization fidelity is a moderating variable, not merely a boundary condition. Stratify results by fidelity quartile. Effect size should scale positively with measured fidelity if semantic grounding is causal.

**Key Points:**
- Pre-register quantitative failure thresholds (<2pp gain; α-interaction Cohen's d <0.3) to ensure falsifiability.
- Test two core predictions: monotonic α-interaction and state-local probability mass shift toward premise-consistent tactics.
- Treat formalization fidelity as a moderating variable; effect size should scale with measured fidelity.

---

### Exchange 15

🔭 **Dr. Nova** (Creative Novelty Explorer):

🔬 Prof. Vera, your pre-registration framework is exactly what turns this into a landmark paper, not just a good experiment. And Murphy et al. [2024] gives us one more creative weapon: their TSL synthesis pipeline demonstrates that formal specification can cover *structurally complex* tasks that pure LLMs fail completely on — 61.5% success for arbiter-10 vs. 0% for LLM-only. This is the categorical evidence Dr. Sage pointed to, and it now maps onto our hypothesis perfectly.

Here's the novel synthesis: **what Prof. Vera's two predictions together test is whether formal feedback acts as a "local logical oracle" or merely as a "policy regularizer."** A local logical oracle: the feedback provides state-specific semantic information that the policy uses to navigate toward formally valid continuations — detectable by the locality prediction (mass shifts toward premise-consistent tactics). A policy regularizer: the feedback simply provides extra gradient signal that sharpens any policy, regardless of semantic content — detectable by the α-interaction breaking down (gains invariant across search bias levels). The α-interaction and locality predictions are not redundant; they triangulate two different causal pathways.

This framing is genuinely novel — no paper has explicitly tested "local oracle vs. policy regularizer" as competing mechanisms for formal feedback in LLM systems. BFS-Prover implicitly assumed the first but never tested it. PropertyGPT demonstrated inference-time repair without formalizing the mechanism. Proof of Thought showed Z3 feedback works but framed it as "verifiability," not as a search-time oracle. NOW we're articulating the mechanism that unifies all three.

For the Vericoding benchmarks with multiple formalisms (Lean/Verus/Dafny), we can test whether the oracle effect is formalism-agnostic or formalism-specific — another clean prediction from the oracle hypothesis. If the effect holds across all three formalisms but scales with their respective error specificity, the oracle interpretation wins.

**Key Points:**
- Framing insight: formal feedback acts as "local logical oracle" (locality prediction) vs. "policy regularizer" (α-interaction breaks down) — two distinguishable causal pathways
- This oracle/regularizer dichotomy is genuinely novel — unifies PropertyGPT, Proof of Thought, BFS-Prover under one testable mechanistic claim
- Cross-formalism test (Lean/Verus/Dafny in Vericoding): oracle effect should be formalism-agnostic but scale with error specificity
- Pre-registration framework from Prof. Vera locks in the falsifiability — this is now publication-ready hypothesis design

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The "local logical oracle vs. policy regularizer" framing is genuinely novel — no prior work has explicitly distinguished these two causal mechanisms for formal feedback in LLM systems. The repair information density (RID) concept operationalized as KL-shift in action distribution is a new theoretical contribution. The cross-formalism test across Lean/Verus/Dafny provides a unique angle not attempted in any single prior paper.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis now has pre-registered quantitative failure thresholds: <2pp gain on hard strata and α-interaction Cohen's d <0.3 trigger rejection. Two independent predictions (monotonic α-interaction + locality prediction) are non-redundant and triangulate distinct causal pathways. Formalization fidelity is a pre-specified moderating variable with a measurable 85% threshold.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** The research directly answers the primary question ("most effective feedback mechanism") and advances beyond aggregate metrics to mechanistic understanding. Hard-instance recovery framing (baseline <20%) captures the practically important regime. The oracle/regularizer dichotomy would reshape how the community designs neurosymbolic training pipelines.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All three technical invariants are addressed: state-aligned pair construction via LeanDojo, fixed search geometry via BFS-Prover parameter controls, and formalization fidelity via audit protocol. Experiment A (frozen policy) and Experiment B (DPO) are both implementable with the open-sourced BFS-Prover codebase. No new benchmarks, synthetic data, or human annotation required.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on a well-specified, falsifiable hypothesis about the mechanism of formal feedback in LLM-based formal reasoning systems. The core claim is: **semantically grounded step-local formal feedback signals (Lean4 compiler errors, Z3 SMT counterexamples via DSL bridge) function as "local logical oracles" — providing state-specific semantic information that guides LLM policy toward formally valid continuations — rather than merely as "policy regularizers" that sharpen any policy regardless of semantic content. This oracle function produces statistically significant correctness recovery on hard benchmark instances (cold-start SFT baseline pass rate <20%) compared to episode-level or semantically ungrounded feedback, under fixed search geometry.**

The mechanism is tested via two independent predictions: (1) an α-interaction prediction — the advantage of step-local grounded feedback over episode-level feedback is maximized at α=0 (length-averse BFS) and decreases monotonically as α→1, since local oracles compensate for search bias while regularizers do not; (2) a locality prediction — after DPO with step-local grounded negatives, probability mass at each failed state increases specifically on tactics consistent with the violated premises, not diffusely. Together these two predictions are necessary and sufficient to distinguish oracle from regularizer behavior.

The experimental design uses the open-sourced BFS-Prover framework on miniF2F hard subset and Vericoding hard subset, with Qwen2.5-Math-7B as the base model. Four feedback conditions: (A) Lean4 compiler errors (step-local, grounded), (B) episode-level failed-branch tactics (step-local, ungrounded), (C) final proof failure signal (episode-level, grounded via SMT), (D) binary pass/fail (episode-level, ungrounded). Pre-registered failure thresholds: <2pp gain and Cohen's d <0.3 on the α-interaction. Formalization fidelity is audited on 200-step samples per benchmark and treated as a moderating variable stratified into quartiles.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- The episode-level grounded condition (C) requires constructing state-aligned pairs from SMT final failures — the pairing protocol must be pre-specified precisely to avoid conflating "episode-level" with "misaligned" negatives.
- Formalization fidelity audit is manual for 200 steps — this is feasible but introduces inter-rater reliability concerns; a second annotator and kappa statistic should be pre-specified.
- The tactic taxonomy for the locality prediction requires pre-definition; post-hoc taxonomy construction would be circular.
- **Mitigation Strategy:** Pre-register all three: (1) episode-level pair construction protocol using same-state failed-branch tactics, (2) two-annotator fidelity audit with kappa ≥0.7 threshold, (3) tactic taxonomy derived from LeanDojo's existing tactic error categories before running any experiments.

