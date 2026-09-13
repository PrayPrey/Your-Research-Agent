# Research Idea

## Title
Probing-Based Model Selection for Time Series Foundation Models: Characterizing Semantic vs. Temporal Knowledge

## Motivation
Time series foundation models (TSFMs) now include both native architectures (Chronos, Lag-Llama) and LLM-adapted models (Time-LlaMA, ChatTime), yet practitioners lack principled guidance for selecting between them. Current model selection relies on expensive trial-and-error across benchmarks. A critical gap exists: we don't understand *what knowledge types* each architecture captures, nor how task characteristics should inform model choice. This research addresses the need for interpretable, efficient model selection in the growing TSFM ecosystem.

## Main Idea
We hypothesize that probing classifiers applied to TSFM intermediate representations can quantify semantic (contextual metadata) versus temporal (pattern-based) information content, enabling prediction of which model type will excel on a given task. The core mechanism: LLM-adapted models encode richer semantic information from pretraining, while native TSFMs specialize in temporal patterns. By computing the semantic-to-temporal information ratio via linear probes, we can recommend the appropriate model type.

**Methodology:** Train linear probes on TSFM representations to predict semantic features (domain labels, metadata) and temporal features (periodicity, trends). Use probe accuracy as a proxy for mutual information content. Evaluate model selection accuracy across Monash, FinTSB, and GIFT-Eval benchmarks.

**Expected Outcomes:** Model selection accuracy >65% (vs. 50% random baseline), validated through 88+ task-model pairs. This framework provides interpretable insights into TSFM knowledge attribution while offering practical guidance for deployment decisions.