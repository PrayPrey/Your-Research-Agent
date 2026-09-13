# 2. Related Work

Our work sits at the intersection of data curation for language model pretraining and fairness analysis in large language models. We review both streams and demonstrate that neither, taken alone, addresses the gap we fill.

## 2.1 Data Curation for Pretraining Performance

The past two years have produced a sequence of rigorous, large-scale studies of how pretraining data curation affects downstream model performance. DCLM [Li et al., 2024] establishes that fastText quality filtering of CommonCrawl (the DCLM-POOL) achieves 64% MMLU at 7B scale with 2.6T tokens — a substantial improvement over unfiltered web data. The DCLM study ablates filtering methods, deduplication, and dataset composition systematically, making it the closest reference point for our experimental design. However, DCLM explicitly acknowledges that "bias, toxicity, and safety" are out of scope, and does not measure fairness outcomes of the filtering decisions it studies.

FineWeb [Penedo et al., 2024] demonstrates competitive MMLU and ARC performance via C4-like filtering plus deduplication on 15T tokens of CommonCrawl. Like DCLM, FineWeb's evaluation is performance-only. DoReMi [Xie et al., 2023] introduces domain reweighting via a proxy model that shifts domain proportions to improve few-shot accuracy (+6.5%) and reduce the tokens needed to reach baseline performance (2.6×). DoReMi demonstrates that domain composition is a powerful lever — but measures only performance outcomes of domain reweighting, not demographic structure changes. Dolma [Soldaini et al., 2024] provides modular filtering infrastructure and explicitly documents demographic limitations (primarily English, Western-centric), but does not provide a quantitative methodology to measure how filtering decisions alter demographic-occupation associations.

These works collectively establish that curation hyperparameters have large, measurable effects on downstream performance. Our contribution is to extend this framework to fairness-relevant corpus structure — showing that the same curation decisions that improve MMLU also systematically alter H(occupation|demographic), and providing the first audit methodology to quantify this effect.

## 2.2 Fairness in Large Language Models

The fairness literature has documented extensive output-level disparities in LLMs. Bender et al. [2021] ("Stochastic Parrots") argue qualitatively that large-scale web corpora encode harms through statistical patterns in language. Parrish et al. [2022] introduce BBQ, a benchmark for measuring social biases (race, gender, religion, and others) in question answering. Zhao et al. [2018] introduce WinoBias, a coreference resolution benchmark sensitive to gender-stereotyped occupations. Nadeem et al. [2021] introduce StereoSet, measuring stereotype endorsement in completion tasks.

While these benchmarks measure model outputs, they do not trace observed disparities to specific pretraining data decisions. Several studies have shown that different LLMs produce different fairness benchmark scores [CITE: survey paper], but these studies compare models trained on different data pipelines and architectures simultaneously — making it impossible to isolate the effect of curation from other design decisions.

Closer to our work, several papers have examined how training data composition affects model behavior. [CITE: demographic bias in web corpora] document demographic imbalances in web corpora; [CITE: documenting large webtext corpora] argue for better documentation of corpus demographic properties. However, these works describe properties of corpora rather than measuring how specific curation operations alter those properties as a function of hyperparameters.

Our work provides the missing piece: a controlled mapping from curation hyperparameters (fastText percentile threshold) to quantitative corpus-level demographic structure changes, validated across 7 configurations with statistical rigor.

## 2.3 Corpus Analysis and Data Documentation

Data documentation frameworks [Gebru et al., 2018; Bender & Friedman, 2018] advocate for structured disclosure of dataset demographic properties. Datasheet-style documentation has been applied to several pretraining corpora [Soldaini et al., 2024; Penedo et al., 2024]. However, these approaches describe static corpus properties rather than measuring how curation operations transform those properties.

Information-theoretic approaches to corpus analysis are less common. [CITE: entropy in corpora] have measured distributional properties of training data, but not in the context of quality filtering effects on demographic associations. Our use of conditional entropy H(occupation|demographic) as a direct measure of demographic-occupation association density is, to our knowledge, novel in the context of curation ablations.

## 2.4 Our Position

Our work is differentiated from all three streams above:

- **From data curation work** (DCLM, FineWeb, DoReMi): We add the fairness dimension that these works explicitly exclude, using the same experimental framework (controlled ablations on DCLM-POOL) they pioneered.

- **From fairness in LLMs work** (BBQ, WinoBias, Stochastic Parrots): We trace fairness-relevant signals to the corpus level before model training, providing a model-free audit methodology rather than post-hoc output analysis.

- **From data documentation work** (Dolma, Datasheets): We provide a quantitative, measurement-oriented methodology rather than a documentation checklist — practitioners can run our audit on any corpus configuration and receive numerical fairness-relevance signals.

The Path-Dependent Curation Fairness Hypothesis (PCFH) unifies these perspectives: different curation paths create path-dependent corpus structures with measurable fairness implications, and our corpus audit methodology provides the diagnostic tool to surface these differences before training.
