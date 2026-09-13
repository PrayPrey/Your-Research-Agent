# Human Review Notes — Phase 6.5 Adversarial Review

> **Purpose:** Minor issues from adversarial review for human attention. NOT auto-fixed.
> **Date**: 2026-03-15
> **Rounds contributing**: R1

---

## Summary

| Category | Count |
|----------|-------|
| Formatting / Internal consistency | 3 |
| Style / Clarity | 2 |
| Related work gap | 1 |
| Missing limitation | 2 |

**Total**: 8 minor items (mn-2 through mn-7 from R1 review, plus 2 additional from Persona 3)

**Note**: mn-1 (d-range 0.13–0.41 vs. 0.061–0.41) was promoted to MAJOR and fixed in the revised paper. See 065_changelog.md.

---

## Round 1 Issues

### Formatting / Internal Consistency

**mn-2 [AC-2]**
- **Location**: Table 3
- **Issue**: The all-MiniLM-L6-v2 and all-mpnet-base-v2 rows in Table 3 provide raw H←A and A←H cosine values alongside Cohen's d for all three tiers. The paraphrase-MiniLM rows for T2 and T3 only report "H←A > A←H, d=X" without raw cosine values. This is inconsistent formatting within the table.
- **Context**: The raw cosine values for paraphrase-MiniLM T2 and T3 are not included in the ground truth YAML, so this may reflect a data availability constraint rather than an editorial choice.
- **Recommendation**: Either add the missing raw values to the paraphrase-MiniLM T2/T3 rows (if retrievable from the pipeline output), or add a table footnote explaining the formatting difference (e.g., "Raw cosine values not computed for paraphrase-MiniLM T2/T3 in pipeline run; inequality confirmed by Mann-Whitney U test").
- **Priority**: Medium — a reviewer checking the table will notice the inconsistency.

**mn-4 [BR-1 / BR-3]**
- **Location**: §5 opening paragraph
- **Issue**: The section opens with "We present results in four acts corresponding to our four main claims" but the paper contains five hypothesis subsections (§5.1 h-e1 through §5.5 h-m4) plus a summary §5.6. The "four acts" language does not match the paper's own five-subsection structure.
- **Context**: This appears to be a drafting artifact — the "four acts" framing was likely written before §5.5 (mediation analysis) was added to the five-hypothesis framework.
- **Recommendation**: Change "We present results in four acts corresponding to our four main claims" to "We present results across five sub-hypotheses: semantic accommodation exists (§5.1), scales with RLHF tier quality (§5.2), is directionally asymmetric (§5.3), is not driven by within-conversation quality discrimination (§5.4), and is not mediated by a politeness-style proxy (§5.5)." Alternatively, if the "acts" framing is important for narrative flow, update to "five acts."
- **Priority**: High — a bored reviewer will notice this immediately after reaching §5.

**mn-5 [BR-2]**
- **Location**: Figure Captions section (end of paper), Figure 4 and Figure 6 captions
- **Issue**: Figure 4 references the file "fig1_delta_distributions.png" and Figure 6 references "fig1_beta_pm_comparison.png." Both filenames begin with "fig1_" despite being Figures 4 and 6. This appears to be a pipeline artifact where figure filenames were not updated to match final figure numbering.
- **Recommendation**: Rename figure files to "fig4_delta_distributions.png" and "fig6_beta_pm_comparison.png" (or equivalent), and update the captions accordingly. This is a housekeeping item with no effect on content.
- **Priority**: Low — cosmetic, but may confuse readers who try to locate figures by filename in a code repository.

---

### Style / Clarity

**mn-3 [AC-3]**
- **Location**: §1 Contributions list, Contribution 2
- **Issue**: "Cohen's d T1→T3 = 0.18–0.25" rounds 0.183 to 0.18 and treats 0.254 as the upper bound at 0.25. Table 2 shows the full set as 0.183, 0.254, 0.238. The range 0.18–0.25 is technically a minor understatement (the true upper bound is 0.254, not 0.25).
- **Recommendation**: Consider updating to "0.18–0.26" (rounded to 2 decimal places correctly) or listing all three values explicitly: "d = 0.183 (all-MiniLM), 0.254 (paraphrase-MiniLM), 0.238 (mpnet)." The current rounding is defensible but "0.25" understates the paraphrase-MiniLM result by 0.004.
- **Priority**: Low — acceptable rounding in most venues; only a concern if a reviewer checks Table 2 carefully.

**mn-6 [SE-4]**
- **Location**: §5.4 Interpretation paragraph; §6.1 Finding 4
- **Issue**: The verbosity and topical breadth interpretation of the Δ < 0 result is stated as the paper's explanation without flagging it as a post-hoc hypothesis. Specifically: "We interpret this as reflecting the verbosity and topical breadth of rejected responses" (§5.4) and "The H-M3 reversal adds an important nuance: 'quality' in the RLHF sense... is not the same as 'conversational informativeness'" (§6.1) read as established findings rather than plausible interpretations awaiting confirmation.
- **Recommendation**: Add a parenthetical to the verbosity interpretation sentence in §5.4: "We interpret this as reflecting the verbosity and topical breadth of rejected responses (post-hoc hypothesis; see §7.2 for a proposed length-controlled replication)." A similar hedge in §6.1 would be appropriate.
- **Priority**: Medium — Persona 3 (Skeptical Expert) specifically flagged this; a methods-focused reviewer may push back on presenting an unconfirmed interpretation as the explanation.

---

### Related Work Gap

**mn-7 [SE-7]**
- **Location**: §2.1 (Related Work — Communication Accommodation Theory)
- **Issue**: The Related Work section grounds C_sem in Danescu-Niculescu-Mizil et al. (2012) and CAT theory, but omits the lexical entrainment literature that is directly relevant to accommodation measurement. Key missing citations: Brennan & Clark (1996, conceptual pacts and lexical entrainment), Nenkova et al. (2008, entrainment in speech), Levitan & Hirschberg (2011, acoustic accommodation).
- **Recommendation**: Add 1–2 sentences in §2.1 briefly acknowledging the lexical entrainment tradition and positioning C_sem's semantic-embedding approach relative to it. Example: "Our work extends a broader tradition of lexical and acoustic entrainment measurement [Brennan & Clark, 1996; Nenkova et al., 2008; Levitan & Hirschberg, 2011], moving from surface-level convergence to semantic embedding space." This strengthens the paper's positioning in the linguistic accommodation literature.
- **Priority**: Medium — strengthens the contribution framing; not required for acceptance but improves scholarly positioning.

---

### Missing Limitations

**mn-8 [SE-5]**
- **Location**: §6.2 Limitations (not currently present as L1–L5)
- **Issue**: The C_sem metric computes (H_{t+1}, A_t) pair similarity without controlling for conversational history. In multi-turn conversations, prior turns may systematically influence H_{t+1} in ways not captured by the A_t partner-specificity test. For example, if the human asked a question two turns earlier that is topically similar to A_t, H_{t+1} will appear more aligned with A_t even without genuine accommodation in turn t+1. This within-conversation carryover confound is neither tested nor acknowledged.
- **Recommendation**: Add as L6 in §6.2: "Within-conversation carryover: C_sem is computed on (H_{t+1}, A_t) pairs without controlling for prior conversational history. Prior turns may influence H_{t+1} independently of accommodation to A_t. Future work could address this by computing C_sem conditioned on prior-turn embeddings or using a conversation-history baseline."
- **Priority**: Medium — sophisticated reviewers may raise this; adding it as an acknowledged limitation preempts the objection.

**mn-9 [SE-6]**
- **Location**: §3.3 or §6.2 Limitations
- **Issue**: The paraphrase-MiniLM-L6-v2 model is specifically fine-tuned for paraphrase detection, which may systematically influence cosine similarities differently from the other two models. The paper cites robustness across three models, but does not discuss how model-specific training objectives affect C_sem measurement validity. The paraphrase model's training objective (maximize similarity for paraphrase pairs) may produce a different sensitivity profile for accommodation measurement than the all-purpose semantic similarity models.
- **Recommendation**: Add a brief note in §3.3 or §6.2 L2: "paraphrase-MiniLM's training objective (paraphrase detection) may produce systematically different sensitivity to accommodation signal vs. the two general-purpose semantic similarity models; the convergence of results across all three models mitigates this concern."
- **Priority**: Low — mitigated by the observed convergence across models; worth noting but not a material concern given the 3/3 replication.

---

## Recommended Priority

1. **Fix First (High Visibility)**:
   - mn-4: "Four acts" vs. five hypothesis sections — immediately visible inconsistency in §5 opening
   - mn-6: Verbosity interpretation — flag as post-hoc hypothesis in §5.4 and §6.1

2. **Consider Before Submission**:
   - mn-2: Table 3 paraphrase formatting inconsistency — add footnote or retrieve missing values
   - mn-7: Lexical entrainment citations in §2.1 — strengthens scholarly positioning
   - mn-8: Conversational carryover limitation — add as L6 in §6.2

3. **Low Priority / Polish**:
   - mn-3: Cohen's d range rounding in Contribution 2 (0.25 vs 0.254)
   - mn-5: Figure filename cleanup (fig1_ prefix artifacts)
   - mn-9: Paraphrase model training objective note in §3.3

---

## Round 2 Issues (from R2 Adversarial Review, 2026-03-15)

> **Note**: NV-M1 and NV-M2 were MAJOR issues — fixed in 06_paper_r2.md. The following are MINOR items from R2 review, collected here for human attention. NOT auto-fixed.

### NV-1: paraphrase-MiniLM T2 Cohen's d value in Table 3

- **Location**: Table 3, paraphrase-MiniLM row, T2 column
- **Issue**: Table 3 reports d = 0.35 for paraphrase-MiniLM T2. Phase 4 h-m2 validation shows the actual value is 0.3853, which rounds to 0.39. The value 0.35 appears to have originated in the ground truth YAML (also shows 0.35), suggesting the error propagated from YAML construction to the paper. The conclusion (H←A > A←H) is unaffected.
- **Fix**: Update Table 3 paraphrase T2 Cohen's d from 0.35 to 0.39 (rounded from 0.3853). Update ground truth YAML directional_asymmetry.paraphrase_minilm_T2.cohen_d accordingly.
- **Priority**: Medium — a reviewer checking Phase 4 files against Table 3 will find this discrepancy.

---

### NV-2: mpnet T1 H←A value in Table 3 (minor transcription)

- **Location**: Table 3, all-mpnet-base-v2 row, T1 H←A column
- **Issue**: Table 3 and ground truth YAML report mpnet T1 C_sem^H←A = 0.0838. Phase 4 h-m2 validation shows 0.0826. Difference = 0.0012. Small but a reproducibility note.
- **Fix**: Update Table 3 mpnet T1 H←A from 0.0838 to 0.0826. Update ground truth YAML accordingly.
- **Priority**: Low — negligible impact on any conclusion; worth fixing for reproducibility.

---

### NV-3: h-m3 strongest falsification operationalization mislabeled

- **Location**: §5.4 discussion text; ground truth YAML within_prompt_delta.strongest_falsification
- **Issue**: §5.4 and the YAML report "strongest falsification: T3-OP1, d = −0.738." Phase 4 h-m3 validation shows T3 raw (OP1) d = −0.716 and T3 length_matched (OP2) d = −0.738. The value −0.738 corresponds to OP2 (length-matched), not OP1 (raw). The paper's Table 4 row "T3 (helpful-online)" shows "d = −0.74" in the OP1 column, which is also incorrect (should be −0.72 for OP1 raw).
- **Fix**: In §5.4, update "d = −0.738 for OP1" to "d = −0.738 for OP2 (length-matched); OP1 raw d = −0.716." Update ground truth YAML strongest_falsification entry to specify OP2. Update Table 4 T3 OP1 cell from −0.74 to −0.72.
- **Priority**: Low — the magnitude is essentially the same and the conclusion (strong falsification in T3) is unaffected. But technically the OP label is wrong.

---

### NV-5: h-m4 R² values — rounding and transcription errors in Table 5

- **Location**: Table 5, R² column
- **Issue**: Three discrepancies between Table 5 and Phase 4 h-m4 validation:
  1. all-MiniLM R²: Paper=0.008, Phase4=0.0071. Rounds to 0.007, not 0.008.
  2. paraphrase R²: Paper=0.007, Phase4=0.0122. Material error — 0.012 ≠ 0.007.
  3. mpnet R²: Paper=0.012, Phase4=0.0101. Rounds to 0.010, not 0.012.
  The null conclusion (β_PM ≈ 0, p ≈ 0.99) is entirely unaffected — all R² values are below 0.013 regardless. The footnote "R² ≤ 0.012" remains valid for corrected values.
- **Fix**: Update Table 5 R² to: all-MiniLM=0.007, paraphrase=0.012, mpnet=0.010. Update the §5.5 footnote to read "R² ≤ 0.012" (unchanged — the maximum is 0.0122 ≈ 0.012).
- **Priority**: Medium — the paraphrase discrepancy (0.007 vs 0.012) is large enough that a reviewer checking against Phase 4 files will notice. The null conclusion is robust regardless.

---

## Updated Recommended Priority (including R2 items)

1. **Fix Before Submission (High Visibility)**:
   - mn-4: "Four acts" vs. five hypothesis sections (§5 opening)
   - NV-1: paraphrase T2 d=0.35 → 0.39 in Table 3 (Phase 4 says 0.3853)
   - NV-5: paraphrase R²=0.007 → 0.012 in Table 5 (Phase 4 says 0.0122)

2. **Consider Before Submission**:
   - mn-2: Table 3 paraphrase formatting inconsistency
   - mn-6: Post-hoc hedge on verbosity interpretation in §5.4 and §6.1
   - mn-7: Lexical entrainment citations in §2.1
   - mn-8: Conversational carryover limitation as L6 in §6.2
   - NV-3: OP1 vs OP2 label for strongest h-m3 falsification

3. **Low Priority / Polish**:
   - mn-3: Cohen's d range rounding in Contribution 2
   - mn-5: Figure filename cleanup
   - mn-9: Paraphrase model training objective note
   - NV-2: mpnet T1 H←A = 0.0826 vs 0.0838 (difference = 0.0012)
