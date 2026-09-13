from typing import List
from pathlib import Path
import pycparser
from pycparser import c_parser, c_generator
import subprocess
import tempfile
from mutation_operators import Mutant, MutationOperator

class CASTParser:
    def __init__(self):
        self.parser = c_parser.CParser()

    def parse(self, c_code: str):
        return self.parser.parse(c_code, filename='<none>')

    def unparse(self, ast) -> str:
        generator = c_generator.CGenerator()
        return generator.visit(ast)

    def check_compilability(self, c_code: str) -> bool:
        with tempfile.NamedTemporaryFile(suffix='.c', delete=False, mode='w') as f:
            f.write(c_code)
            f.flush()

            result = subprocess.run(
                ['gcc', '-c', f.name, '-o', '/dev/null'],
                capture_output=True,
                timeout=5
            )
            Path(f.name).unlink(missing_ok=True)
            return result.returncode == 0

class MutantGenerator:
    def __init__(self, operators: List[MutationOperator]):
        self.operators = operators
        self.parser = CASTParser()

    def generate_mutants(self, c_program: str) -> List[Mutant]:
        try:
            ast = self.parser.parse(c_program)
            all_mutants = []

            for operator in self.operators:
                mutants = operator.apply(ast, c_program)
                all_mutants.extend(mutants)

            return self.filter_compilable(all_mutants)
        except Exception as e:
            print(f"Error generating mutants: {e}")
            return []

    def filter_compilable(self, mutants: List[Mutant]) -> List[Mutant]:
        compilable = []
        for mutant in mutants:
            try:
                if self.parser.check_compilability(mutant.mutated_code):
                    compilable.append(mutant)
            except Exception:
                continue
        return compilable

    def count_by_operator(self, mutants: List[Mutant]) -> dict:
        from collections import Counter
        return Counter(m.operator_type for m in mutants)
