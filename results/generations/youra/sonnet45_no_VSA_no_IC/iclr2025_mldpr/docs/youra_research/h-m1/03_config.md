# Configuration Specification: h-m1 Friction Features Lower Entry Cost

**Date:** 2026-08-19  
**Hypothesis ID:** h-m1  
**Type:** MECHANISM  
**Tier:** 1

---

## 1. Dataset Configuration

### 1.1 Discovery Parameters

```yaml
discovery:
  initial_query_size: 5000           # Target number of dataset IDs to fetch from HuggingFace API
  filters:
    has_readme: true                  # Require README.md present
    created_before: "2026-08-19"      # Temporal cutoff (exclude datasets created after today)
  expected_candidates: 3000           # Expected number after filtering (informational)
  output_path: "data/h-m1/hf_dataset_ids.csv"
```

### 1.2 Stratified Sampling Parameters

```yaml
sampling:
  sample_size_per_group: 1000         # Target: 1,000 API uploads + 1,000 manual uploads
  minimum_per_group: 500              # Minimum acceptable sample size per group (fallback threshold)
  random_seed: 42                     # Fixed seed for reproducibility
  exclude_ambiguous: true             # Exclude datasets with AMBIGUOUS upload method classification
  output_path: "data/h-m1/sampled_ids.txt"
```

### 1.3 Pilot Validation Parameters

```yaml
pilot_validation:
  total_sample_size: 100              # Total datasets for manual review
  stratification:
    api_samples: 50                   # Number of API-uploaded datasets
    manual_samples: 50                # Number of manual-uploaded datasets
  random_seed: 42                     # Fixed seed for reproducibility
  output_path: "data/h-m1/validation_pilot_100.csv"
```

---

## 2. Upload Method Classification Configuration

### 2.1 Heuristic Signal Weights

```yaml
upload_classification:
  signals:
    # API upload signals
    commit_user_agent:
      pattern: "huggingface_hub"
      case_sensitive: false
      weight: strong                  # Most reliable indicator
    
    generic_commit_messages:
      patterns:
        - "^Upload dataset$"
        - "^Update dataset$"
        - "^Upload files$"
        - "^Add data$"
        - "^Upload .+ via \\w+$"
      threshold: 0.5                  # >50% of commits must match
      weight: medium
    
    dataset_info_json:
      filename: "dataset_info.json"
      location: "root"                # Must be in root directory
      weight: strong
    
    auto_generated_yaml:
      markers:
        - "dataset_info:\\s*\\n\\s+features:"
        - "dataset_info:\\s*\\n\\s+splits:"
        - "dataset_info:\\s*\\n\\s+configs:"
      weight: medium
    
    # Manual upload signals
    custom_prose:
      min_paragraphs: 3
      min_narrative_paragraphs: 2
      narrative_patterns:
        - "\\b(we|our|this dataset|these data)\\b"
        - "\\b(collected|created|designed|built)\\b"
        - "\\b(contains|includes|comprises)\\b"
      weight: medium
    
    dragdrop_pattern:
      time_window_seconds: 300        # 5-minute window
      min_file_adds: 3                # ≥3 file uploads in window
      weight: weak
    
    ui_tags:
      expected_order: ["task_categories", "language", "license"]
      weight: medium
  
  # Classification logic
  decision_rules:
    api_threshold: 2                  # ≥2 API signals with 0 manual signals → API
    manual_threshold: 2               # ≥2 manual signals with 0 API signals → MANUAL
    ambiguous_conditions:
      - "api_count > 0 AND manual_count > 0"
      - "api_count + manual_count < 2"
  
  output_path: "data/h-m1/upload_classified.csv"
```

---

## 3. Metadata Parsing Configuration

### 3.1 Field Parsing Rules (h-e1 validated)

```yaml
metadata_parsing:
  target_fields: 6
  
  fields:
    dependencies:
      patterns:
        - "requirements\\.txt"
        - "pip install"
        - "conda install"
        - "\\b[a-z_-]+[>=<]=\\d+"
        - "dependencies:\\s*\\n\\s+-"
      case_sensitive: false
      presence_threshold: "match_found"  # Binary: 1 if any pattern matches, 0 otherwise
    
    version:
      patterns:
        - "v?\\d+\\.\\d+(\\.\\d+)?"
        - "\\d{4}-\\d{2}-\\d{2}"
        - "version:\\s*\\d+"
        - "##\\s*Version"
      case_sensitive: false
      presence_threshold: "match_found"
    
    data_source_url:
      patterns:
        - "https?://[^\\s]+"
      exclude_domains:
        - "github.com"
        - "huggingface.co"
        - "gitlab.com"
      presence_threshold: "match_found"
    
    preprocessing_code:
      code_block_min_length: 50
      programming_keywords:
        - "def "
        - "import "
        - "library("
        - "require("
        - "function"
        - "class "
      file_extensions:
        - ".py"
        - ".R"
        - ".ipynb"
      presence_threshold: "code_block_or_file_ref"
    
    license:
      patterns:
        - "\\b(MIT|Apache|GPL|BSD|CC-BY|CC0|CC-BY-SA|CC-BY-NC)\\b"
        - "license:\\s*[\\w-]+"
        - "##\\s*License"
      case_sensitive: false
      presence_threshold: "match_found"
    
    collection_date:
      patterns:
        - "\\d{4}-\\d{2}-\\d{2}"
        - "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\\s+\\d{4}"
        - "\\d{4}(?!\\d)"
        - "collected (on|in|during)"
        - "data (from|collected|gathered)"
        - "##\\s*Collection"
      case_sensitive: false
      presence_threshold: "match_found"
  
  # Completeness score calculation
  completeness_formula: "sum(field_presence) / 6 * 100"  # Percentage (0-100)
  decimal_places: 1
  
  output_path: "data/h-m1/completeness_scores.csv"
```

---

## 4. Statistical Analysis Configuration

### 4.1 Hypothesis Testing Parameters

```yaml
statistical_analysis:
  # Test selection
  normality_test:
    method: "shapiro_wilk"
    alpha: 0.05                       # p > 0.05 → assume normality
    min_sample_size: 3                # Minimum n for Shapiro-Wilk
  
  equal_variance_test:
    method: "levene"
    alpha: 0.05                       # p > 0.05 → assume equal variance
  
  primary_test:
    parametric:
      equal_variance: "ttest_ind"     # scipy.stats.ttest_ind(equal_var=True)
      unequal_variance: "welch_ttest" # scipy.stats.ttest_ind(equal_var=False)
    nonparametric: "mann_whitney"     # scipy.stats.mannwhitneyu
  
  # Significance thresholds
  alpha: 0.05                         # Two-tailed significance level
  confidence_level: 0.95              # For confidence intervals
  
  # Effect size
  effect_size_metric: "cohen_d"       # Standardized mean difference
  pooled_std_formula: "sqrt(((n1-1)*s1^2 + (n2-1)*s2^2) / (n1+n2-2))"
  
  # Thresholds for interpretation
  thresholds:
    significance: 0.05                # p < 0.05 → statistically significant
    small_effect: 0.2                 # Cohen's d (informational)
    medium_effect: 0.5                # Cohen's d (informational)
    large_effect: 0.8                 # Cohen's d (informational)
    practical_significance_pp: 10.0   # Absolute percentage point difference
```

### 4.2 Outlier Detection (Informational Only)

```yaml
outlier_detection:
  enabled: true
  method: "z_score"
  threshold: 3.0                      # |z| > 3 → flag as outlier
  action: "flag_only"                 # Do NOT remove, only report in validation report
```

---

## 5. Pilot Validation Configuration

### 5.1 Validation Thresholds

```yaml
pilot_validation:
  thresholds:
    classification_accuracy: 0.85     # >85% upload method classification accuracy required
    parsing_accuracy: 0.90            # >90% field presence parsing accuracy required
  
  # Accuracy calculations
  classification_accuracy_formula: "sum(upload_method_match) / total_datasets"
  parsing_accuracy_formula: "sum(all_field_matches) / (total_datasets * 6)"  # 6 fields per dataset
  
  # Error analysis
  export_errors: true
  error_output_paths:
    classification: "data/h-m1/classification_errors.csv"
    parsing: "data/h-m1/parsing_errors.csv"
```

---

## 6. Gate Decision Configuration

### 6.1 Success Criteria

```yaml
gate_decision:
  criteria:
    primary:
      description: "Direction confirmed AND statistically significant"
      conditions:
        - "mean_api > mean_manual"
        - "p_value < 0.05"
      required: true                  # Must pass for PASS gate result
    
    validation:
      description: "Classification and parsing accuracy thresholds met"
      conditions:
        - "classification_accuracy > 0.85"
        - "parsing_accuracy > 0.90"
      required: true                  # Must pass for PASS gate result
    
    secondary:
      description: "Substantial effect size"
      conditions:
        - "abs(mean_diff_pp) >= 10.0"
      required: false                 # Informational only, not blocking
  
  # Gate result mapping
  pass_condition: "primary AND validation"
  fail_conditions:
    - "NOT primary"
    - "NOT validation"
  
  output_path: "docs/youra_research/h-m1/04_validation.md"
```

---

## 7. API & Rate Limit Configuration

### 7.1 HuggingFace API

```yaml
api:
  huggingface:
    base_url: "https://huggingface.co"
    api_key_env_var: "HUGGINGFACE_API_KEY"  # Optional, increases rate limit
    rate_limits:
      free_tier: 1000                 # requests/hour
      authenticated_tier: 10000       # requests/hour (with API key)
    
    retry_policy:
      max_retries: 5
      backoff_strategy: "exponential"
      base_delay_seconds: 1
      max_delay_seconds: 60
      retry_on_codes: [429, 500, 502, 503]
    
    timeout:
      connect_seconds: 10
      read_seconds: 30
    
    # Parallelization
    concurrency:
      max_workers: 10                 # Thread pool size
      semaphore_permits: 10           # Max concurrent requests
```

### 7.2 Performance Estimates

```yaml
performance:
  estimated_api_calls:
    discovery: 8000                   # 5,000 list + 3,000 metadata
    classification: 3000              # Commit history + file listings
    extraction: 2000                  # README fetch
    total: 13000
  
  estimated_runtime:
    free_tier_hours: 13               # 13,000 calls / 1,000 per hour
    authenticated_tier_hours: 1.3     # 13,000 calls / 10,000 per hour
  
  memory:
    peak_mb: 20
    disk_space_mb: 1
```

---

## 8. Output File Paths

### 8.1 Data Artifacts

```yaml
output_paths:
  discovery: "data/h-m1/hf_dataset_ids.csv"
  classification: "data/h-m1/upload_classified.csv"
  sampled_ids: "data/h-m1/sampled_ids.txt"
  completeness_scores: "data/h-m1/completeness_scores.csv"
  pilot_sample: "data/h-m1/validation_pilot_100.csv"
  classification_errors: "data/h-m1/classification_errors.csv"
  parsing_errors: "data/h-m1/parsing_errors.csv"
```

### 8.2 Reports & Documentation

```yaml
report_paths:
  validation_report: "docs/youra_research/h-m1/04_validation.md"
  analysis_notebook: "notebooks/h-m1_analysis.ipynb"
```

### 8.3 Intermediate Checkpoints

```yaml
checkpoints:
  enabled: true
  checkpoint_dir: "data/h-m1/checkpoints"
  files:
    - "discovery_checkpoint.json"
    - "classification_checkpoint.json"
    - "extraction_checkpoint.json"
  staleness_hours: 24                 # Re-run if checkpoint >24 hours old
```

---

## 9. Logging Configuration

### 9.1 Log Levels

```yaml
logging:
  level: "INFO"                       # DEBUG, INFO, WARNING, ERROR
  format: "[%(asctime)s] %(levelname)s: %(message)s"
  date_format: "%Y-%m-%d %H:%M:%S"
  
  handlers:
    console:
      enabled: true
      level: "INFO"
    
    file:
      enabled: true
      level: "DEBUG"
      path: "logs/h-m1_pipeline.log"
      max_bytes: 10485760             # 10 MB
      backup_count: 3                 # Keep 3 rotated logs
```

### 9.2 Progress Tracking

```yaml
progress:
  enabled: true
  update_frequency:
    discovery: 100                    # Log every 100 datasets
    classification: 50                # Log every 50 datasets
    extraction: 50                    # Log every 50 datasets
  
  format: "Processed {current} / {total} ({percentage:.1f}%). Mean completeness so far: {mean:.1f}%"
```

---

## 10. Environment Configuration

### 10.1 Python Dependencies

```yaml
dependencies:
  python_version: ">=3.9"
  packages:
    huggingface_hub: ">=0.25.0"
    datasets: ">=3.0.0"
    pandas: ">=2.0.0"
    numpy: ">=1.24.0"
    scipy: ">=1.10.0"
    matplotlib: ">=3.5.0"
    requests: ">=2.28.0"
  
  dev_packages:
    pytest: ">=7.0.0"
    black: ">=22.0.0"
    mypy: ">=1.0.0"
    jupyter: ">=1.0.0"
```

### 10.2 Execution Modes

```yaml
execution:
  default_mode: "full_pipeline"       # Run all phases sequentially
  
  modes:
    full_pipeline:
      phases: ["discovery", "classification", "sampling", "extraction", "pilot_export", "analysis"]
    
    resume_from_checkpoint:
      phases: ["auto_detect"]         # Detect latest checkpoint and resume
    
    phase_by_phase:
      phases: ["manual"]              # User specifies which phase to run
  
  # Validation flags
  skip_validation: false              # Set to true to skip pilot validation step (NOT RECOMMENDED)
  force_rerun: false                  # Set to true to ignore checkpoints and re-run all phases
```

---

## 11. Validation Report Template

### 11.1 Report Structure

```yaml
validation_report:
  sections:
    - title: "Hypothesis Statement"
      content: "Restate h-m1 mechanism claim"
    
    - title: "Data Summary"
      content: "Sample sizes, mean scores, distribution statistics"
    
    - title: "Statistical Results"
      content: "Test used, p-value, Cohen's d, mean difference, CI"
    
    - title: "Pilot Validation Results"
      content: "Classification accuracy, parsing accuracy, error analysis"
    
    - title: "Gate Decision"
      content: "PASS/FAIL, rationale, criteria checklist"
    
    - title: "Key Findings"
      content: "Interpretation (strong/moderate/weak support, null, reverse)"
    
    - title: "Next Steps"
      content: "IF PASS → h-m2; IF FAIL → stop/reassess"
  
  format: "markdown"
  include_visualizations: true
  visualization_types:
    - "distribution_comparison"       # Histograms of API vs manual completeness
    - "effect_size_chart"             # Cohen's d with confidence interval
    - "field_prevalence"              # Bar chart of field presence rates
```

---

## 12. Testing Configuration

### 12.1 Unit Test Targets

```yaml
testing:
  unit_tests:
    - "test_upload_classification"
    - "test_metadata_parsing"
    - "test_completeness_scoring"
    - "test_statistical_analysis"
    - "test_gate_decision"
  
  integration_tests:
    - "test_end_to_end_pipeline"
  
  test_data:
    path: "tests/h-m1/fixtures"
    sample_datasets:
      - dataset_id: "squad"
        upload_method: "API"
        expected_fields: [1, 1, 1, 1, 1, 1]
      - dataset_id: "glue"
        upload_method: "MANUAL"
        expected_fields: [1, 1, 0, 1, 0, 0]
```

---

## 13. Summary

**Configuration Highlights:**
- **Dataset:** 1,000 API + 1,000 manual uploads (min 500 per group), seed=42
- **Classification:** 7 heuristic signals (4 API, 3 manual), ≥2 threshold for label
- **Parsing:** 6 fields (h-e1 rules), binary presence, completeness = mean × 100
- **Statistical:** t-test (or Welch/Mann-Whitney fallback), α=0.05, effect size ≥10pp
- **Validation:** Pilot 100 samples (50/50 split), classification >85%, parsing >90%
- **Gate:** Primary (direction + p<0.05) + Validation → PASS/FAIL
- **API:** HuggingFace free tier (1k req/hr) or authenticated (10k req/hr), retry with backoff
- **Performance:** ~13k API calls, 1.3-13 hours runtime (authenticated/free), <20 MB RAM

**Next Steps:** Task breakdown (03_tasks.yaml), Implementation
