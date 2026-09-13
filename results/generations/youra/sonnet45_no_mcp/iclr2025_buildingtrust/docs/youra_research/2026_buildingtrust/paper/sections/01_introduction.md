# Introduction

Understanding where large language models fail requires systematic error analysis, but re-evaluating models on thousands of benchmark questions is prohibitively expensive—costing thousands of dollars in API fees and requiring access that may not be publicly available. A previous approach requiring GPT-4 and Claude API access failed with mock data contamination when credentials were unavailable, highlighting the fragility of API-dependent methods. What if the data we need already exists, hiding in plain sight within published technical reports?

Building trustworthy LLM systems demands understanding failure patterns, yet current approaches create barriers: only well-funded labs can afford systematic error analysis, creating a knowledge gap that hinders trustworthiness research. As LLMs become integral to critical applications affecting millions of users—from medical diagnosis systems to legal document analysis—understanding systematic weaknesses cannot remain the exclusive domain of organizations with large API budgets.

## The Deeper Challenge

Large language models fail on certain types of questions, and understanding these failure patterns is essential for building trustworthy systems. Benchmarks like TruthfulQA and MMLU reveal that even frontier models struggle with specific question categories, showing systematic weaknesses. However, analyzing these error patterns requires item-level model outputs across many questions. The conventional wisdom assumes that obtaining this data demands expensive re-evaluation: running models on benchmark questions through paid APIs.

This assumption creates a fundamental barrier. Previous work focused on developing sophisticated error detection methods, assuming data collection was a solved problem. Yet API costs ($22-45 per experiment for running GPT-4, Claude-3, and Llama-3 on benchmark subsets) and credential requirements create real obstacles. When our initial clustering-based approach required live API access, it failed catastrophically—defaulting to mock data when credentials were unavailable, producing meaningless results that passed superficial validation checks. The data collection barrier proved more fundamental than any analysis algorithm.

The gap in existing work is that published technical reports from major labs contain detailed benchmark results, but no prior work has systematically validated whether this data has sufficient granularity and completeness for error pattern analysis. Researchers assumed published results were too coarse-grained (aggregate scores only) or didn't consider checking systematically because the default assumption was that re-evaluation is necessary. If published data proves sufficient, we could eliminate expensive re-evaluation and enable any researcher to study error patterns using freely available public data.

## Our Insight

Major LLM labs systematically publish category-level benchmark results across model generations, providing a previously untapped data source for systematic error analysis without requiring re-evaluation. Technical reports from OpenAI, Anthropic, and Meta consistently include category-level breakdowns (12-15 categories per benchmark) with 100% data completeness across both baseline and current model generations. This granularity is sufficient for weak supervision approaches to error taxonomy, eliminating the need for expensive API calls or re-evaluation.

Why did others miss this? Researchers assumed published results only contained aggregate scores (single accuracy numbers) or that extracting structured data from PDFs was too unreliable. We took a different view: we systematically validated data availability rather than assuming—treating it as an empirical question requiring rigorous gate validation (MUST_WORK hypothesis). The failure of our previous API-dependent approach forced this pivot to public-data-only methods, which led to discovering this existing data source.

The mechanism is intuitive: major labs publish detailed results because of competitive pressure—they want to show not just that their model is good overall, but specifically where it excels. This creates a public data trail that persists in technical reports. Category-level rates provide the weak supervision signal needed for item-level clustering: questions in the same category share error patterns, enabling taxonomy generation without item-level ground truth. It's like using weather station measurements (category-level) to understand local microclimates (item-level)—coarse-grained observations combined with spatial features enable fine-grained inference.

## Contributions

Building on this insight that published data may be sufficient, we make three contributions:

**Systematic validation across model families and time.** We validate that all three targeted model families (GPT from OpenAI, Claude from Anthropic, Llama from Meta) provide category-level error rate data for both baseline (2022-2023) and current (2023-2024) model generations across two standard trustworthiness benchmarks (TruthfulQA, MMLU). This empirical finding establishes that category-level reporting is systematic practice across the frontier LLM ecosystem, not a single-organization artifact.

**Quantification of data quality for weak supervision.** We measure granularity (12 categories for TruthfulQA, 15 for MMLU) and completeness (100% of expected data cells present with zero missing values), demonstrating that published results exceed the minimum requirements (≥10 categories, ≥90% completeness) from weak supervision literature for robust clustering. This methodological contribution validates that coarse-grained category labels can support fine-grained item-level analysis.

**Demonstration of public-data-only viability.** By eliminating API dependency, we show that systematic error analysis is accessible to any researcher with internet access, not just well-funded labs. This practical contribution democratizes trustworthiness research, enabling academic researchers without API budgets, practitioners building guardrails, and auditors assessing model behavior to study failure patterns using freely available published data.

## Paper Organization

We organize the paper as follows: Section 2 discusses related work in LLM error analysis, benchmark meta-analysis, and weak supervision approaches. Section 3 describes our validation methodology, explaining why systematic data availability checking requires explicit empirical validation. Section 4 presents our experimental setup and validation protocol. Section 5 reports results showing perfect family coverage, granularity exceeding thresholds, and 100% data completeness. Section 6 discusses implications for error taxonomy research, acknowledges limitations of foundation-only validation, and frames broader impact on research accessibility. Section 7 concludes with future directions for completing the taxonomy generation pipeline.
