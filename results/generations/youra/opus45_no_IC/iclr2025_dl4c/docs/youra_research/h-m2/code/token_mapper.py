"""LineToTokenMapper: Map tokenizer offset_mapping to source line numbers."""

from bisect import bisect_right
from typing import Dict, List, Tuple, Any


class LineToTokenMapper:
    """Maps token positions to source code line numbers using tokenizer offset_mapping."""

    def __init__(self, tokenizer: Any):
        """
        Args:
            tokenizer: transformers.PreTrainedTokenizerFast with return_offsets_mapping support.
        """
        self.tokenizer = tokenizer

    def build_line_map(self, code_str: str, tokens: List[str] = None) -> Dict[int, int]:
        """Tokenize code_str and return token_idx -> line_num (1-indexed) mapping."""
        enc = self.tokenizer(code_str, return_offsets_mapping=True, add_special_tokens=False)
        return self.map_offsets_to_lines(code_str, enc["offset_mapping"])

    def map_offsets_to_lines(
        self,
        code_str: str,
        offset_mapping: List[Tuple[int, int]]
    ) -> Dict[int, int]:
        """Map offset_mapping to line numbers.

        Args:
            code_str: Source code string
            offset_mapping: List of (char_start, char_end) per token from tokenizer

        Returns:
            Dict mapping token_idx -> line_num (1-indexed). Special tokens (0,0) excluded.
        """
        line_starts = [0]
        for i, c in enumerate(code_str):
            if c == '\n':
                line_starts.append(i + 1)

        result = {}
        for token_idx, (start, end) in enumerate(offset_mapping):
            if start == end == 0:
                continue
            line_num = bisect_right(line_starts, start)
            result[token_idx] = line_num

        return result

    def get_token_line_pairs(
        self,
        code_str: str
    ) -> List[Tuple[int, str, int]]:
        """Get (token_idx, token_text, line_num) triples for debugging."""
        enc = self.tokenizer(code_str, return_offsets_mapping=True, add_special_tokens=False)
        line_map = self.map_offsets_to_lines(code_str, enc["offset_mapping"])

        tokens = self.tokenizer.convert_ids_to_tokens(enc["input_ids"])
        result = []
        for idx, token in enumerate(tokens):
            line = line_map.get(idx, -1)
            result.append((idx, token, line))

        return result
