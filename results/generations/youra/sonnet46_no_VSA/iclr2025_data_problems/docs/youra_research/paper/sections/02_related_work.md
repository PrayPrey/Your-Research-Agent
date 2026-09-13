# 2. Related Work

## 2.1 CCNet and Perplexity-Based Quality Filtering

Wenzek et al. [2019] introduced CCNet, a pipeline for extracting high-quality monolingual text from CommonCrawl by training language-specific KenLM n-gram models on Wikipedia and scoring web documents by perplexity. The original design is explicitly per-language: each language receives its own KenLM model trained on its Wikipedia, and cutoffs are applied from language-specific tercile boundaries stored in `cutoff.csv`. This per-language calibration was not an afterthought — it acknowledges that perplexity scales depend on the reference corpus and should not be compared across languages.

However, practitioners adapting CCNet for large-scale multilingual pipelines have often simplified this design by applying a single global percentile threshold to the combined multi-language document pool. This simplification discards the per-language calibration in the original CCNet design. Dolma [Soldaini et al., 2024] applies Pythia-based perplexity scores; RedPajama-V2 [Weber et al., 2024] provides pre-computed ccnet_perplexity as a quality signal metadata field intended for downstream filtering. In each case, the path from pre-computed perplexity to actual data selection — including whether filtering is applied globally or per-language — is left to the practitioner. Our work shows that the most natural choice (global k-th percentile) has consequences that are not obvious from the CCNet paper's description.

## 2.2 Multilingual Dataset Quality Audits

Caswell et al. [2021] provide the most systematic audit of per-language quality differences in multilingual web corpora, evaluating over 100 languages in mC4. They document severe quality disparities in low-resource languages and argue that per-language quality evaluation is necessary — but they do not measure the associativity between language membership and retention rate under a global threshold. Their findings are qualitative and concern different filtering signals (not ccnet_perplexity specifically).

Adelani et al. [2023] audit quality filtering for African languages and find that global filters consistently fail for low-resource languages. Niyomugabo et al. [2025] (BhashaKritika) identify that per-language KenLM scoring is necessary even as a prerequisite quality evaluation step. These works motivate per-language approaches but do not provide quantitative V measurements for a specific dataset-signal-threshold combination that practitioners can calibrate correction strategies against.

## 2.3 Retention Rate Tuning for Multilingual Filtering

The work closest to ours is Turki et al. [2026], who study cross-lingual quality classifiers and find that retention rate tuning is necessary when applying multilingual quality filters — globally calibrated classifiers systematically under-retain some language groups. They adopt percentile-based (relative) thresholds computed per regression head as a best practice. Importantly, they endorse per-language percentile calibration as superior to absolute threshold calibration, providing indirect prior support for the correction hypothesis we formulate (h-m1). However, their setting differs: they work with neural classifiers trained on the mC4 corpus, not with pre-computed KenLM perplexity signals from RedPajama-V2.

Singh et al. [2024] (Repetition over Diversity) find that per-language filtering strategies produce qualitatively different diversity-quality tradeoffs than English-centric approaches. Chaudhary et al. [2025] (JQL) explicitly note that "absolute thresholds lack general validity unless supported by extensive ablation" and adopt percentile-based filtering — another endorsement of per-language calibration without a direct measurement of the V baseline we provide.

## 2.4 RedPajama-V2 and Quality Signals

Weber et al. [2024] describe the RedPajama-V2 dataset and its quality signal pipeline. They acknowledge that "ML-based quality signals have been reported to lead to biases or underrepresent minorities" and include ccnet_perplexity as one of 40+ quality signals computed for 5 languages (en, de, fr, es, it). They do not quantify the language-group retention disparity produced by global thresholding on any individual quality signal. Our work fills this gap for ccnet_perplexity, providing a calibrated Cramér's V measurement that the RedPajama-V2 paper itself lacks.

## 2.5 Our Position

Our work is the first to quantify the language-group retention disparity (Cramér's V) from global ccnet_perplexity thresholding on RedPajama-V2, across multiple threshold levels, with Holm-corrected significance. This fills the gap between CCNet's per-language design intent (Wenzek et al.) and the practitioner-observed disparity (Caswell et al.) by providing a precise, reproducible measurement. The V = 0.40–0.57 baseline we establish enables future correction studies (per-language percentile, iso-retention z-score, CCNet-consistent tercile) to be properly powered and evaluated. The finding that prior estimates underestimate actual V by 25–40% is an empirical contribution to the literature on multilingual quality filtering calibration.
