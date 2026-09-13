# Research Idea

## Title
Contrastive Differential Evaluation of Language Acquisition (C-DELA): Measuring How Multi-Agent Language Games Improve LLM Compositional Abilities

## Motivation
Current LLM training relies almost exclusively on supervised and preference losses, lacking the interactive dynamics that cognitive science identifies as crucial for genuine language acquisition. While language emergence research shows that multi-agent communication games produce compositional, generalizable languages in small-scale agents, LLMs exhibit a "compositionality gap"—failing to combine known concepts effectively. A critical barrier to progress is the absence of rigorous metrics that can detect whether interactive training actually improves fundamental language properties in LLMs, rather than just behavioral performance.

## Main Idea
We propose C-DELA, a framework to measure whether multi-agent language games induce genuine representational improvements in LLMs. The core hypothesis: interactive training creates functional pressures (referential success, communicative efficiency) that reshape internal representations, producing measurable gains in compositionality, grounding, displacement, and transmission efficiency.

**Methodology:** Train LLMs on referential language games with 2-4 agents, then apply probing classifiers to compare pre/post-training representations. Contrastive perturbation establishes noise floors, enabling calibrated metrics (CGS, GAI, DCM, TES) that distinguish genuine improvements from measurement variance.

**Expected Outcomes:** Compositional Gain Scores exceeding 0.1 (normalized) would demonstrate that interactive training closes the compositionality gap. This provides the first rigorous measurement framework for language gamification research, enabling principled comparison of interactive training approaches.