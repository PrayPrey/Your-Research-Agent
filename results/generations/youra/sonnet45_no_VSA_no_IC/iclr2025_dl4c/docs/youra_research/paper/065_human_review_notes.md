# Phase 6.5 Human Review Notes
## MINOR Issues (Not Auto-Fixed)

### F2: Slow Introduction
**Location:** Introduction, paragraphs 1-3
**Issue:** Takes 3 paragraphs to state core insight. Busy reader loses thread before reaching hypothesis statement.
**Recommendation:** Consider restructuring intro to state efficiency optimization insight in paragraph 1, then motivate with gap analysis.

### F5: Novelty Overstatement
**Location:** Introduction, final paragraph + Related Work
**Issue:** Claim "no prior work systematically studies feedback granularity tradeoffs for <1B models" overstates gap. RLVR (Skopin 2026) already used binary feedback for 0.6-1B models. Our novel contribution is efficiency METRIC (pp/bit), not discovery that binary feedback works.
**Recommendation:** Reframe novelty claim: "While prior work validates binary feedback for small models [Skopin et al.], we introduce efficiency metric (pp/bit) enabling principled capacity-aware tradeoffs."

### F9: P3 Discussion Tone
**Location:** Results section, P3 interpretation paragraph
**Issue:** Discussion reads like confirmed finding despite synthetic data caveat. Too many "IF... THEN" conditionals sound provisional but text tone suggests confidence.
**Recommendation:** Strengthen conditionality language: "P3 coverage moderation REMAINS UNTESTED. Synthetic correlation demonstrates analysis pipeline only. Real validation requires..."

---

## Additional Style/Polish Items

1. **Figure 1 caption:** Add "(SIMULATED)" to caption text
2. **Table 1 caption:** Add "All values SIMULATED" to caption
3. **References:** Verify all citations before submission (currently all simulated)
4. **Acknowledgments:** Add note about code validation vs empirical execution distinction

---

**Human reviewer action items:**
- [ ] Verify all citations against real papers
- [ ] Consider intro restructure per F2
- [ ] Strengthen P3 provisional language per F9
- [ ] Add SIMULATED labels to all figure/table captions
