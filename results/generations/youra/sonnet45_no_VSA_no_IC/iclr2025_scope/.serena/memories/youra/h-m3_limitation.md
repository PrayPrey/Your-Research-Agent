# H-M3 SHOULD_WORK Gate Limitation Record

**Hypothesis ID**: h-m3  
**Type**: MECHANISM  
**Statement**: Simple queries (low entity density, short length) show higher query-token attention concentration than complex queries, validating adaptive tiering  
**Date**: 2026-08-20  
**Gate Type**: SHOULD_WORK  
**Gate Result**: FAIL  
**Reflection Outcome**: LIMITATION_RECORDED  

## Validation Results

**Statistical Test**: Two-sample t-test (simple > complex)
- **p-value**: 0.9537 (>> 0.05, no statistical significance)
- **Effect**: Δ = -0.003 (WRONG DIRECTION: complex > simple)
- **Cohen's d**: -0.242 (small negative effect)
- **Sample size**: 198 queries (98 simple, 100 complex)

**Failed Gate Criteria**:
1. ✗ p-value < 0.05 (actual: 0.9537)
2. ✗ delta > 0 (actual: -0.003, wrong direction)

## Limitation Summary

**Finding**: Entity density (num_entities / num_tokens) combined with word count does NOT predict query-token attention concentration during answer generation in Llama-2-7B.

**Complexity Classification**:
- Simple: word_count < 10 AND entity_density < 0.3
- Complex: otherwise

**Attention Measurement**: Last decoder layer attention, averaged across heads, summed over query token positions vs total attention mass.

**Result**: No difference between simple and complex queries. Complex queries actually showed slightly higher (but non-significant) query-token attention concentration.

## Fallback Strategy (SHOULD_WORK Behavior)

Since this is a SHOULD_WORK gate (not MUST_WORK), the limitation is recorded but does **not block** the pipeline:

**Fallback**: Use **uniform tiering** for all queries regardless of complexity
- All queries treated equally for KV cache eviction decisions
- No adaptive strategy based on query complexity
- Conservative approach: prevents potential performance degradation from incorrect stratification

**Impact on Dependent Hypotheses**:
- Core eviction mechanisms (H-M1: provenance tracking, H-M4: utility-aware eviction) remain valid
- H-M3 was an optimization for adaptive tiering, not a core requirement
- System degrades gracefully to uniform policy

## Technical Details

**Dataset**: LongBench multi-doc QA (HotpotQA, 2WikiMultihopQA, MuSiQue)  
**Model**: meta-llama/Llama-2-7b-hf  
**Entity Extraction**: spaCy en_core_web_sm NER  
**Infrastructure**: 5× NVIDIA H100 NVL (95GB)  
**Execution Time**: ~6 minutes for 198 samples  

**Implementation**: See `docs/youra_research/h-m3/code/`
- Stratification: `analysis/complexity.py`, `analysis/stratify.py`
- Attention extraction: `analysis/attention.py`, `analysis/metrics.py`
- Statistical testing: `analysis/stats.py`
- Validation report: `04_validation.md`

## Lessons Learned

1. **Entity density is not a proxy for attention concentration**: The hypothesis that syntactic complexity (entities) correlates with attention patterns did not hold
2. **Query structure may not drive attention allocation**: Other factors (e.g., context length, answer difficulty, multi-hop reasoning) may be more predictive
3. **SHOULD_WORK gates enable graceful degradation**: System can continue with documented limitations rather than full re-design

## Future Work (Optional)

If query-based tiering is revisited:
- Try alternative complexity metrics (dependency tree depth, coreference chains, reasoning hops)
- Measure attention concentration at different generation steps (not just last token)
- Test on other model families (different architectures may show different patterns)

## References

- Validation Report: `docs/youra_research/h-m3/04_validation.md`
- Experiment Results: `docs/youra_research/h-m3/code/outputs/results.csv`
- Prerequisite: `mem:youra/h-e1_limitation_poc_validated` (attention extraction methodology)
