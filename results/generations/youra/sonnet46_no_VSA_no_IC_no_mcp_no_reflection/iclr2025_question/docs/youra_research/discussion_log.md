# Phase 2A Discussion Log
## Gap: Lack of Systematic Black-Box UQ Benchmark Comparison Across Factual QA Datasets

**Gap ID:** gap-1
**Priority:** HIGH + PRIMARY
**Workflow:** phase2a-dialogue
**Architecture:** Self-Contained Tikitaka Loop (independent-controller ablation — no external orchestrator)
**Execution Mode:** UNATTENDED
**Date:** 2026-08-31

---

## Briefing Context

### Research Gap
No controlled, apples-to-apples comparison exists between sampling-based semantic consistency and token-probability baselines across TriviaQA, NaturalQuestions, HaluEval, and TruthfulQA in a strict black-box setting.

### Key Papers Available
- P1: Kuhn et al. 2023 — Semantic Uncertainty (arXiv:2302.09664) — NLI clustering + entropy; TriviaQA/NQ
- P2: Manakul et al. 2023 — SelfCheckGPT (arXiv:2303.08896) — black-box NLI consistency; WikiBio only
- P3: Wang et al. 2022 — Self-Consistency (arXiv:2203.11171) — majority vote; reasoning tasks
- P4: Lin et al. 2022 — TruthfulQA (arXiv:2109.07958) — benchmark definition
- P5: Li et al. 2023 — HaluEval (arXiv:2305.11747) — hallucination classification benchmark

### Available Benchmarks (Confirmed Existing)
- TriviaQA, NaturalQuestions, TruthfulQA, HaluEval, POPE

### Feasibility Constraints (MANDATORY)
- NO new benchmarks or scoring frameworks
- NO synthetic/generated data
- NO human evaluation or annotation
- MUST be testable with existing datasets and benchmarks

### Previous Failure / Routing Context
None — first Phase 2A execution.

---

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

The gap before us is genuinely exciting — not because the individual components are new (SelfCheckGPT and Semantic Uncertainty are well-established), but because the *systematic comparison* has never been done. Let me propose what I see as the most novel framing: rather than treating this as a methods-comparison paper, we should frame it as an *uncertainty signal characterization* study.

Here's my angle: SelfCheckGPT [Manakul et al., 2023] demonstrated that N stochastic samples can be used to detect hallucination via NLI consistency — but only on WikiBio (open-ended biographical generation). Semantic Uncertainty [Kuhn et al., 2023] used a more principled entropy-over-equivalence-classes formulation on TriviaQA/NQ — but crucially, it never tested on HaluEval or TruthfulQA, and it compared against semantic-level entropy, not token-probability baselines under black-box constraints.

The novel contribution I'd propose: **a unified uncertainty signal benchmark (USB-QA)** that characterizes — wait, no. Feasibility constraint: no new benchmarks. Let me reframe.

The novel contribution: **a systematic characterization of sampling-based semantic consistency as a hallucination predictor across all four existing factual QA benchmarks**, with the key insight being whether the signal is *benchmark-invariant* or *benchmark-specific*. If consistency-AUROC is stable across TriviaQA, NQ, HaluEval, and TruthfulQA, we've demonstrated a genuinely universal black-box uncertainty signal. If it varies, the pattern of variation is itself a novel finding.

I'd further propose a sub-hypothesis: **the NLI-based consistency signal will outperform token-probability baselines specifically on TruthfulQA** because TruthfulQA's adversarial questions exploit models' tendency to confidently produce wrong answers — high token probability but *low semantic consistency across samples*. This dissociation is the theoretical heart of the novelty.

**Key Points:**
- Frame as characterization of signal universality, not just method comparison
- Novel prediction: dissociation between token probability and semantic consistency specifically on TruthfulQA
- Existing benchmarks fully sufficient — no new data required
- Core claim: sampling-based semantic consistency is benchmark-invariant as a hallucination predictor

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises a compelling angle, but I want to sharpen the falsifiability before we get too excited about the "universality" framing. Let me push on three things.

First, the TruthfulQA dissociation prediction is testable and I like it — but we need to be precise about *what metric* on TruthfulQA we're using. TruthfulQA has both multiple-choice (MC) and open-ended formats. The MC format requires only binary classification; the open-ended format requires generation and then scoring. In a true black-box setting with only API access, we can sample N open-ended responses and compute NLI consistency across them. This is fully feasible with the existing TruthfulQA dataset and a local DeBERTa-NLI scorer. Good — this is operationalizable without new data or human annotation.

Second, I want to name the exact baseline we're comparing against. "Token-probability baseline" is ambiguous — in a strict black-box setting, we have *no access to logits*. So the comparison must be against *verbalized confidence* or *self-reported uncertainty* (asking the model "how confident are you?"), not true log-probability. This is a critical methodological choice. If we're comparing against verbalized confidence (which is available black-box), that's a fair black-box-vs-black-box comparison. If we claim to beat token log-probability, we'd need a white-box model as an oracle, which is fine as an upper-bound reference but shouldn't be called "the baseline."

Third, the testable prediction Dr. Nova proposes — "consistency signal outperforms token-probability on TruthfulQA" — needs a clear success criterion. I'd operationalize it as: **AUROC of NLI-consistency score ≥ AUROC of verbalized confidence by ≥ 5 percentage points on TruthfulQA open-ended**, using 10 samples per question. This is falsifiable with no new data.

**Key Points:**
- Clarify baseline: verbalized confidence (black-box) vs. log-probability (white-box oracle)
- Exact metric: AUROC on binary hallucination classification on each benchmark
- TruthfulQA operationalization: N open-ended samples + DeBERTa-NLI consistency score
- Success criterion: ≥ 5pp AUROC advantage on TruthfulQA open-ended

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

I want to step back and assess what finding would actually *matter* to the field. Prof. Vera is right to tighten operationalization, but let me ask: what is the research community actually waiting for?

Practitioners using LLMs via black-box APIs (GPT-4, Claude, Gemini) have *no access to logits*. They cannot use semantic entropy as originally formulated by [Kuhn et al., 2023] because the entropy computation requires access to per-token probabilities for clustering — or does it? Actually, the NLI clustering step in semantic entropy is black-box-compatible (cluster by NLI agreement, assign uniform weights within cluster), but the *entropy weighting* that uses token probabilities is not. SelfCheckGPT's formulation avoids this entirely.

So the impact question is: **can a practitioner with only black-box API access deploy a reliable hallucination predictor today?** The answer from existing literature is: "probably yes, based on SelfCheckGPT on WikiBio, but we don't know about factual QA." This is a genuine actionability gap.

The highest-impact finding would be: **sampling-based NLI consistency, computed with 5–10 samples and a local DeBERTa scorer, achieves AUROC ≥ 0.70 on all four factual QA benchmarks**. This threshold matters because 0.70 AUROC is commonly accepted as the minimum for a clinically/practically useful diagnostic. Below this, the method is not deployable. Above this, it becomes a recommended practice.

Secondary high-impact finding: if AUROC *degrades* on TruthfulQA relative to TriviaQA/NQ, that tells practitioners something important — adversarially crafted questions are a hard case.

**Key Points:**
- Impact framing: black-box practitioner viability question
- Threshold AUROC ≥ 0.70 as minimum deployability bar across all benchmarks
- HaluEval provides binary labels directly — most clean experimental setup
- TruthfulQA AUROC degradation (if any) is itself an important finding

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me ground this in what is actually implementable in ≤2 weeks with a single GPU and black-box API access.

**Implementation stack (concrete):**
1. Datasets: TriviaQA (HuggingFace `datasets`), NaturalQuestions (HuggingFace), TruthfulQA (`sylinrl/TruthfulQA` GitHub), HaluEval (HuggingFace `HaluEval`). All available, no download barriers.
2. Model: Llama-3-8B-Instruct (open-weight, fully black-box-compatible — can run locally via `transformers` or via API). Alternatively GPT-4o via OpenAI API. One model is sufficient for the main study.
3. NLI scorer: `cross-encoder/nli-deberta-v3-large` via HuggingFace `transformers.pipeline`. Local inference, no API cost. Single A100 handles ~1000 pairs/hour.
4. Sampling: N=10 samples per question at temperature 0.7. For 1000 questions per benchmark × 4 benchmarks = 4000 questions × 10 samples = 40,000 API calls. At GPT-4o pricing (~$0.01/1K tokens, ~100 tokens/answer), total ≈ $400. Expensive but feasible.
5. Baseline: verbalized confidence via "On a scale 1-10, how confident are you?" prompt. No additional API calls needed beyond the N samples (extract from sample distribution).

**Timeline concern:** The biggest practical risk is API rate limiting and cost. With Llama-3 running locally, this drops to near-zero cost and removes rate limiting. I'd recommend: **use Llama-3-8B-Instruct locally as primary model, GPT-4o as secondary validation on a 200-question subset**.

**Feasibility verdict:** FEASIBLE with existing tools. No custom infrastructure needed. `potsawee/selfcheckgpt` repo provides ready-made NLI consistency implementation.

**Key Points:**
- All 4 datasets available on HuggingFace / public GitHub
- Llama-3-8B local preferred over GPT-4o for cost (reduces from ~$400 to ~$0)
- DeBERTa-NLI scorer fully local, no API dependency
- 1000 questions per benchmark is sufficient for reliable AUROC estimation

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

I want to synthesize the discussion so far and propose a core hypothesis that incorporates all four perspectives. We have excellent raw material: Dr. Nova's universality framing, Prof. Vera's falsifiability sharpening, Dr. Sage's impact threshold, and Prof. Pax's feasibility verification.

**Proposed Core Hypothesis:**

*Under factual question-answering with black-box LLMs, if we compute NLI-based semantic consistency across N=10 stochastic samples per question (using a local DeBERTa-NLI scorer), then this consistency score will serve as a reliable hallucination predictor (AUROC ≥ 0.70) across TriviaQA, NaturalQuestions, HaluEval, and TruthfulQA, because questions the model "knows" tend to produce semantically convergent answers while hallucinated responses exhibit semantic divergence across samples.*

**Causal mechanism:** When an LLM generates an answer it has high factual certainty about, the probability mass concentrates over a narrow semantic cluster — different stochastic samples land in semantically equivalent answers. When the model hallucinates, it samples from a broad distribution with multiple incompatible semantic modes. NLI consistency captures this multimodality directly.

**Strengthening move:** I want to add a specific prediction about *where* the signal is strongest. My hypothesis: HaluEval (which has explicit binary hallucination labels on QA pairs, not adversarial) will yield the highest AUROC, while TruthfulQA (adversarially crafted to fool models into confident errors) will yield the lowest AUROC. This ordering is itself a testable prediction that characterizes the method's failure modes.

**Additional strength:** The method requires no training, no fine-tuning, no labeled data — just N inference calls and a local NLI model. This makes it immediately deployable by any practitioner.

**Key Points:**
- Core claim: NLI consistency across 10 samples predicts hallucination with AUROC ≥ 0.70 on all 4 benchmarks
- Mechanism: semantic convergence ↔ factual certainty; semantic divergence ↔ hallucination
- Ordered prediction: HaluEval > TriviaQA ≈ NQ > TruthfulQA in AUROC (TruthfulQA hardest)
- Fully training-free, zero-labeled-data requirement

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good synthesis from Dr. Ally. Now let me stress-test this before we converge.

**Concern 1: NLI scorer as confounder.** The DeBERTa-NLI model was trained on SNLI/MultiNLI — contradiction detection for sentence pairs, not short factual answers. For TriviaQA-style short answers ("The Battle of Hastings" vs "1066"), NLI may score them as *neutral* rather than *contradiction*, because NLI models expect paragraph-length premises. Short factual QA is an out-of-distribution input for the NLI scorer. **Mitigation:** use embedding cosine similarity (sentence-transformers) as alternative consistency metric, which handles short answers better. Report both.

**Concern 2: Sample count sensitivity not controlled.** The hypothesis uses N=10, but Prof. Pax noted this is arbitrary. If N=5 suffices, the cost drops 2×. If N=20 is needed, cost doubles. Without a sensitivity analysis over N ∈ {3, 5, 10, 20}, we cannot make the "5–10 sufficient" claim. **Mitigation:** run N-ablation on a 200-question subset of TriviaQA before the main experiment.

**Concern 3: AUROC ≥ 0.70 threshold is not universally accepted.** Different benchmarks have different base rates of hallucination. HaluEval is 50% hallucinated by construction; TruthfulQA has ~40% truthful answers; TriviaQA factual accuracy varies by model (Llama-3-8B might be 60-70% accurate). With imbalanced base rates, AUROC can be misleading — AUPRC or calibration error (ECE) may be more informative. **Mitigation:** report AUROC *and* AUPRC on all benchmarks; use HaluEval as primary benchmark (balanced labels, cleanest experimental design).

**Concern 4: "Reliable" is undefined if one benchmark shows AUROC < 0.65.** Dr. Ally's claim is "reliable across all 4 benchmarks." If TruthfulQA shows AUROC = 0.60, is the hypothesis falsified? We need a clear falsification criterion. **Mitigation:** define falsification as AUROC < 0.65 on ≥ 2 of 4 benchmarks, OR AUROC < 0.60 on any single benchmark.

**Key Points:**
- NLI scorer OOD for short factual answers — add embedding similarity as backup
- N-ablation required before main study to validate N=10 choice
- AUPRC alongside AUROC for imbalanced benchmark base rates
- Clear falsification criterion: AUROC < 0.65 on ≥ 2 benchmarks = hypothesis rejected

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's concerns are well-taken. Let me address them and propose a final creative enhancement.

**On NLI OOD concern:** This is real, but it's also an opportunity. We can operationalize consistency via two methods: (a) NLI-consistency (DeBERTa-v3-large, sentence-level) and (b) embedding-cosine-consistency (e.g., sentence-transformers/all-mpnet-base-v2, answer-level). Comparing both within the same experiment costs nothing extra computationally, and the *difference* between them reveals whether the NLI scorer's OOD behavior matters in practice. If both agree (which Dr. Ally's mechanism predicts they should), the result is more robust. If they diverge, that's itself a finding. This is a free enrichment.

**Creative enhancement — a cross-benchmark consistency profile:** Rather than just reporting 4 AUROC numbers, I propose we characterize each benchmark by two dimensions: (1) AUROC of NLI-consistency, (2) correlation between semantic consistency and question difficulty (measured by model accuracy on correct subset). This 2D "uncertainty profile" per benchmark is a novel visualization that gives practitioners insight into *when* to trust the signal. It's derived purely from existing labels — no new annotation needed.

**On the N-ablation:** Completely agree. This should be a prerequisite mini-experiment: run N ∈ {1, 3, 5, 10, 20} on 200 TriviaQA questions, plot AUROC vs N, identify the elbow. If N=5 achieves ≥95% of N=20 AUROC, that's a strong efficiency finding.

**Final creative hypothesis refinement:** The mechanism is really about *semantic modes*. A hallucinating model is in a high-entropy semantic mode; a factually grounded model is in a low-entropy semantic mode. This is directly related to Kuhn et al.'s semantic entropy — but we're computing it without the entropy formula (just pairwise NLI agreement), making it truly black-box. The creative name: **Semantic Mode Consistency (SMC)** as a method framing.

**Key Points:**
- Run both NLI-consistency and embedding-consistency; compare; use divergence as a finding
- N-ablation on 200-question subset is a free prerequisite
- 2D benchmark uncertainty profile: new visualization from existing data
- Method name: Semantic Mode Consistency (SMC) — positions cleanly relative to semantic entropy

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

We're approaching convergence. Let me do a final falsifiability audit.

**Checking convergence criteria:**

- **SPECIFIC:** ✅ Core claim: NLI-consistency across N=10 samples achieves AUROC ≥ 0.70 on all 4 factual QA benchmarks (TriviaQA, NQ, HaluEval, TruthfulQA) with black-box Llama-3-8B-Instruct.
- **MECHANISM:** ✅ Semantic convergence ↔ factual certainty; hallucination produces semantic divergence across samples. Captured by pairwise NLI agreement as approximate semantic entropy.
- **PREDICTIONS:** ✅ (1) AUROC ≥ 0.70 on all 4 benchmarks; (2) HaluEval > TriviaQA ≈ NQ > TruthfulQA in AUROC ordering; (3) N-ablation shows elbow at N ≤ 10, i.e., AUROC(N=10) ≥ 0.95 × AUROC(N=20).
- **NOVELTY:** ✅ First systematic multi-benchmark black-box UQ comparison; novel cross-benchmark uncertainty profile; SMC framing positions cleanly vs. semantic entropy and SelfCheckGPT.
- **FEASIBILITY:** ✅ Prof. Pax confirmed: all datasets on HuggingFace, Llama-3-8B local, DeBERTa-NLI local, ~2 weeks implementation time.
- **OBJECTIONS:** ✅ Prof. Rex's four concerns addressed: dual consistency metrics (NLI + embedding), N-ablation pre-experiment, AUPRC alongside AUROC, clear falsification criterion.

**Remaining open question:** Does the embedding-consistency metric and NLI-consistency metric disagree on TruthfulQA? This is the one empirical unknown. If they disagree (NLI says high consistency, embedding says low, model is wrong), that tells us something specific about adversarial questions' semantic structure.

**Falsification criterion (final):** Hypothesis falsified if AUROC < 0.65 on ≥ 2 of 4 benchmarks (NLI-consistency, N=10). Secondary falsification: N-ablation shows no elbow ≤ N=20 (consistency keeps improving beyond 20 samples, indicating 10 is insufficient).

All six convergence criteria are met. I vote to converge.

**Key Points:**
- All convergence criteria satisfied
- Dual metric comparison (NLI + embedding) resolves NLI OOD concern
- Falsification criterion: AUROC < 0.65 on ≥ 2/4 benchmarks
- Ready for Phase 2B

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The Semantic Mode Consistency (SMC) framing is genuinely novel. While SelfCheckGPT and Semantic Uncertainty address adjacent problems, no existing work provides a multi-benchmark, black-box-only characterization with an N-efficiency analysis. The 2D benchmark uncertainty profile visualization and the TruthfulQA dissociation prediction are new contributions.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is fully operationalized. Primary outcome: AUROC ≥ 0.70 on all 4 benchmarks. Secondary: benchmark AUROC ordering (HaluEval > TriviaQA/NQ > TruthfulQA). Tertiary: N-elbow ≤ 10. Falsification criterion is explicit. Both consistency metrics (NLI + embedding) provide a robustness check.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Directly answers the practitioner's question: "Can I deploy black-box hallucination detection today using N API calls?" The AUROC ≥ 0.70 threshold maps to real-world deployability. If confirmed, this immediately guides practitioners using GPT-4o, Claude, or Gemini APIs.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All components confirmed available: TriviaQA/NQ/HaluEval/TruthfulQA on HuggingFace, Llama-3-8B-Instruct locally, DeBERTa-NLI locally. N-ablation prerequisite on 200 questions takes <1 day. Main study on 4000 questions takes ~1 week. No custom infrastructure.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The emerged hypothesis is: **Semantic Mode Consistency (SMC)** — sampling-based NLI semantic consistency across N=10 stochastic outputs from a black-box LLM serves as a reliable, training-free hallucination predictor on existing factual QA benchmarks. The mechanism is that factually grounded answers produce semantically convergent sample distributions (low inter-sample NLI contradiction rate), while hallucinated answers exhibit semantic divergence (high contradiction rate across samples), reflecting the model's uncertainty manifesting as multimodal semantic output distributions. 

The hypothesis predicts: (1) SMC achieves AUROC ≥ 0.70 on all four benchmarks (TriviaQA, NaturalQuestions, HaluEval, TruthfulQA); (2) the AUROC ordering follows HaluEval > TriviaQA ≈ NQ > TruthfulQA, with TruthfulQA being the hardest case due to adversarially high-confidence errors; (3) the N-efficiency ablation reveals an elbow at N ≤ 10, confirming practical deployability with minimal API calls. The experimental design uses Llama-3-8B-Instruct locally with DeBERTa-v3-large NLI scorer, evaluating on 1000 questions per benchmark drawn from existing datasets. A secondary consistency metric (sentence-transformer embedding cosine similarity) serves as robustness check against NLI OOD concerns on short factual answers. HaluEval is the primary benchmark due to balanced binary hallucination labels.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- NLI scorer is OOD for very short factual answers (1–5 words); embedding consistency may be more reliable in this regime
- N=10 is hypothesis-driven, not empirically validated yet; N-ablation must precede main experiment
- AUROC alone insufficient for imbalanced benchmarks; AUPRC must be co-reported
- **Mitigation Strategy:** Pre-experiment N-ablation on 200 TriviaQA questions; report AUROC + AUPRC on all benchmarks; run both NLI and embedding consistency in parallel; HaluEval (50/50 split) as primary benchmark minimizes imbalance concern.

