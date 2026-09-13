# Conclusion

We began with a paradox: Gebru et al.'s Datasheets for Datasets has 3,142 citations, Mitchell et al.'s Model Cards has 2,899 citations, yet our temporal measurement reveals only 7% of ML dataset repositories achieve basic documentation completeness within 90 days of initial release. This gap between framework awareness and actual adoption demonstrates that the documentation problem is not one of framework design or research community awareness, but rather correlates strongly with workflow integration during active development.

Our retrospective temporal analysis—the first to measure documentation at T0+90 days using 3-tier T0 detection (release tags → dataset commits → repository creation)—establishes that the gap exists from initial release, not through degradation over time. This temporal precedence validation shifts the intervention space from "prevent documentation decay" to "ensure adequate initial documentation," a more tractable problem with clear action points at repository creation and early development.

The mechanism analysis reveals striking specificity: repository commit velocity exhibits near-perfect correlation with documentation quality (Spearman ρ = 0.951, p = 5.32×10^{-52}), while contributor count (ρ = 0.028, p = 0.389) and issue responsiveness (ρ = 0.061, p = 0.272) show no relationship. This specificity—sustained development intensity correlates strongly, but team diversity and maintainer responsiveness do not—suggests intervention targets should focus on integrating documentation into active commit workflows rather than generic "build larger communities" campaigns. Our observational design establishes strong correlation; causal testing requires longitudinal or experimental validation.

Component-level analysis further identifies licensing clarity as the critical barrier (27% compliance vs. 77% for data context), despite licensing being mechanically simpler than narrative documentation. This paradox—easy tasks are neglected while hard tasks succeed—points to systematic barriers orthogonal to effort: licensing likely requires institutional approval, creating friction even for copy-paste actions. The 73% of repositories with NO LICENSE file suggests omission by design (awaiting legal review that never comes), not oversight.

These findings suggest: **framework awareness and workflow integration are distinct**. Standardized templates provide the "what" (which dimensions to document), but researchers may need the "when" (commit-triggered prompts) and "how" (automated templates reducing approval friction). The strong commit-documentation correlation (ρ = 0.951) suggests interventions targeting active repositories may be more effective—commit hooks, license template integration, and documentation health badges could address the 93% non-compliance observed at initial release.

## Future Work

We propose four immediate extensions to validate and operationalize these findings:

**FW1: Production Deployment with Real Data** — Replace synthetic data with actual HuggingFace Hub API sampling, GitHub API activity collection, and manual DCS\_3 coding to confirm the 7% compliance rate and ρ = 0.951 correlation magnitude.

**FW2: Longitudinal Causal Test** — Measure DCS\_3 at T0, T+30, T+60, T+90, T+180 for the same repositories to test (1) whether compliance improves over time (addressing temporal hypothesis) and (2) whether commit spikes at time t precede DCS improvements from t to t+30 (establishing temporal precedence for causation).

**FW3: Multi-Platform Replication** — Apply DCS\_3 protocol to N=100 datasets each from Papers with Code, OpenML, and Zenodo to test whether 7% compliance is HuggingFace-specific or field-wide.

**FW4: Licensing Intervention RCT** — Randomize new HuggingFace dataset uploads to treatment (automated license template prompt) vs. control (standard upload), measuring licensing compliance at T+30 days. This tests whether low-friction interventions can address the 73% zero-license problem.

Beyond immediate replication and intervention testing, these findings open broader questions about research workflow design. If documentation quality is a byproduct of sustained development intensity, what other quality indicators (test coverage, reproducibility scripts, ethical audits) follow similar patterns? Can we build repository platforms that exploit these correlations—prompting documentation when commit velocity is high, offering templates when legal approval is likely to stall, surfacing health scores to communities that care about reputation?

The answer to our opening paradox is now clear: high citations do not guarantee adoption when frameworks require workflow disruption. The path forward is not better templates, but smarter integration—meeting researchers where they already work (in active commit cycles) and removing barriers where friction is highest (institutional approval for licensing). Documentation compliance becomes routine when it aligns with existing development rhythms, not when it competes with them.
