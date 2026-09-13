"""Map character spans to token indices."""


class SpanMapper:
    """Map NER character spans to tokenizer token spans."""

    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def char_to_token_span(self, text, char_span):
        """Map (start_char, end_char) -> (start_token, end_token)."""
        inputs = self.tokenizer(text, return_offsets_mapping=True, add_special_tokens=True)

        start_char, end_char = char_span
        start_token = None
        end_token = None

        # offset_mapping is a list of (start, end) tuples (no batch dim)
        for i, (token_start, token_end) in enumerate(inputs.offset_mapping):
            if token_start <= start_char < token_end:
                start_token = i
            if token_start < end_char <= token_end:
                end_token = i + 1
                break

        if start_token is None or end_token is None:
            raise ValueError(f"Span {char_span} not aligned to tokens in: {text[:50]}...")

        return (start_token, end_token)
