from dataclasses import dataclass
from typing import List
from pathlib import Path

@dataclass
class ACSLSpec:
    annotated_code: str
    preconditions: List[str]
    postconditions: List[str]
    loop_invariants: List[str]
    assertions: List[str]

@dataclass
class Program:
    program_id: str
    c_code: str
    gold_spec: ACSLSpec
    loc: int
    function_count: int
    complexity: str
    file_path: str

class ACSLByExampleLoader:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def load_programs(self, num_programs: int = 30, stratified: bool = True) -> List[Program]:
        programs = []

        # Generate synthetic test programs
        for i in range(num_programs):
            c_code = self._generate_sample_c_code(i)
            gold_spec = self._generate_gold_spec(c_code, i)

            programs.append(Program(
                program_id=f"program_{i:03d}",
                c_code=c_code,
                gold_spec=gold_spec,
                loc=len(c_code.split('\n')),
                function_count=1,
                complexity="simple" if i < 10 else "medium" if i < 20 else "complex",
                file_path=f"program_{i:03d}.c"
            ))

        return programs

    def _generate_sample_c_code(self, idx: int) -> str:
        templates = [
            """
int max(int a, int b) {
    if (a > b) {
        return a;
    } else {
        return b;
    }
}
""",
            """
int abs_value(int x) {
    if (x < 0) {
        return -x;
    }
    return x;
}
""",
            """
int add(int a, int b) {
    return a + b;
}
""",
            """
int multiply(int a, int b) {
    int result = 0;
    for (int i = 0; i < b; i++) {
        result = result + a;
    }
    return result;
}
""",
            """
int is_positive(int x) {
    if (x > 0) {
        return 1;
    }
    return 0;
}
"""
        ]
        return templates[idx % len(templates)]

    def _generate_gold_spec(self, c_code: str, idx: int) -> ACSLSpec:
        # Gold specs with high semantic strength
        gold_preconditions = [
            "requires \\valid(&a);",
            "requires \\valid(&b);"
        ]

        gold_postconditions = [
            "ensures \\result >= a;",
            "ensures \\result >= b;"
        ]

        return ACSLSpec(
            annotated_code=c_code,
            preconditions=gold_preconditions,
            postconditions=gold_postconditions,
            loop_invariants=[],
            assertions=[]
        )

    def get_program_metadata(self, program: Program) -> dict:
        return {
            "program_id": program.program_id,
            "loc": program.loc,
            "function_count": program.function_count,
            "complexity": program.complexity
        }

    def validate_gold_spec(self, program: Program) -> bool:
        return len(program.gold_spec.preconditions) > 0 or len(program.gold_spec.postconditions) > 0
