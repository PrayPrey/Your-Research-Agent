"""Counterfactual annotation for parsed traces."""
from dataclasses import dataclass
from trace_parser import ParsedTrace

@dataclass
class CFAnnotation:
    has_line: bool
    has_expected: bool
    has_actual: bool
    has_type_info: bool
    has_variable_state: bool
    identifies_root_cause: bool
    cf_score: float

class CounterfactualAnnotator:
    def annotate(self, trace: ParsedTrace, bug_line: int) -> CFAnnotation:
        """Compute counterfactual annotation from parsed trace."""
        has_line = len(trace.line_numbers) > 0
        has_expected = trace.expected is not None
        has_actual = trace.actual is not None
        has_type_info = trace.type_info is not None
        has_variable_state = len(trace.variable_state) > 0
        identifies_root_cause = bug_line in trace.line_numbers if has_line else False
        feature_sum = sum([has_line, has_expected, has_actual, has_type_info, has_variable_state])
        cf_score = feature_sum / 5.0
        return CFAnnotation(
            has_line=has_line,
            has_expected=has_expected,
            has_actual=has_actual,
            has_type_info=has_type_info,
            has_variable_state=has_variable_state,
            identifies_root_cause=identifies_root_cause,
            cf_score=cf_score,
        )

if __name__ == "__main__":
    annotator = CounterfactualAnnotator()
    trace = ParsedTrace(
        line_numbers=[5, 10],
        expected="4",
        actual="3",
        type_info="AssertionError",
        variable_state={"x": "1"},
        call_chain=["test_add"],
    )
    annotation = annotator.annotate(trace, bug_line=5)
    print(f"CF Score: {annotation.cf_score}")
    print(f"Identifies root cause: {annotation.identifies_root_cause}")
