# Logic Design: H-E1 Friction Measurement System

**Hypothesis ID:** h-e1  
**Design Version:** 1.0  
**Date:** 2026-08-19  
**Owner:** Phase 3 Logic Design  

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase  
**Status:** Green-field API design - existing code is for different h-e1 version  
**Analyzed Path:** N/A  
**Relevant Symbols:** None - new implementation for metadata extraction system  

---

## 1. API Clients

### 1.1 OpenML Client

**Applied:** Standard REST API client pattern + openml-python library

```python
from typing import Dict, Optional, Any
import openml
import time
from datetime import datetime

class OpenMLExtractor:
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
    
    def list_active_datasets(self, limit: Optional[int] = None) -> list[int]:
        """List active dataset IDs. Returns: list of dataset IDs"""
        datasets = openml.datasets.list_datasets(status="active", output_format="dataframe")
        ids = datasets.index.tolist()
        return ids[:limit] if limit else ids
    
    def extract_metadata(self, dataset_id: int) -> Dict[str, Any]:
        """Extract metadata for single dataset.
        
        Returns: {
            'platform': 'openml',
            'dataset_id': int,
            'extraction_timestamp': str,
            'extraction_status': 'success'|'failure',
            'error_message': str|None,
            'metadata': {
                'collection_date': str|None,
                'licence': str|None,
                'url': str|None,
                'original_data_url': str|None,
                'paper_url': str|None,
                'version': str|None
            }
        }
        """
        for attempt in range(self.max_retries):
            try:
                dataset = openml.datasets.get_dataset(dataset_id, download_data=False)
                return {
                    'platform': 'openml',
                    'dataset_id': dataset_id,
                    'extraction_timestamp': datetime.utcnow().isoformat(),
                    'extraction_status': 'success',
                    'error_message': None,
                    'metadata': {
                        'collection_date': getattr(dataset, 'collection_date', None),
                        'licence': getattr(dataset, 'licence', None),
                        'url': getattr(dataset, 'url', None),
                        'original_data_url': getattr(dataset, 'original_data_url', None),
                        'paper_url': getattr(dataset, 'paper_url', None),
                        'version': str(dataset.version) if dataset.version else None
                    }
                }
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return self._error_record(dataset_id, str(e))
                time.sleep(2 ** attempt)
        return self._error_record(dataset_id, "Max retries exceeded")
    
    def _error_record(self, dataset_id: int, error: str) -> Dict[str, Any]:
        return {
            'platform': 'openml',
            'dataset_id': dataset_id,
            'extraction_timestamp': datetime.utcnow().isoformat(),
            'extraction_status': 'failure',
            'error_message': error,
            'metadata': {}
        }
```

---

### 1.2 HuggingFace Client

**Applied:** Dataset Hub API pattern + YAML frontmatter parsing

```python
from typing import Dict, Optional, Any
from datasets import list_datasets
from huggingface_hub import DatasetCard
import time
from datetime import datetime
import re

class HuggingFaceExtractor:
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
    
    def list_datasets(self, limit: Optional[int] = None) -> list[str]:
        """List dataset IDs. Returns: list of dataset ID strings"""
        datasets = list(list_datasets())
        ids = [d.id for d in datasets]
        return ids[:limit] if limit else ids
    
    def extract_metadata(self, dataset_id: str) -> Dict[str, Any]:
        """Extract metadata from dataset card.
        
        Returns: {
            'platform': 'huggingface',
            'dataset_id': str,
            'extraction_timestamp': str,
            'extraction_status': 'success'|'failure',
            'error_message': str|None,
            'metadata': {
                'license': str|None,
                'version': str|None,
                'source_url': str|None,
                'preprocessing_code': str|None,
                'collection_date': str|None,
                'dependencies': str|None
            }
        }
        """
        for attempt in range(self.max_retries):
            try:
                card = DatasetCard.load(dataset_id)
                card_data = card.data.to_dict() if card.data else {}
                
                return {
                    'platform': 'huggingface',
                    'dataset_id': dataset_id,
                    'extraction_timestamp': datetime.utcnow().isoformat(),
                    'extraction_status': 'success',
                    'error_message': None,
                    'metadata': {
                        'license': card_data.get('license'),
                        'version': self._extract_version(card_data),
                        'source_url': self._extract_source_url(card_data),
                        'preprocessing_code': self._extract_code(card.text or ''),
                        'collection_date': None,  # Rarely documented
                        'dependencies': self._extract_dependencies(card_data, card.text or '')
                    }
                }
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return self._error_record(dataset_id, str(e))
                time.sleep(2 ** attempt)
        return self._error_record(dataset_id, "Max retries exceeded")
    
    def _extract_version(self, card_data: dict) -> Optional[str]:
        if 'dataset_info' in card_data and 'version' in card_data['dataset_info']:
            return card_data['dataset_info']['version']
        return None
    
    def _extract_source_url(self, card_data: dict) -> Optional[str]:
        for key in ['source_datasets', 'homepage', 'repository']:
            if key in card_data and card_data[key]:
                return str(card_data[key])
        return None
    
    def _extract_code(self, card_text: str) -> Optional[str]:
        """Extract code blocks from markdown."""
        code_blocks = re.findall(r'```[\w]*\n(.*?)```', card_text, re.DOTALL)
        return '\n'.join(code_blocks) if code_blocks else None
    
    def _extract_dependencies(self, card_data: dict, card_text: str) -> Optional[str]:
        if 'requires' in card_data:
            return str(card_data['requires'])
        # Search in text
        if 'pip install' in card_text or 'import' in card_text:
            return card_text[:200]  # First 200 chars with dependency info
        return None
    
    def _error_record(self, dataset_id: str, error: str) -> Dict[str, Any]:
        return {
            'platform': 'huggingface',
            'dataset_id': dataset_id,
            'extraction_timestamp': datetime.utcnow().isoformat(),
            'extraction_status': 'failure',
            'error_message': error,
            'metadata': {}
        }
```

---

### 1.3 UCI Web Scraper

**Applied:** BeautifulSoup HTML parsing + rate limiting pattern

```python
from typing import Dict, Optional, Any
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import re

class UCIExtractor:
    BASE_URL = "https://archive.ics.uci.edu/ml/datasets"
    
    def __init__(self, timeout: int = 30, max_retries: int = 3, rate_limit: float = 1.0):
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limit = rate_limit
        self.last_request_time = 0
    
    def list_datasets(self, limit: Optional[int] = None) -> list[str]:
        """Scrape dataset listing page for dataset names. Returns: list of dataset names"""
        # ponytail: Simplified - real implementation scrapes listing page
        raise NotImplementedError("Implement listing page scraper")
    
    def extract_metadata(self, dataset_name: str) -> Dict[str, Any]:
        """Scrape dataset detail page.
        
        Returns: {
            'platform': 'uci',
            'dataset_id': str,
            'extraction_timestamp': str,
            'extraction_status': 'success'|'failure',
            'error_message': str|None,
            'metadata': {
                'license': str|None,
                'version': str|None,
                'data_source': str|None,
                'preprocessing_methodology': str|None,
                'dependencies': str|None,
                'collection_date': str|None
            }
        }
        """
        self._enforce_rate_limit()
        
        for attempt in range(self.max_retries):
            try:
                url = f"{self.BASE_URL}/{dataset_name}"
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                return {
                    'platform': 'uci',
                    'dataset_id': dataset_name,
                    'extraction_timestamp': datetime.utcnow().isoformat(),
                    'extraction_status': 'success',
                    'error_message': None,
                    'metadata': {
                        'license': self._parse_license(soup),
                        'version': self._parse_version(soup),
                        'data_source': self._parse_data_source(soup),
                        'preprocessing_methodology': self._parse_methodology(soup),
                        'dependencies': self._parse_dependencies(soup),
                        'collection_date': self._parse_collection_date(soup)
                    }
                }
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return self._error_record(dataset_name, str(e))
                time.sleep(2 ** attempt)
        return self._error_record(dataset_name, "Max retries exceeded")
    
    def _enforce_rate_limit(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()
    
    def _parse_license(self, soup: BeautifulSoup) -> Optional[str]:
        # ponytail: Single selector - add fallbacks only if needed
        license_elem = soup.find(string=re.compile(r'license|License', re.I))
        if license_elem and license_elem.parent:
            return license_elem.parent.get_text(strip=True)
        return None
    
    def _parse_version(self, soup: BeautifulSoup) -> Optional[str]:
        version_elem = soup.find(string=re.compile(r'version|Version|Date Donated', re.I))
        if version_elem and version_elem.parent:
            return version_elem.parent.get_text(strip=True)
        return None
    
    def _parse_data_source(self, soup: BeautifulSoup) -> Optional[str]:
        source_section = soup.find('p', string=re.compile(r'Source', re.I))
        return source_section.get_text(strip=True) if source_section else None
    
    def _parse_methodology(self, soup: BeautifulSoup) -> Optional[str]:
        method_section = soup.find('p', string=re.compile(r'Data Set Information', re.I))
        return method_section.get_text(strip=True) if method_section else None
    
    def _parse_dependencies(self, soup: BeautifulSoup) -> Optional[str]:
        dep_elem = soup.find(string=re.compile(r'software|Software|Requirement', re.I))
        if dep_elem and dep_elem.parent:
            return dep_elem.parent.get_text(strip=True)
        return None
    
    def _parse_collection_date(self, soup: BeautifulSoup) -> Optional[str]:
        date_elem = soup.find(string=re.compile(r'Date Donated|Donated', re.I))
        if date_elem and date_elem.parent:
            text = date_elem.parent.get_text(strip=True)
            # Extract date pattern
            date_match = re.search(r'\d{1,2}/\d{1,2}/\d{4}|\d{4}', text)
            return date_match.group(0) if date_match else None
        return None
    
    def _error_record(self, dataset_name: str, error: str) -> Dict[str, Any]:
        return {
            'platform': 'uci',
            'dataset_id': dataset_name,
            'extraction_timestamp': datetime.utcnow().isoformat(),
            'extraction_status': 'failure',
            'error_message': error,
            'metadata': {}
        }
```

---

## 2. Parsing Rules Module

**Applied:** Binary classification pattern with configurable thresholds

### 2.1 Parsing Rules Interface

```python
from typing import Dict, Any, Optional
import re
from dataclasses import dataclass

@dataclass
class ParsingConfig:
    """Configuration for parsing thresholds and patterns."""
    preprocessing_code_min_length: int = 50
    preprocessing_code_keywords: list[str] = None
    data_source_url_min_length: int = 10
    url_pattern: str = r'http(s)?://[^\s]+'
    date_patterns: list[str] = None
    license_min_length: int = 5
    license_placeholders: list[str] = None
    version_pattern: str = r'v?\d+\.?\d*\.?\d*|version\s+\d+'
    dependencies_min_length: int = 20
    
    def __post_init__(self):
        if self.preprocessing_code_keywords is None:
            self.preprocessing_code_keywords = ['import', 'function', 'def', 'library', 'require']
        if self.date_patterns is None:
            self.date_patterns = [
                r'\d{4}-\d{2}-\d{2}',  # ISO 8601
                r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
                r'\b\d{4}\b'  # Year only
            ]
        if self.license_placeholders is None:
            self.license_placeholders = ['N/A', 'Unknown', 'TODO', 'TBD', '']


class FieldParser:
    def __init__(self, config: Optional[ParsingConfig] = None):
        self.config = config or ParsingConfig()
    
    def parse_preprocessing_code(self, value: Any) -> int:
        """Returns: 1 if present, 0 if absent"""
        if not value or not isinstance(value, str):
            return 0
        
        if len(value) <= self.config.preprocessing_code_min_length:
            return 0
        
        # Check for keywords or file extensions
        has_keyword = any(kw in value for kw in self.config.preprocessing_code_keywords)
        has_extension = bool(re.search(r'\.(py|R|ipynb|jl)', value))
        
        return 1 if (has_keyword or has_extension) else 0
    
    def parse_data_source_url(self, value: Any) -> int:
        """Returns: 1 if present, 0 if absent"""
        if not value or not isinstance(value, str):
            return 0
        
        if len(value) <= self.config.data_source_url_min_length:
            return 0
        
        return 1 if re.search(self.config.url_pattern, value) else 0
    
    def parse_collection_date(self, value: Any) -> int:
        """Returns: 1 if present, 0 if absent"""
        if not value or not isinstance(value, str):
            return 0
        
        for pattern in self.config.date_patterns:
            if re.search(pattern, value):
                return 1
        return 0
    
    def parse_license(self, value: Any) -> int:
        """Returns: 1 if present, 0 if absent"""
        if not value or not isinstance(value, str):
            return 0
        
        # Check length
        if len(value) <= self.config.license_min_length:
            return 0
        
        # Exclude placeholders
        if value.strip() in self.config.license_placeholders:
            return 0
        
        return 1
    
    def parse_version(self, value: Any) -> int:
        """Returns: 1 if present, 0 if absent"""
        if not value or not isinstance(value, str):
            return 0
        
        return 1 if re.search(self.config.version_pattern, value, re.I) else 0
    
    def parse_dependencies(self, value: Any) -> int:
        """Returns: 1 if present, 0 if absent"""
        if not value:
            return 0
        
        # Handle list type
        if isinstance(value, list):
            return 1 if len(value) > 0 else 0
        
        # Handle string type
        if isinstance(value, str):
            return 1 if len(value) > self.config.dependencies_min_length else 0
        
        return 0
    
    def parse_all_fields(self, metadata: Dict[str, Any]) -> Dict[str, int]:
        """Parse all 6 fields. Returns: {'field_name': 0|1}"""
        return {
            'preprocessing_code': self.parse_preprocessing_code(metadata.get('preprocessing_code')),
            'data_source_url': self.parse_data_source_url(metadata.get('data_source_url') or metadata.get('source_url')),
            'collection_date': self.parse_collection_date(metadata.get('collection_date')),
            'license': self.parse_license(metadata.get('license') or metadata.get('licence')),
            'version': self.parse_version(metadata.get('version')),
            'dependencies': self.parse_dependencies(metadata.get('dependencies'))
        }
```

---

## 3. Validation Module

**Applied:** Confusion matrix calculation pattern

### 3.1 Validation Metrics

```python
from typing import Dict, List
import json

class ValidationMetrics:
    def __init__(self, automated_labels: Dict[str, Dict[str, int]], 
                 manual_labels: Dict[str, Dict[str, int]]):
        """
        Args:
            automated_labels: {dataset_id: {field: 0|1}}
            manual_labels: {dataset_id: {field: 0|1}}
        """
        self.automated = automated_labels
        self.manual = manual_labels
    
    def calculate_accuracy(self) -> Dict[str, float]:
        """Calculate accuracy metrics.
        
        Returns: {
            'overall_accuracy': float,
            'per_field_accuracy': {'field': float},
            'confusion_matrix': {'TP': int, 'FP': int, 'TN': int, 'FN': int}
        }
        """
        fields = ['preprocessing_code', 'data_source_url', 'collection_date', 
                  'license', 'version', 'dependencies']
        
        total_correct = 0
        total_count = 0
        per_field = {}
        
        # Confusion matrix counters
        TP = FP = TN = FN = 0
        
        for field in fields:
            correct = 0
            count = 0
            
            for dataset_id in self.manual:
                if dataset_id not in self.automated:
                    continue
                
                auto_val = self.automated[dataset_id].get(field, 0)
                manual_val = self.manual[dataset_id].get(field, 0)
                
                if auto_val == manual_val:
                    correct += 1
                    total_correct += 1
                    if manual_val == 1:
                        TP += 1
                    else:
                        TN += 1
                else:
                    if auto_val == 1 and manual_val == 0:
                        FP += 1
                    else:
                        FN += 1
                
                count += 1
                total_count += 1
            
            per_field[field] = (correct / count * 100) if count > 0 else 0.0
        
        overall = (total_correct / total_count * 100) if total_count > 0 else 0.0
        
        return {
            'overall_accuracy': overall,
            'per_field_accuracy': per_field,
            'confusion_matrix': {'TP': TP, 'FP': FP, 'TN': TN, 'FN': FN}
        }
    
    def calculate_cohen_kappa(self, field: str) -> float:
        """Calculate Cohen's kappa for inter-rater reliability."""
        agree = 0
        total = 0
        p_yes = p_no = 0
        
        for dataset_id in self.manual:
            if dataset_id not in self.automated:
                continue
            
            auto_val = self.automated[dataset_id].get(field, 0)
            manual_val = self.manual[dataset_id].get(field, 0)
            
            if auto_val == manual_val:
                agree += 1
            
            p_yes += auto_val
            p_no += (1 - auto_val)
            total += 1
        
        if total == 0:
            return 0.0
        
        p_observed = agree / total
        p_yes_expected = (p_yes / total) ** 2
        p_no_expected = (p_no / total) ** 2
        p_expected = p_yes_expected + p_no_expected
        
        return (p_observed - p_expected) / (1 - p_expected) if p_expected < 1 else 1.0
```

---

## 4. Throughput Analysis Module

**Applied:** Extrapolation calculation pattern

### 4.1 Throughput Calculator

```python
from typing import Dict, List
from datetime import datetime

class ThroughputAnalyzer:
    def __init__(self, extraction_logs: List[Dict]):
        """
        Args:
            extraction_logs: [{
                'dataset_id': str,
                'platform': str,
                'start_time': str (ISO 8601),
                'end_time': str (ISO 8601),
                'status': 'success'|'failure'
            }]
        """
        self.logs = extraction_logs
    
    def calculate_throughput(self) -> Dict[str, float]:
        """Calculate per-platform throughput.
        
        Returns: {
            'openml': float,  # records/hour
            'huggingface': float,
            'uci': float,
            'overall': float
        }
        """
        platforms = ['openml', 'huggingface', 'uci']
        throughput = {}
        
        for platform in platforms:
            platform_logs = [log for log in self.logs if log['platform'] == platform]
            
            if not platform_logs:
                throughput[platform] = 0.0
                continue
            
            success_count = sum(1 for log in platform_logs if log['status'] == 'success')
            
            # Calculate total time
            start_times = [datetime.fromisoformat(log['start_time']) for log in platform_logs]
            end_times = [datetime.fromisoformat(log['end_time']) for log in platform_logs]
            
            total_seconds = (max(end_times) - min(start_times)).total_seconds()
            total_hours = total_seconds / 3600 if total_seconds > 0 else 1
            
            throughput[platform] = success_count / total_hours
        
        # Overall throughput (weighted average or sum depending on parallel execution)
        throughput['overall'] = sum(throughput[p] for p in platforms)
        
        return throughput
    
    def extrapolate_time(self, target_counts: Dict[str, int], 
                         throughput: Dict[str, float]) -> Dict[str, Any]:
        """Extrapolate time for full-scale extraction.
        
        Args:
            target_counts: {'openml': 7000, 'huggingface': 2500, 'uci': 500}
            throughput: {'openml': float, 'huggingface': float, 'uci': float}
        
        Returns: {
            'per_platform_hours': {'openml': float, 'huggingface': float, 'uci': float},
            'total_hours': float,  # Assuming parallel execution
            'feasible': bool  # < 336 hours
        }
        """
        per_platform = {}
        
        for platform, count in target_counts.items():
            if throughput[platform] > 0:
                per_platform[platform] = count / throughput[platform]
            else:
                per_platform[platform] = float('inf')
        
        # Parallel execution - max of platform times
        total_hours = max(per_platform.values())
        
        return {
            'per_platform_hours': per_platform,
            'total_hours': total_hours,
            'feasible': total_hours < 336
        }
```

---

## 5. Friction Scoring Module

**Applied:** Binary feature detection + composite scoring

### 5.1 Friction Scorer

```python
from typing import Dict
from dataclasses import dataclass

@dataclass
class FrictionFeatures:
    """Binary presence of friction-reduction features."""
    automated_field_extraction: int  # 0 or 1
    prefilled_templates: int
    validation_feedback: int
    programmatic_api: int
    
    def composite_score(self) -> int:
        """Sum of 4 binary features. Range: 0-4"""
        return (self.automated_field_extraction + 
                self.prefilled_templates + 
                self.validation_feedback + 
                self.programmatic_api)


class FrictionScorer:
    def score_platform(self, platform: str, evidence: Dict[str, str]) -> FrictionFeatures:
        """Assign friction scores based on documentation review.
        
        Args:
            platform: 'openml'|'huggingface'|'uci'
            evidence: {
                'automated_extraction_url': str,
                'template_url': str,
                'validation_url': str,
                'api_url': str
            }
        
        Returns: FrictionFeatures with binary scores
        """
        # ponytail: Manual scoring - automated detection not needed for 3 platforms
        if platform == 'openml':
            return FrictionFeatures(
                automated_field_extraction=1,  # ARFF auto-extraction
                prefilled_templates=0,
                validation_feedback=0,
                programmatic_api=1  # openml-python API
            )
        elif platform == 'huggingface':
            return FrictionFeatures(
                automated_field_extraction=0,
                prefilled_templates=1,  # Dataset card templates
                validation_feedback=1,  # YAML validation
                programmatic_api=1  # Hub API
            )
        elif platform == 'uci':
            return FrictionFeatures(
                automated_field_extraction=0,
                prefilled_templates=0,
                validation_feedback=0,
                programmatic_api=0  # Web forms only
            )
        else:
            raise ValueError(f"Unknown platform: {platform}")
```

---

## 6. Batch Processing Pipeline

**Applied:** Orchestration pattern for pilot extraction

### 6.1 Pipeline Orchestrator

```python
from typing import List, Dict, Any
import json
from pathlib import Path

class ExtractionPipeline:
    def __init__(self, openml_client: OpenMLExtractor, 
                 hf_client: HuggingFaceExtractor,
                 uci_client: UCIExtractor,
                 parser: FieldParser):
        self.openml = openml_client
        self.hf = hf_client
        self.uci = uci_client
        self.parser = parser
    
    def run_pilot_extraction(self, 
                            openml_count: int = 100,
                            hf_count: int = 100, 
                            uci_count: int = 50,
                            output_path: str = "pilot_extraction.json") -> Dict[str, Any]:
        """Run pilot extraction for all platforms.
        
        Returns: {
            'records': List[Dict],  # All extracted records
            'metrics': {
                'openml_success_rate': float,
                'hf_success_rate': float,
                'uci_success_rate': float
            }
        }
        """
        records = []
        
        # OpenML extraction
        openml_ids = self.openml.list_active_datasets(limit=openml_count)
        for dataset_id in openml_ids:
            record = self.openml.extract_metadata(dataset_id)
            if record['extraction_status'] == 'success':
                record['parsed_fields'] = self.parser.parse_all_fields(record['metadata'])
            records.append(record)
        
        # HuggingFace extraction
        hf_ids = self.hf.list_datasets(limit=hf_count)
        for dataset_id in hf_ids:
            record = self.hf.extract_metadata(dataset_id)
            if record['extraction_status'] == 'success':
                record['parsed_fields'] = self.parser.parse_all_fields(record['metadata'])
            records.append(record)
        
        # UCI extraction (placeholder - needs dataset list implementation)
        # uci_names = self.uci.list_datasets(limit=uci_count)
        # for dataset_name in uci_names:
        #     record = self.uci.extract_metadata(dataset_name)
        #     if record['extraction_status'] == 'success':
        #         record['parsed_fields'] = self.parser.parse_all_fields(record['metadata'])
        #     records.append(record)
        
        # Calculate success rates
        openml_success = sum(1 for r in records if r['platform'] == 'openml' and r['extraction_status'] == 'success')
        hf_success = sum(1 for r in records if r['platform'] == 'huggingface' and r['extraction_status'] == 'success')
        uci_success = sum(1 for r in records if r['platform'] == 'uci' and r['extraction_status'] == 'success')
        
        metrics = {
            'openml_success_rate': (openml_success / openml_count * 100) if openml_count > 0 else 0,
            'hf_success_rate': (hf_success / hf_count * 100) if hf_count > 0 else 0,
            'uci_success_rate': (uci_success / uci_count * 100) if uci_count > 0 else 0
        }
        
        # Save to file
        output = {'records': records, 'metrics': metrics}
        Path(output_path).write_text(json.dumps(output, indent=2))
        
        return output
```

---

## 7. MUST_WORK Gate Evaluator

**Applied:** Boolean gate logic

```python
from typing import Dict, Any

class GateEvaluator:
    def evaluate_must_work_gate(self, 
                                friction_scores: Dict[str, int],
                                extraction_metrics: Dict[str, float],
                                parsing_accuracy: float,
                                throughput_feasible: bool) -> Dict[str, Any]:
        """Evaluate MUST_WORK gate conditions.
        
        Args:
            friction_scores: {'openml': int, 'huggingface': int, 'uci': int}
            extraction_metrics: {
                'openml_success_rate': float,
                'hf_success_rate': float,
                'uci_success_rate': float
            }
            parsing_accuracy: float (0-100)
            throughput_feasible: bool
        
        Returns: {
            'gate_result': 'PASS'|'FAIL',
            'conditions': {
                'friction_scores_assigned': bool,
                'openml_hf_success': bool,
                'uci_success': bool,
                'parsing_accuracy': bool,
                'throughput_feasible': bool
            }
        }
        """
        conditions = {
            'friction_scores_assigned': all(isinstance(v, int) and 0 <= v <= 4 
                                           for v in friction_scores.values()),
            'openml_hf_success': (extraction_metrics['openml_success_rate'] > 80 and 
                                 extraction_metrics['hf_success_rate'] > 80),
            'uci_success': extraction_metrics['uci_success_rate'] > 70,
            'parsing_accuracy': parsing_accuracy > 90,
            'throughput_feasible': throughput_feasible
        }
        
        gate_result = 'PASS' if all(conditions.values()) else 'FAIL'
        
        return {
            'gate_result': gate_result,
            'conditions': conditions
        }
```

---

## Implementation Notes

**Pseudo-code not included (standard patterns):**
- Error handling: try-except with exponential backoff
- Logging: Standard Python logging module
- Configuration loading: JSON/YAML file reading

**Key thresholds (from config):**
- preprocessing_code: >50 chars + keywords
- data_source_url: >10 chars + URL pattern
- license: >5 chars, exclude placeholders
- dependencies: >20 chars or non-empty list

**Success metrics:**
- Extraction success: OpenML/HF >80%, UCI >70%
- Parsing accuracy: >90% overall, >75% per field
- Throughput: <336 hours for 10k datasets

---

**File paths referenced:**
- /home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_mldpr/docs/youra_research/h-e1/03_prd.md
- /home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_mldpr/docs/youra_research/h-e1/02c_experiment_brief.md
