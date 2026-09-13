# Experimental Setup

Our evaluation tests five pre-registered predictions (P1-P5) using Jiang et al.'s 348-defect corpus and prospective trial simulation. All experimental protocols were pre-specified in our verification plan to prevent p-hacking and selective reporting.

## Research Questions

We structure our experiments around five falsifiable predictions:

**P1 (Contractability):** ≥40% of environment-stage API defects from Jiang et al.'s corpus are expressible as version-stable, ≤10-second executable invariants. *Rationale*: Without sufficient contractability, the entire approach becomes impractical.

**P2 (Marginal Detection):** Combined contracts (structural + metamorphic + composition) uniquely detect ≥25% more environment-stage API defects than CI-only baseline, before training begins. *Rationale*: Demonstrates marginal value beyond existing best practices.

**P3 (Lifecycle Shift):** Median time-to-first-failure reduces by ≥5 hours with contracts versus CI-only. *Rationale*: Validates that early detection translates to practical time savings.

**P4 (Version Stability):** False-positive rate <5% across ±2 minor library releases. *Rationale*: Ensures contracts survive real-world version drift without brittleness.

**P5 (Cross-Repo Reusability):** Same contract library applies to ≥3/5 distinct repositories using identical library versions without modification. *Rationale*: Validates library-level abstraction claim versus repo-specific tests.

## Defect Corpus and Baselines

### Dataset: Jiang et al. 348-Defect Corpus

We use the publicly available defect corpus from Jiang et al. [1], comprising 348 real bugs from 255 PyTorch-based repositories with ≥1K GitHub stars. The corpus includes issue descriptions, reproduction steps, git commit references, and manual defect categorization. We filter for environment-stage API defects (N=175 after filtering) defined as defects that (1) surface before model convergence analysis begins, (2) involve external library interfaces, and (3) are not training hyperparameter tuning issues.

**Corpus Statistics:**
- Repositories: 255 (computer vision: 68%, NLP: 22%, RL: 7%, other: 3%)
- Median repository maturity: 2.3K stars, 150 closed issues
- Defect discovery: 58% reported by re-users adapting code, 23% by original authors, 19% by code reviewers

**Why This Corpus:** Jiang et al.'s dataset provides ecological validity—these are real defects encountered in production ML workflows, not synthetic test cases. The corpus size (N=348) enables statistical power for detecting 25% effect sizes with 80% power at α=0.05 [power analysis omitted for space].

### Baseline Methods

We compare against three baselines representing current practice and adversarial alternatives:

**No-CI (Control):** Version pinning only (pip freeze, requirements.txt) with no automated testing. Mirrors 75% of ML repositories per Wolter et al. [2]. Detection occurs when researchers manually run code and observe failures.

**CI-Only (Best Practice):** pytest integration tests + version pinning, executed via GitHub Actions on every pull request. Represents current best practice for well-maintained repositories.

**Execution-Only (Adversarial):** Import all modules and execute one minimal forward pass per API function. Catches obvious crashes and import errors but does not validate invariants. Designed to stress-test whether contracts provide marginal value beyond "just run the code once."

## Experimental Design by Prediction

### P1: Contractability Measurement (h-e1)

**Protocol:** Blinded retrospective coding with inter-rater reliability check.

**Procedure:**
1. Two independent coders (blinded to contractability hypothesis) apply 3-question filter to each defect:
   - Q1: Does library documentation specify an invariant that, if validated, would detect this defect?
   - Q2: Can this invariant be evaluated in ≤10 seconds on consumer hardware (no GPU cluster)?
   - Q3: Is this invariant version-stable across ±2 minor library releases (check release notes)?

2. Defects passing all three questions are labeled "contractable" and stratified by type:
   - Structural: Shape, dtype, device constraints
   - Metamorphic: Mathematical properties (probability sums, identity relations)
   - Composition: Cross-library binding consistency

3. Calculate contractability rate with 95% Wilson score confidence interval.

4. Measure inter-rater agreement via Cohen's kappa (threshold: κ ≥ 0.7 for acceptable reliability).

**Success Criterion:** Contractability rate ≥40% with CI lower bound >35%.

**Falsification:** If contractability <40%, we conclude that library documentation is insufficient for automatic contract generation, and pivot to structural-only contracts with reduced scope claims.

### P2: Marginal Detection (h-c1)

**Protocol:** Full-corpus evaluation with McNemar's test for paired proportions.

**Procedure:**
1. Implement contracts for all contractable defects from P1.
2. For each defect, record detection status under four conditions:
   - No-CI: Does defect surface without intervention?
   - CI-Only: Do existing integration tests catch it?
   - Execution-Only: Does minimal forward pass catch it?
   - Contracts: Do our contracts catch it?

3. Construct Venn diagram showing exclusive and overlapping detection across methods.

4. Calculate marginal detection:
   - contracts_exclusive = defects caught by contracts but NOT by CI
   - marginal_rate = contracts_exclusive / (CI_detected + contracts_exclusive)

5. Test significance via McNemar's test (paired proportions, α=0.05).

**Success Criterion:** Marginal detection ≥25%, McNemar p<0.05, demonstrating that contracts provide value beyond current best practices.

**Falsification:** If marginal detection <15%, we conclude that contracts primarily automate existing testing practices without novel detection capability.

### P3: Lifecycle Shift (h-m4)

**Protocol:** Prospective trial simulation with time-to-first-failure (TTFF) measurement.

**Procedure:**
1. Simulate 100 pull requests (50 control: CI-only, 50 treatment: CI + contracts), stratified by repository maturity and defect complexity.

2. For each PR, inject one defect from Jiang et al.'s corpus at a random commit.

3. Measure TTFF as hours from commit timestamp to first failure signal:
   - CI-only: Time until pytest integration test fails OR researcher manually reports issue
   - CI + contracts: Time until contract validation fails (environment-setup) OR pytest fails (if contract missed it)

4. For defects undetected at environment-stage, use Jiang et al.'s reported discovery times (median: 10.08 hours for training-stage defects).

5. Compare TTFF distributions via Mann-Whitney U test (non-parametric, handles skewed distributions).

**Success Criterion:** Median TTFF reduction ≥5 hours, Mann-Whitney p<0.05.

**Falsification:** If lifecycle shift <3 hours, we conclude that contracts do not provide sufficient practical time savings to justify adoption friction.

**Note on Simulation:** We use simulated PRs rather than live GitHub deployments for two reasons: (1) prospective live trials require 6-12 months to accumulate sufficient defects, exceeding review timelines, and (2) ethical constraints prevent injecting defects into production repositories. We validate simulation fidelity via retrospective analysis (see Section 5.3) showing 3.75-hour observed TTFF reduction on historical data.

### P4: Version Stability (h-c4)

**Protocol:** Version-transition benchmark across real library updates.

**Procedure:**
1. Construct benchmark of 100 test cases spanning 20 PyTorch/HuggingFace version transitions (±2 minor releases from reference version).

2. Each test case includes:
   - A code snippet exercising a specific API (e.g., `model.forward()`, `tokenizer.encode()`)
   - Ground truth: "should pass" (valid usage) or "should fail" (known breaking change documented in release notes)

3. Execute all contracts on all version combinations, recording false positives (contract fails on valid usage) and false negatives (contract passes on breaking change).

4. Calculate FPR = false_positives / (false_positives + true_negatives), with 95% Wilson CI.

**Success Criterion:** FPR <5% with CI upper bound <8%.

**Falsification:** If FPR >5%, contracts are too brittle for practical deployment under version drift.

### P5: Cross-Repo Reusability (h-c2)

**Protocol:** Deploy identical contract library to multiple repositories, measure applicability.

**Procedure:**
1. Select 5 computer vision repositories (ResNet fine-tuning, YOLO object detection, SegFormer segmentation, CLIP zero-shot, Vision Transformer classification) using PyTorch 1.12 + torchvision 0.13.

2. Deploy same contract library (PyTorch structural + metamorphic contracts, no repo-specific customization) to all 5 repositories.

3. Run environment-setup validation, recording:
   - Contracts applicable without modification (success)
   - Contracts require repo-specific adjustments (partial success)
   - Contracts inapplicable due to missing library coverage (failure)

4. Calculate applicability rate = repos_applicable / total_repos.

**Success Criterion:** ≥3/5 repositories use contracts without modification.

**Falsification:** If <3/5, contracts are not genuinely library-level abstractions but rather repo-specific tests in disguise.

## Evaluation Metrics

| Metric | Definition | Interpretation |
|--------|------------|----------------|
| **Contractability Rate** | % defects expressible as contracts | Feasibility of approach |
| **Detection Rate** | % defects caught by method | Absolute performance |
| **Marginal Detection** | % defects caught exclusively by contracts | Value beyond baselines |
| **Time-to-First-Failure (TTFF)** | Hours from commit to failure detection | Practical time savings |
| **False Positive Rate** | % false alarms on valid usage | Brittleness measure |
| **Applicability Rate** | % repos using contracts unchanged | Reusability measure |

## Ethical Considerations

All experiments use publicly available defect data (Jiang et al.) or simulated environments. No live defects were injected into production repositories. Retrospective analysis (Section 5.3) uses only public GitHub data (commit timestamps, CI logs) from repositories with permissive licenses (MIT, Apache 2.0).

---

**References (Section 4 only - full list in Section 7)**

[1] Jiang et al. (2023). An Empirical Study of Bugs in PyTorch-Based Deep Learning Systems.  
[2] Wolter et al. (2025). Reproducibility Practices in Machine Learning Research.
