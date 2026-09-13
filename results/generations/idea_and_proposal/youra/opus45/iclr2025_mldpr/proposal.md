# Research Proposal: Versioned Living Benchmarks: Automated Saturation Detection for Sustainable ML Evaluation

## 1. Introduction

### 1.1 Background

Machine learning (ML) benchmarks serve as the cornerstone of scientific progress in the field, enabling standardized evaluation and comparison of models across research groups worldwide. However, the ML benchmarking ecosystem faces a critical sustainability crisis. As documented by Koch et al. (2021), benchmark concentration has increased dramatically, with a small number of datasets dominating evaluation practices despite growing awareness of their limitations. This concentration creates a troubling dynamic: models increasingly overfit to static datasets, performance variance compresses as state-of-the-art approaches converge, and benchmarks progressively lose their discriminative power to distinguish genuinely superior methods from those that have merely learned dataset-specific artifacts.

The phenomenon of benchmark saturation manifests when top-performing models achieve near-identical scores, rendering further progress on the benchmark meaningless as a signal of genuine capability improvement. Bouthillier et al. (2021) demonstrated that performance variance from data sampling, initialization, and hyperparameters is measurable and meaningful, yet current benchmarking practices fail to leverage this insight for detecting staleness. Meanwhile, Madaan et al. (2024) validated metrics for seed variance and monotonicity that could inform saturation detection, but no systematic framework exists to operationalize these findings.

Current solutions to benchmark staleness require unsustainable manual curation effort. Creating new benchmarks demands significant expert time for data collection, annotation, and validation. The TabArena project (2025) demonstrates that living benchmarks with continuous maintenance protocols can preserve utility, but the resource requirements limit scalability. Major ML repositories—OpenML, HuggingFace Datasets, and the UCI ML Repository—face practical challenges in implementing and enforcing best practices for benchmark evolution while maintaining the reproducibility that scientific progress demands.

### 1.2 Research Objectives

This research proposes Versioned Living Benchmarks (VLB), a framework that addresses the fundamental tension between benchmark evolution and reproducibility through automated saturation detection and principled epoch transitions. Our primary objectives are:

1. **Develop and validate automated saturation detection mechanisms** based on continuous monitoring of top-k model performance variance, establishing reliable triggers for benchmark evolution.

2. **Design and implement epoch versioning protocols** that introduce fresh data when saturation is detected while preserving cross-temporal comparability through semantic versioning and dual scoring.

3. **Demonstrate framework viability** on tabular classification benchmarks, validating that epoch transitions restore benchmark discriminative power while maintaining meaningful historical model comparisons.

4. **Establish replicable infrastructure** suitable for adoption by major ML repositories, reducing the manual overhead currently required for sustainable benchmark maintenance.

### 1.3 Research Significance

This research addresses a critical gap in the ML data ecosystem identified by the workshop's core themes. By automating saturation detection and providing principled evolution mechanisms, VLB offers several significant contributions:

**Scientific Impact:** VLB enables benchmarks to remain discriminative over time, ensuring that reported performance improvements reflect genuine capability advances rather than dataset-specific overfitting. This directly addresses the overuse and overfitting problems highlighted in current ML data practices.

**Practical Impact:** By reducing manual curation overhead, VLB makes living benchmarks sustainable for repository administrators. The framework provides concrete infrastructure that OpenML, HuggingFace, and similar platforms can adopt to implement best practices for benchmark maintenance.

**Methodological Impact:** The dual scoring protocol establishes a new paradigm for holistic and contextualized benchmarking, enabling both current-epoch evaluation and historical consistency assessment. This addresses the workshop's concern about overemphasis on single metrics.

**Reproducibility Impact:** Semantic versioning preserves the ability to reproduce historical results while allowing benchmarks to evolve, resolving the apparent tension between reproducibility and relevance that currently paralyzes benchmark development.

## 2. Methodology

### 2.1 Framework Overview

The Versioned Living Benchmarks framework consists of three integrated components: (1) a variance monitoring system for saturation detection, (2) an epoch transition mechanism for benchmark evolution, and (3) a dual scoring protocol for cross-temporal comparability. We detail each component below.

### 2.2 Variance-Based Saturation Detection

#### 2.2.1 Performance Variance Monitoring

Let $\mathcal{M}_t = \{m_1, m_2, \ldots, m_n\}$ denote the set of models submitted to a benchmark at time $t$, and let $s_i$ represent the performance score of model $m_i$ on the benchmark's primary metric. We define the top-k performance set as:

$$S_k(t) = \{s_i : m_i \in \text{top-}k(\mathcal{M}_t)\}$$

The performance variance at time $t$ is computed as:

$$\sigma^2(t) = \frac{1}{k-1} \sum_{s_i \in S_k(t)} (s_i - \bar{s})^2$$

where $\bar{s}$ is the mean performance of the top-k models.

#### 2.2.2 Baseline Variance Establishment

For each benchmark epoch $E_n$, we establish a baseline variance $\sigma^2_{\text{base}}$ computed from the first $T_{\text{init}}$ days of submissions after epoch initialization:

$$\sigma^2_{\text{base}}(E_n) = \frac{1}{T_{\text{init}}} \sum_{t=1}^{T_{\text{init}}} \sigma^2(t)$$

We set $T_{\text{init}} = 30$ days and $k = 10$ models based on typical benchmark submission patterns.

#### 2.2.3 Saturation Detection Criterion

The variance compression ratio at time $t$ is defined as:

$$\rho(t) = \frac{\sigma^2(t)}{\sigma^2_{\text{base}}}$$

Saturation is detected when the compression ratio falls below threshold $\tau$ for a sustained period $T_{\text{confirm}}$:

$$\text{Saturated}(t) = \mathbb{1}\left[\forall t' \in [t - T_{\text{confirm}}, t]: \rho(t') < \tau\right]$$

We set $\tau = 0.5$ and $T_{\text{confirm}} = 14$ days to avoid false positives from temporary variance fluctuations.

### 2.3 Epoch Transition Mechanism

#### 2.3.1 Semantic Versioning Protocol

Benchmark versions follow semantic versioning: $v_{\text{major}}.\text{minor}.\text{patch}$

- **Major version** ($v_{n}.0.0$): New epoch with fresh data, triggered by saturation detection
- **Minor version** ($v_{n}.m.0$): Data quality corrections without distribution shift
- **Patch version** ($v_{n}.m.p$): Documentation or metadata updates only

#### 2.3.2 Fresh Data Integration

Upon saturation detection, the epoch transition proceeds as follows:

1. **Data Sourcing:** Draw fresh samples from the continuous data pipeline, ensuring distribution alignment with the benchmark's target domain.

2. **Quality Validation:** Apply automated quality checks including:
   - Feature completeness: $\geq 95\%$ non-missing values
   - Label quality: Inter-annotator agreement $\kappa \geq 0.8$ (for labeled data)
   - Distribution alignment: Maximum mean discrepancy (MMD) with previous epoch $< \epsilon_{\text{MMD}}$

3. **Epoch Initialization:** Create new epoch $E_{n+1}$ with version $v_{n+1}.0.0$, resetting the baseline variance calculation.

The distribution alignment constraint ensures semantic continuity:

$$\text{MMD}^2(\mathcal{D}_{E_n}, \mathcal{D}_{E_{n+1}}) = \left\| \frac{1}{|\mathcal{D}_{E_n}|} \sum_{x \in \mathcal{D}_{E_n}} \phi(x) - \frac{1}{|\mathcal{D}_{E_{n+1}}|} \sum_{x' \in \mathcal{D}_{E_{n+1}}} \phi(x') \right\|^2_{\mathcal{H}}$$

where $\phi$ is a kernel feature map and $\epsilon_{\text{MMD}} = 0.1$.

### 2.4 Dual Scoring Protocol

#### 2.4.1 Current Epoch Score

The current epoch score $S_{\text{current}}(m, E_n)$ evaluates model $m$ on the active epoch's test set using standard metrics (accuracy, F1, AUC-ROC depending on task).

#### 2.4.2 Historical Consistency Score

The historical consistency score measures rank stability across epochs:

$$S_{\text{hist}}(m) = \frac{1}{|E_{\text{prev}}|} \sum_{E_j \in E_{\text{prev}}} \text{RankCorr}(r_m(E_j), r_m(E_n))$$

where $r_m(E_j)$ is the rank of model $m$ in epoch $E_j$, and $E_{\text{prev}}$ is the set of previous epochs where $m$ was evaluated.

#### 2.4.3 Composite Score

The final dual score combines both components:

$$S_{\text{dual}}(m) = \alpha \cdot S_{\text{current}}(m, E_n) + (1 - \alpha) \cdot S_{\text{hist}}(m)$$

We set $\alpha = 0.7$ to prioritize current performance while rewarding consistency.

### 2.5 Experimental Design

#### 2.5.1 Data Collection

**Primary Dataset:** We will utilize the TabArena benchmark infrastructure, which provides continuous data ingestion for tabular classification tasks. We will collect:
- Historical submission records (model predictions, timestamps, performance scores)
- Dataset metadata and version history
- At least 4 epochs of data spanning 12-18 months

**Simulated Saturation:** To ensure sufficient saturation events for analysis, we will supplement real data with controlled simulations where we artificially compress performance variance by sampling from converged model distributions.

#### 2.5.2 Experimental Conditions

**Condition 1 (Control):** Static benchmark with no epoch transitions, representing current practice.

**Condition 2 (Manual Transition):** Epoch transitions triggered by expert judgment, representing the TabArena approach.

**Condition 3 (VLB Automated):** Epoch transitions triggered by automated saturation detection using the proposed variance monitoring system.

#### 2.5.3 Evaluation Metrics

**Primary Metric - Variance Restoration:**
$$\Delta\sigma^2 = \frac{\sigma^2_{\text{post-transition}} - \sigma^2_{\text{pre-transition}}}{\sigma^2_{\text{baseline}}}$$

Success criterion: $\Delta\sigma^2 > 0$ with $\sigma^2_{\text{post-transition}} > 0.5 \times \sigma^2_{\text{baseline}}$, $p < 0.05$ (paired t-test).

**Secondary Metric - Cross-Temporal Rank Correlation:**
$$r_s = \text{Spearman}(R_{E_n}, R_{E_{n+1}})$$

Success criterion: $r_s > 0.7$ for adjacent epochs, $r_s > 0.5$ for epochs separated by 2-3 transitions.

**Tertiary Metric - Detection Accuracy:**
Comparison of automated saturation detection against expert-labeled saturation events:
- Precision: Proportion of triggered transitions that experts agree were necessary
- Recall: Proportion of expert-identified saturation events that were automatically detected

#### 2.5.4 Statistical Analysis Plan

**Sample Size:** Minimum 4 epochs with 50+ unique model submissions per epoch, providing 80% power to detect medium effect sizes (Cohen's $d = 0.6$).

**Primary Analysis:** Paired t-test comparing pre-transition (saturated) versus post-transition variance, with one-tailed test for directional hypothesis.

**Secondary Analysis:** Spearman correlation coefficients with 95% confidence intervals for cross-temporal rank validity.

**Sensitivity Analysis:** Vary saturation threshold $\tau \in \{0.3, 0.4, 0.5, 0.6, 0.7\}$ to determine optimal values and assess robustness.

#### 2.5.5 Falsification Criteria

The hypothesis will be rejected if:
1. Post-transition variance $\leq 0.3 \times$ baseline variance (epoch transitions fail to restore discriminative power)
2. Variance compression correlation with expert-judged saturation $r < 0.3$ (automated detection is invalid)
3. Cross-temporal rank correlation $r_s < 0.5$ for adjacent epochs (dual scoring fails to preserve comparability)

### 2.6 Implementation Architecture

The VLB system will be implemented as a modular Python framework with the following components:

1. **Variance Monitor:** Continuous tracking of submission performance with configurable $k$, $\tau$, and $T_{\text{confirm}}$ parameters.

2. **Transition Manager:** Orchestrates epoch transitions including data validation, version tagging, and baseline reset.

3. **Dual Scorer:** Computes and maintains both current and historical scores with configurable $\alpha$ weighting.

4. **Repository Adapter:** Standardized interfaces for integration with OpenML, HuggingFace, and similar platforms.

All code will be released under an open-source license with comprehensive documentation to facilitate adoption.

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Outcome 1 - Validated Saturation Detection:** We expect to demonstrate that performance variance compression reliably indicates benchmark saturation, with automated detection achieving $>80\%$ agreement with expert judgment. This validates the core mechanism enabling sustainable benchmark evolution.

**Outcome 2 - Restored Discriminative Power:** We anticipate that epoch transitions will restore performance variance to $>50\%$ of baseline levels, confirming that fresh data introduction breaks dataset-specific overfitting patterns. Statistical significance ($p < 0.05$) will establish the reliability of this effect.

**Outcome 3 - Preserved Comparability:** We expect cross-temporal rank correlations $>0.7$ for adjacent epochs, demonstrating that the dual scoring protocol maintains meaningful historical model comparisons despite benchmark evolution.

**Outcome 4 - Reduced Maintenance Overhead:** Compared to manual curation approaches, we anticipate VLB will reduce the expert time required for benchmark maintenance by $>50\%$ while achieving comparable or superior outcomes in terms of benchmark relevance.

### 3.2 Scientific Impact

This research contributes to the emerging science of ML evaluation by establishing principled, empirically-validated methods for benchmark lifecycle management. The variance-based saturation detection mechanism provides a quantitative foundation for decisions that currently rely on informal expert judgment. The dual scoring protocol advances holistic benchmarking practices by explicitly balancing current relevance against historical consistency.

### 3.3 Practical Impact

**For Repository Administrators:** VLB provides concrete infrastructure that major ML repositories can adopt to implement sustainable benchmark maintenance. The modular architecture and standardized interfaces minimize integration effort while the automated detection reduces ongoing operational burden.

**For ML Researchers:** Living benchmarks that maintain discriminative power ensure that reported improvements reflect genuine capability advances. The preserved cross-temporal comparability enables meaningful longitudinal analysis of research progress.

**For the ML Community:** By addressing the benchmark saturation problem systematically, VLB helps restore trust in benchmark-based evaluation and reduces the problematic concentration on a small number of static datasets.

### 3.4 Broader Impact

This research directly addresses several themes central to the workshop's mission:

- **Best practices for revising and deprecating datasets:** VLB provides principled criteria and mechanisms for benchmark evolution
- **Benchmark reproducibility:** Semantic versioning preserves historical reproducibility while enabling evolution
- **Overfitting and overuse of benchmark datasets:** Automated saturation detection directly targets this problem
- **Non-traditional/alternative benchmarking paradigms:** The living benchmark concept with dual scoring represents a paradigm shift from static evaluation

### 3.5 Limitations and Future Work

We acknowledge several limitations that define directions for future research:

1. **Domain Scope:** Initial validation focuses on tabular classification; extension to vision, NLP, and generative models requires additional investigation of domain-specific saturation signals.

2. **Threshold Sensitivity:** The 0.5× variance threshold is heuristic; future work should develop adaptive thresholds based on dataset characteristics.

3. **Infrastructure Requirements:** VLB requires continuous data pipelines, which may not be available for all benchmark domains.

4. **Community Adoption:** Technical solutions alone are insufficient; successful adoption requires alignment with community incentives and repository policies.

If successful, VLB provides foundational infrastructure for a new generation of sustainable, evolving benchmarks that remain relevant without sacrificing the reproducibility essential to scientific progress. We envision this work catalyzing broader adoption of living benchmark practices across the ML ecosystem.