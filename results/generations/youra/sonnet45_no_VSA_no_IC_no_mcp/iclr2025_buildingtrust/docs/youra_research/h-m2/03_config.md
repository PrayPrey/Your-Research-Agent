# Configuration: h-m2

**Hypothesis:** h-m2  
**Type:** MECHANISM (EXISTENCE)  
**Gate:** MUST_WORK (matched - mismatched ≥ 20pp OR relative improvement ≥ 50%)  
**Date:** 2026-08-24  

Applied: Hardcoded dict pattern (h-m1 base)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Verified h-m1 actual config implementation  
**Config Files Found**: `docs/youra_research/h-m1/code/config.py`  
**Pattern Used**: Hardcoded dict (CONFIG global)

---

## Inherited Configuration (Base Hypothesis)

### Config Pattern (From h-m1 Actual Code)

```python
# From: docs/youra_research/h-m1/code/config.py (ACTUAL CODE)
CONFIG = {
    "data": {
        "h_e1_results_path": "...",
        "entity_label": 0,
        "non_entity_label": 1
    },
    "split": {
        "random_state": 42
    },
    "seed": 42
}
```

**Verified from**: h-m1 actual implementation (hardcoded dict)

---

## Complete Configuration (Copy-Paste Ready)

```python
"""Configuration for h-m2 matched correction routing experiment."""

CONFIG = {
    # Data Configuration
    "data": {
        "h_m1_results_path": "/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_buildingtrust/docs/youra_research/h-m1/code/results/classification_results.json",
        "sample_size_per_model": 50,  # 50 entity-error cases per model
        "models": ["gpt-3.5-turbo", "llama-2-7b"]
    },
    
    # Model Settings (GPT-3.5)
    "gpt35": {
        "model_name": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 150,
        "api_key_env": "OPENAI_API_KEY"
    },
    
    # Model Settings (Llama-2-7B)
    "llama2": {
        "model_name": "meta-llama/Llama-2-7b-chat-hf",
        "temperature": 0.7,
        "max_tokens": 150,
        "hf_token_env": "HUGGINGFACE_TOKEN"
    },
    
    # Entity Extraction
    "entity_extraction": {
        "spacy_model": "en_core_web_sm",
        "max_entities": 3
    },
    
    # Retrieval Settings
    "retrieval": {
        "corpus": "wikipedia",
        "method": "wikipedia_api",  # ponytail: Wikipedia API simple, upgrade to BM25/dense if needed
        "top_k": 3,
        "sentences_per_doc": 2
    },
    
    # COT Baseline
    "cot": {
        "prompt_template": "Question: {question}\nIncorrect answer: {incorrect_answer}\n\nLet's think step by step to find the correct answer:"
    },
    
    # RAG Matched
    "rag": {
        "prompt_template": "Context: {context}\n\nQuestion: {question}\nIncorrect answer: {incorrect_answer}\n\nBased on the context, provide the correct answer:"
    },
    
    # Evaluation Settings
    "evaluation": {
        "judge_model": "gpt-3.5-turbo",
        "judge_temperature": 0.0,
        "judge_prompt": "Are these answers equivalent?\nAnswer A: {answer_a}\nAnswer B: {answer_b}\nRespond 'yes' or 'no'.",
        "metrics": ["success_rate", "difference", "relative_improvement"]
    },
    
    # Gate Thresholds
    "gate": {
        "difference_threshold": 0.20,  # 20 percentage points
        "relative_improvement_threshold": 0.50  # 50%
    },
    
    # Paths
    "paths": {
        "results_dir": "./results/",
        "figures_dir": "./figures/",
        "results_file": "./results/correction_results.json"
    },
    
    # Visualization
    "visualization": {
        "figure_dpi": 300,
        "figure_format": "png"
    },
    
    # Reproducibility
    "seed": 42
}
```

---

## Configuration Notes

1. **h_m1_results_path**: Load entity-error cases from h-m1 classifier outputs
2. **Retrieval method**: Wikipedia API (stdlib urllib) → skipped BM25/dense retrieval, add when API rate limits
3. **Entity extraction**: spaCy en_core_web_sm → max_entities=3 prevents over-retrieval
4. **GPT-judge**: temperature=0.0 for deterministic semantic equivalence checks
5. **Gate**: 20pp difference OR 50% relative improvement, both models must pass
6. **seed=42**: Consistent with h-m1 base hypothesis

---

**Config Version:** 1.0  
**Status:** Ready for Phase 4 Implementation
