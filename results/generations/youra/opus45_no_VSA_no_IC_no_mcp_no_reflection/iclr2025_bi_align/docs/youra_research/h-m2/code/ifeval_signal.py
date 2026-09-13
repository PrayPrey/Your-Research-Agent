"""IFEvalRewardSignal copied from H-E1 (avoids import path conflicts)."""
import re
import torch
import torch.nn as nn


class BaselineChecker:
    """Binary constraint satisfaction (hard 0/1), for comparison."""

    def check(self, response: str, constraints: list[dict]) -> float:
        scores = []
        for c in constraints:
            score = self._check_single(response, c)
            scores.append(score)
        return sum(scores) / len(scores) if scores else 0.0

    def _check_single(self, response: str, c: dict) -> float:
        c_type = c.get("type", "unknown")

        if c_type == "keyword":
            keywords = c.get("keywords", [])
            must_include = c.get("must_include", True)
            if not keywords:
                return 1.0
            found = all(kw.lower() in response.lower() for kw in keywords)
            return 1.0 if (found == must_include) else 0.0

        elif c_type == "length":
            target = c.get("target", 100)
            op = c.get("op", "at_least")
            unit = c.get("unit", "words")
            count = self._count_units(response, unit)

            if op == "at_least":
                return 1.0 if count >= target else 0.0
            elif op == "at_most":
                return 1.0 if count <= target else 0.0
            elif op == "exactly":
                return 1.0 if count == target else 0.0
            return 0.0

        elif c_type == "format":
            return self._check_format(response, c.get("subtype", ""))

        elif c_type == "case":
            return self._check_case(response, c.get("case_type", ""))

        return 0.5

    def _count_units(self, text: str, unit: str) -> int:
        if unit == "sentences":
            return len(re.split(r'[.!?]+', text.strip()))
        elif unit == "paragraphs":
            return len([p for p in text.split('\n\n') if p.strip()])
        return len(text.split())

    def _check_format(self, text: str, subtype: str) -> float:
        if subtype == "json":
            return 1.0 if re.search(r'\{[^}]+\}', text) else 0.0
        elif subtype == "bullet":
            return 1.0 if re.search(r'^\s*[-*•]', text, re.MULTILINE) else 0.0
        return 0.5

    def _check_case(self, text: str, case_type: str) -> float:
        if case_type == "capital":
            return 1.0 if text == text.upper() else 0.0
        elif case_type == "lowercase":
            return 1.0 if text == text.lower() else 0.0
        return 0.5


class IFEvalRewardSignal(nn.Module):
    """Soft constraint satisfaction with gradient flow."""

    def __init__(self, soft_margin: float = 0.1):
        super().__init__()
        self.soft_margin = soft_margin
        self.scale = nn.Parameter(torch.tensor(1.0))

    def _soft_threshold(self, value: float, target: float, op: str) -> torch.Tensor:
        margin = self.soft_margin * target if target > 0 else self.soft_margin
        margin = max(margin, 0.01)

        if op == "at_least":
            diff = (value - target) / margin
        elif op == "at_most":
            diff = (target - value) / margin
        elif op == "exactly":
            diff = (margin - abs(value - target)) / margin
        else:
            diff = 0.0

        return torch.sigmoid(torch.tensor(diff, dtype=torch.float32))

    def check_length_constraint(self, text: str, target: int, op: str, unit: str = "words") -> torch.Tensor:
        if unit == "sentences":
            count = len(re.split(r'[.!?]+', text.strip()))
        elif unit == "paragraphs":
            count = len([p for p in text.split('\n\n') if p.strip()])
        else:
            count = len(text.split())
        return self._soft_threshold(float(count), float(target), op)

    def check_keyword_constraint(self, text: str, keywords: list, must_include: bool) -> torch.Tensor:
        if not keywords:
            return torch.tensor(1.0, dtype=torch.float32)

        matches = sum(1 for kw in keywords if kw.lower() in text.lower())
        ratio = matches / len(keywords)

        if must_include:
            return torch.tensor(ratio, dtype=torch.float32)
        else:
            return torch.tensor(1.0 - ratio, dtype=torch.float32)

    def check_format_constraint(self, text: str, fmt: str) -> torch.Tensor:
        if fmt == "json":
            match = re.search(r'\{[^}]+\}', text)
            return torch.tensor(1.0 if match else 0.0, dtype=torch.float32)
        elif fmt == "bullet":
            matches = len(re.findall(r'^\s*[-*•]', text, re.MULTILINE))
            return torch.sigmoid(torch.tensor(float(matches) - 0.5, dtype=torch.float32))
        return torch.tensor(0.5, dtype=torch.float32)

    def check_case_constraint(self, text: str, case_type: str) -> torch.Tensor:
        if case_type == "capital":
            upper_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
            return torch.tensor(upper_ratio, dtype=torch.float32)
        elif case_type == "lowercase":
            lower_ratio = sum(1 for c in text if c.islower()) / max(len(text), 1)
            return torch.tensor(lower_ratio, dtype=torch.float32)
        return torch.tensor(0.5, dtype=torch.float32)

    def forward(self, response: str, constraints: list[dict]) -> torch.Tensor:
        if not constraints:
            return self.scale * torch.tensor(0.5, dtype=torch.float32)

        scores = []
        for c in constraints:
            c_type = c.get("type", "unknown")

            if c_type == "keyword":
                score = self.check_keyword_constraint(
                    response, c.get("keywords", []), c.get("must_include", True)
                )
            elif c_type == "length":
                score = self.check_length_constraint(
                    response, c.get("target", 100), c.get("op", "at_least"), c.get("unit", "words")
                )
            elif c_type == "format":
                score = self.check_format_constraint(response, c.get("subtype", ""))
            elif c_type == "case":
                score = self.check_case_constraint(response, c.get("case_type", ""))
            else:
                score = torch.tensor(0.5, dtype=torch.float32)

            scores.append(score)

        stacked = torch.stack(scores)
        mean_score = stacked.mean()
        return self.scale * mean_score
