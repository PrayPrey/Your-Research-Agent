# Research Idea: Differentiable Synthesis Pathway Modeling for Materials Foundation Models

## Title
Differentiable Neural SDE Framework for End-to-End Synthesis-to-Property Optimization in Materials Discovery

## Motivation
Current materials foundation models predict properties from crystal structures but ignore synthesis pathways, creating a critical theory-experiment gap. While computational methods identify promising materials, ~60% fail experimental realization due to synthesis challenges. Existing approaches treat synthesizability as a post-processing filter, preventing optimization of synthesis parameters. This gap limits real-world impact of AI-driven materials discovery, particularly for applications like battery materials and catalysts where synthesis-induced defects critically affect performance.

## Main Idea
We propose integrating learnable neural stochastic differential equations (SDEs) into materials foundation models to model time-dependent synthesis transformations. The core innovation is a hybrid continuous-discrete dynamics framework where synthesis conditions (temperature profiles, pressure, precursors) drive SDE evolution of coarse-grained states (phase fractions, grain size, defect density), which then map to final crystal structures. This creates the first end-to-end differentiable pipeline from synthesis parameters to material properties, enabling gradient-based inverse design.

**Methodology:** Train on 19K text-mined synthesis recipes using three-stage transfer learning (structure pre-training → synthesis training → joint fine-tuning), achieving 3-4× data efficiency. Hybrid SDE+jump processes capture both continuous dynamics and discrete nucleation events.

**Expected Impact:** Experimental validation targeting >70% success rate (vs. 40% baseline) in achieving target properties through optimized synthesis parameters, directly addressing the synthesis-property gap in materials discovery.