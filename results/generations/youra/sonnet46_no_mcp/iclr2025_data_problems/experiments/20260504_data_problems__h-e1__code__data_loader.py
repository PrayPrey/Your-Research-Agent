from __future__ import annotations
import logging
from typing import TYPE_CHECKING

from datasets import load_dataset

if TYPE_CHECKING:
    from config import Config

logger = logging.getLogger(__name__)

BBH_SUBTASKS = [
    "boolean_expressions", "causal_judgement", "date_understanding",
    "disambiguation_qa", "dyck_languages", "formal_fallacies",
    "geometric_shapes", "hyperbaton", "logical_deduction_five_objects",
    "logical_deduction_seven_objects", "logical_deduction_three_objects",
    "movie_recommendation", "multistep_arithmetic_two",
    "navigate", "object_counting", "penguins_in_a_table",
    "reasoning_about_colored_objects", "ruin_names",
    "salient_translation_error_detection", "snarks",
    "sports_understanding", "temporal_sequences",
    "tracking_shuffled_objects_five_objects",
    "tracking_shuffled_objects_seven_objects",
    "tracking_shuffled_objects_three_objects",
    "web_of_lies", "word_sorting",
]


class DataLoader:
    def __init__(self, config: "Config"):
        self.config = config

    def format_text(self, item: dict, dataset: str) -> str:
        """Format benchmark item to text string per config.text_format."""
        if self.config.text_format == "question_only":
            if dataset == "mmlu":
                return item["question"]
            elif dataset == "hellaswag":
                return item["ctx"]
            else:  # bbh
                return item["input"]
        else:  # question_choices (default)
            if dataset == "mmlu":
                return f"{item['question']} {' '.join(item['choices'])}"
            elif dataset == "hellaswag":
                return f"{item['ctx']} {' '.join(item['endings'])}"
            else:  # bbh — no choices field
                return item["input"]

    def load_mmlu(self) -> dict[str, list[str]]:
        """Load all 57 MMLU sub-tasks from cais/mmlu split='test'."""
        result = {}
        for task in self.config.mmlu_tasks:
            try:
                ds = load_dataset(
                    self.config.mmlu_hf_id,
                    task,
                    split=self.config.mmlu_split,
                )
                result[task] = [self.format_text(item, "mmlu") for item in ds]
            except Exception as e:
                logger.warning(f"Failed to load MMLU sub-task '{task}': {e}")
        return result

    def load_hellaswag(self) -> dict[str, list[str]]:
        """Load HellaSwag from Rowan/hellaswag split='validation'."""
        ds = load_dataset(
            self.config.hellaswag_hf_id,
            split=self.config.hellaswag_split,
        )
        return {"hellaswag": [self.format_text(item, "hellaswag") for item in ds]}

    def load_bbh(self) -> dict[str, list[str]]:
        """Load BIG-Bench Hard from lukaemon/bbh; merge all sub-tasks into 'bbh'."""
        all_texts = []
        for subtask in BBH_SUBTASKS:
            try:
                ds = load_dataset(
                    self.config.bbh_hf_id,
                    subtask,
                    split=self.config.bbh_split,
                )
                for item in ds:
                    all_texts.append(self.format_text(item, "bbh"))
            except Exception as e:
                logger.warning(f"Failed to load BBH sub-task '{subtask}': {e}")
        return {"bbh": all_texts}

    def load_all(self) -> dict[str, list[str]]:
        """Merge MMLU (57) + HellaSwag (1) + BBH (1) = 59 sub-tasks."""
        return {**self.load_mmlu(), **self.load_hellaswag(), **self.load_bbh()}
