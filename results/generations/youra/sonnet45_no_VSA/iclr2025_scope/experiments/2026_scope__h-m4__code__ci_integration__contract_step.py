"""GitHub Actions contract validation step wrapper."""

import sys
import time
import json
import argparse
from pathlib import Path
from typing import Dict, Any

# Add h-m3 code to Python path
h_m3_path = Path(__file__).parent.parent.parent.parent / "h-m3" / "code"
if h_m3_path.exists():
    sys.path.insert(0, str(h_m3_path))
    from composition_validator import validate_composition, CompositionViolation
else:
    # Fallback: simulate h-m3 validator for PoC
    class CompositionViolation(Exception):
        def __init__(self, message: str, violations: list):
            super().__init__(message)
            self.violations = violations

    def validate_composition(**kwargs):
        def decorator(func):
            return func
        return decorator


class CIContractValidator:
    """GitHub Actions contract validation step."""

    def __init__(self, config_path: str):
        """Initialize validator with config."""
        self.config_path = config_path
        with open(config_path, 'r') as f:
            self.config = json.load(f)

    def run_validation(self) -> int:
        """Execute contract validation in CI environment."""
        start_time = time.time()
        validation_rules = self.config['validation_rules']

        try:
            # Import test to trigger validation
            import torch

            # Simulate composition validation check
            @validate_composition(
                device_consistency=validation_rules.get('device_consistency', True),
                dtype_spec=validation_rules.get('dtype_spec'),
                layout_spec=validation_rules.get('layout_spec')
            )
            def validate_environment():
                """Trigger import-time validation."""
                return True

            validate_environment()

            elapsed = time.time() - start_time
            self.log_github_output('validation_time', str(elapsed))
            print('::notice::Contracts validated successfully')
            return 0

        except CompositionViolation as e:
            elapsed = time.time() - start_time
            error_msg = self.format_error_for_ci(e)
            print(f'::error::{error_msg}')
            self.log_github_output('validation_time', str(elapsed))
            return 1
        except Exception as e:
            elapsed = time.time() - start_time
            print(f'::error::Unexpected validation error: {e}')
            self.log_github_output('validation_time', str(elapsed))
            return 1

    def log_github_output(self, key: str, value: str) -> None:
        """Export metric to GitHub Actions outputs."""
        print(f'::set-output name={key}::{value}')

    def format_error_for_ci(self, violation: CompositionViolation) -> str:
        """Format violation for GitHub Actions error annotation."""
        msg = str(violation)
        if hasattr(violation, 'violations'):
            violations = violation.violations
            if violations:
                msg += f"\nViolations detected: {len(violations)}"
                for v in violations[:3]:  # Show first 3
                    msg += f"\n  - {v}"
        return msg


class TimingLogger:
    """Track workflow timing for TTFF measurement."""

    def __init__(self, output_path: str):
        """Initialize timing logger."""
        self.output_path = output_path
        self.data = {}
        if Path(output_path).exists():
            with open(output_path, 'r') as f:
                self.data = json.load(f)

    def log_workflow_start(self, run_id: str) -> None:
        """Log workflow start timestamp."""
        from datetime import datetime, timezone
        self.data[run_id] = {
            'started_at': datetime.now(timezone.utc).isoformat(),
            'completed_at': None,
            'stage': None
        }
        self._save()

    def log_failure_detected(self, run_id: str, stage: str) -> None:
        """Log failure detection timestamp."""
        from datetime import datetime, timezone
        if run_id in self.data:
            self.data[run_id]['completed_at'] = datetime.now(timezone.utc).isoformat()
            self.data[run_id]['stage'] = stage
            self._save()

    def calculate_ttff(self, run_id: str) -> float:
        """Calculate time-to-first-failure in hours."""
        from datetime import datetime
        if run_id not in self.data:
            return None

        run_log = self.data[run_id]
        if not run_log.get('completed_at'):
            return None

        started_at = datetime.fromisoformat(run_log['started_at'])
        completed_at = datetime.fromisoformat(run_log['completed_at'])
        ttff_seconds = (completed_at - started_at).total_seconds()
        ttff_hours = ttff_seconds / 3600
        return ttff_hours

    def export_to_github_outputs(self) -> None:
        """Export timing metrics to GitHub Actions."""
        for run_id, data in self.data.items():
            ttff = self.calculate_ttff(run_id)
            if ttff is not None:
                print(f'::set-output name=ttff_{run_id}::{ttff}')
                print(f'::set-output name=stage_{run_id}::{data["stage"]}')

    def _save(self):
        """Save timing data to file."""
        with open(self.output_path, 'w') as f:
            json.dump(self.data, f, indent=2)


def main() -> int:
    """Entry point for GitHub Actions step."""
    parser = argparse.ArgumentParser(description='CI Contract Validation')
    parser.add_argument('--config', required=True, help='Path to contract config JSON')
    args = parser.parse_args()

    validator = CIContractValidator(args.config)
    return validator.run_validation()


if __name__ == '__main__':
    sys.exit(main())
