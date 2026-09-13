# Logic Design Document
# Hypothesis: H-E1 - Documentation Copilot Existence Test

**Version:** 1.0  
**Date:** 2026-04-15  
**Author:** Logic Agent (TEST mode)  
**Hypothesis ID:** h-e1  
**Hypothesis Type:** EXISTENCE (FOUNDATION)  
**Phase:** 3 - Implementation Planning  
**Budget:** 4 subtasks (from Epic E-2)

---

## 1. Codebase Analysis (Serena)

**Analysis Status:** GREEN-FIELD (No existing codebase)

**Foundation Hypothesis Context:**
- No base hypothesis to analyze
- No existing APIs to extend
- Clean slate implementation
- Standard Python class design patterns apply

**Applied Pattern:** Standard Python class-based architecture with type hints and docstrings

---

## 2. API Signatures

### 2.1 Core Classes

#### Class: `SuggestionGenerator`
**Module:** `src/copilot/generator.py`  
**Purpose:** Main engine for generating documentation suggestions

```python
from typing import Dict, List, Optional
from dataclasses import dataclass
import torch
from transformers import pipeline

@dataclass
class DatasetProperties:
    """Dataset metadata extracted from uploaded files."""
    dataset_type: str  # 'vision' | 'nlp' | 'tabular'
    file_formats: List[str]  # e.g., ['csv', 'json']
    num_samples: Optional[int]
    features: Dict[str, str]  # feature_name -> data_type
    distributions: Dict[str, Any]  # basic statistics
    metadata: Dict[str, Any]  # user-provided metadata

@dataclass
class Suggestion:
    """Generated suggestion with tracking metadata."""
    id: str
    text: str
    section_name: str
    dataset_type: str
    timestamp: float
    examples_used: List[str]  # IDs of examples used in prompt

class SuggestionGenerator:
    """
    LLM-based documentation suggestion generator using few-shot prompting.
    
    Applied: Few-Shot Prompting Pattern (Archon KB)
    """
    
    def __init__(
        self,
        model_name: str = "meta-llama/Llama-3-8B-Instruct",
        temperature: float = 0.7,
        max_length: int = 500,
        device: int = 0
    ):
        """
        Initialize suggestion generator.
        
        Args:
            model_name: HuggingFace model ID (instruction-tuned LLM)
            temperature: Sampling temperature (0.7 for balanced creativity)
            max_length: Max tokens to generate per suggestion
            device: GPU device ID (0 for first GPU, -1 for CPU)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_length = max_length
        self.device = device
        
        # Initialize transformers pipeline
        self.generator = pipeline(
            "text-generation",
            model=model_name,
            device=device if torch.cuda.is_available() else -1
        )
        
        self.corpus_manager = None  # Set via set_corpus()
        self.tracker = None  # Set via set_tracker()
    
    def set_corpus(self, corpus_manager: 'CorpusManager') -> None:
        """Inject corpus manager dependency."""
        self.corpus_manager = corpus_manager
    
    def set_tracker(self, tracker: 'SuggestionTracker') -> None:
        """Inject tracker dependency."""
        self.tracker = tracker
    
    def generate_suggestion(
        self,
        dataset_properties: DatasetProperties,
        section_name: str
    ) -> Suggestion:
        """
        Generate documentation suggestion for a specific template section.
        
        Args:
            dataset_properties: Extracted properties from uploaded dataset
            section_name: Template section (e.g., "Dataset Description")
        
        Returns:
            Suggestion object with generated text and metadata
        
        Raises:
            ValueError: If corpus_manager not set
            RuntimeError: If LLM inference fails
        """
        if not self.corpus_manager:
            raise ValueError("Corpus manager not set. Call set_corpus() first.")
        
        # Step 1: Select 3 relevant examples from corpus
        examples = self._select_examples(
            dataset_properties.dataset_type,
            section_name,
            k=3
        )
        
        # Step 2: Build few-shot prompt
        prompt = self._build_prompt(
            dataset_properties,
            section_name,
            examples
        )
        
        # Step 3: Generate suggestion via LLM
        output = self.generator(
            prompt,
            max_length=self.max_length,
            temperature=self.temperature,
            do_sample=True,
            top_p=0.95
        )
        
        suggestion_text = output[0]['generated_text']
        
        # Step 4: Create Suggestion object
        suggestion = Suggestion(
            id=self._generate_id(),
            text=suggestion_text,
            section_name=section_name,
            dataset_type=dataset_properties.dataset_type,
            timestamp=time.time(),
            examples_used=[e['id'] for e in examples]
        )
        
        # Step 5: Log to tracker if available
        if self.tracker:
            self.tracker.log_suggestion(suggestion)
        
        return suggestion
    
    def _select_examples(
        self,
        dataset_type: str,
        section_name: str,
        k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Select k most relevant examples from corpus.
        
        Args:
            dataset_type: 'vision' | 'nlp' | 'tabular'
            section_name: Template section name
            k: Number of examples to select (default 3)
        
        Returns:
            List of example dictionaries with 'id', 'content', 'metadata'
        """
        # Delegate to corpus manager
        return self.corpus_manager.get_examples(
            dataset_type=dataset_type,
            section=section_name,
            limit=k
        )
    
    def _build_prompt(
        self,
        properties: DatasetProperties,
        section_name: str,
        examples: List[Dict[str, Any]]
    ) -> str:
        """
        Build few-shot prompt with dataset properties and examples.
        
        Args:
            properties: Dataset metadata
            section_name: Target template section
            examples: List of 3 example dataset cards
        
        Returns:
            Formatted prompt string for LLM
        """
        prompt_parts = [
            "You are a documentation assistant. Generate a helpful suggestion for this dataset documentation.",
            "",
            f"Dataset Properties:",
            f"  Type: {properties.dataset_type}",
            f"  File formats: {', '.join(properties.file_formats)}",
            f"  Number of samples: {properties.num_samples or 'Unknown'}",
            f"  Features: {len(properties.features)} features",
            "",
            f"Template Section: {section_name}",
            "",
            "High-quality Examples:",
        ]
        
        # Add 3 examples
        for i, example in enumerate(examples, 1):
            prompt_parts.extend([
                f"",
                f"Example {i}:",
                f"{example['content'][:300]}...",  # Truncate for context length
            ])
        
        prompt_parts.extend([
            "",
            f"Generate a helpful suggestion for the '{section_name}' section:",
        ])
        
        return "\n".join(prompt_parts)
    
    def _generate_id(self) -> str:
        """Generate unique suggestion ID."""
        import uuid
        return f"sugg_{uuid.uuid4().hex[:12]}"
```

---

#### Class: `PropertyExtractor`
**Module:** `src/copilot/property_extractor.py`  
**Purpose:** Extract dataset properties from uploaded files

```python
from typing import Dict, List, Any, Optional
import pandas as pd
import json

class PropertyExtractor:
    """
    Extract dataset properties for suggestion generation.
    
    Applied: Dataset Introspection Pattern (Archon KB)
    """
    
    def extract(self, file_paths: List[str]) -> DatasetProperties:
        """
        Extract properties from dataset files.
        
        Args:
            file_paths: List of uploaded file paths
        
        Returns:
            DatasetProperties object with extracted metadata
        
        Raises:
            ValueError: If files cannot be parsed
        """
        # Detect file formats
        file_formats = self._detect_formats(file_paths)
        
        # Infer dataset type (vision/NLP/tabular)
        dataset_type = self._infer_type(file_paths, file_formats)
        
        # Extract features and distributions
        features, distributions = self._analyze_data(
            file_paths[0],  # Primary data file
            file_formats[0]
        )
        
        # Count samples
        num_samples = self._count_samples(file_paths[0], file_formats[0])
        
        return DatasetProperties(
            dataset_type=dataset_type,
            file_formats=file_formats,
            num_samples=num_samples,
            features=features,
            distributions=distributions,
            metadata={}
        )
    
    def _detect_formats(self, file_paths: List[str]) -> List[str]:
        """Detect file formats from extensions."""
        return [path.split('.')[-1].lower() for path in file_paths]
    
    def _infer_type(
        self,
        file_paths: List[str],
        file_formats: List[str]
    ) -> str:
        """
        Infer dataset type from files.
        
        Returns:
            'vision' | 'nlp' | 'tabular'
        """
        # Image formats → vision
        image_formats = {'jpg', 'jpeg', 'png', 'bmp', 'tiff'}
        if any(fmt in image_formats for fmt in file_formats):
            return 'vision'
        
        # Text formats → NLP
        text_formats = {'txt', 'json', 'jsonl'}
        if any(fmt in text_formats for fmt in file_formats):
            # Heuristic: check for text content
            return 'nlp'
        
        # Default: tabular
        return 'tabular'
    
    def _analyze_data(
        self,
        file_path: str,
        file_format: str
    ) -> tuple[Dict[str, str], Dict[str, Any]]:
        """
        Analyze data file for features and distributions.
        
        Returns:
            (features_dict, distributions_dict)
        """
        if file_format == 'csv':
            df = pd.read_csv(file_path, nrows=1000)  # Sample for speed
            features = {col: str(df[col].dtype) for col in df.columns}
            distributions = {
                col: {
                    'mean': float(df[col].mean()) if pd.api.types.is_numeric_dtype(df[col]) else None,
                    'std': float(df[col].std()) if pd.api.types.is_numeric_dtype(df[col]) else None,
                    'unique': int(df[col].nunique())
                }
                for col in df.columns
            }
            return features, distributions
        
        # Fallback for other formats
        return {}, {}
    
    def _count_samples(self, file_path: str, file_format: str) -> Optional[int]:
        """Count number of samples in dataset."""
        if file_format == 'csv':
            return sum(1 for _ in open(file_path)) - 1  # Exclude header
        return None
```

---

#### Class: `SuggestionTracker`
**Module:** `src/tracking/tracker.py`  
**Purpose:** Track user interactions and calculate acceptance rates

```python
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import json
import time

@dataclass
class InteractionLog:
    """Single user interaction with a suggestion."""
    suggestion_id: str
    text: str
    section_name: str
    dataset_type: str
    timestamp: float
    status: str  # 'pending' | 'accepted' | 'rejected' | 'modified'
    modified_text: Optional[str] = None
    user_id: Optional[str] = None
    time_to_decision: Optional[float] = None

class SuggestionTracker:
    """
    Track suggestions and user interactions for acceptance rate calculation.
    
    Applied: User Interaction Logging Pattern (Archon KB - GitHub Copilot)
    """
    
    def __init__(self, log_dir: str = "data/logs/interactions"):
        """
        Initialize suggestion tracker.
        
        Args:
            log_dir: Directory to store interaction logs
        """
        self.log_dir = log_dir
        self.suggestions: List[InteractionLog] = []
        self._ensure_log_dir()
    
    def _ensure_log_dir(self) -> None:
        """Create log directory if it doesn't exist."""
        import os
        os.makedirs(self.log_dir, exist_ok=True)
    
    def log_suggestion(self, suggestion: Suggestion, user_id: Optional[str] = None) -> None:
        """
        Log a generated suggestion.
        
        Args:
            suggestion: Suggestion object from generator
            user_id: Optional user identifier
        """
        log = InteractionLog(
            suggestion_id=suggestion.id,
            text=suggestion.text,
            section_name=suggestion.section_name,
            dataset_type=suggestion.dataset_type,
            timestamp=suggestion.timestamp,
            status='pending',
            user_id=user_id
        )
        self.suggestions.append(log)
    
    def log_user_action(
        self,
        suggestion_id: str,
        action: str,
        modified_text: Optional[str] = None
    ) -> None:
        """
        Record user's response to a suggestion.
        
        Args:
            suggestion_id: ID of the suggestion
            action: 'accepted' | 'rejected' | 'modified'
            modified_text: If action='modified', the edited version
        
        Raises:
            ValueError: If suggestion_id not found or invalid action
        """
        if action not in {'accepted', 'rejected', 'modified'}:
            raise ValueError(f"Invalid action: {action}")
        
        for log in self.suggestions:
            if log.suggestion_id == suggestion_id:
                log.status = action
                log.modified_text = modified_text
                log.time_to_decision = time.time() - log.timestamp
                break
        else:
            raise ValueError(f"Suggestion ID not found: {suggestion_id}")
    
    def calculate_acceptance_rate(self, user_id: Optional[str] = None) -> float:
        """
        Calculate acceptance rate.
        
        Args:
            user_id: If specified, calculate for specific user only
        
        Returns:
            Acceptance rate as percentage (0-100)
        """
        # Filter by user if specified
        logs = self.suggestions
        if user_id:
            logs = [log for log in logs if log.user_id == user_id]
        
        total = len(logs)
        if total == 0:
            return 0.0
        
        accepted = sum(
            1 for log in logs
            if log.status in {'accepted', 'modified'}
        )
        
        return (accepted / total) * 100.0
    
    def get_stratified_rates(self) -> Dict[str, float]:
        """
        Calculate acceptance rates by dataset type.
        
        Returns:
            Dict mapping dataset_type to acceptance rate
        """
        rates = {}
        for dataset_type in {'vision', 'nlp', 'tabular'}:
            type_logs = [
                log for log in self.suggestions
                if log.dataset_type == dataset_type
            ]
            if type_logs:
                total = len(type_logs)
                accepted = sum(
                    1 for log in type_logs
                    if log.status in {'accepted', 'modified'}
                )
                rates[dataset_type] = (accepted / total) * 100.0
        
        return rates
    
    def export_logs(self, output_path: str) -> None:
        """
        Export interaction logs to JSON file.
        
        Args:
            output_path: Path to output JSON file
        """
        with open(output_path, 'w') as f:
            json.dump(
                [asdict(log) for log in self.suggestions],
                f,
                indent=2
            )
```

---

## 3. Algorithms and Pseudo-code

### 3.1 Example Selection Algorithm

**Purpose:** Select 3 most relevant examples from corpus for few-shot prompting

**Complexity:** O(n) where n = corpus size for dataset type

```python
def select_examples(corpus, dataset_type, section_name, k=3):
    """
    Select k most relevant examples from corpus.
    
    Strategy:
    1. Filter by dataset_type (vision/NLP/tabular)
    2. Filter by section availability
    3. Rank by quality score (completeness)
    4. Return top k
    """
    # Step 1: Filter by dataset type
    candidates = [
        example for example in corpus
        if example['dataset_type'] == dataset_type
    ]
    
    # Step 2: Filter by section availability
    candidates = [
        example for example in candidates
        if section_name in example['sections']
    ]
    
    # Step 3: Rank by quality score (descending)
    candidates.sort(key=lambda x: x['quality_score'], reverse=True)
    
    # Step 4: Return top k
    return candidates[:k]
```

**Time Complexity:** O(n log n) due to sorting  
**Space Complexity:** O(n) for filtered list

---

### 3.2 Acceptance Rate Calculation

**Purpose:** Calculate median acceptance rate across all users

**Complexity:** O(m) where m = number of users

```python
def calculate_median_acceptance(tracker):
    """
    Calculate median acceptance rate across all users.
    
    Returns:
        median_acceptance (float): Median percentage (0-100)
    """
    # Step 1: Get unique user IDs
    user_ids = set(log.user_id for log in tracker.suggestions if log.user_id)
    
    # Step 2: Calculate per-user acceptance rates
    user_rates = []
    for user_id in user_ids:
        rate = tracker.calculate_acceptance_rate(user_id=user_id)
        user_rates.append(rate)
    
    # Step 3: Calculate median
    if not user_rates:
        return 0.0
    
    user_rates.sort()
    n = len(user_rates)
    
    if n % 2 == 0:
        median = (user_rates[n//2 - 1] + user_rates[n//2]) / 2
    else:
        median = user_rates[n//2]
    
    return median
```

**Time Complexity:** O(m log m) due to sorting  
**Space Complexity:** O(m) for user_rates list

---

## 4. Tensor Shapes (Not Applicable)

**Note:** This is not a deep learning training experiment. Tensor shapes are only relevant for LLM inference (handled by transformers library internally).

**LLM Input:**
- Prompt text: Variable length (truncated to model max_length)
- Tokenized input: `[batch_size=1, seq_len]` (handled by pipeline)

**LLM Output:**
- Generated tokens: `[batch_size=1, generated_len]`
- Decoded text: String (suggestion)

---

## 5. Subtask Specifications

### Subtask E-2-1: Dataset Property Extraction
**Parent Epic:** E-2 (Suggestion Generator)  
**File:** `src/copilot/property_extractor.py`  
**API:** `PropertyExtractor.extract(file_paths) -> DatasetProperties`  
**Complexity:** 3/20

**Implementation Steps:**
1. Detect file formats from extensions
2. Infer dataset type (vision/NLP/tabular) from file formats and content
3. Parse data files (CSV, JSON, images) to extract features
4. Calculate basic statistics (distributions) for tabular data
5. Count number of samples
6. Return DatasetProperties object

---

### Subtask E-2-2: Example Selection Algorithm
**Parent Epic:** E-2 (Suggestion Generator)  
**File:** `src/copilot/generator.py` (method: `_select_examples`)  
**API:** `_select_examples(dataset_type, section_name, k=3) -> List[Dict]`  
**Complexity:** 2/20

**Implementation Steps:**
1. Call corpus_manager.get_examples() with filters
2. Corpus manager filters by dataset_type and section
3. Rank by quality score (completeness >85%)
4. Return top k=3 examples

---

### Subtask E-2-3: Prompt Construction
**Parent Epic:** E-2 (Suggestion Generator)  
**File:** `src/copilot/generator.py` (method: `_build_prompt`)  
**API:** `_build_prompt(properties, section_name, examples) -> str`  
**Complexity:** 2/20

**Implementation Steps:**
1. Format dataset properties (type, formats, features)
2. Format template section name
3. Add 3 examples (truncated to 300 chars each for context length)
4. Construct prompt string with instruction, properties, examples, task
5. Return formatted prompt

---

### Subtask E-2-4: LLM Inference Integration
**Parent Epic:** E-2 (Suggestion Generator)  
**File:** `src/copilot/generator.py` (method: `generate_suggestion`)  
**API:** `generate_suggestion(properties, section) -> Suggestion`  
**Complexity:** 7/20

**Implementation Steps:**
1. Initialize transformers pipeline in __init__ (model loading, GPU config)
2. Call _select_examples() to get 3 examples
3. Call _build_prompt() to construct prompt
4. Run LLM inference: pipeline(prompt, max_length=500, temperature=0.7)
5. Extract generated text from output
6. Create Suggestion object with metadata
7. Log to tracker if available
8. Return Suggestion

---

## 6. Applied Patterns from Archon KB

**Applied:** Few-Shot Prompting for LLM Generation (Pattern ID: FSP-001)
- Core: 3 high-quality examples + dataset properties → LLM → suggestion
- Rationale: More reliable than zero-shot, no fine-tuning required for PoC
- Source: Archon Knowledge Base - "LLM prompting strategies"

**Applied:** User Interaction Logging (Pattern ID: UIL-002)
- Core: Log every suggestion + user action → calculate acceptance rate
- Rationale: Proven pattern from GitHub Copilot metrics
- Source: Archon Knowledge Base - "AI assistance evaluation"

**Applied:** Dataset Introspection (Pattern ID: DI-003)
- Core: Analyze file formats, features, distributions → extract properties
- Rationale: Contextual suggestions require understanding dataset structure
- Source: Archon Knowledge Base - "Data pipeline patterns"

---

## 7. External Dependencies (None - Foundation Hypothesis)

**Note:** This is a foundation hypothesis with no base hypothesis to extend.

**No external APIs to call from previous hypotheses.**

---

## 8. Error Handling

### 8.1 LLM Inference Failures
```python
try:
    output = self.generator(prompt, max_length=500, temperature=0.7)
except Exception as e:
    logger.error(f"LLM inference failed: {e}")
    # Fallback: Return template-based suggestion
    return self._fallback_suggestion(section_name)
```

### 8.2 Property Extraction Failures
```python
try:
    properties = extractor.extract(file_paths)
except ValueError as e:
    logger.warning(f"Property extraction failed: {e}")
    # Fallback: Use minimal properties
    properties = DatasetProperties(
        dataset_type='unknown',
        file_formats=[],
        num_samples=None,
        features={},
        distributions={},
        metadata={}
    )
```

---

## 9. Testing Requirements

### 9.1 Unit Tests
- `test_property_extraction()`: Verify extraction from CSV, JSON files
- `test_example_selection()`: Verify k=3 examples returned, correct filtering
- `test_prompt_construction()`: Verify prompt format, truncation
- `test_acceptance_calculation()`: Verify correct percentage calculation

### 9.2 Integration Tests
- `test_end_to_end_suggestion()`: Upload dataset → extract → generate → log
- `test_user_interaction_flow()`: Generate → accept/reject → calculate rate

---

**Document Status:** ✅ Complete  
**Subtasks Defined:** 4/4 (E-2-1, E-2-2, E-2-3, E-2-4)  
**APIs Specified:** SuggestionGenerator, PropertyExtractor, SuggestionTracker  
**Applied Patterns:** 3 from Archon KB  
**Generated:** 2026-04-15 (Logic Agent - TEST mode)
