"""TokenClassifier: Generate binary execution mask from trace + line map."""

from typing import Dict, List, Set, Any
from token_mapper import LineToTokenMapper


class TokenClassifier:
    """Classifies tokens as executed (1) or non-executed (0) based on trace data."""

    def __init__(self, mapper: LineToTokenMapper):
        self.mapper = mapper

    def classify_tokens(
        self,
        code_str: str,
        executed_lines: Set[int]
    ) -> List[int]:
        """Generate binary mask for tokens based on executed lines.

        Args:
            code_str: Source code string
            executed_lines: Set of line numbers (1-indexed) that were executed

        Returns:
            List of 0/1 values, one per token. 1 = executed, 0 = not executed.
        """
        line_map = self.mapper.build_line_map(code_str)
        enc = self.mapper.tokenizer(code_str, return_offsets_mapping=True, add_special_tokens=False)
        num_tokens = len(enc["input_ids"])

        mask = []
        for token_idx in range(num_tokens):
            line_num = line_map.get(token_idx, -1)
            if line_num > 0 and line_num in executed_lines:
                mask.append(1)
            else:
                mask.append(0)

        return mask

    def classify_with_details(
        self,
        code_str: str,
        executed_lines: Set[int]
    ) -> Dict[str, Any]:
        """Classify tokens and return detailed info for debugging."""
        enc = self.mapper.tokenizer(code_str, return_offsets_mapping=True, add_special_tokens=False)
        line_map = self.mapper.map_offsets_to_lines(code_str, enc["offset_mapping"])

        tokens = self.mapper.tokenizer.convert_ids_to_tokens(enc["input_ids"])
        mask = []
        details = []

        for token_idx, token in enumerate(tokens):
            line_num = line_map.get(token_idx, -1)
            executed = line_num > 0 and line_num in executed_lines
            mask.append(1 if executed else 0)
            details.append({
                "idx": token_idx,
                "token": token,
                "line": line_num,
                "executed": executed
            })

        return {
            "mask": mask,
            "details": details,
            "num_tokens": len(tokens),
            "num_executed": sum(mask),
            "executed_lines": sorted(executed_lines)
        }
