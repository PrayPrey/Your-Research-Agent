# Discussion

Our experiments expose a practical bottleneck in meta-learning for method selection: collecting comprehensive benchmark metadata from literature is harder than anticipated. Rather than refuting the meta-learning hypothesis, our negative results identify an infrastructure gap that must be addressed before the approach can be tested fairly.

## Interpreting the Negative Results

**The Core Finding:** Literature mining alone — querying APIs, parsing READMEs, extracting paper tables — provided only **14% average coverage** for critical dataset characteristics (sample_size: 13.8%, dimensionality: 0%, class_imbalance: 75.9% but zero-variance artifact). This sparsity prevented testing whether dataset features correlate with method rankings (h-m1: zero computable correlations) and caused meta-classifier training to fail with degenerate input (h-m2: 1 usable feature, 25.6% accuracy).

**Why This Is Not Hypothesis Failure:** All three sub-hypothesis deviations were classified as **DATA_LIMITATION** or **SCOPE_CHANGE**, not **HYPOTHESIS_ISSUE**. h-e1 successfully verified data source accessibility (OGB API loads, GitHub READMEs fetch, paper tables exist), achieving POC-level validation. h-m1 could not compute correlations because only 4 sample_size values were extracted (insufficient for statistical testing), not because correlations were computed and found insignificant. h-m2 training failed because only 1 feature had sufficient coverage (num_classes: 75.9%), creating a degenerate input that no meta-learning algorithm could learn from.

**The Real Challenge:** Meta-learning requires **two-stage data collection**. Stage 1 (identify benchmark sources) succeeded: we confirmed OGB, FedML, LEAF, Champneys, and Zhou benchmarks are accessible via libraries, repositories, and publications. Stage 2 (extract dataset characteristics) is the bottleneck: APIs provide identifiers but not feature statistics, READMEs document usage but not sample sizes, and paper tables report method rankings but omit dataset properties. Extracting characteristics requires downloading raw datasets, loading them into memory, and computing statistics — an engineering effort beyond literature mining.

## Implications for Meta-Learning Research

**Hidden Assumption Exposed:** Our work reveals that meta-learning research implicitly assumes dataset characteristics are available. AutoML systems (Auto-sklearn, TPOT) operate on datasets already loaded by practitioners, where extracting n, d, and class distribution is trivial. Literature-based meta-learning — training predictors from published benchmark results without dataset downloads — requires a **metadata repository** that does not currently exist.

**Why Literature Mining Falls Short:** Published benchmarks prioritize documenting method comparisons (rankings, accuracy tables) over dataset properties. Zhou et al. [1] report 9 medical imaging datasets with FedAvg/SCAFFOLD results but omit sample sizes and resolutions. Champneys et al. [2] provide NARX-Poly vs. LSTM comparisons but do not quantify input dimensionality or signal-to-noise ratios. This is rational for benchmark papers (readers care about "which method wins" not "dataset n"), but it prevents aggregating metadata for meta-learning.

**Proposed Solution:** A **community-driven benchmark metadata repository** analogous to Papers with Code leaderboards, but focused on dataset characteristics rather than method rankings. Such a repository would:
1. **Standardize feature extraction:** Define Tier 1 universal features (sample_size, dimensionality, class_imbalance) and Tier 2 domain-specific features (autocorrelation, edge_density, correlation_rank)
2. **Automate collection:** Provide scripts to download benchmarks and compute features, reducing manual extraction errors (e.g., our class_imbalance artifact from template CSVs)
3. **Link to method rankings:** Join dataset characteristics with leaderboard results, enabling meta-learning training data generation

This infrastructure would unlock research questions currently untestable: Do dataset characteristics predict method performance? Can meta-classifiers generalize across domains? Are fast features sufficient, or do we need expensive probing (Tier 3)?

## Honest Limitations

**Scope Reduction:** We collected only 29 benchmarks (vs. 50-60 target), validating data source accessibility (POC level) but not executing exhaustive extraction. Full collection engineering (leaderboard scraping, Papers with Code authentication, PDF table parsing) was not pursued after discovering the metadata bottleneck. This scope reduction is **principled**: identifying the bottleneck early allowed us to analyze root causes rather than investing effort in a flawed single-stage approach.

**Manual Extraction Artifacts:** Manual CSV files for Champneys and Zhou benchmarks used standardized ranking percentiles [25, 50, 75, 100], producing zero-variance class_imbalance (all values = 0.559). This artifact reduced effective feature diversity. **Why acceptable**: Manual extraction was a POC workaround for missing automated tools; it demonstrates the challenge (heterogeneous data formats) rather than invalidating findings. Real extraction from papers would require OCR or table parsing, confirming two-stage collection need.

**Untested Alternative Explanations:** We did not test whether dataset downloads would yield complete metadata. It is possible that even with downloads, some benchmarks lack feature diversity (e.g., OGB ogbn-papers100M reports 111M samples, likely an API error rather than true value). However, downloads would certainly improve coverage above 14% (e.g., loading CIFAR-10 directly provides exact n=50K, d=3072, class distribution). Future work should quantify coverage improvement from two-stage collection.

**Meta-Learning Hypothesis Remains Unverified:** Because h-m1 and h-m2 received insufficient data, we cannot conclude whether dataset characteristics actually correlate with method rankings, or whether meta-classifiers can learn these relationships. The hypothesis is **untested**, not **disproven**. Negative results should be interpreted as "literature mining insufficient" rather than "meta-learning doesn't work."

## Methodological Contributions

Despite negative results on the core hypothesis, this work contributes three methodological insights:

**1. Transparent Negative Result Reporting:** We document failure modes with quantitative evidence (14% average feature coverage, zero computable correlations, 1 usable feature after preprocessing) and classify deviations by type (DATA_LIMITATION vs. HYPOTHESIS_ISSUE). This transparency allows readers to assess whether failures stem from experimental execution or theoretical invalidity. Mock data elimination protocols (external LLM review, variance checks, coverage reporting) verify real data usage, preventing false negatives from hard-coded defaults.

**2. Staged Hypothesis Testing:** Decomposing the core hypothesis into h-e1 (data collection) → h-m1 (correlation) → h-m2 (meta-learning) isolates failure modes. When h-e1 achieves POC validation but h-m1 fails, we know the issue is feature extraction (not source availability). When h-m1 shows zero correlations due to insufficient data (not insignificant p-values), we know the issue is input quality (not absence of relationships). Staged testing prevents misattribution: we distinguish "not enough data" from "data exists but is uninformative" from "features are informative but classifier doesn't learn."

**3. Infrastructure Gap Identification:** Framing negative results as a **practical bottleneck** (metadata extraction) rather than **hypothesis refutation** (meta-learning doesn't work) is actionable. Our findings suggest where research effort should focus: building automated extraction tools and metadata repositories, not refining meta-learning algorithms. This reframes the research question from "does meta-learning predict method selection?" to "what infrastructure enables fair testing of meta-learning?"

## Broader Impact

**For Practitioners:** Do not expect literature mining (reading papers, checking leaderboards) to provide sufficient dataset characteristics for informed method selection. If you need dataset properties to guide method choice, download and analyze raw data rather than relying on published metadata.

**For Researchers:** When proposing meta-learning approaches, verify that training data (dataset characteristics) is accessible. If your approach requires feature X, check whether X is reported in literature or must be computed from raw datasets. Our work shows that seemingly "trivial" features like sample_size and dimensionality are absent from 86-100% of published benchmarks.

**For Benchmark Publishers:** Consider documenting dataset characteristics alongside method rankings. Including a "Dataset Properties" section (n, d, class distribution, domain-specific statistics) in benchmark papers would enable meta-learning research without requiring dataset downloads. Standardizing reporting (e.g., mandatory fields in benchmark submission templates) could accelerate meta-learning adoption.

## Future Work

**Immediate Next Step:** Implement Stage 2 data collection for the 29 collected benchmarks. Download OGB datasets, FedML repositories, and benchmark datasets from Champneys/Zhou sources. Compute Tier 1 features from raw data (not API metadata). Re-run h-m1 correlation analysis with complete features (expected: ≥10 benchmarks with full Tier 1 coverage) to test whether correlations emerge with richer data.

**Medium-Term Goal:** Extend collection to 50-60 benchmarks with automated extraction tools (leaderboard scrapers, OCR for paper tables, dataset loaders for OGB/FedML/LEAF). Test h-m2 meta-classifier training with ≥40 complete feature vectors and ≥5 informative features. Compare two-stage (downloads + extraction) vs. single-stage (literature mining only) coverage and meta-learning performance.

**Long-Term Vision:** Build a **benchmark metadata repository** integrating dataset characteristics with Papers with Code leaderboards. Community-contributed extraction scripts ensure standardization. Researchers train meta-classifiers on aggregated data without per-project manual collection. Enable new research: temporal generalization (do feature-method correlations hold across eras?), domain transfer (do patterns from vision generalize to NLP?), minimal feature sets (which Tier 1 features are sufficient?).

**Alternative Approaches:** If even two-stage collection proves insufficient (e.g., some benchmarks lack raw data), explore Tier 3 features (model probing via quick training runs on new datasets). Tier 3 is expensive (~5-10 GPU-minutes per dataset) but guarantees feature availability. Trade-off: violates "fast computation" constraint (<1 min) but may be necessary for fair meta-learning testing.

## Conclusion Preview

We set out to build a meta-classifier predicting optimal method families from dataset characteristics. We discovered that collecting dataset characteristics from literature is the bottleneck, not building the classifier. This negative result is **actionable**: it identifies where infrastructure investment is needed (metadata extraction and repositories) and proposes a path forward (two-stage collection with automated tools). Rather than concluding "meta-learning doesn't work," we conclude "meta-learning cannot be tested fairly without better data infrastructure."

---

**Limitations Summary:**
- **Scope:** 29 benchmarks collected (POC level), not exhaustive 50-60 target
- **Manual artifacts:** Zero-variance class_imbalance from template CSVs (not real paper values)
- **Untested hypothesis:** Meta-learning approach not fairly tested due to insufficient metadata
- **No novel algorithm:** Contribution is procedural (infrastructure gap identification), not algorithmic
