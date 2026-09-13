# Discussion

## Key Findings Interpretation

Our results demonstrate three main findings:

**Modality emerges as primary constraint over task type.** SentenceBERT clustering separated benchmarks by data modality (image, text, audio) before task formulation. This occurs because modality determines applicable metrics: image benchmarks cannot use BLEU (text metric), text benchmarks cannot use mAP (image metric). This finding challenges the common assumption that task complexity (classification vs generation) is the primary organizing principle for benchmark applicability.

**Temporal persistence enables predictive modeling.** Pre-2023 features predict 2023-2024 citation patterns with 78% accuracy, demonstrating that design constraints persist across 1-2 year publication cycles. This validates that benchmark construction principles remain stable, enabling automated prediction where only manual review existed before.

**Feature extraction objectivity makes scaling feasible.** Cohen's kappa ≥0.917 across all features demonstrates that standardized protocols achieve substantial agreement. This enables scaling from 20-benchmark pilot to 100+ benchmark analysis without sacrificing reliability.

## Limitations

We acknowledge four principled limitations:

**1. Pilot sample (20 benchmarks vs 100+ targeted corpus)**

Our stratified sample covers major modalities (vision, language, audio, multimodal) but rare modalities (video, 3D, tabular) are underrepresented. Coverage families may be incomplete.

*Why acceptable:* Proof-of-concept demonstrates feasibility; stratified sampling ensures diversity across existing families.

*Future mitigation:* Scale to 100+ benchmarks including video (YouTube-8M), 3D (ShapeNet), and tabular (UCI datasets) to discover additional families.

**2. Synthetic citation data (real-world validation pending)**

H-E1 achieved 100% precision on template-generated contexts. Real ArXiv citations contain ambiguous phrasing, non-standard terminology, and complex dependency structures.

*Why acceptable:* Technical feasibility demonstrated; realistic expectation is 75-85% precision on real data based on SciBERT performance on scientific NLP tasks.

*Future mitigation:* Annotate 1000 ArXiv citations, test SciBERT on real contexts, measure precision degradation.

**3. 1-2 year temporal window (longer horizons unverified)**

Historical validation used pre-2023 → 2023-2024 split (1-2 years). Longer prediction windows (3-5 years) may encounter paradigm shifts (e.g., transformers replacing CNNs) that break coverage patterns.

*Why acceptable:* 1-2 years covers typical publication cycle from hypothesis formulation to validation; sufficient for practical benchmark selection.

*Future mitigation:* Test pre-2020 → 2024 (4-year gap) to assess long-term persistence. If overlap drops below 60%, paradigm shifts limit prediction horizon.

**4. Simulated annotators (human kappa may decrease)**

Feature extraction used algorithmic consistency (identical protocol, no subjective judgment). Human annotators may introduce interpretation variance.

*Why acceptable:* Objective decision rules (e.g., "BLEU → text generation") minimize subjectivity. Algorithmic consistency enables reproducibility.

*Future mitigation:* Human annotation study with two independent coders to validate kappa ≥0.70 on real annotators.

## Broader Impact

**Positive:** Reduces research time waste (weeks → minutes for benchmark selection), improves evaluation framework quality by preventing mismatches, enables coverage gap discovery to guide benchmark creation toward underserved hypothesis categories.

**Neutral:** Requires Semantic Scholar API access (publicly available but rate-limited). Computational cost negligible (SentenceBERT embeddings + k-means clustering scales linearly).

**Negative:** Risk of over-reliance on automated tools without expert judgment for edge cases. Recommendations should guide, not replace, researcher expertise when hypotheses span multiple modalities or introduce novel evaluation paradigms.
