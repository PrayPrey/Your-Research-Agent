# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-24T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: Gap 1
- **Gap Title**: Unified Data Curation Frameworks Across FM Training Stages
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 7

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 7

**Convergence Reason**: Hypothesis refined through multi-persona discussion addressing novelty, testability, feasibility, and significance concerns

### Key Insights
- Transfer analysis paradigm applies to data curation, not just model parameters (Dr. Nova)
- Testability requires concrete mechanism specification and falsifiable predictions (Prof. Vera)
- Scientific contribution is meta-analysis characterizing transfer behavior, not inventing new techniques (Dr. Sage)
- Feasibility hinges on narrowing scope to low-level hygiene operations independent of stage objectives (Prof. Pax)
- Refined hypothesis addresses stage objective mismatch by categorizing techniques (Dr. Ally)
- Avoiding circular logic requires showing differential transfer across categories, not just "best practices work" (Prof. Rex)

### Breakthrough Moments
- **Exchange 4**: Prof. Pax identifies stage objective mismatch (pre-training coverage vs fine-tuning performance vs RLHF alignment) as fundamental barrier to full-strategy transfer
- **Exchange 5**: Dr. Ally narrows hypothesis from "cumulative curation intelligence" to "transfer stability of low-level heuristics," making it concretely testable
- **Exchange 7**: Dr. Nova reframes from "transfer is universally good" to "characterize transfer landscape with taxonomy," avoiding circular logic and defining clear research contribution

---

## Final Hypothesis

### Title
Characterizing Transfer Stability of Data Curation Techniques Across Foundation Model Training Stages

### Hypothesis ID
H-CurationTransferTaxonomy-v1

### Core Claim
Under foundation model training (pre-training → fine-tuning → RLHF), if we apply curation heuristics discovered during pre-training to downstream stages, then low-level quality filters (deduplication, perplexity-based outlier removal) will transfer robustly while high-level strategies (domain mixing, task-specific filters) will require stage-specific tuning, because low-level operations address universal data hygiene properties independent of stage objectives while high-level strategies are objective-dependent.

### Mechanism
Certain curation operations address universal data hygiene properties (duplicates, format errors, statistical outliers) independent of stage objectives. These objective-independent operations transfer robustly because their optimal thresholds depend on data quality characteristics that persist across stages, not on training goals that change per stage. Conversely, objective-dependent strategies (domain mixing for coverage, task filters for performance, preference filters for alignment) fail to transfer because their optimal configurations vary with each stage's distinct optimization target.

**Causal Chain:**
1. Low-level curation operations (deduplication, outlier removal) address universal data hygiene independent of stage objectives
2. Transfer stability correlates with objective-independence—operations tied to stage goals require stage-specific tuning
3. Applying transferred low-level thresholds yields performance equivalent to stage-tuned thresholds, while transferred high-level strategies degrade performance

---

## Predictions

### P1 (Primary)
**Statement**: Models fine-tuned with transferred pre-training deduplication and perplexity thresholds will perform within 1% of models fine-tuned with stage-tuned thresholds on MMLU, HellaSwag benchmarks

**Test Method**: Ablation study comparing Transferred vs Stage-Tuned conditions for deduplication and perplexity filtering, measuring downstream benchmark accuracy

**Success Criterion**: Performance delta ≤ 1% (demonstrates robust transfer for low-level operations)

**Falsification**: Performance delta > 1% would indicate transfer-stable category is misclassified

### P2
**Statement**: Models fine-tuned with transferred pre-training domain mixing ratios will show >5% performance degradation compared to stage-tuned domain mixing on downstream tasks

**Test Method**: Ablation comparing transferred pre-training domain ratios to fine-tuning-optimized ratios

**Success Criterion**: Performance delta > 5% (demonstrates transfer sensitivity for high-level strategies)

**Falsification**: Performance delta ≤ 5% would suggest high-level strategies also transfer robustly, contradicting taxonomy

### P3
**Statement**: Transferred low-level thresholds will outperform baseline (no curation) by >2% while high-level transferred strategies may underperform baseline

**Test Method**: Three-way comparison: Transferred, Stage-Tuned, Baseline-None for both low-level and high-level techniques

**Success Criterion**: Low-level transferred > baseline by >2%, high-level transferred ≤ baseline

**Falsification**: If both categories show same relationship to baseline, differential transfer is not established

---

## Novelty

### What's New
First systematic characterization of transfer stability landscape for data curation techniques across FM training stages. Creates empirically-grounded taxonomy categorizing curation operations by transfer robustness rather than treating curation as monolithic.

### Differentiation from Prior Work

**vs. DataComp, instruction filtering, preference data selection**  
These are stage-specific curation techniques. This work characterizes which techniques transfer across stages and which require stage-specific tuning.

**vs. Meta-learning for hyperparameter transfer**  
Applies transfer analysis to data curation domain, not model hyperparameters. Investigates curation as learned knowledge.

**vs. Multi-stage training pipelines (pre-train + fine-tune + RLHF)**  
Focuses on data curation transfer, not model parameter transfer. Investigates curation as learned knowledge rather than static recipes.

---

## Experimental Design

### Datasets
- **Pre-training**: C4 or RedPajama (extract documented filtering thresholds)
- **Fine-tuning**: Dolly-15k or Alpaca (apply transferred vs tuned thresholds)
- **Evaluation**: MMLU, HellaSwag, TruthfulQA benchmarks

### Models
- Llama-2-7B or Pythia-6.9B (mid-size models balance feasibility with meaningful measurement)

### Baselines
1. **No Curation**: Raw datasets without filtering
2. **Stage-Independent Best Practices**: Standard dedup + perplexity filtering independently optimized per stage
3. **Transferred Thresholds**: Apply pre-training-derived thresholds to downstream stages

### Variables
- **Independent**: Curation Strategy Source (Transferred/Stage-Tuned/Baseline), Curation Technique Category (Transfer-Stable/Sensitive/Non-Transferable)
- **Dependent (Primary)**: Downstream Task Performance (MMLU, HellaSwag accuracy)
- **Controlled**: Model architecture, hyperparameters, pre-training data quality

---

## Limitations

### Scope Boundaries
**Applies to:**
- Foundation model training pipelines with sequential stages (pre-training, fine-tuning, RLHF)
- Language models trained on text corpora
- Curation techniques with quantifiable thresholds

**Does NOT apply to:**
- Single-stage training (no transfer opportunity)
- Multimodal models (visual/audio curation may have different transfer properties)
- Curation strategies without clear thresholds (qualitative filtering)
- Domain-specific models with minimal distribution shift between stages

### Known Limitations
- Experiment focuses on text-based language models
- Transfer stability may depend on degree of distribution shift (not systematically varied)
- Taxonomy is proposed categories, not derived from theory
- Does not address computational cost of curation operations

### Key Assumptions
1. Pre-training curation thresholds were optimized (or near-optimal) for pre-training
2. Distribution shift between stages doesn't fundamentally change outlier definitions
3. Low-level operations are truly objective-independent across stages
4. Performance differences are attributable to curation, not confounds
5. Existing benchmarks are sensitive enough to detect 1-2% performance differences

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | Hypothesis refined through 7 exchanges from "cumulative curation intelligence" to "transfer stability taxonomy" addressing feasibility concerns (Prof. Pax), testability gaps (Prof. Vera), and novelty positioning (Dr. Sage) |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None |
| **Phase 2B Readiness** | READY |

---
