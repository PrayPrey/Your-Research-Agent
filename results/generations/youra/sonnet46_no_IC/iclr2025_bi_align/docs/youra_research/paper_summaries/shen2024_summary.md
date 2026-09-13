# Towards Bidirectional Human-AI Alignment: A Systematic Review

## Key Metadata
- **Authors:** Hua Shen, Tiffany Knearem, Reshmi Ghosh, et al. (24 authors)
- **Year:** 2024
- **Venue:** arXiv (2406.09264) / NeurIPS 2024; citations: 71 (systematic review), 14 (position paper)
- **Core Contribution:** 400+ paper systematic review establishing bidirectional alignment as a distinct research paradigm with two directions: (1) AI aligning with Humans (H→AI), (2) Humans aligning with AI (AI→H).

## Section Summaries

### Abstract
Current AI alignment research focuses almost exclusively on aligning AI with human values (H→AI). This systematic review argues for a bidirectional framework: both AI must align with humans AND humans must adapt to AI systems. The review synthesizes 400+ papers across HCI, NLP, and ML to map the bidirectional alignment landscape. Key gap identified: the AI→H direction (how humans adapt to AI) is severely under-studied.

### Introduction & Motivation
The unidirectional focus on H→AI alignment (RLHF, RLAIF, constitutional AI) leaves unexplored how AI systems shape human understanding, behavior, and trust. Bidirectional alignment is critical for long-term human-AI collaboration. The gap between human preferences (win_rate) and AI-annotator preferences (LC_winrate) is an empirical instantiation of the bidirectional alignment gap — humans prefer outputs the AI annotator discounts (or vice versa).

### Methodology
Systematic literature review of 400+ papers using PRISMA methodology. Papers coded along two axes: (1) alignment direction (H→AI vs AI→H) and (2) alignment level (value, behavioral, cognitive). The AlpacaEval Δ = LC_winrate − win_rate operationalizes the empirical gap between H→AI signal (win_rate: human preference) and AI→H signal (LC_winrate: GPT-4 preference, controlling for length). When Δ < 0, GPT-4 rates lower than humans — the AI annotator systematically disagrees with humans.

### Experiments & Results
Finding: 89% of reviewed papers address H→AI alignment; only 11% address AI→H. The bidirectional gap is identified as an open empirical challenge. No prior systematic measurement of how model quality moderates the bidirectional gap. The ICLR 2025 Workshop on Bidirectional Human-AI Alignment directly follows from this gap identification.

### Discussion & Conclusion
The paper calls for research quantifying the bidirectional gap empirically. Our work (testing ρ(win_rate, Δ)) directly answers this call: does model capability moderate how large the bidirectional misalignment is? Limitation: conceptual framework; empirical operationalization needed.

## Key Contributions
- 400+ paper systematic review of bidirectional alignment
- Taxonomy of H→AI vs AI→H alignment directions
- Identification of AI→H direction as severely under-studied research gap

## Potential Relevance
This paper establishes the theoretical motivation for the h-m2 hypothesis. Δ = LC_winrate − win_rate operationalizes the bidirectional gap as a per-model empirical quantity. If ρ(win_rate, Δ) < 0 (capability predicts smaller |Δ|), it implies that capability improvements implicitly reduce bidirectional misalignment — a policy-relevant finding for the ICLR 2025 workshop audience.
