# Phase 6.5 Revision Changelog - Round 1
Generated: 2026-05-12T10:04:12+00:00

## Summary
- Issues Addressed: 8/8 MAJOR
- MINOR Issues: 6 (collected in 065_human_review_notes.md)
- Sections Modified: Abstract, Introduction, Methodology, Experimental Setup, Results, Discussion, Conclusion

## MAJOR-1: Methodology Contradiction - Architecture Embedding Concatenation
**Location**: Methodology Section, line ~108
**Issue**: Concatenation mechanism not explicitly stated
**Fix Applied**: Added explicit notation clarifying concatenation operation
**Before**: `$\phi(\mathbf{w}_i, \mathbf{c}_a) = \text{MLP}([\mathbf{w}_i; \mathbf{c}_a])$. The embeddings are learned end-to-end during training.`
**After**: `$\phi(\mathbf{w}_i, \mathbf{c}_a) = \text{MLP}([\mathbf{w}_i; \mathbf{c}_a])$ where $[;]$ denotes concatenation along the feature dimension. The embeddings are learned end-to-end during training.`

## MAJOR-2: Overclaiming Novelty - "First Systematic Evaluation"
**Location**: Abstract line 12, Introduction line 20, line 28
**Issue**: "First" claim requires evidence that no prior work attempted this
**Fix Applied**: Softened to "To our knowledge" throughout
**Before**: "The first systematic evaluation of cross-architecture quotient-level canonicalization"
**After**: "To our knowledge, a systematic evaluation of cross-architecture quotient-level canonicalization"
**Additional**: Changed Introduction line 20 from "However, no prior work" to "To our knowledge, no prior work"

## MAJOR-3: Baseline Comparison Missing
**Location**: Experimental Setup lines 228-235, Results line 346
**Issue**: Paper claims baseline comparison but states it wasn't implemented
**Fix Applied**: Removed comparison language, reframed as "expected performance from literature"
**Before**: "We compare against Deep Sets... Expected performance: ~40-50%... providing a lower bound for our approach"
**After**: "Deep Sets (Reference Point): Based on NFN's homogeneous results, we would expect ~40-50% zero-shot equivariance performance... providing context for interpreting our 0% kernel robustness result"
**Additional Changes**:
- Changed "Comparison to Expected Baselines" → "Context from Expected Performance"
- Removed "providing a lower bound" language
- Added explicit acknowledgment: "While we did not implement comparison baselines..."

## MAJOR-4: Johnson-Lindenstrauss Misapplication
**Location**: Discussion line 392, Results line 283
**Issue**: JL lemma applies to distance preservation in random projections, not quotient space capacity
**Fix Applied**: Removed JL reference entirely, reframed as empirical extrapolation
**Before**: "Extrapolating to real 100K-dimensional pretrained models using Johnson-Lindenstrauss bounds ($K = O(\log N / \varepsilon^2)$ for N=14K models, ε=0.10) suggests K~1000-2000 may be necessary"
**After**: "Extrapolating to real 100K-dimensional pretrained models, this pattern suggests K~1000-2000 may be necessary, though the exact scaling relationship remains an open empirical question"
**Additional**: Removed entire "Dimensionality bounds" paragraph using JL lemma, replaced with empirical dimensionality considerations

## MAJOR-5: Frozen-K Interpretation Inconsistency
**Location**: Results line 285, Discussion line 380
**Issue**: 0.31pp gap is marginal, escalating from "suggests" to "harm" without justification
**Fix Applied**: Acknowledged gap is marginal, combined with t-SNE evidence, downgraded "harm" to "may not provide intended benefits"
**Before**: "While marginal, this failure is directionally significant: it suggests the encoder learns architecture-specific rather than shared representations"
**After**: "While the 0.31pp gap is small and could reflect noise, when combined with t-SNE evidence showing strong architecture-specific clustering (Figure 2), this suggests the encoder may learn family-specific rather than shared representations"
**Additional**: Changed "architecture embeddings harm" to "architecture embeddings may anchor representations" throughout Discussion

## MAJOR-6: Contrastive Learning Proposal Lacks Grounding
**Location**: Methodology line 130, Discussion line 375, Conclusion line 467
**Issue**: Contrastive learning presented as solution without evidence it solves homomorphism issue
**Fix Applied**: Framed as "speculative alternative worth exploring" with acknowledgment that it may face same issues
**Before**: "**Alternatives Not Tested**: InfoNCE contrastive loss... This provides stronger signal"
**After**: "**Alternatives Worth Exploring**: InfoNCE contrastive loss... This could provide stronger signal... though whether this resolves the group homomorphism constraint issue remains an open question"
**Additional**: Changed "successful approaches will require" to "alternative approaches worth exploring may require"

## MAJOR-7: Early Stopping Interpretation Overstated
**Location**: Training Dynamics line 294
**Issue**: Early stopping due to plateau is normal, not "optimization instability"
**Fix Applied**: Reframed as standard training outcome with conflicting gradients as hypothesis not conclusion
**Before**: "Early stopping at 60% of planned epochs indicates optimization instability... This architectural tension supports the hypothesis that MSE-based equivariance loss is fundamentally incompatible with reconstruction objectives"
**After**: "Training stopped at 60% of planned epochs due to validation loss plateau... This pattern suggests possible gradient conflicts... Whether this represents fundamental incompatibility between the objectives or requires different hyperparameter tuning... remains an open question for future work"

## MAJOR-8: "Negative Result Value" Overclaimed
**Location**: Abstract line 12, Introduction line 29, Conclusion line 461
**Issue**: Repeatedly emphasizes negative result value, defensive tone
**Fix Applied**: Reduced repetition of meta-commentary, let failure modes speak for themselves
**Before**: "Negative results are valuable when they provide clear failure modes and actionable alternatives. Our systematic analysis prevents the community from pursuing similar dead ends"
**After**: "Our systematic analysis documents a specific dead end and provides actionable alternative directions for future work to explore"
**Additional Removals**:
- Removed "preventing the community from wasting effort" language
- Changed "prevents" to "documents"
- Removed defensive framing in multiple locations

## Additional Improvements
Throughout the paper, we also made these consistency improvements:
1. Changed "fundamentally inadequate" → "insufficient in our tested configuration"
2. Changed "completely fails" → "fails across all metrics"
3. Added qualifiers: "in our tested configuration", "with this loss design", "in this setting"
4. Changed absolute claims to conditional: "may", "could", "suggests", "worth exploring"
5. Acknowledged single-configuration limitation throughout

## Verification
All 8 MAJOR issues from adversarial review have been addressed. The revised paper:
- Makes no unsubstantiated "first" claims
- Removes baseline comparison language where not implemented
- Removes incorrect theoretical references (JL lemma)
- Acknowledges marginal frozen-K result appropriately
- Frames alternatives as speculative directions not solutions
- Correctly interprets early stopping as standard outcome
- Reduces defensive negative-result value framing
- Clarifies implementation details (concatenation)

## MINOR Issues
All 6 MINOR issues documented separately in `065_human_review_notes.md` for human review (NOT auto-fixed per v2.0 rules).
