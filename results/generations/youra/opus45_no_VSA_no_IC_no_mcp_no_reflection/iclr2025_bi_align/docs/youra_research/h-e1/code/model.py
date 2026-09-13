"""H-E1 Model: IFEvalRewardSignal with soft scoring for gradient flow."""
import re
import math
import torch
import torch.nn as nn
from transformers import AutoModelForCausalLM, AutoTokenizer
from config import Config


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

        elif c_type == "startend":
            return self._check_startend(response, c)

        elif c_type == "punctuation":
            return self._check_punctuation(response, c.get("rule", ""))

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
        elif subtype == "title":
            return 1.0 if re.search(r'^#+\s|\*\*[^*]+\*\*', text, re.MULTILINE) else 0.0
        return 0.5

    def _check_case(self, text: str, case_type: str) -> float:
        if case_type == "capital":
            return 1.0 if text == text.upper() else 0.0
        elif case_type == "lowercase":
            return 1.0 if text == text.lower() else 0.0
        return 0.5

    def _check_startend(self, text: str, c: dict) -> float:
        if c.get("check") == "end":
            phrase = c.get("end_phrase", "")
            if phrase:
                return 1.0 if text.strip().endswith(phrase) else 0.0
        return 0.5

    def _check_punctuation(self, text: str, rule: str) -> float:
        if rule == "no_comma":
            return 1.0 if ',' not in text else 0.0
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
        elif fmt == "title":
            match = re.search(r'^#+\s|\*\*[^*]+\*\*', text, re.MULTILINE)
            return torch.tensor(1.0 if match else 0.0, dtype=torch.float32)
        return torch.tensor(0.5, dtype=torch.float32)

    def check_structural_constraint(self, text: str, spec: dict) -> torch.Tensor:
        subtype = spec.get("subtype", "")
        if subtype == "sections":
            sections = len(re.findall(r'^#{1,3}\s', text, re.MULTILINE))
            return torch.sigmoid(torch.tensor(float(sections) - 0.5, dtype=torch.float32))
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
            elif c_type == "structural":
                score = self.check_structural_constraint(response, c)
            elif c_type == "case":
                score = self.check_case_constraint(response, c.get("case_type", ""))
            else:
                score = torch.tensor(0.5, dtype=torch.float32)

            scores.append(score)

        stacked = torch.stack(scores)
        mean_score = stacked.mean()
        return self.scale * mean_score


def load_generator(cfg: Config):
    """Load model and tokenizer."""
    import torch
    device = cfg.device if torch.cuda.is_available() else "cpu"

    tokenizer = AutoTokenizer.from_pretrained(cfg.model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        cfg.model_id,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        device_map="auto" if device == "cuda" else None,
        low_cpu_mem_usage=True,
    )
    model.eval()

    return model, tokenizer, device


def generate_responses(model, tokenizer, prompts: list[str], cfg: Config, device: str) -> list[str]:
    """Batch generate responses."""
    import torch

    torch.manual_seed(cfg.seed)
    responses = []

    for i in range(0, len(prompts), cfg.batch_size):
        batch = prompts[i:i + cfg.batch_size]

        inputs = tokenizer(
            batch,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=1024,
        )
        if device == "cuda":
            inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=cfg.max_new_tokens,
                do_sample=True,
                temperature=cfg.temperature,
                pad_token_id=tokenizer.pad_token_id,
            )

        for j, output in enumerate(outputs):
            input_len = inputs["input_ids"][j].shape[0]
            response = tokenizer.decode(output[input_len:], skip_special_tokens=True)
            responses.append(response)

    return responses
