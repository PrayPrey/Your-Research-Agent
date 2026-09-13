"""Pattern memory module for transfer learning experiment."""
from dataclasses import dataclass
import time


@dataclass
class Pattern:
    error_type: str
    code_region: str
    fix_template: str
    problem_id: str
    success_count: int = 0
    created_at: float = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()


class PatternMemory:
    def __init__(self):
        self.patterns = []
        self.usage_log = []

    def store_pattern(self, error_type, code_region, fix_template, problem_id):
        for p in self.patterns:
            if p.error_type == error_type and p.code_region == code_region:
                p.success_count += 1
                return

        pattern = Pattern(
            error_type=error_type,
            code_region=code_region,
            fix_template=fix_template,
            problem_id=problem_id,
            success_count=1
        )
        self.patterns.append(pattern)

    def retrieve_similar(self, current_error, current_code, top_k=3):
        if not current_error:
            return []

        error_type = self._extract_error_type(current_error)
        candidates = [p for p in self.patterns if p.error_type == error_type]

        scored = []
        for p in candidates:
            score = self._score_similarity(p, current_code)
            scored.append((score, p))

        scored.sort(reverse=True, key=lambda x: x[0])
        return [p for _, p in scored[:top_k]]

    def _extract_error_type(self, error_msg):
        if "IndexError" in error_msg or "index" in error_msg.lower():
            return "IndexError"
        if "TypeError" in error_msg or "type" in error_msg.lower():
            return "TypeError"
        if "ValueError" in error_msg or "value" in error_msg.lower():
            return "ValueError"
        if "NameError" in error_msg:
            return "NameError"
        return "GenericError"

    def _score_similarity(self, pattern, code):
        score = 0
        if pattern.code_region.lower() in code.lower():
            score += 2
        score += pattern.success_count * 0.5
        return score

    def log_usage(self, pattern, used):
        self.usage_log.append({
            "pattern_id": id(pattern),
            "used": used,
            "timestamp": time.time()
        })

    def get_usage_stats(self):
        if not self.usage_log:
            return {"usage_rate": 0.0, "total_retrieved": 0, "total_used": 0}

        total_used = sum(x["used"] for x in self.usage_log)
        total_retrieved = len(self.usage_log)
        usage_rate = total_used / total_retrieved if total_retrieved > 0 else 0.0

        return {
            "usage_rate": usage_rate,
            "total_retrieved": total_retrieved,
            "total_used": total_used
        }
