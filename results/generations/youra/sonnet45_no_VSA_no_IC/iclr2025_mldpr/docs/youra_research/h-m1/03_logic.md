# Logic Specification: h-m1 Friction Features Lower Entry Cost

**Date:** 2026-08-19  
**Hypothesis ID:** h-m1  
**Type:** MECHANISM  
**Tier:** 1

---

## 1. Overview

Core logic components for h-m1 validation pipeline:
1. **Upload Method Classification:** Heuristic-based detector (7 signals → binary label)
2. **Metadata Parsing:** 6-field presence detection (regex + keyword matching, reuses h-e1 rules)
3. **Statistical Validation:** t-test with normality/variance checks, fallback to non-parametric
4. **Pilot Validation:** Manual review accuracy calculation (classification + parsing)
5. **Gate Decision:** Threshold-based PASS/FAIL logic

---

## 2. Upload Method Classification Logic

### 2.1 Input/Output Contract

**Input:**
```python
dataset_id: str  # HuggingFace dataset identifier (e.g., "squad", "glue")
```

**Output:**
```python
UploadClassification(
    dataset_id: str,
    upload_method: Literal["API", "MANUAL", "AMBIGUOUS"],
    confidence: int,  # 0-7, count of matching signals
    matched_signals: list[str]  # Signal names that fired
)
```

### 2.2 Signal Detection Functions

**Signal 1: Commit User-Agent (API)**
```python
def detect_commit_user_agent(dataset_id: str) -> bool:
    """
    Check if commit history contains huggingface_hub user-agent.
    
    API: HfApi().list_repo_commits(repo_id=dataset_id, repo_type="dataset")
    Returns: True if any commit has user-agent containing "huggingface_hub"
    """
    commits = fetch_commit_history(dataset_id)
    for commit in commits:
        if "huggingface_hub" in commit.get("user_agent", "").lower():
            return True
    return False
```

**Signal 2: Commit Message Pattern (API)**
```python
def detect_generic_commit_messages(dataset_id: str) -> bool:
    """
    Check if commit messages are generic (automated) vs custom prose.
    
    Generic patterns: ["Upload dataset", "Update dataset", "Upload files", "Add data"]
    Returns: True if >50% of commits match generic patterns
    """
    commits = fetch_commit_history(dataset_id)
    generic_patterns = [
        r"^Upload dataset$",
        r"^Update dataset$",
        r"^Upload files$",
        r"^Add data$",
        r"^Upload .+ via \w+$"  # "Upload README.md via huggingface_hub"
    ]
    
    generic_count = 0
    for commit in commits:
        msg = commit.get("title", "")
        if any(re.match(pattern, msg, re.IGNORECASE) for pattern in generic_patterns):
            generic_count += 1
    
    return (generic_count / len(commits)) > 0.5 if commits else False
```

**Signal 3: File Structure (API)**
```python
def detect_dataset_info_json(dataset_id: str) -> bool:
    """
    Check if dataset_info.json exists in root directory.
    
    API: HfApi().list_repo_files(repo_id=dataset_id, repo_type="dataset")
    Returns: True if "dataset_info.json" in file list
    """
    files = fetch_file_list(dataset_id)
    return "dataset_info.json" in files
```

**Signal 4: README YAML Frontmatter (API)**
```python
def detect_auto_generated_yaml(readme_content: str) -> bool:
    """
    Check if README YAML frontmatter has auto-generated dataset_info block.
    
    Pattern: YAML block with standardized keys (features, splits, configs)
              in specific order, consistent formatting
    Returns: True if YAML matches auto-generation pattern
    """
    # Extract YAML frontmatter (between --- delimiters)
    yaml_match = re.search(r'^---\n(.*?)\n---', readme_content, re.DOTALL)
    if not yaml_match:
        return False
    
    yaml_text = yaml_match.group(1)
    
    # Auto-generated markers: "dataset_info:" block with standardized structure
    auto_markers = [
        r'dataset_info:\s*\n\s+features:',
        r'dataset_info:\s*\n\s+splits:',
        r'dataset_info:\s*\n\s+configs:'
    ]
    
    return any(re.search(marker, yaml_text) for marker in auto_markers)
```

**Signal 5: README Prose Style (MANUAL)**
```python
def detect_custom_prose(readme_content: str) -> bool:
    """
    Check if README has custom narrative text (vs template/minimal).
    
    Indicators:
    - Multiple paragraphs (>3)
    - Custom headings (not template defaults like "Dataset Card", "Data Fields")
    - Narrative sentences (>10 words, contains "we", "this dataset", "our")
    
    Returns: True if README appears manually written
    """
    # Remove YAML frontmatter
    content = re.sub(r'^---\n.*?\n---\n', '', readme_content, flags=re.DOTALL)
    
    # Count paragraphs (newline-separated text blocks)
    paragraphs = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 50]
    
    # Check for narrative markers
    narrative_patterns = [
        r'\b(we|our|this dataset|these data)\b',
        r'\b(collected|created|designed|built)\b',
        r'\b(contains|includes|comprises)\b'
    ]
    
    narrative_count = sum(
        1 for p in paragraphs
        if any(re.search(pattern, p, re.IGNORECASE) for pattern in narrative_patterns)
    )
    
    return len(paragraphs) >= 3 and narrative_count >= 2
```

**Signal 6: Drag-and-Drop File Pattern (MANUAL)**
```python
def detect_dragdrop_pattern(dataset_id: str) -> bool:
    """
    Check if multiple files were uploaded in short time window (<5 min).
    
    Indicates: Manual drag-and-drop upload (batch file selection)
    vs: Programmatic upload (typically single commit with all files)
    
    Returns: True if ≥3 files uploaded within 5-minute window
    """
    commits = fetch_commit_history(dataset_id)
    
    # Group commits by 5-minute windows
    time_windows = defaultdict(list)
    for commit in commits:
        timestamp = parse_timestamp(commit["date"])
        window_key = timestamp // 300  # 5-minute buckets
        time_windows[window_key].append(commit)
    
    # Check if any window has ≥3 file-add commits
    for window_commits in time_windows.values():
        file_adds = [c for c in window_commits if "add" in c.get("title", "").lower()]
        if len(file_adds) >= 3:
            return True
    
    return False
```

**Signal 7: Metadata UI Tags (MANUAL)**
```python
def detect_ui_tags(readme_content: str) -> bool:
    """
    Check if YAML tags field has web UI formatting patterns.
    
    Web UI pattern: tags as list with specific ordering (task_categories first,
                    then language, then license), with specific YAML formatting
    
    Returns: True if tags formatting matches web UI pattern
    """
    yaml_match = re.search(r'^---\n(.*?)\n---', readme_content, re.DOTALL)
    if not yaml_match:
        return False
    
    yaml_text = yaml_match.group(1)
    
    # Web UI ordering: task_categories, language, license (in that order)
    ui_ordering_pattern = r'task_categories:.*?\nlanguage:.*?\nlicense:'
    
    return bool(re.search(ui_ordering_pattern, yaml_text, re.DOTALL))
```

### 2.3 Classification Decision Logic

**Pseudo-code:**
```python
def classify_upload_method(dataset_id: str) -> UploadClassification:
    """
    Classify dataset upload method based on 7 heuristic signals.
    """
    # Fetch data (cached where possible)
    commits = fetch_commit_history(dataset_id)
    files = fetch_file_list(dataset_id)
    readme = fetch_readme(dataset_id)
    
    # Detect signals
    api_signals = [
        ("commit_user_agent", detect_commit_user_agent(dataset_id)),
        ("generic_commit_msgs", detect_generic_commit_messages(dataset_id)),
        ("dataset_info_json", detect_dataset_info_json(dataset_id)),
        ("auto_yaml", detect_auto_generated_yaml(readme))
    ]
    
    manual_signals = [
        ("custom_prose", detect_custom_prose(readme)),
        ("dragdrop_pattern", detect_dragdrop_pattern(dataset_id)),
        ("ui_tags", detect_ui_tags(readme))
    ]
    
    # Count matching signals
    api_count = sum(1 for _, fired in api_signals if fired)
    manual_count = sum(1 for _, fired in manual_signals if fired)
    confidence = api_count + manual_count
    
    # Collect matched signal names
    matched = [name for name, fired in api_signals + manual_signals if fired]
    
    # Classification logic
    if api_count >= 2 and manual_count == 0:
        upload_method = "API"
    elif manual_count >= 2 and api_count == 0:
        upload_method = "MANUAL"
    else:
        upload_method = "AMBIGUOUS"  # Mixed signals or insufficient evidence
    
    return UploadClassification(
        dataset_id=dataset_id,
        upload_method=upload_method,
        confidence=confidence,
        matched_signals=matched
    )
```

**Edge Cases:**
- No commit history available: Return AMBIGUOUS (confidence=0)
- README unavailable: Can still classify from commits + file structure (API signals only)
- Single commit (initial upload): Rely on file structure + README signals

---

## 3. Metadata Parsing Logic

### 3.1 Input/Output Contract

**Input:**
```python
readme_content: str  # Full README.md text
```

**Output:**
```python
FieldPresence(
    dependencies: int,        # 0 or 1
    version: int,             # 0 or 1
    data_source_url: int,     # 0 or 1
    preprocessing_code: int,  # 0 or 1
    license: int,             # 0 or 1
    collection_date: int      # 0 or 1
)
```

### 3.2 Field Parsing Functions (h-e1 validated rules)

**Field 1: Dependencies**
```python
def parse_dependencies(readme: str) -> int:
    """
    Detect presence of software dependencies.
    
    Patterns:
    - requirements.txt mention
    - pip install / conda install commands
    - Package names with version specifiers (e.g., "pandas>=1.0.0")
    
    Returns: 1 if any pattern matches, 0 otherwise
    """
    patterns = [
        r'requirements\.txt',
        r'pip install',
        r'conda install',
        r'\b[a-z_-]+[>=<]=\d+',  # package>=version
        r'dependencies:\s*\n\s+-'  # YAML dependencies list
    ]
    
    return 1 if any(re.search(p, readme, re.IGNORECASE) for p in patterns) else 0
```

**Field 2: Version**
```python
def parse_version(readme: str) -> int:
    """
    Detect presence of dataset version number or date-based version.
    
    Patterns:
    - Semantic versioning (v1.2.3, 2.0.1)
    - Date-based versions (2023-05-01, YYYY-MM-DD)
    - Version: header
    
    Returns: 1 if any pattern matches, 0 otherwise
    """
    patterns = [
        r'v?\d+\.\d+(\.\d+)?',  # v1.2.3 or 1.2
        r'\d{4}-\d{2}-\d{2}',   # 2023-05-01
        r'version:\s*\d+',       # version: 2
        r'##\s*Version'          # ## Version heading
    ]
    
    return 1 if any(re.search(p, readme) for p in patterns) else 0
```

**Field 3: Data Source URL**
```python
def parse_data_source_url(readme: str) -> int:
    """
    Detect presence of original data source URL.
    
    Patterns:
    - http/https URLs
    - Exclude GitHub/HuggingFace repository URLs (those are hosting, not original source)
    
    Returns: 1 if external URL found, 0 otherwise
    """
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, readme)
    
    # Filter out hosting platforms
    exclude_domains = ["github.com", "huggingface.co", "gitlab.com"]
    external_urls = [
        url for url in urls
        if not any(domain in url for domain in exclude_domains)
    ]
    
    return 1 if external_urls else 0
```

**Field 4: Preprocessing Code**
```python
def parse_preprocessing_code(readme: str) -> int:
    """
    Detect presence of preprocessing code or scripts.
    
    Patterns:
    - Code blocks >50 chars with programming keywords (def, import, function, library)
    - File extensions (.py, .R, .ipynb)
    - References to preprocessing scripts
    
    Returns: 1 if any pattern matches, 0 otherwise
    """
    # Extract code blocks (fenced with ``` or indented)
    code_blocks = re.findall(r'```.*?\n(.*?)```', readme, re.DOTALL)
    code_blocks += re.findall(r'(?:^|\n)((?:    .+\n)+)', readme)
    
    # Check for programming keywords in code blocks
    keywords = ['def ', 'import ', 'library(', 'require(', 'function', 'class ']
    has_code = any(
        len(block) > 50 and any(kw in block for kw in keywords)
        for block in code_blocks
    )
    
    # Check for script file references
    script_patterns = [r'\.py\b', r'\.R\b', r'\.ipynb\b', r'preprocess\.', r'preprocessing_']
    has_script_ref = any(re.search(p, readme) for p in script_patterns)
    
    return 1 if (has_code or has_script_ref) else 0
```

**Field 5: License**
```python
def parse_license(readme: str) -> int:
    """
    Detect presence of license identifier.
    
    Patterns:
    - Common license abbreviations (MIT, Apache, GPL, CC-BY, CC0, BSD)
    - YAML license field
    - License heading
    
    Returns: 1 if any pattern matches, 0 otherwise
    """
    license_patterns = [
        r'\b(MIT|Apache|GPL|BSD|CC-BY|CC0|CC-BY-SA|CC-BY-NC)\b',
        r'license:\s*[\w-]+',  # YAML license field
        r'##\s*License'         # ## License heading
    ]
    
    return 1 if any(re.search(p, readme, re.IGNORECASE) for p in license_patterns) else 0
```

**Field 6: Collection Date**
```python
def parse_collection_date(readme: str) -> int:
    """
    Detect presence of data collection date or time period.
    
    Patterns:
    - Date formats (YYYY-MM-DD, Month YYYY, YYYY)
    - Keywords: "collected on", "collected in", "data from"
    
    Returns: 1 if any pattern matches, 0 otherwise
    """
    date_patterns = [
        r'\d{4}-\d{2}-\d{2}',  # 2023-05-01
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}',  # May 2023
        r'\d{4}(?!\d)',  # 2023 (year alone, not part of longer number)
        r'collected (on|in|during)',
        r'data (from|collected|gathered)',
        r'##\s*Collection'  # ## Collection heading
    ]
    
    return 1 if any(re.search(p, readme, re.IGNORECASE) for p in date_patterns) else 0
```

### 3.3 Completeness Score Calculation

**Pseudo-code:**
```python
def calculate_completeness(field_presence: FieldPresence) -> float:
    """
    Calculate metadata completeness score as percentage.
    
    Formula: (sum of field presence) / 6 × 100
    
    Returns: Float in range [0.0, 100.0]
    """
    fields = [
        field_presence.dependencies,
        field_presence.version,
        field_presence.data_source_url,
        field_presence.preprocessing_code,
        field_presence.license,
        field_presence.collection_date
    ]
    
    completeness = (sum(fields) / 6.0) * 100.0
    return round(completeness, 1)  # 1 decimal place
```

**Examples:**
- All fields present: `[1,1,1,1,1,1]` → 100.0%
- Half fields: `[1,1,0,1,0,0]` → 50.0%
- No fields: `[0,0,0,0,0,0]` → 0.0%

---

## 4. Statistical Validation Logic

### 4.1 Input/Output Contract

**Input:**
```python
api_scores: np.ndarray     # Completeness scores for API-uploaded datasets
manual_scores: np.ndarray  # Completeness scores for manual-uploaded datasets
```

**Output:**
```python
StatisticalResults(
    p_value: float,
    cohen_d: float,
    mean_diff_pp: float,
    ci_lower: float,
    ci_upper: float,
    mean_api: float,
    mean_manual: float,
    std_api: float,
    std_manual: float,
    normality_api: bool,
    normality_manual: bool,
    equal_variance: bool,
    test_used: str  # "ttest_ind", "welch_ttest", "mann_whitney"
)
```

### 4.2 Normality Check

**Pseudo-code:**
```python
def check_normality(scores: np.ndarray, alpha: float = 0.05) -> bool:
    """
    Test if data follows normal distribution using Shapiro-Wilk test.
    
    H0: Data is normally distributed
    Returns: True if p > alpha (fail to reject H0, assume normality)
    """
    from scipy.stats import shapiro
    
    if len(scores) < 3:
        return False  # Shapiro-Wilk requires n ≥ 3
    
    stat, p_value = shapiro(scores)
    return p_value > alpha
```

### 4.3 Equal Variance Check

**Pseudo-code:**
```python
def check_equal_variance(scores1: np.ndarray, scores2: np.ndarray, alpha: float = 0.05) -> bool:
    """
    Test if two groups have equal variance using Levene's test.
    
    H0: Variances are equal
    Returns: True if p > alpha (fail to reject H0, assume equal variance)
    """
    from scipy.stats import levene
    
    stat, p_value = levene(scores1, scores2)
    return p_value > alpha
```

### 4.4 Test Selection & Execution

**Pseudo-code:**
```python
def run_statistical_test(api_scores: np.ndarray, manual_scores: np.ndarray) -> StatisticalResults:
    """
    Select and run appropriate statistical test based on data properties.
    
    Decision tree:
    1. Check normality (both groups)
    2. IF both normal: Check equal variance
       - IF equal variance: Standard t-test
       - ELSE: Welch's t-test
    3. IF either non-normal: Mann-Whitney U test
    """
    from scipy.stats import ttest_ind, mannwhitneyu
    
    # Normality checks
    normal_api = check_normality(api_scores)
    normal_manual = check_normality(manual_scores)
    both_normal = normal_api and normal_manual
    
    # Select test
    if both_normal:
        # Check equal variance
        equal_var = check_equal_variance(api_scores, manual_scores)
        
        if equal_var:
            # Standard independent samples t-test
            t_stat, p_value = ttest_ind(api_scores, manual_scores, equal_var=True)
            test_used = "ttest_ind"
        else:
            # Welch's t-test (unequal variance)
            t_stat, p_value = ttest_ind(api_scores, manual_scores, equal_var=False)
            test_used = "welch_ttest"
    else:
        # Non-parametric Mann-Whitney U test
        u_stat, p_value = mannwhitneyu(api_scores, manual_scores, alternative='two-sided')
        test_used = "mann_whitney"
    
    # Calculate effect size (Cohen's d)
    mean_api = np.mean(api_scores)
    mean_manual = np.mean(manual_scores)
    std_api = np.std(api_scores, ddof=1)
    std_manual = np.std(manual_scores, ddof=1)
    
    # Pooled standard deviation
    n_api = len(api_scores)
    n_manual = len(manual_scores)
    pooled_std = np.sqrt(((n_api - 1) * std_api**2 + (n_manual - 1) * std_manual**2) / (n_api + n_manual - 2))
    
    cohen_d = (mean_api - mean_manual) / pooled_std if pooled_std > 0 else 0.0
    mean_diff_pp = mean_api - mean_manual
    
    # 95% confidence interval (approximate for t-test, exact for Welch)
    from scipy.stats import t as t_dist
    df = n_api + n_manual - 2 if test_used == "ttest_ind" else None  # Welch df calculation omitted for brevity
    se = pooled_std * np.sqrt(1/n_api + 1/n_manual)
    t_critical = t_dist.ppf(0.975, df) if df else 1.96  # fallback to z-score if df unavailable
    ci_lower = mean_diff_pp - t_critical * se
    ci_upper = mean_diff_pp + t_critical * se
    
    return StatisticalResults(
        p_value=p_value,
        cohen_d=cohen_d,
        mean_diff_pp=mean_diff_pp,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        mean_api=mean_api,
        mean_manual=mean_manual,
        std_api=std_api,
        std_manual=std_manual,
        normality_api=normal_api,
        normality_manual=normal_manual,
        equal_variance=equal_var if both_normal else None,
        test_used=test_used
    )
```

### 4.5 Interpretation Logic

**Directional Check:**
```python
def check_direction(mean_api: float, mean_manual: float) -> bool:
    """Returns True if API > manual (predicted direction)"""
    return mean_api > mean_manual
```

**Significance Check:**
```python
def check_significance(p_value: float, alpha: float = 0.05) -> bool:
    """Returns True if p < alpha (statistically significant)"""
    return p_value < alpha
```

**Effect Size Check:**
```python
def check_effect_size(mean_diff_pp: float, threshold: float = 10.0) -> bool:
    """Returns True if absolute difference ≥ threshold (practical significance)"""
    return abs(mean_diff_pp) >= threshold
```

---

## 5. Pilot Validation Logic

### 5.1 Input/Output Contract

**Input:**
```python
automated_labels: pd.DataFrame  # Columns: dataset_id, upload_method, [6 field flags]
ground_truth: pd.DataFrame      # Same structure, manually reviewed
```

**Output:**
```python
ValidationMetrics(
    classification_accuracy: float,  # 0.0-1.0
    parsing_accuracy: float,         # 0.0-1.0
    classification_errors: list[str],  # Dataset IDs with misclassified upload method
    parsing_errors: list[tuple[str, str]]  # (dataset_id, field_name) with incorrect labels
)
```

### 5.2 Classification Accuracy Calculation

**Pseudo-code:**
```python
def calculate_classification_accuracy(automated: pd.DataFrame, ground_truth: pd.DataFrame) -> float:
    """
    Calculate upload method classification accuracy.
    
    Accuracy = (# correct classifications) / (total datasets)
    """
    merged = automated.merge(ground_truth, on="dataset_id", suffixes=("_auto", "_gt"))
    
    correct = (merged["upload_method_auto"] == merged["upload_method_gt"]).sum()
    total = len(merged)
    
    return correct / total if total > 0 else 0.0
```

**Error Analysis:**
```python
def identify_classification_errors(automated: pd.DataFrame, ground_truth: pd.DataFrame) -> list[str]:
    """
    Identify dataset IDs with incorrect upload method classification.
    """
    merged = automated.merge(ground_truth, on="dataset_id", suffixes=("_auto", "_gt"))
    
    errors = merged[merged["upload_method_auto"] != merged["upload_method_gt"]]
    return errors["dataset_id"].tolist()
```

### 5.3 Parsing Accuracy Calculation

**Pseudo-code:**
```python
def calculate_parsing_accuracy(automated: pd.DataFrame, ground_truth: pd.DataFrame) -> float:
    """
    Calculate field presence parsing accuracy across all 6 fields.
    
    Accuracy = (# correct field labels) / (total field labels)
    Total labels = 100 datasets × 6 fields = 600
    """
    fields = ["dependencies", "version", "data_source_url", "preprocessing_code", "license", "collection_date"]
    
    merged = automated.merge(ground_truth, on="dataset_id", suffixes=("_auto", "_gt"))
    
    correct_labels = 0
    total_labels = 0
    
    for field in fields:
        field_auto = f"{field}_auto"
        field_gt = f"{field}_gt"
        
        correct_labels += (merged[field_auto] == merged[field_gt]).sum()
        total_labels += len(merged)
    
    return correct_labels / total_labels if total_labels > 0 else 0.0
```

**Error Analysis:**
```python
def identify_parsing_errors(automated: pd.DataFrame, ground_truth: pd.DataFrame) -> list[tuple[str, str]]:
    """
    Identify (dataset_id, field_name) tuples with incorrect parsing.
    """
    fields = ["dependencies", "version", "data_source_url", "preprocessing_code", "license", "collection_date"]
    
    merged = automated.merge(ground_truth, on="dataset_id", suffixes=("_auto", "_gt"))
    
    errors = []
    for field in fields:
        field_auto = f"{field}_auto"
        field_gt = f"{field}_gt"
        
        mismatches = merged[merged[field_auto] != merged[field_gt]]
        for _, row in mismatches.iterrows():
            errors.append((row["dataset_id"], field))
    
    return errors
```

---

## 6. Gate Decision Logic

### 6.1 Input/Output Contract

**Input:**
```python
statistical_results: StatisticalResults
validation_metrics: ValidationMetrics
```

**Output:**
```python
GateDecision(
    gate_result: Literal["PASS", "FAIL"],
    rationale: str,
    primary_criterion_met: bool,
    validation_criteria_met: bool,
    effect_size_sufficient: bool
)
```

### 6.2 Decision Rules

**Pseudo-code:**
```python
def make_gate_decision(stats: StatisticalResults, validation: ValidationMetrics) -> GateDecision:
    """
    Determine PASS/FAIL for MUST_WORK gate based on success criteria.
    
    PRIMARY criteria (required for PASS):
    1. Direction confirmed: mean_api > mean_manual
    2. Statistical significance: p_value < 0.05
    
    VALIDATION criteria (required for PASS):
    3. Classification accuracy > 0.85
    4. Parsing accuracy > 0.90
    
    SECONDARY criteria (informational, not blocking):
    5. Effect size ≥ 10 percentage points
    """
    # Primary criterion: Direction + significance
    direction_ok = stats.mean_api > stats.mean_manual
    significance_ok = stats.p_value < 0.05
    primary_met = direction_ok and significance_ok
    
    # Validation criteria
    classification_ok = validation.classification_accuracy > 0.85
    parsing_ok = validation.parsing_accuracy > 0.90
    validation_met = classification_ok and parsing_ok
    
    # Secondary criterion (effect size)
    effect_size_sufficient = abs(stats.mean_diff_pp) >= 10.0
    
    # Gate decision
    if primary_met and validation_met:
        gate_result = "PASS"
        rationale = (
            f"Direction confirmed (μ_API={stats.mean_api:.1f}% > μ_manual={stats.mean_manual:.1f}%, "
            f"p={stats.p_value:.4f}). Validation thresholds met "
            f"(classification={validation.classification_accuracy:.2%}, "
            f"parsing={validation.parsing_accuracy:.2%})."
        )
        
        if effect_size_sufficient:
            rationale += f" Effect size substantial ({stats.mean_diff_pp:.1f}pp ≥ 10pp threshold)."
        else:
            rationale += f" NOTE: Effect size small ({stats.mean_diff_pp:.1f}pp < 10pp threshold)."
    
    elif not primary_met:
        gate_result = "FAIL"
        if not direction_ok:
            rationale = (
                f"Primary criterion FAILED: Reverse direction detected "
                f"(μ_API={stats.mean_api:.1f}% < μ_manual={stats.mean_manual:.1f}%). "
                f"Hypothesis prediction violated."
            )
        else:  # not significance_ok
            rationale = (
                f"Primary criterion FAILED: No statistically significant difference detected "
                f"(p={stats.p_value:.4f} ≥ 0.05). "
                f"Mean difference {stats.mean_diff_pp:.1f}pp is not significant."
            )
    
    else:  # not validation_met
        gate_result = "FAIL"
        validation_failures = []
        if not classification_ok:
            validation_failures.append(
                f"Classification accuracy {validation.classification_accuracy:.2%} ≤ 85%"
            )
        if not parsing_ok:
            validation_failures.append(
                f"Parsing accuracy {validation.parsing_accuracy:.2%} ≤ 90%"
            )
        
        rationale = (
            f"Validation criteria FAILED: {'; '.join(validation_failures)}. "
            f"Upload method classifier or metadata parser unreliable."
        )
    
    return GateDecision(
        gate_result=gate_result,
        rationale=rationale,
        primary_criterion_met=primary_met,
        validation_criteria_met=validation_met,
        effect_size_sufficient=effect_size_sufficient
    )
```

### 6.3 Next Steps Logic

**Pseudo-code:**
```python
def determine_next_steps(gate_decision: GateDecision) -> str:
    """
    Determine next actions based on gate result.
    """
    if gate_decision.gate_result == "PASS":
        return (
            "PASS: Proceed to h-m2 (cross-platform comparison). "
            "h-m1 mechanism validated — friction-reduction features lower entry cost."
        )
    else:
        # FAIL: Different responses based on failure mode
        if not gate_decision.primary_criterion_met:
            return (
                "FAIL: STOP verification plan (h-m2, h-m3 blocked). "
                "Causal mechanism claim unsupported. "
                "Reassess hypothesis: Consider alternative friction proxies (user surveys) "
                "or abandon friction-reduction mechanism."
            )
        else:  # Validation failure
            return (
                "FAIL: Refine upload method classifier or metadata parser. "
                "Re-run pilot validation until accuracy thresholds met. "
                "IF unable to reach thresholds: STOP, document tool limitation."
            )
```

---

## 7. Summary

**Logic Components:**
1. **Upload Method Classifier:** 7 heuristic signals → binary/ambiguous label (confidence-scored)
2. **Metadata Parser:** 6 regex-based field detectors (h-e1 rules) → binary presence vector → completeness %
3. **Statistical Analyzer:** Normality/variance checks → t-test/Welch/Mann-Whitney → p-value + Cohen's d
4. **Pilot Validator:** Manual review accuracy (classification >85%, parsing >90%)
5. **Gate Decider:** Primary (direction + p<0.05) + Validation → PASS/FAIL

**Key Design Decisions:**
- **Heuristic classifier:** Transparent, interpretable, no training data required
- **Reuse h-e1 parsing:** Validated rules (90%+ accuracy), no re-invention
- **Robust statistical tests:** Normality/variance checks with fallbacks (non-parametric)
- **Pilot validation gates:** Prevents garbage-in-garbage-out (classifier/parser errors)
- **Tiered success criteria:** Primary (MUST_WORK), Secondary (effect size), Validation (accuracy)

**Next Steps:** Configuration specification (03_config.md), Task breakdown (03_tasks.yaml)
