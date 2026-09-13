"""AST-based contract decorator injector."""

import ast
from dataclasses import dataclass
from typing import List, Optional


class InjectionError(Exception):
    """Raised when contract injection fails."""
    pass


@dataclass
class ContractInjectionPoint:
    """Location for contract injection."""
    function_name: str
    class_name: Optional[str]
    line_number: int
    contract_type: str


class DecoratorInjector:
    """Injects contract decorators into Python scripts via AST manipulation."""

    def find_injection_points(self, script: str) -> List[ContractInjectionPoint]:
        """
        Identify functions/methods for contract injection.

        Args:
            script: Python source code string

        Returns:
            List of injection points
        """
        injection_points = []

        try:
            tree = ast.parse(script)
        except SyntaxError:
            return []

        # Find nn.Module classes and forward methods
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if inherits from nn.Module
                is_module = any(
                    isinstance(base, ast.Attribute) and base.attr == "Module"
                    or isinstance(base, ast.Name) and "Module" in base.id
                    for base in node.bases
                )

                if is_module:
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name == "forward":
                            injection_points.append(
                                ContractInjectionPoint(
                                    function_name="forward",
                                    class_name=node.name,
                                    line_number=item.lineno,
                                    contract_type="structural"
                                )
                            )

        return injection_points

    def inject_contracts(
        self,
        script: str,
        injection_points: List[ContractInjectionPoint],
        contract_type: str
    ) -> str:
        """
        Inject contract decorators into script.

        Args:
            script: Original Python source
            injection_points: Functions to decorate
            contract_type: "structural" | "metamorphic"

        Returns:
            Modified source with decorators

        Raises:
            InjectionError: If AST parsing fails
        """
        try:
            tree = ast.parse(script)
        except SyntaxError as e:
            raise InjectionError(f"Failed to parse script: {e}")

        # Add import at top
        import_node = ast.ImportFrom(
            module='contracts.validator',
            names=[
                ast.alias(name=f'validate_{contract_type}', asname=None)
            ],
            level=0
        )

        # Insert import after docstring if present
        insert_pos = 0
        if (tree.body and isinstance(tree.body[0], ast.Expr) and
                isinstance(tree.body[0].value, ast.Constant)):
            insert_pos = 1

        tree.body.insert(insert_pos, import_node)

        # Inject decorators
        for point in injection_points:
            if point.contract_type == contract_type:
                func_node = self._find_function_at_line(tree, point.line_number)
                if func_node:
                    decorator_node = ast.Name(
                        id=f'validate_{contract_type}',
                        ctx=ast.Load()
                    )
                    func_node.decorator_list.append(decorator_node)

        # Convert back to source
        modified_source = ast.unparse(tree)
        return modified_source

    def inject_structural_contracts(self, script: str) -> str:
        """Convenience: inject structural contracts."""
        points = self.find_injection_points(script)
        structural_points = [p for p in points if p.contract_type == "structural"]
        if not structural_points:
            return script
        return self.inject_contracts(script, structural_points, "structural")

    def inject_metamorphic_contracts(self, script: str) -> str:
        """Convenience: inject metamorphic contracts."""
        points = self.find_injection_points(script)
        metamorphic_points = [p for p in points if p.contract_type == "metamorphic"]
        if not metamorphic_points:
            return script
        return self.inject_contracts(script, metamorphic_points, "metamorphic")

    def _find_function_at_line(self, tree: ast.AST, line_number: int) -> Optional[ast.FunctionDef]:
        """Find function definition at specific line number."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.lineno == line_number:
                return node
        return None
