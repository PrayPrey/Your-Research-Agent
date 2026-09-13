# Citation Verification Log
**Date:** 2026-07-11  
**Paper:** Semantic Validity of Data Augmentation  
**Venue:** ICML 2025  

## Summary

- **Total Citations Extracted:** 6 papers
- **Verified via Semantic Scholar:** 6/6 (100%)
- **With arXiv IDs:** 5/6 (83.3%)
- **High-Impact Papers (>100 cites):** 4/6 (66.7%)

## Citations by Category

### Data Augmentation Surveys

1. **Yang et al. 2022** - Image Data Augmentation Survey
   - **Status:** ✓ VERIFIED
   - **Semantic Scholar ID:** 55db03005681111f0c822c416ab473c49e00f04d
   - **arXiv:** 2204.08610
   - **Citations:** 399
   - **Venue:** arXiv preprint
   - **Usage in Paper:** Primary augmentation survey reference, establishes that existing surveys lack semantic validity analysis

2. **Wen et al. 2020/2021** - Time Series Data Augmentation Survey
   - **Status:** ✓ VERIFIED
   - **Semantic Scholar ID:** e5cd9e7bd60954a0523cc849ad6c92c0ede2d271
   - **arXiv:** 2002.12478
   - **Citations:** 836
   - **Venue:** IJCAI 2021
   - **Year Note:** Published in 2021 proceedings, arXiv preprint 2020
   - **Usage in Paper:** Foundational augmentation principles, general augmentation taxonomy

### Label Noise Literature

3. **Song et al. 2022** - Learning From Noisy Labels Survey
   - **Status:** ✓ VERIFIED (replaces "Wei et al. 2021" reference)
   - **Semantic Scholar ID:** 5ffe9b1d8219438f0343995ad3ea1a888e3d9f8e
   - **arXiv:** 2007.08199
   - **Citations:** 1394
   - **Venue:** IEEE Transactions on Neural Networks and Learning Systems
   - **Year Note:** Published 2022, arXiv preprint 2020
   - **Usage in Paper:** Primary label noise survey, establishes that label noise research focuses on annotation errors not augmentation-induced noise
   - **Replacement Note:** Narrative blueprint references "Wei et al. 2021" but no highly-cited comprehensive label noise survey by Wei et al. was found. Song et al. 2022 is the most comprehensive and highly-cited survey from that period.

4. **Patrini et al. 2017** - Making DNNs Robust to Label Noise
   - **Status:** ✓ VERIFIED
   - **Semantic Scholar ID:** 91d331d2bdd5fc86400c40c497bcb4c741c652be
   - **arXiv:** 1609.03683
   - **Citations:** 1697
   - **Venue:** CVPR 2017
   - **Year Note:** Published 2017, arXiv preprint 2016
   - **Usage in Paper:** Classical loss correction approach for label noise, foundational reference

### Gap Identification Papers

5. **Purba et al. 2025** - Horizontal/Vertical Flip Augmentation
   - **Status:** ✓ VERIFIED
   - **Semantic Scholar ID:** 0226afe702d4172202cd01588b1d064c275a653b
   - **arXiv:** None (DOI: 10.36085/jsai.v8i2.8769)
   - **Citations:** 0 (recent publication)
   - **Venue:** JSAI (Journal Scientific and Applied Informatics)
   - **Usage in Paper:** Example of applied horizontal flip without semantic validation (Gap 1 from Phase 1)

### Baseline Performance Documentation

6. **Mantzaris 2025** - MNIST Without Augmentation
   - **Status:** ✓ VERIFIED
   - **Semantic Scholar ID:** 85c9376023e33f8592603009b598220f1ee1e921
   - **arXiv:** 2510.03598
   - **Citations:** 0 (recent publication)
   - **Venue:** arXiv preprint
   - **Usage in Paper:** Documents MNIST baseline CNN performance (~98% without augmentation)

## Verification Method

All citations verified using Semantic Scholar MCP:
- Tool: `mcp__hamid-vakilzadeh-mcpsemanticscholar__paper_details`
- Tool: `mcp__hamid-vakilzadeh-mcpsemanticscholar__paper_relevance_search`

### Queries Used

1. Direct arXiv lookup: `ARXIV:2204.08610` (Yang et al.)
2. Direct arXiv lookup: `ARXIV:2002.12478` (Wen et al.)
3. Relevance search: "Patrini Making Deep Neural Networks Robust to Label Noise 2017"
4. Relevance search: "learning with noisy labels survey deep learning" (for label noise survey)
5. Direct Semantic Scholar ID: `0226afe702d4172202cd01588b1d064c275a653b` (Purba et al.)

## Important Notes

### "Wei et al. 2021" Reference Issue

The narrative blueprint references "Wei et al. 2021" as a label noise survey. However:

- **Search Results:** Multiple papers by Wei et al. in 2021 found, but none are comprehensive label noise surveys
- **Candidates Found:**
  - Wei, Tong et al. 2021: "Robust Long-Tailed Learning under Label Noise" (65 cites) - Specific to long-tailed learning
  - Wei, Hongxin et al. 2021: "Open-set Label Noise Can Improve Robustness" (110 cites) - Specific to open-set noise
  - Wei, Jiaheng et al. 2021: "Understanding Label Smoothing when Learning with Noisy Labels" (18 cites) - Specific to label smoothing

- **Replacement:** Song et al. 2022 "Learning From Noisy Labels With Deep Neural Networks: A Survey" (1394 citations)
  - This is the most comprehensive and highly-cited label noise survey from that period
  - Published in IEEE TNNLS (top-tier venue)
  - ArXiv preprint from 2020 (arXiv:2007.08199)

### Citation Count Verification

All citation counts retrieved from Semantic Scholar as of 2026-07-11:
- Yang et al. 2022: 399 citations ✓ (matches narrative blueprint)
- Wen et al. 2020: 836 citations ✓ (matches narrative blueprint)
- Song et al. 2022: 1394 citations (new, replaces Wei et al.)
- Patrini et al. 2017: 1697 citations
- Purba et al. 2025: 0 citations (recent)
- Mantzaris 2025: 0 citations (recent)

## BibTeX File Location

**File:** `/workspace/TEST_scsl/docs/youra_research/paper/06_references.bib`

## Recommendations for Paper Writing

1. **Update References:** Replace "Wei et al. 2021" with "Song et al. 2022" in all section drafts
2. **Citation Style:** Use ICML standard citation format (Author Year) in text
3. **High-Impact Focus:** Emphasize highly-cited surveys (Yang 399, Wen 836, Song 1394, Patrini 1697)
4. **Gap Narrative:** Use Purba et al. 2025 as concrete example of Gap 1 (augmentation without semantic validation)
5. **Baseline Reference:** Use Mantzaris 2025 for MNIST baseline performance documentation

## Additional Papers from Phase 1 Research

The following papers were identified in Phase 1 targeted research but not yet included in references:

- Gao, Zhuopeng 2025: GAN-based augmentation achieving 99.79% MNIST accuracy
- Muchlis et al. 2025: Flip augmentation effectiveness study
- Fan 2024: Traditional augmentation vs synthetic data comparison (arXiv:2409.05225)

**Recommendation:** Add these if specific empirical comparisons or MNIST performance benchmarks are needed in Results/Discussion sections.

## Verification Status

✓ All citations verified via Semantic Scholar MCP  
✓ arXiv IDs confirmed for 5/6 papers  
✓ Citation counts accurate as of 2026-07-11  
✓ BibTeX file generated in ICML format  
✓ Ready for paper writing (Phase 6 Step 3-5)  
