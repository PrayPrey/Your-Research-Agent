# Methodology

## Overview

Building on our observation that documentation has lower correctness requirements than code, we design a system that prioritizes rapid, contextual suggestion generation over perfect accuracy. Our AI-powered documentation copilot uses few-shot prompting with high-quality exemplars to generate suggestions that researchers can accept, modify, or reject with minimal interaction friction.

The system operates in three stages: (1) analyze uploaded dataset properties to extract contextual features, (2) retrieve relevant examples from a curated corpus of high-quality documentation, and (3) generate contextual suggestions via LLM few-shot prompting. We integrate this into the documentation workflow such that researchers see AI-generated suggestions while filling template fields and can interact with single-click accept/modify/reject actions.

## Dataset Property Analysis

When a researcher uploads a dataset to the repository, our system automatically analyzes structural and semantic properties to inform suggestion generation.

**Structural Analysis:** We extract file formats (CSV, JSON, Parquet), data types (numeric, categorical, text, image), size metrics (number of samples, features, file size), and statistical distributions (value ranges, missing data patterns, class balance).

**Domain Classification:** We classify the dataset type—vision, NLP, or tabular—based on file extensions, column names, and content patterns. Vision datasets are identified by image file extensions (.jpg, .png) and directory structures. NLP datasets are detected through text column presence and vocabulary characteristics. Tabular datasets are identified by structured formats with numeric or categorical features.

**Rationale:** Contextual suggestions must reflect actual dataset characteristics to be perceived as helpful. Generic text that could apply to any dataset is readily identified and rejected by users. By analyzing dataset properties, we can generate domain-specific suggestions that reference relevant features, appropriate use cases, and plausible limitations.

**Alternatives Considered:** Template-based generation with fixed placeholders would be faster but produces generic content that users ignore. Property-driven personalization increases computational cost but substantially improves perceived relevance.

## Few-Shot Prompting with Exemplar Corpus

Rather than fine-tuning a custom model, we employ few-shot prompting with carefully curated examples, enabling rapid deployment without training infrastructure.

**Exemplar Corpus:** We curate 500 high-quality dataset documentation examples from HuggingFace, filtering for completeness (>85% of Datasheet fields filled) and semantic meaningfulness. The corpus is stratified by domain: 200 vision datasets, 200 NLP datasets, 100 tabular datasets.

**Example Retrieval:** For each documentation field to be filled, we retrieve 3-5 relevant examples from the corpus based on dataset type and property similarity. For instance, when generating suggestions for a vision dataset's "Uses and Applications" section, we retrieve examples from similar vision datasets (image classification, object detection).

**LLM Generation:** We use Llama-3-8B-Instruct [1] with few-shot prompting. The prompt includes:
- Dataset properties extracted in stage 1
- The documentation section to be filled (e.g., "Dataset Description")
- 3 high-quality examples from similar datasets
- Generation instructions emphasizing contextual relevance

**Prompt Template:**
```
You are a documentation assistant. Generate a suggestion for the following dataset.

Dataset Properties:
- Type: vision
- Format: Images (JPEG)
- Size: 10,000 samples
- Domain: Medical imaging

Documentation Section: Dataset Description

High-Quality Examples:
[Example 1 from similar dataset]
[Example 2 from similar dataset]
[Example 3 from similar dataset]

Generate a contextual suggestion for this section:
```

**Model Configuration:** Temperature = 0.7 (balancing creativity with consistency), max_length = 500 tokens, device = cuda:0 (GPU acceleration for real-time generation).

**Rationale:** Few-shot prompting provides "good enough" quality at minimal deployment cost. Fine-tuning would require extensive training infrastructure, hyperparameter optimization, and model deployment complexity—all premature optimization before validating that users will engage with suggestions. By deferring fine-tuning until after proving acceptance, we reduce time-to-deployment from months to weeks.

**Alternatives Considered:** Fine-tuned Llama-3-8B would likely produce higher quality suggestions but demands corpus curation, training compute (multi-GPU for days), and complex deployment. API-based models (GPT-4, Claude) would simplify infrastructure but introduce latency and cost constraints that could limit scalability.

## User Interaction Design

We minimize interaction friction through single-click accept/modify/reject actions.

**Interface Integration:** Suggestions appear inline as researchers fill documentation template fields. Each suggestion is presented with three action buttons:
- **Accept:** Insert suggestion as-is (fastest path)
- **Modify:** Accept suggestion into editable field for refinement
- **Reject:** Dismiss suggestion and write from scratch

**Default Behavior:** Clicking "Accept" immediately populates the field and advances to the next section. This makes the assisted path faster than manual writing, encouraging adoption through reduced friction.

**Interaction Logging:** Every user action is logged with timestamps for acceptance rate calculation. We track:
- Suggestion ID and content
- User action (accepted/modified/rejected)
- Modified text (if applicable)
- Dataset type and documentation section
- User ID and session timestamp

**Rationale:** Multi-step rating or detailed feedback would provide richer data but increase friction, reducing adoption. By optimizing for speed (single-click actions), we ensure that using the copilot is faster than ignoring it, aligning incentives with engagement.

**Alternatives Considered:** Soliciting quality ratings (1-5 scale) or collecting detailed feedback would inform iterative improvement but would slow the interaction loop. We prioritize adoption over rich feedback in the initial deployment, deferring detailed evaluation to post-deployment surveys.

## Deployment Protocol

We validate our approach through a 2-week pilot deployment with 75 researchers on HuggingFace.

**Participant Recruitment:** We recruited early adopters who volunteered to test the copilot system—acknowledging that self-selection likely inflates acceptance rates but provides initial feasibility evidence.

**Deployment Scale:** Each participant documented 1-5 datasets during the 2-week period, generating approximately 25 suggestions per user (1,875 total suggestions across 75 users). This scale provides statistically meaningful sample size (n > 1,000) for acceptance rate estimation.

**Data Collection:** All suggestion interactions are logged to JSON files (`suggestions_log.json`, `user_interactions.json`) for post-deployment analysis. We record suggestion content, user actions, timestamps, and dataset metadata.

**Evaluation Metric:** Median per-user acceptance rate is our primary metric, calculated as:

```
acceptance_rate = (accepted + modified) / total_suggestions × 100%
```

We aggregate at user level (not suggestion level) to avoid biasing toward high-volume users.

**Success Threshold:** We pre-registered 70% median acceptance as our deployment feasibility threshold. Acceptance below 40% would indicate mechanism failure (suggestions not helpful); between 40-70% would suggest promising but immature technology; above 70% validates deployment readiness.

**Stratified Analysis:** We analyze acceptance rates by dataset type (vision, NLP, tabular) to evaluate cross-domain generalization. Consistent performance across types (variance <10 percentage points) indicates robust scalability without domain-specific tuning.

---

**Word count:** ~1,150 words

**Key Design Decisions:**
1. Few-shot prompting (not fine-tuning) → Rapid deployment
2. Property-driven contextualization → Perceived relevance
3. Single-click interaction → Minimal friction
4. 70% acceptance threshold → Clear go/no-go criterion

**References:**
- [1] Llama-3-8B-Instruct (Meta, 2024)
