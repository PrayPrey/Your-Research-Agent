from __future__ import annotations


class DomainClassifier:
    """Maps benchmark sub-tasks to academic or commonsense domain."""

    COMMONSENSE_TASKS: frozenset = frozenset({
        "hellaswag",
        "bbh_causal_judgement",
        "bbh_date_understanding",
        "bbh_disambiguation_qa",
        "bbh_formal_fallacies",
        "bbh_geometric_shapes",
        "bbh_hyperbaton",
        "bbh_logical_deduction_five_objects",
        "bbh_logical_deduction_seven_objects",
        "bbh_logical_deduction_three_objects",
        "bbh_movie_recommendation",
        "bbh_navigate",
        "bbh_penguins_in_a_table",
        "bbh_reasoning_about_colored_objects",
        "bbh_ruin_names",
        "bbh_salient_translation_error_detection",
        "bbh_snarks",
        "bbh_sports_understanding",
        "bbh_temporal_sequences",
        "bbh_tracking_shuffled_objects_five_objects",
        "bbh_tracking_shuffled_objects_seven_objects",
        "bbh_tracking_shuffled_objects_three_objects",
        "bbh_web_of_lies",
        "bbh_word_sorting",
        # generic bbh catch-all handled in classify()
    })

    def classify(self, subtask_name: str) -> str:
        """Returns 'academic' or 'commonsense'."""
        if subtask_name in self.COMMONSENSE_TASKS:
            return "commonsense"
        # bbh (aggregate) and any bbh_* prefixed tasks are commonsense reasoning
        if subtask_name == "bbh" or subtask_name.startswith("bbh_") or subtask_name == "hellaswag":
            return "commonsense"
        return "academic"

    def build_domain_map(self, subtask_names: list[str]) -> dict[str, str]:
        """Returns {subtask_name: 'academic'|'commonsense'} for all subtasks."""
        return {name: self.classify(name) for name in subtask_names}

    def get_groups(
        self,
        matrix: dict,
        domain_map: dict[str, str],
        corpus: str,
    ) -> tuple[list[float], list[float]]:
        """Returns (academic_rates, commonsense_rates) for given corpus."""
        academic_rates = [
            matrix[t][corpus] for t in matrix if domain_map.get(t) == "academic"
        ]
        commonsense_rates = [
            matrix[t][corpus] for t in matrix if domain_map.get(t) == "commonsense"
        ]
        return academic_rates, commonsense_rates
