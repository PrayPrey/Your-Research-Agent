"""Analyzer-instrumented debugger agent."""
import subprocess
import tempfile
import os
from datetime import datetime
from typing import Dict, List, Optional
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from analyzers.analyzer import SecurityAnalyzer


class InstrumentedDebugger:
    """Debugger agent with security analyzer instrumentation."""

    def __init__(self, model, tokenizer, analyzer_name: str = 'bandit', max_iterations: int = 5):
        self.model = model
        self.tokenizer = tokenizer
        self.analyzer_name = analyzer_name
        self.max_iterations = max_iterations
        self.revision_log = []
        self.analyzer = SecurityAnalyzer(analyzer_name)

    def debug(self, code: str, task_description: str, task_id: str) -> str:
        """Iterative test-and-fix with security analysis."""
        for iteration in range(self.max_iterations):
            # Run security analyzer
            analyzer_results = self.analyze_security(code)

            if analyzer_results['has_issues']:
                # Log security-relevant revision
                self.log_revision(
                    task_id=task_id,
                    iteration=iteration,
                    vulnerable_code=code,
                    fixed_code=None,
                    cwe_types=analyzer_results['cwe_list'],
                    analyzer_triggered=True,
                    severity=analyzer_results['severity'][0] if analyzer_results['severity'] else 'MEDIUM'
                )

                # Generate fix
                issues_desc = '; '.join([i['text'] for i in analyzer_results['issues'][:3]])
                fixed_code = self._generate_fix(code, f"Security issues: {issues_desc}")
                if fixed_code:
                    code = fixed_code
            else:
                # Try runtime execution
                exec_result = self.execute_sandbox(code)
                if exec_result['passed']:
                    return code

                # Log runtime error revision
                self.log_revision(
                    task_id=task_id,
                    iteration=iteration,
                    vulnerable_code=code,
                    fixed_code=None,
                    cwe_types=[],
                    analyzer_triggered=False,
                    severity='LOW'
                )

                # Fix runtime error
                fixed_code = self._generate_fix(code, f"Runtime error: {exec_result['error']}")
                if fixed_code:
                    code = fixed_code

        return code

    def analyze_security(self, code: str) -> Dict:
        """Run static analyzer on code."""
        return self.analyzer.analyze(code)

    def execute_sandbox(self, code: str, timeout: int = 10) -> Dict:
        """Execute code in sandbox."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = f.name

            result = subprocess.run(
                ['python', temp_path],
                capture_output=True,
                timeout=timeout,
                text=True,
                check=False
            )

            os.unlink(temp_path)

            return {
                'passed': result.returncode == 0,
                'error': result.stderr if result.returncode != 0 else None,
                'output': result.stdout
            }
        except subprocess.TimeoutExpired:
            return {'passed': False, 'error': 'Execution timeout', 'output': ''}
        except Exception as e:
            return {'passed': False, 'error': str(e), 'output': ''}

    def _generate_fix(self, code: str, issue_description: str) -> Optional[str]:
        """Generate fixed code using LLM."""
        prompt = f"""Fix the following Python code issue:

Issue: {issue_description}

Original code:
```python
{code}
```

Fixed code:
```python"""

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.5,
            top_p=0.95,
            do_sample=True
        )
        fixed = self.tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)

        # Extract code
        if '```python' in fixed:
            fixed = fixed.split('```python')[1].split('```')[0]
        elif '```' in fixed:
            fixed = fixed.split('```')[1].split('```')[0]

        return fixed.strip() if fixed.strip() else None

    def log_revision(
        self,
        task_id: str,
        iteration: int,
        vulnerable_code: str,
        fixed_code: Optional[str],
        cwe_types: List[str],
        analyzer_triggered: bool,
        severity: str
    ):
        """Log security-relevant revision."""
        self.revision_log.append({
            'task_id': task_id,
            'iteration': iteration,
            'vulnerable_code': vulnerable_code[:500],  # Truncate for storage
            'fixed_code': fixed_code[:500] if fixed_code else None,
            'cwe_types': cwe_types,
            'analyzer_triggered': analyzer_triggered,
            'analyzer_name': self.analyzer_name,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        })

    def get_revision_log(self) -> List[Dict]:
        """Return collected revision traces."""
        return self.revision_log
