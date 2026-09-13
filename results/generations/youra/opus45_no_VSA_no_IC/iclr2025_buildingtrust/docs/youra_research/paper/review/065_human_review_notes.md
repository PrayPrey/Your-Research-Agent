# Human Review Notes (Minor Issues)

The following MINOR issues were identified but NOT auto-fixed. Please review manually:

1. **Abstract phrasing:** "r=0.42-0.58" could be clearer as "r ranging from 0.42 to 0.58"

2. **Future citation (Fan et al., 2026):** Citation date appears to be future relative to typical research conventions. Verify if intentional for paper setting.

3. **Future citation (Bang et al., 2025):** Same future date issue as above.

4. **PC3 variance approximation:** Listed as "~7%" but ground truth doesn't specify exact PC3 value. Consider computing exact value if available.

5. **Conclusion r=0.16 vs H-M2 r=0.162:** Minor precision inconsistency between sections. The 2-decimal rounding (0.16) is now consistent with MAJOR-1 fix, so this may be resolved.

## Round 2 Minor Issues

6. **H-M1 CI/p-value source:** Phase 4 validation file does not document CI=[-0.09, 0.44] or p=0.19 for r(TQA, MMLU). Values appear in ground_truth.yaml. Verify source before publication.

7. **PC3 variance soft-stated:** Paper says "~7%" but Phase 4 only shows PC1 (38.6%) and PC2 (34.3%). Math works (rounds to 80% total), but consider making explicit.

8. **H-M2 subtask p-value rounding:** Paper shows (0.29, 0.31, 0.12) vs Phase 4 (0.2878, 0.3062, 0.1216). Not material but noted.
