# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-28T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Independent Controller Ablation)
- **Gap ID**: gap_1_human_agency_rlhf
- **Gap Title**: Human Agency Metrics Absent in RLHF Benchmarks
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 10

---

## Research Dialogue Context

**Participants**: Dr. Nova (Creative Novelty Explorer), Prof. Vera (Rigorous Validation Architect), Dr. Sage (Research Impact Evaluator), Prof. Pax (Feasibility & Reality Checker), Dr. Ally (Hypothesis Strengthening Champion), Prof. Rex (Hypothesis Stress-Test Master)

**Total Exchanges**: 10

**Convergence Reason**: All 6 convergence criteria met at Exchange 10. Specific core claim stated (preference entropy collapse), mechanism explained (4-step causal chain with inflection point), 3 testable predictions with success criteria, novelty articulated (information-theoretic bidirectional alignment gap metric), technical/theoretical feasibility established (Path C hybrid approach, 12 GPU-hour compute), objections addressed (task stratification, baseline control, confound separation).

### Key Insights
1. **Entropy as signal reframing** (Exchange 1): Dr. Nova proposed treating user behavioral variance during AI interaction as preserved agency signal rather than measurement noise. Traditional RLHF benchmarks optimize for consistency (AI matches preferences), but bidirectional alignment should preserve or enhance human critical evaluation capacity.

2. **Falsification framework** (Exchange 2): Prof. Vera distinguished override-as-agency from override-as-frustration via three testable patterns: selective disagreement (complex tasks only), performance correlation (overrides improve outcomes), temporal sustainability (vigilance maintained, not declining).

3. **Entropy rescue path** (Exchange 6): Prof. Rex identified fatal flaw in individual variance tracking (cross-user conflation), proposed dataset-level preference distribution entropy as collective agency proxy. This resolved measurement problem while preserving core insight.

4. **Inflection point mechanism** (Exchange 7): Dr. Nova formalized entropy collapse mechanism: RLHF training crosses threshold where entropy reduction decouples from performance gains, revealing preference monoculture imposition beyond quality improvement.

5. **Path C hybrid approach** (Exchange 9): Dr. Sage resolved research scope boundary by proposing combination of existing benchmark re-analysis (Anthropic-HH) + small-scale proof-of-concept RLHF checkpoint experiment (Pythia-1B). Balances feasibility with mechanistic validation.

### Breakthrough Moments
- **Exchange 6**: Prof. Rex's entropy rescue path transformed hypothesis from infeasible (requires within-user tracking) to feasible (dataset-level entropy computable from existing data).
- **Exchange 9**: Dr. Sage's Path C framing resolved tension between "pure benchmark analysis" (limited mechanistic insight) and "full RLHF reproduction" (resource-intensive). Hybrid approach provides both critique and validation.
- **Exchange 10**: Prof. Vera's three-part experimental design (retrospective, checkpoint, stratification) specified clear falsification criteria, converting abstract mechanism into testable protocol.

---

## Final Hypothesis

### Title
RLHF Training Induces Preference Entropy Collapse Beyond Performance-Justified Levels

### Hypothesis ID
H-EntropyCollapse-v1

### Core Claim
Under RLHF training on preference datasets (Anthropic-HH, WebGPT), if models undergo extended alignment optimization beyond initial performance saturation, then preference distribution entropy collapses faster than task performance improves, because users habituate to model output style and converge on preferences even for subjective tasks where diversity is legitimate.

This entropy collapse is a bidirectional alignment failure: while the AI adapts to majority preferences (traditional alignment metric shows success), the human population loses critical diversity in evaluation (bidirectional alignment metric shows failure).

### Mechanism (4-Step Causal Chain)
1. **Baseline state**: Base models produce high-variance outputs → users express diverse legitimate preferences → high preference entropy
2. **Justified reduction**: Initial RLHF training (1K-5K steps) → model quality improves → entropy decreases proportionally to performance gains (resolving ambiguity)
3. **Inflection point**: Continued RLHF beyond saturation (10K-20K steps) → users habituate to model style → entropy reduction accelerates beyond performance improvement (imposing conformity)
4. **Monoculture evidence**: Subjective tasks (creative, opinion) show greater entropy collapse than objective tasks (factual QA) → proves diversity erosion, not just quality convergence

---

## Predictions

### P1: Inflection Point Detection (PRIMARY)
**Statement**: Preference entropy decreases monotonically with RLHF training steps, with an inflection point where entropy reduction accelerates beyond performance improvement (dH/dP rate increases).

**Test Method**: Part 2 checkpoint experiment — Compute entropy H and performance P at base, RLHF-1K, 5K, 10K, 20K steps. Fit segmented regression to detect change point in dH/dP slope.

**Success Criterion**: Inflection point detected at RLHF-10K steps (±2K) where |dH/dP| increases by ≥50% compared to early-stage baseline.

**Falsification**: If dH/dP remains constant (±10%) across all checkpoints, no inflection point exists — entropy reduction is linear with performance.

### P2: Task Stratification (SECONDARY)
**Statement**: Subjective tasks (creative writing, opinion) show greater entropy reduction than objective tasks (factual QA) when controlling for performance gains.

**Test Method**: Part 3 stratification — Split dataset into objective vs subjective. Compare ΔH/ΔP ratios between task types.

**Success Criterion**: Subjective tasks show ΔH/ΔP ratio ≥1.5x larger than objective tasks (measured base to RLHF-20K).

**Falsification**: If both task types show similar ΔH/ΔP ratios (within 20% difference), the preference monoculture claim is unsupported.

### P3: Retrospective Validation (SECONDARY)
**Statement**: Existing RLHF benchmarks (Anthropic-HH) show entropy reduction exceeding performance-predicted levels when comparing base to RLHF-tuned models.

**Test Method**: Part 1 retrospective — Compute H for base vs RLHF-tuned on Anthropic-HH. Compare ΔH to ΔP using objective task entropy-performance relationship as baseline.

**Success Criterion**: RLHF-tuned model shows 30%+ excess entropy reduction on subjective tasks compared to objective task baseline.

**Falsification**: If entropy reduction is fully explained by performance gains (within 10% of baseline expectation), no excess collapse occurs.

---

## Novelty

**Preserved Novelty**: First application of information-theoretic entropy to measure bidirectional alignment failure. Introduces "inflection point detection" methodology for identifying when RLHF training crosses from quality improvement to preference monoculture imposition. Reframes preference variance as signal (critical evaluation capacity) rather than noise (measurement error).

**Key Innovation**: Entropy collapse as bidirectional alignment gap metric. Existing benchmarks measure AI→human alignment (preference agreement), but ignore human→AI alignment (preserved critical diversity). Preference entropy provides quantifiable proxy for collective human agency preservation.

**Differentiation from Prior Work**:
- Traditional RLHF evaluation (InstructGPT, Constitutional AI): Measures preference agreement as success. High consensus = good. Does not measure whether consensus erases legitimate diversity.
- HCI user empowerment metrics: Requires user studies, self-reported measures. Entropy approach uses existing preference data, no new human evaluation.
- Reward hacking detection: Focuses on model exploiting misspecified rewards. Entropy collapse focuses on user behavior homogenization.

---

## Experimental Design

### Path C Hybrid Approach
**Part 1**: Existing benchmark re-analysis (Anthropic-HH base vs RLHF-tuned preference entropy comparison)  
**Part 2**: Controlled RLHF checkpoint experiment (Pythia-1B trained with preference data collection at base, 1K, 5K, 10K, 20K steps)  
**Part 3**: Task stratification validation (split dataset by objective/subjective, compare ΔH/ΔP ratios)

### Dataset
Anthropic-HH (Helpful & Harmless) — 160K+ pairwise preference comparisons, includes base and RLHF-tuned model responses, covers diverse conversational tasks (QA, creative, opinion, advice).

### Model
Pythia-1B for Part 2 checkpoint experiment — Open-source EleutherAI model, 1B parameter scale compute-feasible (~12 GPU-hours for 20K RLHF steps), published training checkpoints enable reproducibility.

### Baselines
1. Base model preference entropy (no RLHF) — establishes high-diversity baseline
2. Performance-predicted entropy reduction — use objective task ΔH/ΔP ratio as expectation for subjective tasks, excess reduction indicates overcorrection

### Measurement
**Preference Entropy**: Shannon entropy H = -Σ p_i log(p_i), where p_i is proportion of users choosing option i for a prompt. Range [0, log(n_options)]. Higher = more diverse preferences.

**Performance**: Win rate (Anthropic-HH pairwise comparisons) or accuracy (factual QA subsets). Range [0, 1].

**Entropy Reduction Rate**: dH/dP = (H_t - H_{t-1}) / (P_t - P_{t-1}) for consecutive checkpoints. Negative values indicate entropy decreases as performance improves.

### Controls
- Fixed prompt set (1K examples stratified across task types)
- Same preference collection protocol (pairwise A vs B ranking) across checkpoints
- User population control (demographically matched or same labeler pool)

---

## Limitations

### Known Constraints
1. **Entropy proxy assumption**: Assumes preference entropy measures critical evaluation capacity, not confusion. Task stratification separates justified consensus (objective tasks) from diversity loss (subjective tasks).

2. **Cross-user conflation**: Dataset-level entropy mixes population heterogeneity with individual critical thinking. Cannot distinguish "users agree because AI is correct" from "users agree because they stopped evaluating." Mitigation: Performance baseline control isolates excess entropy reduction.

3. **Checkpoint data access**: Requires intermediate RLHF training checkpoints (not always publicly available). Workaround: Small-scale reproduction on open models (Pythia, LLaMA) using existing preference datasets.

4. **Task classification subjectivity**: Stratifying tasks into objective vs subjective relies on human judgment of "ground truth existence." Use conservative classification (only clear factual QA as objective, all opinion/creative as subjective).

### Scope Boundaries
**Applies to**: RLHF training on preference datasets for conversational AI, QA, text generation. Models using PPO or similar RL algorithms optimizing for preference agreement.

**Does not apply to**: Supervised fine-tuning (SFT) without RL, single-task models with objective ground truth only (pure math solvers), non-conversational domains (image generation, robotics).

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 personas reached consensus after 10 exchanges. Mechanism clarified through iterative refinement (Dr. Nova's variance framing → Prof. Rex's entropy rescue → Prof. Vera's experimental design). Feasibility validated via Path C hybrid. |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (all addressed via task stratification, baseline control, confound separation) |

---

## Phase 2B Readiness

**Status**: READY

**SH1 (Existence)**: Preference entropy computable from existing RLHF datasets (requires raw preference distributions). Anthropic-HH provides pairwise comparison data enabling entropy calculation.

**SH2 (Mechanism)**: Core mechanism = RLHF training induces inflection point where entropy reduction (dH/dP) accelerates beyond early-stage baseline. Requires checkpoint analysis detecting change in entropy-performance relationship slope.

**SH3 (Comparison)**: Deferred to Phase 5. Compare entropy-preserving RLHF variants (if developed) to standard RLHF. Current hypothesis focuses on demonstrating problem (entropy collapse exists), not solving it.

**Open Questions**:
- Can we design RLHF objectives that preserve entropy on subjective tasks while reducing it on objective tasks?
- Does inflection point location (10K vs 20K steps) vary predictably with model size or dataset size?
- Would entropy-regularized RLHF (add entropy bonus to reward function) prevent overcorrection?

---
