## Title
Validating LLM Reasoning via Predictive Coding-Inspired Residual Stream Analysis

## Motivation
LLMs often appear to reason on cognitive tasks like Theory of Mind (ToM), yet frequently rely on heuristic shortcuts that fail under adversarial conditions—the "Clever Hans" problem. Current benchmarks measure behavioral accuracy but cannot distinguish genuine compositional reasoning from pattern matching. This gap is critical: deploying LLMs in high-stakes domains requires mechanistic validation that reasoning is robust, not superficial. Bridging predictive coding theory from cognitive neuroscience with transformer interpretability offers a principled approach to this challenge.

## Main Idea
We hypothesize that genuine reasoning in LLMs produces hierarchical prediction error decay across transformer layers—high residual stream deltas early (encoding novel structure), progressive reduction mid-layers (building representations), low deltas finally (confident inference)—while heuristic responses show flat patterns. We propose V-PC-RAS (Validated Predictive Coding Residual Analysis Score), measuring exponential decay fit quality in layer-wise activation changes, normalized by input complexity.

**Methodology:** (1) Validate residual deltas as prediction error proxies via correlation with MLSAE latent variance (threshold: r>0.5); (2) Compute V-PC-RAS across Pythia models (70M-2.8B) on ToMBench and adversarial HI-TOM benchmarks; (3) Test whether V-PC-RAS predicts adversarial accuracy (r>0.4) while discriminating correct from incorrect responses (Cohen's d>0.5).

**Expected Impact:** A mechanistic diagnostic tool for pre-deployment cognitive auditing, distinguishing robust reasoning from brittle heuristics.