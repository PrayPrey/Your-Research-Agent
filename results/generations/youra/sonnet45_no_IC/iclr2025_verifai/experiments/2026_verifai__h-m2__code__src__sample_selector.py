"""Stratified sampling for LLM extraction validation."""
import random
from typing import List, Dict
from collections import defaultdict

class SampleSelector:
    """Stratified sampling for extraction validation."""
    
    def __init__(self, validator, random_seed: int = 42):
        """Initialize selector."""
        self.validator = validator
        random.seed(random_seed)
    
    def stratified_sample(
        self,
        traces: List[Dict],
        n_queries: int = 25,
        n_results: int = 25
    ) -> Dict[str, List[Dict]]:
        """Sample tool calls with outcome/tool-type balancing."""
        all_calls = []
        
        for trace in traces:
            outcome = "success" if "success" in trace.get("trace_id", "") else "fail"
            for call in trace["tool_calls"]:
                is_valid, query_words, result_words = self.validator.validate_nl_presence(call)
                if is_valid:
                    all_calls.append({
                        "call": call,
                        "outcome": outcome,
                        "tool_type": self.get_tool_type(call.get("tool_name", "")),
                        "query_words": query_words,
                        "result_words": result_words
                    })
        
        # Sample queries (query_words >= 10)
        query_candidates = [c for c in all_calls if c["query_words"] >= 10]
        queries = self._stratified_sample_by_groups(query_candidates, n_queries)
        
        # Sample results (result_words >= 10)
        result_candidates = [c for c in all_calls if c["result_words"] >= 10]
        results = self._stratified_sample_by_groups(result_candidates, n_results)
        
        return {"queries": [q["call"] for q in queries], "results": [r["call"] for r in results]}
    
    def _stratified_sample_by_groups(self, candidates: List[Dict], n: int) -> List[Dict]:
        """Sample with stratification by outcome and tool_type."""
        # Group by (outcome, tool_type)
        groups = defaultdict(list)
        for c in candidates:
            key = (c["outcome"], c["tool_type"])
            groups[key].append(c)
        
        # Calculate samples per group (proportional)
        total = len(candidates)
        selected = []
        
        for key, items in groups.items():
            group_size = len(items)
            target = max(1, int(n * group_size / total))
            sampled = random.sample(items, min(target, group_size))
            selected.extend(sampled)
        
        # Adjust to exact n
        if len(selected) < n:
            remaining = [c for c in candidates if c not in selected]
            selected.extend(random.sample(remaining, n - len(selected)))
        elif len(selected) > n:
            selected = random.sample(selected, n)
        
        return selected
    
    def get_tool_type(self, tool_name: str) -> str:
        """Classify tool type."""
        research_tools = ["rag_search", "exa_search", "arxiv_search", "scholar"]
        data_tools = ["read", "glob", "grep", "bash"]
        
        tool_lower = tool_name.lower()
        if any(t in tool_lower for t in research_tools):
            return "research"
        elif any(t in tool_lower for t in data_tools):
            return "data"
        else:
            return "other"
