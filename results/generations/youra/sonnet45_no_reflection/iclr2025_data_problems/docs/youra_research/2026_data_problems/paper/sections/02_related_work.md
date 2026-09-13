# Related Work

Our work attempted to extend contamination detection methods beyond instance-level approaches toward learning trajectory analysis. We organize related work by detection paradigm, positioning our (failed) attempt within this landscape.

## Instance-Level Detection Methods

**Membership Inference Attacks (MIA)** aim to determine whether a specific sample was in the training set by analyzing model behavior on that sample. Carlini et al. (2021) showed MIA can achieve high accuracy on memorized sequences in language models, while Ye et al. (2022) demonstrated extractability attacks recovering training data verbatim. However, Fu et al. (2024) established fundamental limitations: MIA achieves only AUC≈50% (random guessing) during pretraining because foundation models learn distributions rather than memorizing instances. Their experiments across Pythia and OLMO-2 models showed MIA signals emerge only during finetuning (up to 99.4% AUC), where structured memorization occurs. This limitation motivates approaches that do not rely on instance-level detection.

**Semantic Similarity Detection** matches test samples against training data using embedding-based similarity or n-gram overlap. However, Dekoninck et al. (2024) demonstrated that adversarial paraphrasing evades these methods: their "EAL" attack uses GPT-4 to paraphrase benchmark samples, achieving <2% true positive rate at 1% false positive rate for semantic detectors while preserving ~15% benchmark gains. The attack exploits the distinction between surface form (which changes under paraphrasing) and task structure (which remains constant). This finding invalidates similarity-based detection against motivated adversaries.

**Data Provenance Tracking** attempts to identify contamination sources through dataset auditing, temporal analysis, or license checking. Dodge et al. (2021) documented contamination in C4 and other web-scraped corpora, while Magar and Schwartz (2022) proposed data provenance verification through cryptographic attestation. However, these methods require access to pre-training data manifests, which are often unavailable for closed-source models, and cannot detect contamination introduced through undisclosed data sources.

## Learning Dynamics and Trajectory Analysis

**Example Difficulty and Learning Order** studies have shown that models learn different examples at different rates. Swayamdipta et al. (2020) categorized training examples by confidence dynamics, while Toneva et al. (2019) identified "unforgettable" examples learned early and never forgotten. Feldman (2020) connected memorization to atypical examples, showing long-tailed distributions promote memorization. Our TSG probe approach was inspired by this work: if contaminated samples are learned systematically faster than clean samples, differential learning rates could signal contamination. However, we never implemented this mechanism, so whether it works remains unknown.

**Loss Landscape Geometry** research analyzes training dynamics through the geometry of loss surfaces. Li et al. (2018) visualized loss landscapes using filter normalization, while Fort and Jastrzebski (2019) connected Hessian spectrum to generalization. Jastrzebski et al. (2020) showed that larger learning rates induce flatter minima with better generalization. Our Tier 3 geometric detection (gradient subspace alignment, Hessian anisotropy, CKA compression) was conceptually grounded in this literature: contamination-induced gains might require navigating toward specific regions of parameter space, leaving geometric signatures. This hypothesis remains completely untested due to our implementation failure.

## Benchmark Evaluation and Freshness

**Continuous Evaluation** addresses contamination through constantly refreshed benchmarks. Jain et al. (2024) introduced LiveCodeBench, generating 400+ programming problems weekly to prevent pre-contamination. Kiela et al. (2021) proposed Dynabench for adversarial example collection with model-in-the-loop dataset creation. While effective, these approaches fragment evaluation infrastructure and require substantial curation effort. Our goal was complementary: enable training-time contamination detection so stable benchmarks remain usable. However, our detector's 100% false positive rate makes it unusable for any purpose.

## Data Quality and Curation

**Data Filtering and Selection** methods aim to improve training data quality. Sorscher et al. (2022) showed strategic data selection can match full-dataset performance with significantly fewer samples. Marion et al. (2023) demonstrated influence function-based sample weighting improves downstream task performance. D'Amour et al. (2022) analyzed distribution shift between training and deployment. While related to our data-layer filtering (Tier 1), these works focus on quality metrics rather than contamination detection. Our Tier 1 LSH fingerprinting and temporal isolation were never implemented, so their efficacy remains unknown.

## Position of Our Work

Our three-tier architecture attempted to combine data-layer detection (Tier 1: LSH + temporal filters), manifold-layer detection (Tier 2: TSG probes with differential alignment), and geometry-layer detection (Tier 3: gradient/Hessian/CKA analysis). The novelty was supposed to be: (1) Task Signature Graphs as paraphrase-invariant representations, and (2) geometric inevitability—the hypothesis that contamination-induced gains require detectable parameter alignment via a Pareto constraint limiting evasion.

However, we **failed to implement any detection tier**. All three tiers returned hard-coded `True` values:
- Tier 1: No LSH fingerprinting computation, no temporal isolation check
- Tier 2: No TSG probe generation, no differential alignment computation  
- Tier 3: No gradient/Hessian/CKA/efficiency computation

Therefore, we have not extended prior work. Fu et al.'s observation that MIA fails in pretraining and Dekoninck et al.'s demonstration that EAL evades semantic detection remain the state-of-the-art. Our contribution is not algorithmic but methodological: documenting how validation gaps (mock data checks that verify inputs but not processing) allow complete implementation failures to pass testing.

**Fair Positioning:** Prior detection methods (MIA, semantic similarity, provenance tracking) have documented limitations but represent genuine algorithmic contributions. Our work represents an implementation failure that provides no advancement to contamination detection theory. We include this Related Work section to contextualize what we attempted (geometric extension of detection methods) and why it matters (MIA and semantic methods have known failure modes), even though our attempt failed before testing any theoretical claims.
