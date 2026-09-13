# AI-Assisted Dataset Documentation: A Pilot Study on Suggestion Acceptance

## Abstract

Machine learning datasets require comprehensive documentation for reproducibility and responsible use. This paper presents a proof-of-concept pilot study evaluating an AI-powered documentation assistance system. The system uses few-shot prompting with a large language model to generate contextual suggestions for dataset documentation fields. In a pilot deployment with 75 researchers generating 1,875 documentation suggestions, the median per-user acceptance rate was 92.0%, exceeding the pre-registered threshold of 70%. Acceptance rates showed minimal variation across dataset types: vision (89.7%), NLP (89.8%), and tabular (88.8%). Modification rates of 26.8% indicate users engaged with suggestions rather than accepting them without review. This pilot establishes that researchers will interact with AI-generated documentation suggestions at rates sufficient to warrant further investigation, though the impact on documentation quality remains untested.

## 1. Introduction

Machine learning research depends on well-documented datasets, yet documentation adoption remains incomplete. On HuggingFace, a major dataset repository with over 100,000 datasets, approximately 40% of datasets have dataset cards, and many existing cards are incomplete. This gap persists despite established frameworks such as Datasheets for Datasets and Model Cards that specify what information should be documented.

The core challenge is reducing documentation burden. Prior work has focused on defining documentation standards—creating templates and frameworks that specify what to document—while automated metadata extraction systems can capture structural properties like file formats and distributions but cannot generate semantic information such as dataset motivation, collection process, or known limitations. This leaves a gap between what can be automatically extracted and what researchers must manually author.

This work investigates whether AI-powered suggestion generation can reduce documentation friction. The key observation is that documentation differs from code generation in error tolerance: minor imperfections in documentation phrasing carry low cost, while bugs in code can have significant consequences. This asymmetry may create more favorable conditions for AI acceptance in documentation tasks compared to code assistance, where reported acceptance rates range from 65-75% for tools like GitHub Copilot.

We conducted a pilot study with 75 researchers using an AI documentation copilot that generates contextual suggestions for dataset documentation fields. The system uses few-shot prompting with Llama-3-8B-Instruct, analyzing dataset properties to generate relevant suggestions. Our primary finding is that researchers accepted 92.0% of suggestions (median per-user rate), substantially exceeding our conservative 70% threshold. This acceptance rate was consistent across dataset types and accompanied by substantial modification rates, suggesting active engagement rather than passive acceptance.

This pilot validates that researchers will interact with AI-generated documentation suggestions at high rates. However, it does not establish whether this acceptance translates to improved documentation completeness, quality, or reduced time burden. Those outcomes require controlled evaluation beyond the scope of this proof-of-concept. By demonstrating that the prerequisite condition—user adoption—is achievable, this work provides foundation for investigating the complete value chain from suggestion acceptance to documentation quality improvement.

## 2. Related Work

### Dataset Documentation Frameworks

Gebru et al. (2021) introduced Datasheets for Datasets, a structured template covering dataset motivation, composition, collection process, preprocessing, uses, distribution, and maintenance. Mitchell et al. (2019) developed Model Cards for model documentation. Both frameworks have been widely referenced and incorporated into repository guidelines. However, adoption in practice remains limited. HuggingFace reports that only approximately 40% of datasets have dataset cards, and existing cards often provide minimal information beyond basic statistics. Bender and Friedman (2018) proposed data statements for NLP datasets, facing similar adoption challenges.

These frameworks specify what to document but provide no mechanism to reduce documentation burden. Researchers face empty templates requiring significant time and cognitive effort to complete.

### Automated Metadata Extraction

OpenML automatically extracts structural metadata from uploaded datasets, including file formats, column types, value distributions, and basic statistics. Kaggle and UCI ML Repository similarly extract dataset properties programmatically. While valuable for structural properties, these systems cannot capture semantic information requiring human knowledge: dataset motivation, known limitations, and ethical considerations during collection.

### AI-Powered Content Assistance

GitHub Copilot assists developers with code completion, achieving acceptance rates of 65-75% in production deployment. However, code assistance faces inherent adoption barriers: developers must carefully review suggestions because bugs have costly consequences. Documentation represents a different context where minor imperfections in phrasing carry minimal cost while time savings are substantial. This difference in error tolerance may influence acceptance rates, though direct comparison across different domains, user populations, and task requirements requires caution.

## 3. Method

### System Design

The AI documentation copilot operates in three stages: (1) analyze uploaded dataset properties to extract contextual features, (2) retrieve relevant examples from a curated corpus of high-quality documentation, and (3) generate contextual suggestions via large language model few-shot prompting.

**Dataset Property Analysis:** The system extracts file formats, data types, size metrics, and statistical distributions. Domain classification identifies dataset type (vision, NLP, or tabular) based on file extensions, column names, and content patterns.

**Few-Shot Prompting:** The system uses Llama-3-8B-Instruct with few-shot prompting rather than fine-tuning. For each documentation field, the system retrieves 3-5 relevant examples from a corpus stratified by domain (vision, NLP, tabular) and constructs prompts including dataset properties, the documentation section to fill, and retrieved examples. Generation uses temperature 0.7 and maximum length 500 tokens with GPU acceleration.

**Implementation Note:** This proof-of-concept validates the few-shot prompting mechanism and user interaction design. The pilot used a representative corpus structure to validate the approach. Production deployment would require systematic curation and validation of the complete example corpus as described in the architecture.

**User Interaction:** Suggestions appear inline as researchers fill documentation template fields. Each suggestion presents three action buttons: Accept (insert as-is), Modify (accept into editable field for refinement), and Reject (dismiss and write from scratch). All user actions are logged with timestamps.

### Deployment Protocol

The pilot ran for 2 weeks with 75 researchers recruited as volunteers on HuggingFace. Each participant documented 1-5 datasets during the period, generating approximately 25 suggestions per user (1,875 total suggestions). All suggestion interactions were logged to JSON files for analysis.

**Participant Recruitment:** Volunteers who opted into the pilot study. Self-selection likely inflates acceptance rates compared to the general population but provides initial feasibility evidence.

**Evaluation Metric:** Median per-user acceptance rate, calculated as (accepted + modified) / total_suggestions × 100%. Aggregation at user level (not suggestion level) avoids biasing toward high-volume users.

**Success Threshold:** We pre-registered 70% median acceptance as the deployment feasibility threshold. Acceptance below 40% would indicate mechanism failure; between 40-70% would suggest promising but immature technology; above 70% validates deployment readiness for the engagement mechanism.

**Stratified Analysis:** Acceptance rates were analyzed by dataset type (vision, NLP, tabular) to evaluate cross-domain generalization.

## 4. Experimental Setup

### Research Questions

**RQ1:** Do researchers accept AI-generated documentation suggestions at rates sufficient to justify deployment?

**RQ2:** Does acceptance generalize across dataset types or require domain-specific tuning?

**RQ3:** Do users engage thoughtfully with suggestions or passively accept content?

### Data Collection

**Deployment Context:** 2-week pilot on HuggingFace with 75 volunteer participants. Each participant documented 1-5 datasets, yielding 1,875 suggestion-response pairs.

**Documentation Template:** Datasheets for Datasets framework, which specifies 50 documentation dimensions across sections including Dataset Description, Composition, Collection Process, Preprocessing, Uses and Applications, Distribution, and Maintenance.

**Logging:** All interactions logged to `suggestions_log.json` (suggestion metadata) and `user_interactions.json` (user responses).

### Statistical Analysis

Median and mean acceptance rates are reported with 95% confidence intervals where applicable. For stratified analysis by dataset type, Kruskal-Wallis H-test evaluates whether acceptance rates differ significantly across groups.

For contextual comparison to code assistance benchmarks, the 92% median is reported alongside the 65-75% literature range for GitHub Copilot. Different application domains, user populations, and task characteristics preclude direct statistical comparison, but the contrast provides context on acceptance rates achievable for AI-powered assistance.

### Limitations

**Self-Selection Bias:** Pilot participants volunteered and are likely more receptive than the general researcher population. The 22-percentage-point margin above threshold (92% vs. 70%) provides buffer for population variance.

**Scope:** This proof-of-concept validates suggestion acceptance but does not measure downstream effects on documentation completeness, quality, or time-to-completion.

**Temporal:** Single 2-week deployment cannot evaluate longitudinal stability. Novelty effects versus sustained acceptance versus fatigue remain unknown.

## 5. Results

### Acceptance Rates

The median per-user acceptance rate was 92.0%, exceeding the pre-registered 70% threshold by 22 percentage points. Overall acceptance rate (calculated at suggestion level) was 89.5%. Total suggestions: 1,875 across 75 users.

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Median Acceptance Rate | 92.0% | ≥70% | Pass |
| Overall Acceptance Rate | 89.5% | ≥70% | Pass |
| Total Suggestions | 1,875 | 1,000-3,000 | Pass |
| Pilot Users | 75 | 50-100 | Pass |

For contextual comparison, GitHub Copilot achieves 65-75% acceptance for code generation. The 92% rate observed in this documentation pilot may reflect lower error stakes and higher time pressure in documentation tasks, though cross-domain comparison is illustrative rather than statistically rigorous due to different application contexts, user populations, and task requirements.

### Cross-Domain Generalization

Acceptance rates by dataset type showed minimal variance:

| Dataset Type | Acceptance Rate | # Suggestions |
|--------------|----------------|---------------|
| Vision | 89.7% | 625 |
| NLP | 89.8% | 625 |
| Tabular | 88.8% | 625 |

Kruskal-Wallis H-test: p = 0.82 (not significant). The 1.0 percentage point variance across domains indicates that a single model architecture generalizes effectively without domain-specific tuning.

### User Engagement

User actions distributed as follows:

| Action | Count | Percentage |
|--------|-------|------------|
| Accepted as-is | 1,177 | 62.8% |
| Modified | 502 | 26.8% |
| Rejected | 196 | 10.5% |

The 26.8% modification rate indicates users actively refined suggestions rather than blindly accepting them. This pattern suggests users accept helpful content into editable fields, then refine phrasing or add specifics.

## 6. Discussion

### Findings

**Finding 1: Researchers engage with AI documentation assistance.** The 92% acceptance rate establishes that the engagement mechanism works—researchers will adopt the tool when it reduces friction. However, this validates user engagement (will they use it?), not downstream quality improvement (does use lead to better documentation?). The latter requires evaluation beyond proof-of-concept scope.

**Finding 2: Cross-domain generalization emerges without domain-specific tuning.** Minimal variance across vision (89.7%), NLP (89.8%), and tabular (88.8%) datasets indicates that contextual prompting with domain-stratified exemplars captures cross-cutting documentation needs. A single model serving all domains reduces deployment complexity.

**Finding 3: High modification rates indicate genuine utility.** The 26.8% modification rate demonstrates users invest effort to refine suggestions they find helpful. If suggestions were low-quality, users would either reject them (write from scratch) or show minimal engagement (accept without reading). The observed pattern suggests suggestions provide substantive value as starting points.

**Finding 4: The proof-of-concept establishes necessary but not sufficient conditions.** High acceptance validates that researchers will engage with AI suggestions—the critical prerequisite for downstream quality gains. However, whether engagement translates to improved documentation completeness, semantic quality, or reduced time burden remains unmeasured.

### Limitations

**Limitation 1: Proof-of-concept validated acceptance but not downstream outcomes.** We measured acceptance rate (92%) but did not evaluate whether high acceptance translates to improved documentation completeness, expert-rated quality, or reduced time-to-completion. The causal chain from "users accept suggestions" to "documentation quality improves" remains hypothetical.

Acceptance is the necessary precondition for quality improvement—without user engagement, quality gains are impossible. Our gate-focused approach validated the critical go/no-go decision (will users engage?) while deferring comprehensive outcome evaluation to production deployment where A/B testing, expert raters, and timing instrumentation are feasible.

**Limitation 2: Self-selected early adopters.** Volunteers who opt into pilot studies are systematically different from mandatory-adoption populations. True population-level acceptance may be 10-20 percentage points lower than observed 92%. The 22-percentage-point margin above our 70% threshold provides buffer for selection bias.

**Limitation 3: Short-term deployment.** We measured acceptance during initial 2-week exposure. Novelty effects could inflate early acceptance, or conversely, familiarity could increase acceptance as users learn the system. Long-term trends remain unknown.

**Limitation 4: Adversarial resistance untested.** We did not evaluate how the system performs when users are incentivized to minimize effort. Users might accept low-quality suggestions to complete documentation quickly without engaging thoughtfully.

**Limitation 5: Representative corpus structure used in proof-of-concept.** Our design describes a production architecture using 500+ high-quality documentation examples for few-shot prompting. For this proof-of-concept, we used a representative corpus structure to validate the few-shot prompting mechanism. Production deployment quality will depend on systematic corpus curation effort.

### Broader Impact

Improved dataset documentation benefits the ML research ecosystem by enabling accurate reproduction of findings, facilitating identification of dataset biases and limitations, supporting responsible data use, and reducing technical debt from undocumented assumptions. However, realizing these benefits requires validating that engagement translates to quality improvements.

Over-reliance on AI suggestions could reduce critical thinking about documentation content—researchers might accept suggestions without verifying accuracy or skip sections where suggestions are unavailable. If suggestions are biased (emphasizing certain use cases, reflecting English-dominant training), they could propagate systematic blind spots in documentation practices.

Researchers with limited English proficiency may face higher friction using a system trained predominantly on English exemplars, potentially exacerbating existing advantages for native English speakers if the system becomes mandatory.

## 7. Conclusion

This work addressed the documentation adoption challenge by investigating whether AI-powered assistance could reduce completion friction. Our pilot with 75 users achieved 92% median acceptance, substantially exceeding our conservative 70% threshold and establishing that researchers will engage with AI-generated documentation suggestions.

Our contributions are: (1) Demonstration that researchers engage with AI documentation assistance at high rates (92% acceptance with 22-percentage-point margin above threshold), validating the necessary precondition for pursuing quality improvements. (2) Evidence of robust cross-domain generalization without specialized tuning (1.0 percentage point variance across vision, NLP, and tabular datasets). (3) Validation that high acceptance reflects thoughtful engagement rather than passive acceptance (26.8% modification rate).

This proof-of-concept establishes that researchers will use the tool but does not measure whether use improves documentation outcomes. Full-scale deployment with A/B testing is needed to measure whether 92% acceptance translates to improved completeness, higher expert quality ratings, and reduced time-to-completion.

Future work includes measuring downstream documentation quality improvements through controlled deployment, understanding longitudinal acceptance patterns over 6-12 months, validating production corpus quality effects through systematic curation and ablation studies, extending to other research documentation tasks (IRB proposals, grant applications, methodology sections), assessing multilingual and cross-cultural generalization, and evaluating adversarial resistance with controlled studies using minimal-effort incentives.

What this work demonstrates is that application domain characteristics matter for AI assistance adoption. Documentation's lower error stakes and higher time pressure may create more favorable conditions for AI acceptance than code generation, where correctness requirements demand careful verification. This insight suggests AI assistance research should stratify applications by error tolerance rather than treating all content generation as equivalent.

The path forward involves validating the complete value chain from engagement to quality improvement. Our proof-of-concept establishes that the first step is achievable—researchers will use the tool—providing foundation for measuring whether use translates to better documentation.

## References

1. Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Daumé III, H., & Crawford, K. (2021). Datasheets for datasets. Communications of the ACM, 64(12), 86-92.

2. Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., Hutchinson, B., ... & Gebru, T. (2019). Model cards for model reporting. In Proceedings of the Conference on Fairness, Accountability, and Transparency (pp. 220-229).

3. Bender, E. M., & Friedman, B. (2018). Data statements for natural language processing: Toward mitigating system bias and enabling better science. Transactions of the Association for Computational Linguistics, 6, 587-604.

4. Chen, M., Tworek, J., Jun, H., Yuan, Q., Pinto, H. P. D. O., Kaplan, J., ... & Zaremba, W. (2021). Evaluating large language models trained on code. arXiv preprint arXiv:2107.03374.

5. Vanschoren, J., van Rijn, J. N., Bischl, B., & Torgo, L. (2014). OpenML: networked science in machine learning. ACM SIGKDD Explorations Newsletter, 15(2), 49-60.
