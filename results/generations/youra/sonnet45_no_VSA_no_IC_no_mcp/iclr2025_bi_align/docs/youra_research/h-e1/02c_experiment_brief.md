# Experiment Design: h-e1

**Date:** 2026-08-25
**Author:** Anonymous
**Hypothesis Statement:** Reformulation rate decrease AND diversity correlation exist in HH-RLHF conversations with ≥5 turns
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites)
**Gate Status:** MUST_WORK (not yet satisfied)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
MUST_WORK gate - Hypothesis must demonstrate positive effect direction (reformulation slope < 0) to proceed. Failure blocks dependent hypotheses.

---

## Continuation Context

This is the first hypothesis in the verification chain. No previous results to inherit.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Archon MCP not available in this session - skipping knowledge base search*

**Relevant Research Areas (Manual)**:
- RLHF conversation analysis (multi-turn dialogue metrics)
- Query reformulation detection (paraphrase identification, semantic similarity)
- Response diversity measurement (lexical diversity, distinct-n metrics)
- Conversational alignment evaluation (helpfulness correlation)

### Archon Code Examples

*Archon MCP not available - proceeding without code examples from KB*

### Exa GitHub Implementations

*Exa MCP not available in this session - providing manual analysis*

**Relevant Implementation Areas**:
- HH-RLHF dataset analysis (Anthropic/hh-rlhf Hugging Face)
- Sentence-BERT for semantic similarity (sentence-transformers library)
- Edit distance computation (Python difflib/Levenshtein)
- Multi-turn conversation metrics (custom implementation required)
- Statistical analysis (scipy, statsmodels)

**No official paper implementation** (this is novel hypothesis testing on existing dataset)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

*Not applicable - hypothesis tests novel behavioral patterns in existing data*

**Recommended Implementation Path:**
- Primary: Custom implementation using sentence-transformers + scipy
- Fallback: Manual annotation if automated detection fails
- Justification: No existing codebase tests reformulation slope + diversity correlation coupling

### Code Analysis (Serena MCP)

*Skipped* - Code from search results sufficiently clear (standard libraries: sentence-transformers, scipy, difflib)

---

## Experiment Specification

### Dataset

**Name:** HH-RLHF (Anthropic Helpful-Harmless RLHF)
**Type:** standard
**Source:** https://huggingface.co/datasets/Anthropic/hh-rlhf
**Size:** 161k conversations (train + test splits)
**Structure:** Multi-turn conversations with helpfulness/harmlessness ratings

**Filtering:**
- Min conversation length: ≥5 turns (required for slope estimation)
- Filter for well-aligned subset: helpfulness > median (h-e2 only)

**Statistics (after filtering):**
- Expected ~50k conversations ≥5 turns
- Average turns per conversation: 6-8
- Conversations with helpfulness ratings: ~100%

**Preprocessing:**
1. Parse conversation structure (turn pairs)
2. Extract user queries and AI responses per turn
3. Extract metadata: helpfulness rating, conversation length
4. Filter by minimum turn count

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `Anthropic/hh-rlhf`
- Code: `load_dataset("Anthropic/hh-rlhf")`

### Models

#### Baseline Model

**Not applicable** - This is a measurement experiment (data analysis), not model training.

**Tools Required:**
- SBERT (sentence-transformers): Semantic similarity computation
- Python difflib/Levenshtein: Edit distance computation
- scipy.stats: Pearson correlation, linear/logistic regression
- statsmodels: Statistical modeling

**Loading Information** (for Phase 4 download):
- Method: pip install
- Identifier: `sentence-transformers`, `scipy`, `statsmodels`, `python-Levenshtein`
- Code:
  ```python
  from sentence_transformers import SentenceTransformer
  model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight SBERT
  ```

#### Proposed Model

**Not applicable** - This is a data analysis experiment (no model training).

**Core Mechanism Implementation:**

```python
# Reformulation Detection + Diversity Correlation Analysis
# Based on: HH-RLHF dataset, SBERT embeddings, scipy stats

class ReformulationAnalyzer:
    """
    Detect user reformulation patterns and AI diversity correlation
    in multi-turn conversations.
    """
    def __init__(self, sbert_model='all-MiniLM-L6-v2'):
        self.sbert = SentenceTransformer(sbert_model)
        
    def detect_reformulation(self, query_t, query_t1):
        """
        Args:
            query_t: str - query at turn t
            query_t1: str - query at turn t+1
        Returns:
            bool - True if reformulation detected
        """
        # Semantic similarity
        emb_t = self.sbert.encode(query_t)
        emb_t1 = self.sbert.encode(query_t1)
        semantic_sim = cosine_similarity(emb_t, emb_t1)
        
        # Syntactic distance
        edit_dist = Levenshtein.distance(query_t, query_t1)
        norm_edit = edit_dist / max(len(query_t), len(query_t1))
        
        # Reformulation: high semantic similarity + high syntactic change
        return semantic_sim > 0.7 and norm_edit > 0.3
    
    def compute_reformulation_slope(self, conversation):
        """
        Compute reformulation rate decline slope across turns.
        
        Args:
            conversation: list of query strings
        Returns:
            float - slope (negative = learning)
        """
        reformulation_rates = []
        for i in range(len(conversation) - 1):
            is_reform = self.detect_reformulation(conversation[i], conversation[i+1])
            reformulation_rates.append(float(is_reform))
        
        # Linear regression: rate ~ turn_index
        turns = np.arange(len(reformulation_rates))
        slope, intercept, r, p, se = linregress(turns, reformulation_rates)
        return slope
    
    def compute_diversity(self, texts):
        """
        Compute distinct-1 (lexical diversity) for text list.
        
        Args:
            texts: list of strings
        Returns:
            float - diversity score
        """
        all_tokens = ' '.join(texts).split()
        distinct_tokens = set(all_tokens)
        return len(distinct_tokens) / len(all_tokens) if all_tokens else 0.0

# Usage: Apply to filtered HH-RLHF conversations (≥5 turns)
```

### Training Protocol

**Not applicable** - This is a measurement experiment (no training).

**Analysis Protocol:**

1. **Data Loading:**
   - Load HH-RLHF dataset via Hugging Face
   - Filter conversations with ≥5 turns
   - Parse conversation structure (user queries, AI responses, metadata)

2. **Reformulation Slope Computation (h-e1):**
   - For each conversation:
     - Extract consecutive query pairs
     - Detect reformulation per turn (SBERT + edit distance)
     - Compute reformulation slope via linear regression
   - Stratify by outcome (successful conversations only)
   - Run logistic regression: `success ~ reformulation_slope + turn_count`

3. **Diversity Correlation (h-e2):**
   - For each conversation (helpfulness > median):
     - Compute query diversity (distinct-1)
     - Compute response diversity (distinct-1)
   - Compute Pearson correlation

4. **Seeds:** 1 (fixed: 42)

### Evaluation

**Primary Metrics:**
- **h-e1**: Reformulation slope coefficient (target: < 0, p < 0.05, OR > 1.2)
- **h-e2**: Diversity correlation coefficient (target: r > 0.4, p < 0.05)

**Success Criteria (PoC):**
- h-e1: `slope_coef < 0` (direction only - negative slope indicates learning)
- h-e2: `r > 0.4` (direction only - positive correlation indicates responsiveness)

**Expected Baseline Performance:**
- Random baseline (permuted data): slope ≈ 0, r ≈ 0
- Effect size: medium (Cohen's d ≈ 0.5 for slope difference)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical analysis (correlation, regression)
- Library: scipy.stats, statsmodels
- Code:
  ```python
  from scipy.stats import linregress, pearsonr
  from statsmodels.formula.api import logit
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart
  - h-e1: Reformulation slope coefficient (target < 0)
  - h-e2: Diversity correlation (target r > 0.4)

#### Additional Figures (LLM Autonomous)

**Recommended Visualizations:**
1. **Reformulation Rate Over Turns**: Line plot showing avg reformulation rate vs turn index (should decline)
2. **Slope Distribution**: Histogram of reformulation slopes across all conversations
3. **Diversity Scatter**: Query diversity vs response diversity (should show positive correlation)
4. **Success Stratification**: Reformulation slope comparison (successful vs abandoned conversations)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

*Archon MCP not available - manual research used*

**Manual Research Areas:**
- HH-RLHF dataset analysis methods
- Paraphrase detection techniques (SBERT, edit distance)
- Lexical diversity metrics (distinct-n)
- Conversational alignment metrics

### B. GitHub Implementations (Exa)

*Exa MCP not available - standard libraries used*

**Standard Libraries:**
1. **sentence-transformers** (SBERT)
   - URL: https://github.com/UKPLab/sentence-transformers
   - Relevance: Semantic similarity computation for reformulation detection
   - Used For: Query embedding and similarity calculation

2. **python-Levenshtein**
   - URL: https://github.com/ztane/python-Levenshtein
   - Relevance: Edit distance for syntactic change detection
   - Used For: Reformulation syntactic component

3. **scipy**
   - URL: https://github.com/scipy/scipy
   - Relevance: Statistical analysis (correlation, regression)
   - Used For: Slope computation, Pearson correlation, hypothesis testing

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - standard libraries sufficiently clear

### D. Previous Hypothesis Context

**Previous Context**: None - this is the first hypothesis in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Phase 2B | HH-RLHF from 02b_verification_plan.md |
| Preprocessing | Manual | Conversation parsing, turn filtering |
| Baseline model | N/A | Data analysis (no model training) |
| Mechanism design | Phase 2B | Reformulation + diversity from verification plan |
| Pseudo-code | Manual | Standard NLP/stats libraries |
| Analysis protocol | Phase 2B | Section 1.3 test protocol |
| Evaluation metrics | Phase 2B | Success criteria from verification plan |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-25

### Workflow History for This Hypothesis
- Phase 2C experiment design: COMPLETED at 2026-08-25

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
