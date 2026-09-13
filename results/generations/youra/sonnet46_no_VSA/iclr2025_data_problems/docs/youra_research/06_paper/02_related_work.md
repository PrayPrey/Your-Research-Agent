# Related Work

## CCNet and Perplexity-Based Filtering

CCNet \cite{Wenzek2020} introduced the paradigm of using KenLM language models trained on Wikipedia to score CommonCrawl documents by perplexity, then filtering to retain only low-perplexity "Wikipedia-like" text. A critical design decision in the original CCNet pipeline is that language models are trained *per language*, and the filtering threshold is applied as a *per-language* tercile cutoff defined in a language-specific `cutoff.csv`. This per-language design was intentional: the authors recognized that perplexity scales produced by KenLM models trained on different Wikipedia corpora are not directly comparable across languages.

When practitioners apply CCNet perplexity scores from pre-computed metadata — as in RedPajama-V2 \cite{Weber2024} — they often replace this per-language tercile cutoff with a global percentile threshold for simplicity. Our work shows this substitution introduces large, systematic language-group biases. In this sense, we demonstrate that the practitioner deviation from CCNet's original per-language design is the proximate cause of the disparity we measure.

## Multilingual Quality Filtering

\citet{Caswell2021} conducted a comprehensive audit of web-crawled multilingual datasets including mC4 and multilingual Wikipedia, finding that standard quality metrics derived from English-centric sources apply poorly to non-English text. Their work highlighted that per-language evaluation is necessary and that global thresholds applied to multilingual corpora encode implicit language biases. Our work extends this qualitative finding with a quantitative effect-size measurement (Cramér's V) across a specific, practically important quality signal.

\citet{Jansen2022} showed that perplexity-based quality detection breaks down on multilingual heterogeneous web data, particularly for identifying harmful content across languages with different script systems and Wikipedia representation. We focus on the related but distinct problem of retention disparity in general quality filtering, rather than content classification.

More broadly, the multilingual NLP community has documented a pattern of English-centric data practices that disadvantage other languages \cite{Caswell2021,Jansen2022}. Our contribution is to show that the bias can operate in the opposite direction to typical intuition: it is *Germanic* languages (including English) that are disadvantaged relative to *Romance* languages under global CCNet perplexity thresholds on RedPajama-V2, due to the specific characteristics of Wikipedia corpora in each language family.

## Adaptive Thresholding

\citet{Ali2025} (Judging Quality Across Languages, JQL) advocate for per-language percentile-based thresholds, arguing that "absolute thresholds lack general validity unless supported by extensive ablation" and that "percentile-based filtering is better suited than threshold-based filtering" for multilingual settings. They demonstrate this on proprietary multilingual data with neural language model quality scores. Our work provides the quantitative motivation for this recommendation on a public, widely-used dataset (RedPajama-V2), measuring the exact magnitude of the disparity that per-language thresholds aim to correct.

Turki et al. \cite{Turki2026} study retention rate tuning for multilingual quality classifiers, also arguing for per-language calibration. Our existence baseline — V = 0.40–0.57 — provides the calibration target: a successful per-language calibration strategy should reduce V to near zero.

## Dataset Construction and Bias

Weber et al. \cite{Weber2024} note in the RedPajama-V2 paper that "ML-based quality signals have been reported to lead to biases or underrepresent minorities," and caution that the pre-computed signals require careful application. Our work provides a concrete, empirical instantiation of this caution for the specific case of `ccnet_perplexity` with global percentile thresholds.

Work on data documentation and dataset auditing \cite{Caswell2021} has established the importance of characterizing dataset properties before downstream use. Our measurement study follows this tradition, providing a precise characterization of the retention disparity that any practitioner using `ccnet_perplexity` with a global threshold will introduce.

## Effect Size Measurement for Data Curation

The use of Cramér's V to quantify language-group association in retained vs. filtered document sets is, to our knowledge, novel in the data curation literature. Prior work typically reports per-language retention rates or qualitative assessments; our application of a standard contingency table effect size with Holm-Bonferroni correction across multiple threshold levels provides a reproducible, comparable metric for future correction evaluation.
