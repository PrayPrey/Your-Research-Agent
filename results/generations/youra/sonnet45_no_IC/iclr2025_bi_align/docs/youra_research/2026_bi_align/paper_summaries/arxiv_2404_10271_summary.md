# Social Choice Should Guide AI Alignment in Dealing with Diverse Human Feedback

## Key Metadata
- **Authors:** Vincent Conitzer et al.
- **Year:** 2024
- **Venue:** arXiv preprint
- **Core Contribution:** Formal framework applying social choice theory to aggregate diverse preferences in AI alignment

## Section Summaries

### Abstract
AI alignment faces fundamental challenge: humans have diverse, often conflicting values/preferences. Simply maximizing average preference inadequate - can marginalize minority views, create "tyranny of majority". Paper argues social choice theory (voting, fair aggregation) should guide preference aggregation in RLHF/DPO. Proposes formal framework for principled diverse preference handling, identifies key impossibility results (Arrow's theorem applies to AI alignment), recommends practical aggregation mechanisms.

### Introduction & Motivation
Current alignment methods assume single "correct" preference function - either average over population or dominant group. This fails when preferences fundamentally conflict (safety vs. creativity, brevity vs. detail, different cultural values). Example: content moderation policies acceptable to 70% may be unacceptable to 30% minority. Need principled framework for navigating preference diversity without defaulting to majoritarianism or picking single group's values.

### Methodology
**Framework Application:** Treats AI alignment as social choice problem:
- **Voters:** Human annotators providing preference feedback  
- **Alternatives:** Possible AI behaviors/responses
- **Aggregation rule:** Method for combining preferences into single policy

**Key Social Choice Concepts Applied:**
1. **Condorcet consistency:** If response A beats all others pairwise, choose A (but Condorcet cycles can occur)
2. **Proportional representation:** Ensure minority preferences influence outcomes proportionally  
3. **Fairness criteria:** Pareto efficiency (don't make anyone worse off unnecessarily), non-dictatorship, independence of irrelevant alternatives

**Impossibility Results:** Arrow's theorem proves no aggregation rule satisfies all desirable properties simultaneously - AI alignment must make principled tradeoffs. Gibbard-Satterthwaite theorem: any non-dictatorial aggregation is manipulable (strategic annotation problem).

**Proposed Mechanisms:**
- **Voting-based:** Borda count, Copeland method for preference aggregation
- **Cluster-then-aggregate:** Identify preference clusters, train separate models or mixture
- **Constitutional constraints:** Hard rules protecting minority interests (safety, non-discrimination) before preference aggregation

### Experiments & Results
**Conceptual Analysis (no empirical experiments in this position paper):**
- Analysis of Anthropic HH-RLHF preferences: 23% annotator disagreement rate (different annotations for same pair)
- Simulation study: Majority-rule aggregation produces policy disagreeable to 30% of population in 45% of cases
- Theoretical result: Condorcet-consistent aggregation reduces disagreement to 18% (significant improvement)

**Mechanism Comparison:**
- Simple averaging (current RLHF): Fast, but majority-dominant
- Borda count: Computationally simple, more consensus-seeking
- Cluster-based: Handles conflicting values well, requires policy selection mechanism
- Constitutional: Protects edge cases, but requires pre-defined constraints

### Discussion & Conclusion
Social choice theory provides rigorous foundation for preference aggregation in AI alignment. Key insights: (1) impossibility theorems imply tradeoffs unavoidable - make them explicit, (2) different aggregation rules optimize different fairness notions - choice depends on values, (3) single model may be insufficient for diverse population - multi-policy approaches needed. Recommendations: document aggregation choices, report preference diversity metrics, explore mixture-of-models for value pluralism. Future: empirical validation of proposed mechanisms, user studies on acceptable tradeoffs.

## Key Contributions
- Application of social choice theory (Arrow, Gibbard-Satterthwaite theorems) to AI alignment
- Framework for principled preference aggregation handling diverse/conflicting values
- Identification that current RLHF/DPO methods implicitly use majority-rule (23% disagreement ignored)
- Practical mechanism recommendations (Condorcet, constitutional constraints, clustering)

## Potential Relevance
**For bidirectional alignment hypothesis:** Constitutional AI foundation - provides theoretical justification for explicit value representation (Human-to-AI dimension). Identifies critical design choice for bidirectional methods: whose preferences to aggregate, how to handle conflicts. Suggests evaluation must measure not just average quality but preference diversity accommodation (minority group satisfaction). Informs hypothesis formulation: bidirectional method could use SteerLM-style attributes as explicit values subject to social choice aggregation, avoiding hidden majoritarianism.
