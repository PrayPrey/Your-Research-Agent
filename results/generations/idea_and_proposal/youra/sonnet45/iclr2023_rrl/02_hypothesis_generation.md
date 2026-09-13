# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-06
**Author:** Pray
**Source Round:** 02a_round_2_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-RLHub-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under conditions where RL research requires prior computation reuse, if a comprehensive infrastructure platform is provided with (1) standardized packaging formats (ONNX for policies, Parquet for datasets), (2) quality certification system (Bronze/Silver/Gold badges), (3) decentralized storage (IPFS + optional blockchain), (4) discovery interface with semantic search, and (5) version control for environment compatibility, then RL research accessibility and cost efficiency will significantly increase (measured by: unique researchers using artifacts ≥200, institutions represented ≥50, estimated compute savings ≥100K GPU-hours/year within 12 months post-launch) because reduced barriers to artifact sharing enable community-wide computation reuse, creating a positive feedback loop where contributors receive academic credit (conference reproducibility badges) and users save computational costs.

**Alternative Hypothesis (H0):**
Providing infrastructure for RL artifact sharing will NOT significantly increase research accessibility or cost efficiency beyond ad hoc GitHub sharing. The platform will fail to achieve critical mass (≥200 artifacts within 12 months) or demonstrate measurable compute savings, indicating that infrastructure alone is insufficient without addressing deeper incentive misalignment or community adoption barriers.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Infrastructure Completeness | Independent | Number of core features implemented (0-5): (1) Packaging formats, (2) Quality certification, (3) Decentralized storage, (4) Discovery interface, (5) Version control | 0-5 features (Target: 5/5 at launch) |
| Research Accessibility | Dependent | (a) Unique researchers downloading artifacts, (b) Number of institutions represented, (c) Geographic diversity (countries) | (a) 200+ researchers, (b) 50+ institutions, (c) 15+ countries within 12 months |
| Cost Efficiency | Dependent | (a) Estimated compute hours saved (artifact reuse vs training from scratch), (b) Percentage of survey respondents citing cost savings | (a) 100K+ GPU-hours saved/year, (b) ≥60% cite savings |
| Artifact Quality | Controlled | Quality certification level: Bronze (reproducible script), Silver (3+ independent verifications), Gold (benchmark-tested on CORA/Continual World) | All uploaded artifacts require ≥Bronze; measure % achieving Silver/Gold |
| Community Engagement | Dependent | (a) Artifacts uploaded, (b) Number of contributors, (c) Total downloads, (d) Repeat usage rate | (a) 200+ artifacts, (b) 100+ contributors, (c) 5K+ downloads, (d) 40%+ reuse within 12 months |
| Consortium Sustainability | Independent | Number of institutions in consortium, annual funding per institution | 5-10 institutions, $5K-10K/year per institution (Total: $25-100K/year) |

### 1.3 Causal Mechanism

**5-Step Causal Chain:**

**Step 1: Standardized Packaging → Cross-Framework Compatibility**
- **Mechanism:** ONNX (Open Neural Network Exchange) enables policies trained in PyTorch to be loaded in JAX or TensorFlow without conversion errors. Parquet columnar format handles large trajectory datasets (100GB+) with efficient compression and framework-agnostic loading.
- **Evidence:** ONNX is production-proven in Microsoft, Facebook ML systems for cross-framework model deployment. Parquet is standard in Apache Arrow ecosystem for large-scale data processing.
- **Falsification Point:** If >20% of artifact conversions fail across frameworks, standardization fails.

**Step 2: Cross-Framework Compatibility → Increased Artifact Reuse**
- **Mechanism:** Removing framework lock-in expands potential user base by 3-5x. A PyTorch-trained policy becomes usable by JAX researchers (Google, DeepMind) and TensorFlow researchers (industry), multiplying reuse opportunities.
- **Evidence:** Hugging Face's multi-framework support (PyTorch + TensorFlow + JAX via transformers library) significantly increased model download rates compared to framework-specific hubs.
- **Falsification Point:** If download rates don't differ between single-framework vs multi-framework artifacts, compatibility doesn't drive reuse.

**Step 3: Quality Certification Badges → Trust in Artifact Reliability**
- **Mechanism:** Bronze/Silver/Gold badges signal independent verification levels, reducing perceived risk of using potentially flawed prior computation. Researchers preferentially download certified artifacts (analogous to how citation count signals paper quality).
- **Evidence:** Semantic Scholar literature graph uses quality signals (citation count, venue tier) to rank papers. Academic reproducibility badges increase citation rates by 20-40% (ACM, NeurIPS data).
- **Falsification Point:** If certified artifacts are NOT downloaded more frequently than uncertified ones (controlling for performance), badges don't build trust.

**Step 4: Trust + Reusability → Community Contributions**
- **Mechanism:** Positive feedback loop: Contributors see download metrics (social proof) and receive academic credit via conference reproducibility badges (appears on paper in proceedings), incentivizing continued sharing. This mirrors GitHub stars driving open-source contributions.
- **Evidence:** Conference badges (Best Paper, Outstanding Paper) increase visibility and citations. GitHub projects with visible metrics (stars, downloads) attract more contributors.
- **Falsification Point:** If contributor count plateaus despite high download rates and badge availability, incentives are insufficient.

**Step 5: Growing Artifact Library → Research Democratization**
- **Mechanism:** Critical mass of artifacts (≥200) enables researchers without large compute budgets ($10K+) to leverage community-shared prior computation, reducing entry costs to $100-1K for fine-tuning. This directly addresses Agarwal et al.'s reincarnating RL democratization goal.
- **Evidence:** Reincarnating RL (NeurIPS 2022, 84 citations) explicitly motivates democratizing RL by sharing prior computation. Hugging Face enabled NLP democratization by providing 10K+ pretrained models.
- **Falsification Point:** If usage patterns show only well-resourced institutions (e.g., Google, OpenAI) using RLHub (no small university/individual usage), democratization fails.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | ONNX Production Deployments (Microsoft, Meta) | Cross-framework model serving at scale | Strong |
| Step2 → Step3 | Hugging Face Growth (2018-2024) | Multi-framework support correlated with 10x user growth | Medium-Strong |
| Step3 → Step4 | Semantic Scholar Paper (2018, 425 cit) | Quality signals (citations, venue) drive literature discovery | Strong |
| Step4 → Step5 | ACM Reproducibility Badge Study | Badges increase citations by 20-40% | Medium |
| Step5 → Outcome | Reincarnating RL Paper (2022, 84 cit) | Compute cost is primary barrier to RL democratization | Strong |

**Key Tension:**
**Tension:** Phase 2A round discussion emphasizes decentralized storage (IPFS + blockchain) for resilience, but Archon KB search results (though limited in specificity) suggest infrastructure projects often fail due to maintenance burden and complexity, not centralization. Semantic Scholar succeeded with centralized architecture (AWS-hosted), contradicting decentralization necessity.

**Resolution:** This verification plan tests whether decentralization is ESSENTIAL or OPTIONAL for sustainability. Phase 2B will include:
- **Sub-Hypothesis 2.1:** Centralized alternative (AWS S3 + CloudFront) achieves same adoption as decentralized (IPFS) at lower cost
- **Experiment:** A/B test with pilot users on centralized vs decentralized versions, measuring adoption, performance, and perceived reliability
- **Outcome:** If centralized version achieves ≥90% of decentralized adoption with <50% cost, decentralization is optional (simplify to centralized); otherwise, decentralization is validated as necessary for community trust.

### 1.4 Key Assumptions

1. **RL community will contribute artifacts when incentivized via academic credit**
   - **Evidence:** Conference reproducibility badges increase artifact sharing (ACM, NeurIPS programs). GitHub stars and citations drive open-source contributions in ML community.
   - **Consequence if violated:** Platform remains empty (<50 artifacts), failing to reach critical mass for discovery. Mitigation: Seed with 100+ artifacts from official papers (D4RL, reincarnating_rl, Stable-Baselines3 zoo).

2. **Quality certification is valuable and influences artifact selection decisions**
   - **Evidence:** Semantic Scholar quality signals (citations, venue) drive paper discovery. Users preferentially download higher-rated items on platforms (App Store ratings, GitHub stars).
   - **Consequence if violated:** Uncertified artifacts downloaded equally, wasting certification effort. Mitigation: User survey in pilot phase to validate badge influence on download decisions.

3. **Consortium model with 5-10 institutions can sustain infrastructure costs**
   - **Evidence:** Precedent: Linux Foundation (1000+ members), OpenAI (multi-company consortium initially), Apache Foundation (distributed governance).
   - **Consequence if violated:** Platform shuts down after 2-3 years due to funding loss. Mitigation: Initial consortium commitment contracts for 3-year minimum, with annual renewal negotiations.

4. **IPFS storage costs are manageable for RL artifact sizes**
   - **Evidence:** IPFS free for <1TB (sufficient for 100-200 policy artifacts at ~1-5GB each). Arweave permanent storage costs ~$5/GB one-time.
   - **Consequence if violated:** Storage costs exceed consortium budget ($25-50K/year), forcing reduction in artifact count or quality. Mitigation: Cost monitoring + fallback to centralized S3 ($0.023/GB/month) if IPFS costs exceed projections.

5. **Standardized formats (ONNX, Parquet) enable cross-framework compatibility without significant conversion overhead**
   - **Evidence:** ONNX supports 95%+ of common DL operations (conv, LSTM, attention). Parquet is Apache Arrow standard with libraries in all major languages.
   - **Consequence if violated:** <70% of artifacts convert successfully, limiting cross-framework reuse. Mitigation: Technical validation in prototype phase with 20+ diverse artifacts (different algorithms, environments, frameworks).

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- RL domains with reproducible environments (Atari, MuJoCo, Gym-based tasks, Meta-World, RoboSuite)
- Discrete and continuous control tasks
- Policy-based, value-based, and model-based RL algorithms
- Offline RL datasets (D4RL-compatible)
- Research and educational use cases (academic institutions, industry R&D, individual learners)

**Where It Does NOT Apply:**
- Real-world robotics with hardware-specific policies (sim-to-real gap makes artifact reuse difficult)
- Proprietary RL applications where sharing is restricted by IP/NDAs
- Multi-agent RL with complex opponent modeling (environment non-stationarity complicates artifact transferability)
- LLM-based RL (e.g., RLHF) where artifacts are multi-TB models exceeding practical sharing limits
- Non-reproducible environments (e.g., live trading systems, online ad bidding with shifting distributions)

**Known Limitations:**
- **Environment Versioning Dependency Hell:** MuJoCo v2 vs v3 vs v4 incompatibilities require meticulous metadata. Mitigation: Docker images for reproducibility.
- **Artifact Size Challenges:** Datasets can exceed 100GB (D4RL locomotion datasets). Requires compression + CDN for practical downloads.
- **Framework Version Fragmentation:** PyTorch 1.x vs 2.x, JAX updates break backward compatibility. Requires versioned artifact metadata.
- **Quality Certification Scalability:** Silver/Gold badges require human verification, limiting scale to ~100-500 certified artifacts/year. Mitigation: Automated Bronze, crowd-sourced Silver, expert-panel Gold.

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Research Accessibility - Absolute Target)**:
RLHub will achieve research accessibility democratization measured by:
- **Metric 1:** Unique researchers downloading artifacts ≥ 200 within 12 months post-launch
- **Metric 2:** Institutions represented ≥ 50 (at least 30% from non-top-20 universities or individuals)
- **Metric 3:** Geographic diversity ≥ 15 countries

*Measurement*:
- User registration data (anonymized) tracking institution affiliation, location
- Download logs (privacy-preserving: hash user IDs, aggregate statistics)
- Survey of 50+ users at 6-month and 12-month milestones

*Basis*:
Hugging Face achieved ~10K users within first 2 years (2018-2020) for NLP models. RL community is ~10x smaller (NeurIPS RL papers: ~200/year vs NLP: ~2000/year), so proportional target is 1K users long-term, with 200 as 12-month milestone (20% penetration of active RL researchers).

*Success Criteria for Phase 2B*:
- Primary: ≥200 unique researchers AND ≥50 institutions AND ≥15 countries (ALL must be met)
- Falsification: <100 unique researchers OR <25 institutions OR <8 countries after 12 months triggers hypothesis rejection

**Secondary Predictions:**

**P2 (Cost Efficiency - Compute Savings)**:
RLHub will demonstrate measurable cost efficiency:
- **Metric:** Estimated compute hours saved ≥ 100K GPU-hours within 12 months (calculated as: Σ[artifact_training_cost × download_count] for all artifacts)
- **Survey Metric:** ≥60% of surveyed users report cost savings as primary benefit

*Measurement*:
- Metadata includes original training cost (GPU-hours)
- Download logs enable calculation: savings = training_cost × (downloads - 1)
- User survey (n ≥ 100) with question: "Primary benefit of RLHub: (a) Cost savings, (b) Time savings, (c) Reproducibility, (d) Exploration"

*Success Criteria*:
- 100K GPU-hours saved (conservative: assumes 200 artifacts, avg 1000 GPU-hours training cost, avg 5 downloads each = 200 × 1000 × 4 = 800K GPU-hours saved; threshold set at 12.5% of theoretical max)
- ≥60% survey respondents cite cost as top-3 benefit

**P3 (Community Contributions - Network Effect)**:
RLHub will achieve critical mass through community contributions:
- **Metric:** ≥200 artifacts uploaded, ≥100 unique contributors, ≥5K total downloads within 12 months

*Measurement*:
- Artifact upload logs, contributor profiles
- Download analytics (total and per-artifact)

*Success Criteria*:
- 200+ artifacts (beyond seed content of 100): indicates 2x growth via community
- 100+ contributors: indicates distributed contributions, not single-lab uploads
- 5K+ downloads: indicates artifact reuse (avg 25 downloads/artifact)

**Falsification Criteria:**

The hypothesis will be **REJECTED** if ANY of the following occur within 12 months post-launch:

1. **Primary Accessibility Failure**: <100 unique researchers OR <25 institutions OR <8 countries
   (Indicates infrastructure failed to democratize access beyond current ad hoc sharing)

2. **Cost Efficiency Failure**: Estimated compute savings <50K GPU-hours AND <40% survey respondents cite cost savings
   (Indicates platform doesn't deliver on core value proposition of reducing computational burden)

3. **Community Engagement Failure**: <150 total artifacts (seed 100 + only 50 new community contributions)
   (Indicates community won't contribute despite infrastructure and incentives, violating Assumption 1)

4. **Consortium Collapse**: <3 institutions remaining in consortium after 12 months
   (Indicates sustainability model failed, platform at risk of shutdown per Assumption 3)

5. **Quality Certification Irrelevance**: No statistically significant difference in download rates between certified vs uncertified artifacts (p > 0.05, controlling for performance metrics)
   (Indicates badges don't influence trust, violating Assumption 2)

### 1.7 SOTA Baseline (Not Applicable - Infrastructure Project)

**Mode:** Absolute Performance Validation (Not SOTA Comparison)

**Rationale:** RLHub is an infrastructure project, not an algorithmic method. There is no comparable "SOTA" baseline for RL artifact sharing platforms. Comparisons are against:
- **Status Quo:** Ad hoc GitHub sharing (no discoverability, no quality control, no standardization)
- **Partial Solutions:** D4RL (datasets only), Stable-Baselines3 Zoo (policies only, no community, no badges)

Success is measured by absolute metrics (200+ researchers, 100K+ GPU-hours saved, 200+ artifacts) rather than relative improvement over a baseline method.

### 1.8 Statistical Verification Design

**Study Design:** Longitudinal Platform Analytics + User Surveys

**Measurement Protocol:**

1. **Platform Analytics (Continuous Tracking)**
   - **Metrics:** User registrations, artifact uploads/downloads, contributor count, institution/country diversity
   - **Sampling:** Census (all platform activity logged)
   - **Privacy:** Anonymized user IDs (hashed), aggregate statistics only
   - **Frequency:** Daily logs, monthly aggregated reports

2. **User Surveys (Milestone-Based)**
   - **Timepoints:** 6-month and 12-month post-launch
   - **Sample Size:** n ≥ 100 users per survey (target 50% response rate from active users)
   - **Questions:**
     - Likert scale (1-5): "RLHub reduced my computational costs"
     - Multiple choice: "Primary benefit: (a) Cost, (b) Time, (c) Reproducibility, (d) Exploration"
     - Open-ended: "Barriers to using RLHub artifacts"
   - **Analysis:** Descriptive statistics (means, percentages), qualitative coding for open-ended responses

3. **Compute Savings Estimation**
   - **Formula:** Total savings = Σ[artifact_training_cost_GPU_hours × (download_count - 1)]
   - **Metadata Required:** Each artifact includes original training cost in metadata (e.g., "Training: 500 GPU-hours on V100")
   - **Conservative Assumptions:** Only count downloads that result in actual artifact use (exclude browsing); apply 0.7 multiplier to account for non-usage downloads

4. **Statistical Tests**
   - **Accessibility (Primary):** Descriptive statistics with 95% confidence intervals for user count, institution count, country count
   - **Cost Efficiency:** One-sample t-test (null hypothesis: mean compute savings = 0; alternative: savings > 0, p < 0.05)
   - **Quality Certification Influence:** Independent t-test comparing download rates of certified vs uncertified artifacts (controlling for performance metrics via ANCOVA)

**Power Analysis:**
- **Effect Size:** Not applicable for absolute thresholds (200 researchers, 100K GPU-hours are fixed targets, not relative improvements)
- **Precision:** With n ≥ 100 survey respondents, margin of error ≈ ±10% at 95% confidence for proportion estimates (e.g., % citing cost savings)

**Reporting Standards:**
- Monthly progress reports to consortium steering committee
- 12-month comprehensive evaluation report with:
  - All primary/secondary/falsification metrics
  - User survey results (quantitative + qualitative themes)
  - Lessons learned and refinement recommendations for Year 2

---

## 2. Contribution Summary

**Theoretical Contributions:**
1. **Framework for Community-Driven Quality Certification in Scientific Computing**
   - Formalizes Bronze/Silver/Gold tier system for RL artifact quality validation
   - Provides replicable model for other domains (robotics datasets, simulation environments, neural architectures)
   - Theoretical analysis of incentive alignment via academic credit (reproducibility badges) to overcome tragedy of the commons in artifact sharing

2. **Standardization Schema for RL Artifacts**
   - Defines necessary and sufficient metadata for RL artifact discoverability (algorithm, environment+version, performance, compute cost, license)
   - JSON-LD semantic web compatibility enables cross-platform integration (Papers with Code, OpenML, future platforms)

**Methodological Contributions:**
1. **Packaging Formats for RL Artifacts**
   - ONNX specification for policies (cross-framework compatibility: PyTorch, JAX, TensorFlow)
   - Parquet schema for trajectory datasets (efficient compression, columnar access, framework-agnostic)
   - PyTorch checkpoint standard for value functions (with architecture metadata)

2. **Quality Certification Protocol**
   - **Bronze:** Automated reproducibility testing via CI/CD (performance within 5% of claimed metrics)
   - **Silver:** Crowd-sourced verification (≥3 independent reproductions, community voting)
   - **Gold:** Expert panel benchmark testing (on CORA, Continual World, or domain-specific benchmarks)

3. **Decentralized Storage Architecture**
   - IPFS integration for artifact storage (content-addressed, distributed, censorship-resistant)
   - Optional Arweave blockchain layer for metadata permanence (~$5/GB one-time cost)
   - Hybrid model: metadata in PostgreSQL (fast queries), artifacts in IPFS (resilience)

**Practical Contributions:**
1. **Open-Source Platform: RLHub**
   - **Frontend:** React + TypeScript (semantic search, filter by algorithm/domain/performance, quality badge display)
   - **Backend:** FastAPI + PostgreSQL (metadata DB, user management, analytics)
   - **Storage:** IPFS client (go-ipfs) + Arweave SDK (optional blockchain)
   - **Codebase:** MIT licensed on GitHub (enables community forks, extensions)

2. **Seed Content Curation (100+ High-Quality Artifacts)**
   - Official paper artifacts: reincarnating_rl (Agarwal et al.), selective-reincarnation-marl (InstaDeep)
   - D4RL datasets: 30+ offline RL datasets (locomotion, manipulation, navigation)
   - Stable-Baselines3 RL Zoo: 70+ pretrained policies (Atari, MuJoCo, PyBullet)
   - Total: 100-150 seed artifacts ensuring critical mass at launch

3. **Consortium Governance Model**
   - Multi-institution sustainability: 5-10 institutions (Google Research, DeepMind, OpenAI, Stanford, MIT, Berkeley, CMU, MILA)
   - Cost sharing: $5-10K/year per institution (total: $25-100K/year for hosting + 0.5 FTE maintenance)
   - Governance: Rotating steering committee (2-year terms), technical advisory board (community-elected)

4. **Conference Partnership Template**
   - NeurIPS/ICLR/ICML reproducibility badge integration
   - Acceptance criteria: Artifacts uploaded to RLHub with Bronze certification
   - Badge visibility: Appears on paper in proceedings website (increases citations by 20-40% based on ACM data)
   - Mutual benefit: Conferences improve reproducibility, RLHub gains legitimacy and user acquisition

5. **Impact Measurement Framework**
   - User studies: Pre-launch survey (barriers, desired features), pilot study (alpha with 10-15 users), beta launch (50-100 artifacts, broader community)
   - Impact metrics: (1) Cost savings estimation (GPU-hours saved), (2) Accessibility increase (institutions without large compute), (3) Citation impact (papers using RLHub artifacts)

---

## 3. Key Related Work

**Direct Comparisons (Baselines):**

1. **Status Quo: Ad Hoc GitHub Sharing**
   - **What it is:** Researchers manually upload policies/datasets to personal GitHub repositories
   - **Limitations:** No discoverability (must know author or paper), no quality control (untested code common), no standardization (every repo has different format), no version control (breaking changes without notice)
   - **RLHub Advantage:** Centralized discovery, quality badges, standardized formats, version tracking

2. **D4RL (Datasets for Deep Data-Driven RL)** - Fu et al., 2020
   - **What it is:** Offline RL benchmark suite with 30+ trajectory datasets
   - **Limitations:** Datasets ONLY (no policies, value functions, representations), no quality certification, no discovery interface beyond README, no community contributions (static benchmark)
   - **RLHub Advantage:** Policies + datasets + value functions, quality badges, discovery interface, community-driven growth

3. **RL Baselines Zoo (Stable-Baselines3)** - Raffin & Freitas, 2021
   - **What it is:** Collection of 70+ pretrained RL policies for common benchmarks
   - **Limitations:** Policies ONLY (no datasets), limited to Stable-Baselines3 library (framework lock-in), no community contributions (curated by maintainers), no quality badges
   - **RLHub Advantage:** Multi-artifact types, cross-framework (ONNX), community contributions open, quality certification

4. **Papers with Code (PwC)** - Meta AI
   - **What it is:** Platform linking academic papers to their code repositories
   - **Limitations:** Links to code (not artifacts), no standardized format (every repo different), no artifact-specific metadata (training cost, environment version), no quality certification for artifacts
   - **RLHub Advantage:** Standardized artifact format, rich RL-specific metadata, quality badges, artifact-first (not paper-first) discovery

**Adjacent Infrastructure (Cross-Domain Inspirations):**

5. **Hugging Face Model Hub** - NLP/CV
   - **Relationship:** Direct cross-domain model adapted for RL
   - **What RLHub Adopts:** Model card paradigm → Artifact cards, one-click downloads, quality signals (downloads, likes), community contributions, multi-framework support
   - **What RLHub Adapts:** RL-specific metadata (environment versioning, algorithm type), quality certification tailored to RL validation (Bronze/Silver/Gold instead of just download counts), IPFS decentralization (Hugging Face is centralized)

6. **Semantic Scholar** - Literature Discovery (Ammar et al., 2018, 425 cit)
   - **Relationship:** Evidence for quality signals driving discovery
   - **Key Insight:** Literature graph uses citation count, venue tier, author h-index to rank papers. RLHub uses quality badges, performance metrics, download counts analogously.
   - **Lesson:** Multi-dimensional quality signals (not single metric) enable effective discovery

7. **TensorFlow Hub / PyTorch Hub** - Framework-Specific Model Sharing
   - **Relationship:** Framework-locked predecessors
   - **Limitations:** TF Hub only for TensorFlow models, PyTorch Hub only for PyTorch. No cross-framework support.
   - **RLHub Advantage:** ONNX enables PyTorch → JAX → TensorFlow cross-loading, removing framework barriers

**Differentiation Strategy:**

| Feature | Status Quo (GitHub) | D4RL | SB3 Zoo | Papers with Code | Hugging Face | **RLHub** |
|---------|-------------------|------|---------|-----------------|--------------|-----------|
| **Artifact Types** | Mixed (code) | Datasets | Policies | Code links | Models | **Policies + Datasets + Value Fns** |
| **Quality Certification** | None | Benchmark-tested | Curated | None | Community (downloads) | **Bronze/Silver/Gold badges** |
| **Discovery Interface** | Search GitHub | README | README | Paper search | Model search | **RL-specific (algorithm, env, perf)** |
| **Cross-Framework** | Manual | N/A | Locked to SB3 | Manual | PyTorch/TF/JAX | **ONNX (universal)** |
| **Community Contributions** | Open (chaos) | Static (closed) | Curated (closed) | Links only | Open | **Open with certification** |
| **Version Control** | Git | Static | Git tags | None | Git + model cards | **Environment versioning + Git** |
| **Decentralization** | Distributed (GitHub) | Centralized | Centralized | Centralized | Centralized | **IPFS + optional blockchain** |
| **Academic Credit** | Citations | Citations | Citations | Citations | Downloads/likes | **Reproducibility badges** |

**Key Differentiator:** RLHub is the ONLY platform combining (1) multi-artifact types, (2) cross-framework compatibility, (3) quality certification, (4) RL-specific discovery, (5) decentralized resilience, (6) academic credit integration. Each existing solution solves 1-2 dimensions; RLHub addresses all 6.

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence - Infrastructure Viability):**
**Sub-Hypothesis:** A comprehensive RL artifact sharing platform (RLHub) with 5 core features (packaging, certification, storage, discovery, version control) can be built and sustained via consortium model.

**Verification Experiments:**
- **SH1.1 (Technical Feasibility):** Prototype development (6 months, 2 engineers). Success: All 5 features functional, handles 100+ artifacts, <5% conversion failures.
- **SH1.2 (Consortium Formation):** Outreach to 10 target institutions. Success: ≥5 institutions commit $5-10K/year for 3 years.
- **SH1.3 (Cost Validation):** Pilot deployment (50 artifacts, 20 users, 3 months). Success: Hosting costs <$500/month, IPFS storage feasible.

**SH2 (Mechanism - Causal Links):**
**Sub-Hypothesis:** The 5-step causal chain (Standardization → Compatibility → Reuse → Contributions → Democratization) operates as proposed.

**Verification Experiments:**
- **SH2.1 (Link 1: Standardization → Compatibility):** Convert 20 diverse artifacts to ONNX/Parquet, test cross-framework loading. Success: ≥90% load successfully.
- **SH2.2 (Link 3: Badges → Trust):** A/B test: Show half of users certified artifacts, half uncertified. Success: Certified artifacts have ≥30% higher download rate (p < 0.05).
- **SH2.3 (Link 4: Incentives → Contributions):** Survey 50 potential contributors on willingness to share if badges offered. Success: ≥60% report increased willingness.
- **SH2.4 (Link 5: Library → Democratization):** Track user demographics in pilot. Success: ≥40% of users from non-top-20 institutions or individuals.

**SH3 (Comparison - Centralized vs Decentralized):**
**Sub-Hypothesis:** Decentralized storage (IPFS) provides sufficient advantages over centralized (AWS S3) to justify added complexity.

**Verification Experiment:**
- **SH3.1:** A/B test with pilot users (n=30): 15 use IPFS version, 15 use S3 version. Measure: (1) Download speed, (2) Reliability (uptime), (3) Perceived trust (survey), (4) Cost.
- **Success Criteria:** IPFS version achieves ≥90% of S3 performance AND ≥20% higher trust rating, justifying decentralization.
- **Alternative Outcome:** If S3 version ≥90% as trusted at <50% cost, simplify to centralized architecture.

### Readiness Checklist

- [x] **Core Statement:** Hypothesis structured in "If-Then-Because" format with operationalized variables
- [x] **Causal Mechanism:** 5-step chain decomposed with evidence for each link
- [x] **Testable Predictions:** Primary (accessibility: 200+ researchers, 50+ institutions, 15+ countries) and secondary (cost: 100K GPU-hours, community: 200 artifacts) with quantitative thresholds
- [x] **Falsification Criteria:** Clear rejection conditions (<100 researchers, <50K GPU-hours saved, <150 artifacts)
- [x] **Assumptions:** 5 core assumptions identified with evidence and violation consequences
- [x] **Key Tensions:** Decentralization vs centralization trade-off acknowledged, resolution experiment designed (SH3.1)
- [x] **Scope & Boundaries:** Explicitly defined where hypothesis applies (reproducible RL environments) and does NOT apply (real-world robotics, proprietary IP, multi-TB LLM artifacts)
- [x] **Sub-Hypotheses:** SH1 (Existence), SH2 (Mechanism), SH3 (Comparison) outlined with verification experiments
- [x] **Related Work:** Comprehensive differentiation from 4 direct baselines + 3 cross-domain inspirations
- [x] **Contributions:** Theoretical (quality certification framework), Methodological (packaging formats, certification protocol), Practical (open-source platform, consortium model, conference partnerships)

**READY FOR PHASE 2B:** ✅ All checklist items completed. Hypothesis is scientifically structured, falsifiable, and decomposable into verifiable sub-hypotheses.

### Open Questions

1. **Decentralization Necessity:** Is IPFS decentralization essential for community trust, or is centralized S3 sufficient?
   - **Resolution Path:** SH3.1 experiment (A/B test centralized vs decentralized with pilot users)
   - **Impact:** Determines architecture complexity and cost (IPFS adds ~20% dev time, similar hosting cost)

2. **Quality Certification Scalability:** Can crowd-sourced Silver/Gold badges scale to 500+ artifacts/year without overwhelming volunteers?
   - **Resolution Path:** Pilot with 50 artifacts, measure volunteer hours per badge, project to 500-artifact scale
   - **Impact:** May require paid expert panels for Gold badges (~$50-100 per artifact) if volunteer model doesn't scale

3. **Framework Conversion Coverage:** What percentage of RL algorithms can be successfully exported to ONNX?
   - **Resolution Path:** SH2.1 experiment (convert 20 diverse artifacts covering policy-based, value-based, model-based, on-policy, off-policy)
   - **Impact:** If <80% convert successfully, may need framework-specific storage alongside ONNX (reduces cross-framework benefit)

4. **Artifact Size Limits:** At what artifact size (GB) do download speeds become prohibitive for user adoption?
   - **Resolution Path:** Pilot study with 5-100GB artifacts, measure download completion rates and user satisfaction
   - **Impact:** May require artifact compression standards or CDN integration if >20GB artifacts have <50% completion rate

5. **Conference Partnership Feasibility:** Will NeurIPS/ICLR/ICML agree to reproducibility badge integration?
   - **Resolution Path:** Formal pitch to program chairs (2025-2026), citing ACM precedent and mutual benefits (improved reproducibility)
   - **Impact:** If partnerships fail, need alternative incentive (e.g., direct citation boost metric on RLHub, integration with Google Scholar)

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-06*
