"""Extract structural coupling metrics from Python code via AST parsing."""

import ast
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

import networkx as nx

logger = logging.getLogger(__name__)


@dataclass
class CouplingMetrics:
    """Coupling metrics for a single submission."""

    problem_id: str
    submission_id: str
    coupling_score: float  # Composite: (fan_in + fan_out) / max_degree + centrality / 2.0
    fan_in: int  # Number of modules importing this module
    fan_out: int  # Number of modules this module imports
    centrality: float  # PageRank centrality in call graph


class CouplingMetricsExtractor:
    """Extract structural coupling metrics from Python code via AST parsing."""

    def __init__(self):
        """Initialize extractor with empty graphs."""
        self.dependency_graph: nx.DiGraph = nx.DiGraph()
        self.call_graph: nx.DiGraph = nx.DiGraph()
        self.modules: Dict[str, ast.AST] = {}

    def extract_imports(self, tree: ast.AST, module_name: str) -> List[str]:
        """Extract import statements from AST."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return list(set(imports))  # Remove duplicates

    def build_dependency_graph(self, code_files: Dict[str, str]) -> nx.DiGraph:
        """Build module dependency graph from code files."""
        self.dependency_graph = nx.DiGraph()

        for file_path, source_code in code_files.items():
            try:
                tree = ast.parse(source_code)
                module_name = file_path

                # Add module as node
                self.dependency_graph.add_node(module_name)

                # Extract imports and add edges
                imports = self.extract_imports(tree, module_name)
                for imported_module in imports:
                    self.dependency_graph.add_edge(module_name, imported_module)

            except (SyntaxError, ValueError) as e:
                logger.warning(f"Failed to parse {file_path}: {e}")
                continue

        return self.dependency_graph

    def build_call_graph(self, tree: ast.AST, module_name: str) -> None:
        """Build function call graph from AST."""
        # Extract all function definitions
        functions = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_name = f"{module_name}.{node.name}"
                functions[node.name] = func_name
                self.call_graph.add_node(func_name)

        # Extract function calls
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Get caller context (find parent function)
                caller = None
                if hasattr(node, "_parent_func"):
                    caller = node._parent_func

                # Get callee name
                callee = None
                if isinstance(node.func, ast.Name):
                    callee = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    callee = node.func.attr

                # Add edge if both caller and callee are known
                if caller and callee and callee in functions:
                    caller_full = f"{module_name}.{caller}"
                    callee_full = functions[callee]
                    self.call_graph.add_edge(caller_full, callee_full)

    def compute_coupling_score(self, module_name: str) -> float:
        """Compute composite coupling score."""
        # Fan-in and fan-out
        fan_in = self.dependency_graph.in_degree(module_name) if self.dependency_graph.has_node(module_name) else 0
        fan_out = self.dependency_graph.out_degree(module_name) if self.dependency_graph.has_node(module_name) else 0

        # Centrality
        centrality = 0.0
        if len(self.call_graph.nodes()) > 0:
            try:
                pagerank = nx.pagerank(self.call_graph)
                # Find the highest centrality among functions in this module
                module_functions = [n for n in self.call_graph.nodes() if n.startswith(f"{module_name}.")]
                if module_functions:
                    centrality = max(pagerank.get(f, 0.0) for f in module_functions)
            except (nx.PowerIterationFailedConvergence, ZeroDivisionError):
                centrality = 0.0

        # Normalize structural score
        max_degree = max(
            (self.dependency_graph.degree(n) for n in self.dependency_graph.nodes()),
            default=1
        )
        structural_score = (fan_in + fan_out) / max(max_degree, 1)

        # Composite score
        composite_score = (structural_score + centrality) / 2.0
        return composite_score

    def analyze_submission(
        self, problem_id: str, submission_id: str, code_files: Dict[str, str]
    ) -> Optional[CouplingMetrics]:
        """Analyze a single submission and return coupling metrics."""
        # Reset graphs
        self.dependency_graph = nx.DiGraph()
        self.call_graph = nx.DiGraph()
        self.modules = {}

        try:
            # Build dependency graph
            self.build_dependency_graph(code_files)

            # Build call graph for each file
            for file_path, source_code in code_files.items():
                try:
                    tree = ast.parse(source_code)
                    self.build_call_graph(tree, file_path)
                except (SyntaxError, ValueError):
                    continue

            # Find main module (highest out-degree or first file)
            if len(self.dependency_graph.nodes()) == 0:
                main_module = list(code_files.keys())[0] if code_files else "main"
                self.dependency_graph.add_node(main_module)
            else:
                main_module = max(
                    self.dependency_graph.nodes(),
                    key=lambda n: self.dependency_graph.out_degree(n)
                )

            # Compute metrics
            coupling_score = self.compute_coupling_score(main_module)
            fan_in = self.dependency_graph.in_degree(main_module) if self.dependency_graph.has_node(main_module) else 0
            fan_out = self.dependency_graph.out_degree(main_module) if self.dependency_graph.has_node(main_module) else 0

            # Compute centrality for main module
            centrality = 0.0
            if len(self.call_graph.nodes()) > 0:
                try:
                    pagerank = nx.pagerank(self.call_graph)
                    module_functions = [n for n in self.call_graph.nodes() if n.startswith(f"{main_module}.")]
                    if module_functions:
                        centrality = max(pagerank.get(f, 0.0) for f in module_functions)
                except (nx.PowerIterationFailedConvergence, ZeroDivisionError):
                    centrality = 0.0

            return CouplingMetrics(
                problem_id=problem_id,
                submission_id=submission_id,
                coupling_score=coupling_score,
                fan_in=fan_in,
                fan_out=fan_out,
                centrality=centrality,
            )

        except Exception as e:
            logger.error(f"Failed to analyze submission {submission_id}: {e}")
            return None
