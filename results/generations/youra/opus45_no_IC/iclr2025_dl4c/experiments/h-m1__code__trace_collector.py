"""ExecutionTraceCollector: sys.settrace wrapper for line-level execution tracing."""

import sys
import signal
from typing import Set, Optional, Callable, Any


class TraceTimeoutError(Exception):
    """Raised when traced execution exceeds timeout."""
    pass


class ExecutionTraceCollector:
    """Collects line-level execution traces during Python code execution."""

    def __init__(self):
        self._executed_lines: Set[int] = set()
        self._target_filename: Optional[str] = None

    def trace_function(self, frame, event: str, arg) -> Optional[Callable]:
        """sys.settrace callback. Records 'line' events for target file."""
        if event == "line" and frame.f_code.co_filename == self._target_filename:
            self._executed_lines.add(frame.f_lineno)
        return self.trace_function

    def collect_trace(self, code_str: str, test_input: str = "", timeout: float = 5.0) -> Set[int]:
        """Execute code_str + test_input under trace. Returns executed line numbers.

        Returns partial set on exception/timeout (never raises).
        """
        self._executed_lines = set()
        self._target_filename = "<traced>"

        full_code = code_str + "\n" + test_input if test_input else code_str

        try:
            code_obj = compile(full_code, self._target_filename, "exec")
        except SyntaxError:
            return set()

        def timeout_handler(signum, frame):
            raise TraceTimeoutError("Execution timeout")

        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(timeout))

        sys.settrace(self.trace_function)
        try:
            exec(code_obj, {"__builtins__": __builtins__}, {})
        except (TraceTimeoutError, Exception):
            pass
        finally:
            sys.settrace(None)
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

        return self._executed_lines

    def collect_trace_with_globals(
        self,
        code_str: str,
        test_input: str = "",
        global_vars: Optional[dict] = None,
        timeout: float = 5.0
    ) -> Set[int]:
        """Execute with custom globals (for providing test inputs as variables)."""
        self._executed_lines = set()
        self._target_filename = "<traced>"

        full_code = code_str + "\n" + test_input if test_input else code_str

        try:
            code_obj = compile(full_code, self._target_filename, "exec")
        except SyntaxError:
            return set()

        def timeout_handler(signum, frame):
            raise TraceTimeoutError("Execution timeout")

        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(timeout))

        exec_globals = {"__builtins__": __builtins__}
        if global_vars:
            exec_globals.update(global_vars)

        sys.settrace(self.trace_function)
        try:
            exec(code_obj, exec_globals, {})
        except (TraceTimeoutError, Exception):
            pass
        finally:
            sys.settrace(None)
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

        return self._executed_lines
