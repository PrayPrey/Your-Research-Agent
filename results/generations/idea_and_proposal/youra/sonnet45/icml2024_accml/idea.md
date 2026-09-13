# Title
BioLoop-MVB: A Clinical Trials-Inspired Benchmark for Lab-in-the-Loop Protein Engineering

# Motivation
Foundation models for biology face a critical adoption gap: while iterative ML-experiment systems show promise, lack of standardized evaluation prevents biologists from selecting effective feedback strategies. Existing lab-in-the-loop methods report custom metrics on different tasks, making reproducible comparison impossible. This hinders adoption in resource-constrained labs that cannot afford trial-and-error method selection. We need a standardized benchmark framework that enables evidence-based comparison of experimental feedback integration strategies.

# Main Idea
We propose the first standardized benchmark for lab-in-the-loop protein engineering, adapting clinical trials endpoint methodology to biological AI. The framework evaluates feedback strategies (likelihood reintegration, Bayesian optimization, active learning) using three metric tiers: **primary endpoint** (functional hit rate: % designs with ΔTm > +5°C), **secondary endpoints** (sequence diversity, experimental cost), and **composite score** (efficiency = hit rate × diversity / cost). 

A simulated experimental oracle built from ProTherm/FireProtDB enables reproducible evaluation without wet-lab dependency. We test whether this framework can statistically differentiate methods (p < 0.05) while enabling independent replication (inter-lab CV < 10%). Validation requires oracle correlation r > 0.7 with published experiments across 20 papers.

**Expected impact:** Provides biologists evidence-based guidance for method selection, reduces experimental costs through simulation-based development, and establishes an extensibility template for RNA/CRISPR/drug discovery benchmarks.