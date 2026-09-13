"""Parse execution traces to extract counterfactual information."""
import re
from dataclasses import dataclass, field
from sandbox_executor import ExecutionResult

@dataclass
class ParsedTrace:
    line_numbers: list[int] = field(default_factory=list)
    expected: str | None = None
    actual: str | None = None
    type_info: str | None = None
    variable_state: dict = field(default_factory=dict)
    call_chain: list[str] = field(default_factory=list)

class TraceParser:
    def parse(self, result: ExecutionResult) -> ParsedTrace:
        """Extract counterfactual information from execution result."""
        text = result.traceback or result.stderr
        if not text:
            return ParsedTrace()
        line_numbers = self._extract_line_numbers(text)
        expected, actual = self._extract_expected_actual(text)
        type_info = self._extract_type_info(text)
        variable_state = self._extract_variable_state(text)
        call_chain = self._extract_call_chain(text)
        return ParsedTrace(line_numbers, expected, actual, type_info, variable_state, call_chain)

    def _extract_line_numbers(self, text: str) -> list[int]:
        pattern = r'File "[^"]+", line (\d+)'
        return [int(m) for m in re.findall(pattern, text)]

    def _extract_expected_actual(self, text: str) -> tuple[str | None, str | None]:
        pattern_assert = r'assert\s+(.+?)\s*==\s*(.+?)(?:\s|$)'
        m = re.search(pattern_assert, text)
        if m:
            return m.group(2).strip(), m.group(1).strip()
        pattern_ea = r'Expected[:\s]+(.+?)\n.*?Actual[:\s]+(.+)'
        m2 = re.search(pattern_ea, text, re.IGNORECASE)
        if m2:
            return m2.group(1).strip(), m2.group(2).strip()
        pattern_assert2 = r'AssertionError:\s*(.+?)\s*!=\s*(.+?)(?:\s|$)'
        m3 = re.search(pattern_assert2, text)
        if m3:
            return m3.group(2).strip(), m3.group(1).strip()
        return None, None

    def _extract_type_info(self, text: str) -> str | None:
        pattern = r'\b(\w*Error|\w*Exception)\b'
        matches = re.findall(pattern, text)
        return matches[-1] if matches else None

    def _extract_variable_state(self, text: str) -> dict:
        pattern = r'^(\w+)\s*=\s*(.+)$'
        result = {}
        for m in re.finditer(pattern, text, re.MULTILINE):
            var_name = m.group(1)
            if var_name not in ("File", "Traceback", "Error", "Exception"):
                result[var_name] = m.group(2).strip()
        return result

    def _extract_call_chain(self, text: str) -> list[str]:
        pattern = r'File "[^"]+", line \d+, in (\S+)'
        return re.findall(pattern, text)

if __name__ == "__main__":
    parser = TraceParser()
    result = ExecutionResult(
        stdout="",
        stderr='''Traceback (most recent call last):
  File "test.py", line 5, in test_add
    assert add(1, 2) == 4
AssertionError
''',
        exit_code=1,
        traceback='''Traceback (most recent call last):
  File "test.py", line 5, in test_add
    assert add(1, 2) == 4
AssertionError
''',
        timed_out=False
    )
    parsed = parser.parse(result)
    print(f"Lines: {parsed.line_numbers}")
    print(f"Expected: {parsed.expected}, Actual: {parsed.actual}")
    print(f"Type: {parsed.type_info}")
    print(f"Call chain: {parsed.call_chain}")
