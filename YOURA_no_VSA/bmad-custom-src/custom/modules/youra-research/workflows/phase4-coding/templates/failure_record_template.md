# Failure Record: {{hypothesis_id}}

**Date:** {{timestamp}}
**Hypothesis:** {{hypothesis_id}}
**Final Status:** FAILED
**Gate Result:** {{gate_result}}
**Attempts Used:** {{modification_attempt}}/{{max_modification_attempts}}
**Routed To:** {{route_destination}}

## Hypothesis Statement
{{hypothesis_statement}}

## What Was Tried
{{attempt_history}}

## Why It Failed
**Root Cause:** {{root_cause_summary}}

### Failed Metrics
{{failed_metrics_list}}

## Lessons Learned
{{lessons_learned_list}}

## What NOT To Do in Future Hypotheses
{{anti_patterns_list}}

## What Showed Partial Promise
{{partial_success_list}}

## Recommendations for Alternative Approaches
{{alternative_approaches_list}}

## Routing Information
**Routed To:** {{route_destination}}

{{routing_reason}}

---
*For {{route_destination}} to read on initialization*
*This hypothesis should NOT be retried in its current form*
