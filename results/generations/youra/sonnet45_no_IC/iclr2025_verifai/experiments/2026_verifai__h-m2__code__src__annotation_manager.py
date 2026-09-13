"""Human annotation management and inter-rater agreement."""
import json
from pathlib import Path
from typing import List, Dict
from sklearn.metrics import cohen_kappa_score

class AnnotationManager:
    """Manage human annotations and compute inter-rater agreement."""
    
    def __init__(self, annotations_folder: Path):
        """Initialize manager."""
        self.annotations_folder = annotations_folder
        self.annotations_folder.mkdir(exist_ok=True)
    
    def create_annotation_template(self, samples: Dict[str, List[Dict]], output_file: Path):
        """Generate annotation template JSON."""
        template = {
            "instructions": "Extract all assumptions (from queries) or claims (from results). List one per line.",
            "samples": []
        }
        
        for idx, query_call in enumerate(samples["queries"]):
            template["samples"].append({
                "id": f"query_{idx}",
                "type": "query",
                "text": self._extract_text(query_call.get("parameters", {})),
                "annotator_1_items": [],
                "annotator_2_items": []
            })
        
        for idx, result_call in enumerate(samples["results"]):
            template["samples"].append({
                "id": f"result_{idx}",
                "type": "result",
                "text": self._extract_text(result_call.get("result", "")),
                "annotator_1_items": [],
                "annotator_2_items": []
            })
        
        with open(output_file, 'w') as f:
            json.dump(template, f, indent=2)
        
        return template
    
    def load_annotations(self, annotation_file: Path) -> Dict:
        """Load completed annotations."""
        with open(annotation_file, 'r') as f:
            return json.load(f)
    
    def compute_inter_rater_kappa(self, annotations: Dict) -> float:
        """Compute Cohen's Kappa for inter-rater agreement."""
        # Convert annotations to binary vectors (item present/absent)
        all_items = set()
        for sample in annotations["samples"]:
            all_items.update(sample["annotator_1_items"])
            all_items.update(sample["annotator_2_items"])
        
        item_list = list(all_items)
        annotator_1_vectors = []
        annotator_2_vectors = []
        
        for sample in annotations["samples"]:
            vec_1 = [1 if item in sample["annotator_1_items"] else 0 for item in item_list]
            vec_2 = [1 if item in sample["annotator_2_items"] else 0 for item in item_list]
            annotator_1_vectors.extend(vec_1)
            annotator_2_vectors.extend(vec_2)
        
        if not annotator_1_vectors:
            return 0.0
        
        kappa = cohen_kappa_score(annotator_1_vectors, annotator_2_vectors)
        return kappa
    
    def compute_consensus(self, annotations: Dict, kappa_threshold: float = 0.70) -> Dict:
        """Compute consensus annotations (majority rule)."""
        kappa = self.compute_inter_rater_kappa(annotations)
        
        if kappa < kappa_threshold:
            raise ValueError(f"Inter-rater Kappa ({kappa:.2f}) below threshold ({kappa_threshold})")
        
        consensus = {"samples": [], "kappa": kappa}
        
        for sample in annotations["samples"]:
            items_1 = set(sample["annotator_1_items"])
            items_2 = set(sample["annotator_2_items"])
            
            # Consensus: items in both OR unique items (majority = 1/2 = 50%)
            consensus_items = list(items_1 | items_2)
            
            consensus["samples"].append({
                "id": sample["id"],
                "type": sample["type"],
                "text": sample["text"],
                "consensus_items": consensus_items
            })
        
        return consensus
    
    def _extract_text(self, obj) -> str:
        """Extract text from dict/str."""
        if isinstance(obj, str):
            return obj
        elif isinstance(obj, dict):
            return " ".join(str(v) for v in obj.values())
        else:
            return str(obj)
