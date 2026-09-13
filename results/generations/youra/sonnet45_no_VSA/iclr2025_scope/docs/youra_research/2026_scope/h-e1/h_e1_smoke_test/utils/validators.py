"""Validation utilities for forward and backward passes."""

import torch
import logging
from typing import Dict, Any


class ForwardPassValidator:
    """Validate forward pass outputs."""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def validate_forward_pass(self, model, input_ids: torch.Tensor) -> Dict[str, Any]:
        """Validate forward pass on a single sequence."""
        try:
            with torch.no_grad():
                outputs = model(input_ids)
                logits = outputs.logits

            expected_shape = (input_ids.shape[0], input_ids.shape[1], model.config.vocab_size)
            shape_valid = logits.shape == expected_shape

            has_nan = torch.isnan(logits).any().item()
            has_inf = torch.isinf(logits).any().item()

            logit_min = logits.min().item()
            logit_max = logits.max().item()
            range_valid = (logit_min >= self.config.validation.logit_range_min and
                          logit_max <= self.config.validation.logit_range_max)

            passed = shape_valid and not has_nan and not has_inf and range_valid

            return {
                'passed': passed,
                'shape_valid': shape_valid,
                'has_nan': has_nan,
                'has_inf': has_inf,
                'range_valid': range_valid,
                'logit_min': logit_min,
                'logit_max': logit_max,
                'logit_shape': list(logits.shape)
            }

        except Exception as e:
            self.logger.error(f"Forward pass validation failed: {e}")
            return {'passed': False, 'error': str(e)}


class BackwardPassValidator:
    """Validate backward pass and gradient flow."""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def validate_backward_pass(self, model, input_ids: torch.Tensor) -> Dict[str, Any]:
        """Validate backward pass and gradient computation."""
        try:
            outputs = model(input_ids)
            logits = outputs.logits

            shift_logits = logits[:, :-1, :].contiguous()
            shift_labels = input_ids[:, 1:].contiguous()
            loss = torch.nn.functional.cross_entropy(
                shift_logits.view(-1, shift_logits.size(-1)),
                shift_labels.view(-1)
            )

            loss.backward()

            gradient_checks = []
            all_grads_present = True
            all_grads_in_range = True
            grad_has_nan = False

            for name, param in model.named_parameters():
                if param.requires_grad:
                    if param.grad is None:
                        all_grads_present = False
                        gradient_checks.append({'name': name, 'grad_present': False})
                    else:
                        grad_mag = param.grad.abs().max().item()
                        has_nan = torch.isnan(param.grad).any().item()

                        in_range = (grad_mag >= self.config.validation.gradient_min and
                                   grad_mag <= self.config.validation.gradient_max)

                        if not in_range:
                            all_grads_in_range = False
                        if has_nan:
                            grad_has_nan = True

                        gradient_checks.append({
                            'name': name,
                            'grad_present': True,
                            'grad_magnitude': grad_mag,
                            'in_range': in_range,
                            'has_nan': has_nan
                        })

            passed = all_grads_present and all_grads_in_range and not grad_has_nan

            model.zero_grad()

            return {
                'passed': passed,
                'all_grads_present': all_grads_present,
                'all_grads_in_range': all_grads_in_range,
                'grad_has_nan': grad_has_nan,
                'num_params_checked': len(gradient_checks),
                'gradient_checks': gradient_checks[:5]
            }

        except Exception as e:
            self.logger.error(f"Backward pass validation failed: {e}")
            return {'passed': False, 'error': str(e)}


class SmokeTestValidator:
    """Orchestrate all validation checks."""

    def __init__(self, config):
        self.config = config
        self.forward_validator = ForwardPassValidator(config)
        self.backward_validator = BackwardPassValidator(config)
        self.logger = logging.getLogger(__name__)

    def validate_sequence(self, model, input_ids: torch.Tensor, ssm_monitor=None) -> Dict[str, Any]:
        """Run complete validation on a single sequence."""
        results = {'forward': None, 'backward': None, 'ssm_states': None}

        self.logger.info("Running forward pass validation...")
        results['forward'] = self.forward_validator.validate_forward_pass(model, input_ids)

        self.logger.info("Running backward pass validation...")
        results['backward'] = self.backward_validator.validate_backward_pass(model, input_ids)

        if ssm_monitor and self.config.validation.check_ssm_states:
            self.logger.info("Running SSM state validation...")
            results['ssm_states'] = ssm_monitor.validate_states()

        passed = results['forward']['passed'] and results['backward']['passed']
        if results['ssm_states'] is not None:
            passed = passed and results['ssm_states']['passed']

        results['overall_passed'] = passed

        return results
