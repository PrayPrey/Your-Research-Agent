# Phase 2A Convergence Self-Checks (Audit Trail — IC-Ablation)

Convergence self-judged by Claude against the 6 criteria from `phase2a_config.yaml` /
`personas.yaml`. Thresholds: min_exchanges=15, max_exchanges=20 (phase2a_config.yaml,
authoritative). Anti-leniency rule applied: each criterion requires concrete exchange
evidence.

## Convergence Check @ Exchange 15

- SPECIFIC:    PASS — Under-If-Then-Because core claim drafted in Exchange 6, consolidated with full protocol in Exchange 11: per-layer logit-lens statistics (entropy, max-prob, adjacent-layer KL), per-model held-out (layer, signal, direction) selection, two numeric gate tiers, named models/datasets.
- MECHANISM:   PASS — Exchange 7: hallucination as unresolved candidate competition (grounded in Entropy-Lens validated expansion/pruning reading, Spearman 0.74–0.88); Exchange 13 upgraded to 3 falsifiable steps (separation exists at depth; final-layer calibration suppresses it; suppression is architecture-dependent), retrodicting both h-e1 anomalies (llama2 miss + direction inversion).
- PREDICTIONS: PASS — Exchange 8: P1 (rescue: AUROC ≥ 0.60 both datasets + paired-bootstrap CI-separated ΔAUROC vs final layer on llama2/TriviaQA), P2 (transfer: ±0.05 AUROC tolerance, floor 0.60, both directions), P3 (fusion gain ≥ 0.02, CI excluding zero) — each with test method, success criterion, falsification condition. Exchange 10 added no-regression clause; Exchange 7 depth-band explicitly ungated/exploratory.
- NOVELTY:     PASS — Exchange 1 (empty cell: Entropy-Lens has feature without task; FEPoID has task without this method), challenged directly in Exchanges 5 and 12 and re-verified: differentiation articulated vs Entropy-Lens, FEPoID, Kim 2025, SAPLMA, END/DoLa, HalluShift (novelty check deferred to Phase 2B as planned), and the failed h-e1 family.
- FEASIBILITY: PASS — Exchange 3 (instrument validity + degeneracy screen), Exchange 9 (measurement guards, token aggregation, selection-split-only screening), Exchange 14 (final verdict: no fundamental barriers; v1 archive as empirical existence proof of the extraction loop; risk register frozen). Technical/theoretical feasibility, not cost, per Prof. Pax's mandate.
- OBJECTIONS:  PASS — Exchange 5 (5 attacks) and Exchange 10 (3 asks) answered structurally in Exchanges 6, 8, 11 (vocabulary fix, within-model rescue, two-tier frozen gates, transfer demoted to measured prediction, Chi scope sentence + direction diagnostic, length-stratified check, no-regression clause, confidence stratification). Exchange 15: Rex closes ledger — "no remaining design objections" — with permanent caveats R1–R4 recorded with mitigations.
- All personas spoke: YES — Dr. Nova (1,7), Prof. Vera (2,8,13), Prof. Pax (3,9,14), Dr. Sage (4,12), Prof. Rex (5,10,15), Dr. Ally (6,11). Genuine disagreement present (Rex Exchanges 5/10 attacks; Vera Exchange 2 kill-condition demand; Pax Exchange 3 instrument challenge).
- Exchange count: 15 ≥ min_exchanges (15). Not converged early.
- Verdict: **CONVERGED**
