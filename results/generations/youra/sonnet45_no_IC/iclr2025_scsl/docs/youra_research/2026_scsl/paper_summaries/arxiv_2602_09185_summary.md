# AIDev: Studying AI Coding Agents on GitHub

## Key Metadata
- **Authors:** Li, Zhang, & Hassan
- **Year:** 2026
- **Venue:** arXiv
- **Core Contribution:** Large-scale dataset of 932,791 AI-generated PRs from 116,211 repositories for studying AI agent adoption

## Section Summaries

### Abstract
Presents AIDev dataset: 932,791 Agentic-PRs from 116,211 repositories involving 72,189 developers. Analyzes AI coding agent adoption patterns, developer productivity impacts, and collaboration dynamics. Demonstrates feasibility of large-scale GitHub metadata extraction and analysis infrastructure.

### Introduction & Motivation
AI coding agents (GitHub Copilot, ChatGPT Code Interpreter, Cline, etc.) transforming software development. Gap: no systematic study of AI agent contributions in real-world repositories at scale. Research questions: How prevalent are AI-generated PRs? Do they differ from human PRs? What repositories adopt AI agents most?

### Methodology
**Data Collection Infrastructure:** GitHub GraphQL API + GHArchive for comprehensive metadata extraction. Identified AI-generated PRs via: (1) PR descriptions mentioning AI tools (regex patterns), (2) Commit messages with AI signatures, (3) PR labels (e.g., "ai-generated", "copilot"). Validation: manual inspection of 1,000 random samples (precision 0.94).

**Dataset Scope:** Time range: Jan 2021 - Dec 2025 (5 years). Repositories: 116,211 with ≥1 Agentic-PR. Total PRs: 932,791 Agentic + 8,547,293 human baseline. Metadata collected: commits, reviews, comments, issues, stars, forks, contributors, merge status, time-to-merge, code churn.

**Analysis Dimensions:** (1) Adoption patterns (temporal trends, repository characteristics), (2) PR quality metrics (review comments, merge rate, time-to-merge), (3) Developer productivity (PR velocity, code volume), (4) Collaboration dynamics (reviewer engagement, discussion threads).

### Experiments & Results
**Adoption Trends:** Exponential growth: 12K Agentic-PRs in 2021 → 450K in 2025 (37× increase). Repository size correlation: larger repos (>100 contributors) adopt earlier. Language breakdown: TypeScript (28%), Python (24%), JavaScript (19%), Go (11%), Rust (8%).

**PR Quality:** Agentic-PRs have 15% fewer review comments than human PRs (median 3 vs 3.5). Merge rate slightly lower (78% vs 82%). Time-to-merge faster (median 8 hours vs 14 hours) for Agentic-PRs. Code churn per PR: Agentic +245 LOC/-180 LOC vs Human +320 LOC/-220 LOC (Agentic smaller changes).

**Productivity Impact:** Developers using AI agents submit 32% more PRs/month (median 4.2 vs 3.2). But individual PR sizes smaller (Agentic PRs 40% less LOC). Overall code contribution volume +5% with AI agents. No significant difference in bug-introducing PR rate (9.2% vs 9.5%).

**Repository Characteristics:** Top adopter categories: web frameworks (23%), ML/AI libraries (19%), DevOps tools (15%), data processing (12%). Repositories with >1000 stars adopt 2.3× faster than <100 stars repos. Open-source sustain ability correlation: repos with Agentic-PRs have 12% longer median active lifespan.

**Validation:** Cross-referenced with repository maintainer surveys (N=250). Self-reported AI tool usage matches detected Agentic-PR patterns (Cohen's kappa 0.81). Developer sentiment analysis: 68% positive, 22% neutral, 10% negative toward AI-generated contributions.

### Discussion & Conclusion
Large-scale GitHub metadata analysis infrastructure validated for AI adoption research. Agentic-PRs show distinct patterns: smaller, faster, slightly lower merge rate. AI agents increase PR velocity but not necessarily total code contribution. Future work: causal analysis of productivity gains, longitudinal study of code quality evolution, cross-platform comparison.

## Key Contributions
- AIDev dataset: 932K+ AI-generated PRs across 116K repositories (largest to date)
- Scalable GitHub metadata extraction infrastructure (GraphQL + GHArchive)
- Empirical evidence of AI agent adoption patterns and productivity impacts
- Validated methodology for detecting AI-generated contributions at scale

## Potential Relevance
Demonstrates large-scale (100K+ repositories) GitHub metadata analysis is feasible and validated. Metadata extraction patterns (stars, forks, commits, PRs, merge rates, code churn) directly applicable to repository maintenance classification. Infrastructure approach (GraphQL API + GHArchive + efficient retrieval) provides reference implementation for feature engineering pipeline.
