# Phase 2A: Refinement Summary - Linguistic Agency Markers in RLHF Evaluation

## Metadata
- **Generated at**: 2026-03-17T04:30:00Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap-1
- **Gap Title**: Computational Operationalization of Bidirectional Alignment
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All 6 convergence criteria met - specific claim articulated, causal mechanism explained with 4-step chain, testable predictions defined with quantitative thresholds (p < 0.05, d ≥ 0.15), novelty clearly differentiated from prior work (first computational operationalization of Human→AI alignment), implementation feasibility confirmed (4-week timeline, standard tools, no GPU), major objections addressed via construct validation strategy.

### Key Insights

1. **Paradigm Reframing** (Exchange 1): Dr. Nova reframed HH-RLHF dataset from "ground truth for human preferences" to "trace fossil of human agency" - shifting evaluation from AI-centric to system-centric (human+AI together).

2. **Proxy Validity Challenge** (Exchange 6): Prof. Vera identified proxy validity as critical vulnerability (measuring AI text, inferring human agency) - triggered convergent validation strategy using Cronbach's α, known-groups discrimination, and dose-response gradient.

3. **Automated Construct Checks** (Exchange 8): Prof. Pax resolved rigor vs feasibility tension by proposing zero-annotation construct validation: internal consistency checks, known-groups comparison (helpful vs harmless), dose-response testing (base < online < RS).

4. **Vulnerability-as-Opportunity** (Exchange 11): Dr. Nova reframed Prof. Rex's critical concerns as research contributions - proxy validation becomes methodological paper, confounds become boundary condition discovery, mechanism circularity becomes theoretical integration.

### Breakthrough Moments

- **Exchange 1**: Recognition that linguistic markers in RLHF responses can operationalize bidirectional alignment's missing Human→AI dimension
- **Exchange 6**: Identification of proxy validity as testable assumption (not fatal flaw) via construct validation
- **Exchange 8**: Resolution of validation debate through automated checks (preserving zero-annotation value proposition)
- **Exchange 15**: Synthesis of minimal testable hypothesis with built-in construct validation

---

## Final Hypothesis

### Title
Linguistic Agency Markers as Computational Proxies for Bidirectional Alignment Evaluation in RLHF Systems

### Core Claim
Under RLHF evaluation conditions (HH-RLHF dataset with 161K human preference pairs), computational linguistic markers operationalizing human agency preservation (modal verbs, hedging language, alternative-framing phrases) will demonstrate (1) sufficient distributional variance (CV > 0.3), (2) systematic directional association with RLHF preference status (chosen vs rejected, paired t-test p < 0.05, Cohen's d ≥ 0.15), (3) internal consistency as a construct (Cronbach's α > 0.7), and (4) cross-dataset replication across at least 2 of 3 HH-RLHF splits, providing the first computational operationalization of human agency preservation in bidirectional alignment evaluation.

### Mechanism (4-Step Causal Chain)
1. **RLHF Optimization**: Reward model trained on chosen vs rejected pairs optimizes for human annotator preferences
2. **Efficiency Preference**: Human annotators prefer responses that resolve queries efficiently and directly (task completion priority, grounded in cognitive economy)
3. **Directness → Reduced Options**: Efficient task resolution minimizes uncertainty expressions and alternative framings (supported by Shapira et al. 2026 sycophancy mechanism: RLHF → reduced disagreement/alternatives)
4. **Linguistic Manifestation**: Reduced option presentation appears as fewer modal verbs ("could" options), less hedging ("might" qualifiers), fewer alternative-framing phrases (grounded in Juanchich 2017, Biber et al. 1999)

### Variables
- **Independent Variable**: RLHF preference status (chosen=1, rejected=0, categorical binary)
- **Dependent Variables** (Primary): Modal verb frequency per 100 words (continuous), measured via spaCy POS tagging
- **Dependent Variables** (Secondary): Hedging marker frequency, alternative-framing frequency (both continuous, per 100 words)
- **Control Variables**: Response length (word count), conversation turn number, topic category (HH-RLHF split: base/online/RS)

---

## Predictions

### P1 (Primary - Existence)
**Statement**: Modal verb frequency (could/might/should per 100 words) will be lower in RLHF-chosen responses compared to rejected responses

**Test Method**: Paired t-test on 161K preference pairs, length-normalized modal counts

**Success Criterion**: p < 0.05, Cohen's d ≥ 0.15 (small effect size), direction: chosen < rejected

**Falsification**: If p > 0.05 OR d < 0.15 OR direction reversed, P1 fails

### P2 (Consistency)
**Statement**: All three marker types (modal verbs, hedging, alternative-framing) show consistent directional pattern, demonstrating internal consistency as a construct

**Test Method**: Cronbach's alpha across three marker frequencies

**Success Criterion**: α > 0.7 (acceptable internal consistency), all markers negatively correlated with chosen status

**Falsification**: If α < 0.7 OR markers show inconsistent directions, construct validity questionable

### P3 (Robustness)
**Statement**: P1 effect (modal verb reduction) replicates across at least 2 of 3 HH-RLHF data splits (helpful-base, helpful-online, helpful-rejection-sampled)

**Test Method**: Separate paired t-tests for each split

**Success Criterion**: p < 0.05 and d ≥ 0.15 in at least 2 of 3 splits

**Falsification**: If effect holds in only 1 split or 0 splits, generalization fails

---

## Novelty

**Preserved Novelty**: First computational operationalization of Human→AI alignment dimension identified in bidirectional framework (Shen et al. 2024)

**Key Innovation**: Bridges three established domains in novel integration - bidirectional alignment framework + linguistic agency markers + RLHF evaluation

**Differentiation from Prior Work**:
- **vs Shen et al. 2024**: They provide conceptual framework (400+ paper survey); we operationalize computationally with measurable proxies
- **vs Shapira et al. 2026**: They explain why sycophancy happens; we measure it via linguistic proxies in preference data
- **vs Juanchich 2017**: They study human language in psychology experiments; we apply to AI responses in RLHF context
- **vs Constitutional AI**: They automate harmlessness measurement; we do it for agency preservation (orthogonal dimension)

---

## Experimental Design

### Dataset
- **Name**: Anthropic HH-RLHF
- **Source**: HuggingFace (Anthropic/hh-rlhf)
- **Size**: 161K preference pairs total
  - helpful-base: ~43K pairs
  - helpful-online: ~22K pairs
  - helpful-rejection-sampled: ~52K pairs
- **Structure**: Each pair contains {chosen_response, rejected_response, conversation_history}

### Extraction Tools
- **spaCy 3.7+**: POS tagging and dependency parsing for modal verb detection
- **NLTK**: Hedging language lexicon matching
- **Python regex**: Alternative-framing phrase pattern matching

### Statistical Framework
- **Primary Analysis**: Paired t-tests (within-pair comparison controls for content)
- **Controls**: Partial correlation for length, turn, topic
- **Effect Size**: Cohen's d calculation
- **Validation**: Cronbach's alpha (internal consistency), known-groups discrimination, dose-response gradient

### Implementation Timeline (4 weeks)
- **Week 1**: Infrastructure setup, feature extraction pipeline, automated construct checks
- **Week 2**: Main analysis (paired comparisons, statistical controls)
- **Week 3**: Cross-validation across splits, sensitivity analysis
- **Week 4**: Results interpretation, visualization, write-up

---

## Limitations

1. **Proxy Validity Assumption**: Linguistic markers in AI responses used to infer human agency preservation - assumption grounded in theory (Juanchich 2017) but not directly validated via user studies in RLHF context

2. **HH-RLHF Specificity**: Results may not generalize beyond HH-RLHF dataset to other RLHF preference datasets (acknowledged limitation)

3. **English-Only**: Linguistic patterns language-specific - cross-lingual generalization untested

4. **No User Metadata**: Cannot test individual difference moderators (user expertise, task complexity requires manual annotation)

5. **Retrospective Annotations**: HH-RLHF preferences collected retrospectively, may differ from real-time deployment preferences

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met (specific, mechanism, predictions, novelty, feasibility, objections addressed) |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (all addressed via construct validation strategy) |

---

## Phase 2B Readiness

**Status**: READY

**Existence Testing** (SH1): Linguistic markers must be extractable with sufficient variance (CV > 0.3) from HH-RLHF text data

**Mechanism Testing** (SH2): Markers must correlate with RLHF preference status (chosen vs rejected) with small-to-medium effect (d ≥ 0.15)

**Comparison Testing** (SH3): Results must replicate across HH-RLHF splits; baseline comparison deferred to Phase 5 (or skipped per module.yaml)

**Open Questions for Future Work**:
- Do effects vary by conversation turn (early vs late)?
- Are effects moderated by response length quartiles?
- Do different RLHF training procedures (online vs RS) show different patterns?
- Can markers be validated via user study correlation?

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
