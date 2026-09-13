import torch
import numpy as np
from tqdm import tqdm


TASK_PROMPTS = {
    "mnli": "Premise: {premise}\nHypothesis: {hypothesis}\nRelation:",
    "qqp": "Question 1: {question1}\nQuestion 2: {question2}\nDuplicate:",
    "sst2": "Sentence: {sentence}\nSentiment:"
}

TASK_CHOICES = {
    "mnli": ["entailment", "neutral", "contradiction"],
    "qqp": ["no", "yes"],
    "sst2": ["negative", "positive"]
}

TASK_FIELDS = {
    "mnli": ["premise", "hypothesis"],
    "qqp": ["question1", "question2"],
    "sst2": ["sentence"]
}


class ZeroShotEvaluator:
    def __init__(self, model, tokenizer, device: str):
        self.model = model
        self.tokenizer = tokenizer
        self.device = next(model.parameters()).device

    def _format_prompt(self, example: dict, task_name: str) -> str:
        template = TASK_PROMPTS[task_name]
        fields = TASK_FIELDS[task_name]
        kwargs = {field: example[fields[i]] for i, field in enumerate(fields)}
        return template.format(**kwargs)

    def classify(self, example: dict, task_name: str) -> int:
        prompt = self._format_prompt(example, task_name)
        choices = TASK_CHOICES[task_name]

        probs = []
        for choice in choices:
            full_text = prompt + " " + choice
            inputs = self.tokenizer(full_text, return_tensors="pt", max_length=512, truncation=True).to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs, labels=inputs["input_ids"])
                probs.append(-outputs.loss.item())

        return int(np.argmax(probs))

    def evaluate_task(self, dataset, task_name: str, max_samples: int = None) -> dict:
        correct = 0
        total = min(len(dataset), max_samples) if max_samples else len(dataset)

        for i in tqdm(range(total), desc=f"Evaluating {task_name}"):
            example = dataset[i]
            pred = self.classify(example, task_name)
            if pred == example["label"]:
                correct += 1

        accuracy = correct / total
        baseline = 1.0 / len(TASK_CHOICES[task_name])

        return {
            "accuracy": accuracy,
            "total": total,
            "correct": correct,
            "baseline": baseline
        }
