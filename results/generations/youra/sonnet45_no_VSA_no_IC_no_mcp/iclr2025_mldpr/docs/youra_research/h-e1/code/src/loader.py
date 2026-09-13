import time
from typing import Tuple, Dict, Any
from datasets import load_dataset
from .telemetry import TelemetryLogger

def instrumented_load_dataset(
    dataset_name: str,
    telemetry: TelemetryLogger,
    config: str = None,
    split: str = "train",
    **kwargs
) -> Tuple[Any, Dict[str, Any]]:
    start = time.perf_counter()
    if config:
        dataset = load_dataset(dataset_name, config, split=split, **kwargs)
    else:
        dataset = load_dataset(dataset_name, split=split, **kwargs)
    baseline_ms = (time.perf_counter() - start) * 1000

    telemetry_start = time.perf_counter()
    success = telemetry.log_event({
        'user_id': 'test_user',
        'dataset': dataset_name,
        'action': 'load',
        'timestamp': time.time()
    })
    telemetry_ms = (time.perf_counter() - telemetry_start) * 1000

    overhead_pct = (telemetry_ms / baseline_ms * 100) if baseline_ms > 0 else 0

    return dataset, {
        'baseline_ms': baseline_ms,
        'telemetry_ms': telemetry_ms,
        'overhead_pct': overhead_pct,
        'telemetry_success': success
    }
