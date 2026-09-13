# Research Idea

## Title
ML-HFACS: Adapting Aviation's Human Factors Taxonomy for Systematic Classification of Deep Learning Deployment Failures

## Motivation
Despite deep learning's benchmark successes, real-world deployments frequently fail in ways that remain poorly understood and undocumented. Current ML research lacks systematic frameworks for categorizing failures—79% of papers use weak baselines, and failure discussions remain siloed within domains. Aviation solved a similar problem through HFACS (Human Factors Analysis and Classification System), a validated hierarchical taxonomy enabling cross-incident learning. No equivalent exists for ML, preventing the community from identifying common failure patterns across healthcare, robotics, and other deployment domains.

## Main Idea
We propose adapting aviation's HFACS framework to create ML-HFACS: a 4-level hierarchical taxonomy with 24 categories for classifying ML deployment failures. The core hypothesis is that hierarchical failure classification is domain-invariant—HFACS has successfully transferred to healthcare, maritime, and nuclear domains, suggesting ML sociotechnical systems share similar causal structures.

**Methodology:** Collect 100 documented ML failures (50 industry, 50 public sources), train 3 raters using a standardized 4-hour protocol, and measure inter-rater reliability using Cohen's κ.

**Success criteria:** κ > 0.7 (substantial agreement), >95% failure coverage, and >70% of deployment failures containing organizational/supervisory factors (Levels 1-2).

**Expected impact:** A validated, shareable taxonomy enabling cross-domain failure pattern identification and predictive insights for safer ML deployment.