import re
import string
from collections import Counter
from typing import Dict, List

import torch
from torch import Tensor
from transformers import PreTrainedTokenizer


class LongBenchEvaluator:
    TASKS: List[str] = ["narrativeqa", "qasper", "multifieldqa_en"]

    def __init__(self, model, data_manager, tokenizer: PreTrainedTokenizer,
                 budget_ratio: float = 0.5) -> None:
        self.model = model
        self.data_manager = data_manager
        self.tokenizer = tokenizer
        self.budget_ratio = budget_ratio

    def evaluate_task(self, task_name: str) -> float:
        loader = self.data_manager.get_longbench_test_loaders()[task_name]
        scores = []
        self.model.eval()
        device = next(self.model.parameters()).device

        for batch in loader:
            text = batch["input"][0] if isinstance(batch["input"], list) else batch["input"]
            answers = batch["answers"]
            if isinstance(answers, (list, tuple)) and len(answers) > 0:
                if isinstance(answers[0], (list, tuple)):
                    gt_list = [a[0] for a in answers]
                else:
                    gt_list = list(answers)
            else:
                gt_list = [str(answers)]

            enc = self.tokenizer(
                str(text), return_tensors="pt",
                max_length=4096, truncation=True
            )
            input_ids = enc["input_ids"].to(device)
            attention_mask = enc["attention_mask"].to(device)

            pred = self._generate_with_hard_eviction(input_ids, attention_mask)
            f1 = max(self.qa_f1_score(pred, gt) for gt in gt_list)
            scores.append(f1)

        return sum(scores) / max(len(scores), 1)

    def evaluate_all(self) -> Dict[str, float]:
        results = {}
        for task in self.TASKS:
            f1 = self.evaluate_task(task)
            results[task] = f1
            print(f"  LongBench {task}: F1={f1:.4f}")
        results["mean_f1"] = sum(results[t] for t in self.TASKS) / len(self.TASKS)
        return results

    @staticmethod
    def qa_f1_score(prediction: str, ground_truth: str) -> float:
        def normalize(s: str) -> str:
            s = s.lower()
            s = re.sub(r"\b(a|an|the)\b", " ", s)
            s = "".join(c for c in s if c not in string.punctuation)
            return " ".join(s.split())

        pred_tokens = normalize(prediction).split()
        gt_tokens = normalize(ground_truth).split()
        common = Counter(pred_tokens) & Counter(gt_tokens)
        num_common = sum(common.values())
        if num_common == 0:
            return 0.0
        precision = num_common / len(pred_tokens)
        recall = num_common / len(gt_tokens)
        f1 = 2 * precision * recall / (precision + recall)
        return f1

    def _generate_with_hard_eviction(
        self,
        input_ids: Tensor,
        attention_mask: Tensor,
        max_new_tokens: int = 50,
    ) -> str:
        with torch.no_grad():
            outputs = self.model.base_model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        generated = outputs[0][input_ids.shape[1]:]
        return self.tokenizer.decode(generated, skip_special_tokens=True)


class GLUEEvaluator:
    TASKS: List[str] = ["mnli", "sst2", "qnli"]

    def __init__(self, model, data_manager) -> None:
        self.model = model
        self.data_manager = data_manager

    def evaluate_task(self, task_name: str) -> float:
        loader = self.data_manager.get_glue_val_loaders()[task_name]
        correct = 0
        total = 0
        self.model.eval()
        device = next(self.model.parameters()).device

        with torch.no_grad():
            for batch in loader:
                input_ids = batch["input_ids"].to(device)
                attention_mask = batch["attention_mask"].to(device)
                labels = batch["labels"].to(device)

                logits, _, _ = self.model(input_ids, attention_mask, training_mode=False)
                num_labels = max(int(labels.max().item()) + 1, 2)
                cls_logits = logits[:, -1, :num_labels]
                preds = cls_logits.argmax(dim=-1)
                correct += (preds == labels).sum().item()
                total += labels.size(0)

        return correct / max(total, 1)

    def evaluate_all(self) -> Dict[str, float]:
        results = {}
        for task in self.TASKS:
            acc = self.evaluate_task(task)
            results[task] = acc
            print(f"  GLUE {task}: acc={acc:.4f}")
        results["mean_accuracy"] = sum(results[t] for t in self.TASKS) / len(self.TASKS)
        return results
