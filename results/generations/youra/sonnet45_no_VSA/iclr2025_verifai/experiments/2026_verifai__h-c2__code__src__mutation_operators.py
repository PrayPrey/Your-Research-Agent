from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass
import pycparser
from pycparser import c_ast, c_generator
import copy

@dataclass
class Mutant:
    mutant_id: str
    original_code: str
    mutated_code: str
    operator_type: str
    location: dict

class MutationOperator(ABC):
    @abstractmethod
    def apply(self, ast: c_ast.FileAST, original_code: str) -> List[Mutant]:
        pass

    def get_operator_name(self) -> str:
        return self.__class__.__name__

class ArithmeticMutation(MutationOperator):
    def apply(self, ast: c_ast.FileAST, original_code: str) -> List[Mutant]:
        mutants = []
        mutant_counter = [0]

        class ArithmeticVisitor(c_ast.NodeVisitor):
            def visit_BinaryOp(self, node):
                mutations = {
                    '+': '-',
                    '-': '+',
                    '*': '/',
                    '/': '*'
                }

                if node.op in mutations:
                    mutated_ast = copy.deepcopy(ast)
                    target_node = self._find_matching_node(mutated_ast, node)
                    if target_node:
                        target_node.op = mutations[node.op]
                        gen = c_generator.CGenerator()
                        mutated_code = gen.visit(mutated_ast)

                        mutants.append(Mutant(
                            mutant_id=f"arith_{mutant_counter[0]}",
                            original_code=original_code,
                            mutated_code=mutated_code,
                            operator_type="ArithmeticMutation",
                            location={"line": node.coord.line if node.coord else 0}
                        ))
                        mutant_counter[0] += 1

                self.generic_visit(node)

            def _find_matching_node(self, tree, target):
                for node in c_ast.NodeVisitor().generic_visit(tree) or []:
                    if isinstance(node, type(target)) and node.op == target.op:
                        return node
                return None

        visitor = ArithmeticVisitor()
        visitor.visit(ast)
        return mutants

class RelationalMutation(MutationOperator):
    def apply(self, ast: c_ast.FileAST, original_code: str) -> List[Mutant]:
        mutants = []
        mutant_counter = [0]

        class RelationalVisitor(c_ast.NodeVisitor):
            def visit_BinaryOp(self, node):
                mutations = {
                    '<': '<=',
                    '<=': '<',
                    '>': '>=',
                    '>=': '>',
                    '==': '!=',
                    '!=': '=='
                }

                if node.op in mutations:
                    mutated_ast = copy.deepcopy(ast)
                    gen = c_generator.CGenerator()

                    try:
                        node.op = mutations[node.op]
                        mutated_code = gen.visit(mutated_ast)

                        mutants.append(Mutant(
                            mutant_id=f"rel_{mutant_counter[0]}",
                            original_code=original_code,
                            mutated_code=mutated_code,
                            operator_type="RelationalMutation",
                            location={"line": node.coord.line if node.coord else 0}
                        ))
                        mutant_counter[0] += 1
                    except Exception:
                        pass

                self.generic_visit(node)

        visitor = RelationalVisitor()
        visitor.visit(ast)
        return mutants

class BooleanMutation(MutationOperator):
    def apply(self, ast: c_ast.FileAST, original_code: str) -> List[Mutant]:
        mutants = []
        mutant_counter = [0]

        class BooleanVisitor(c_ast.NodeVisitor):
            def visit_BinaryOp(self, node):
                mutations = {
                    '&&': '||',
                    '||': '&&'
                }

                if node.op in mutations:
                    mutated_ast = copy.deepcopy(ast)
                    gen = c_generator.CGenerator()

                    try:
                        node.op = mutations[node.op]
                        mutated_code = gen.visit(mutated_ast)

                        mutants.append(Mutant(
                            mutant_id=f"bool_{mutant_counter[0]}",
                            original_code=original_code,
                            mutated_code=mutated_code,
                            operator_type="BooleanMutation",
                            location={"line": node.coord.line if node.coord else 0}
                        ))
                        mutant_counter[0] += 1
                    except Exception:
                        pass

                self.generic_visit(node)

        visitor = BooleanVisitor()
        visitor.visit(ast)
        return mutants

class StatementMutation(MutationOperator):
    def apply(self, ast: c_ast.FileAST, original_code: str) -> List[Mutant]:
        return []

class BoundaryMutation(MutationOperator):
    def apply(self, ast: c_ast.FileAST, original_code: str) -> List[Mutant]:
        return []
