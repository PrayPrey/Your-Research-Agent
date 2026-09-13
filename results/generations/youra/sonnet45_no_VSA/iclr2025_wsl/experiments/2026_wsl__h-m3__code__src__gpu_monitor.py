"""GPU memory monitoring (verify CPU-only execution)"""

import time
import torch
import threading
import pandas as pd
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class GPUMonitor:
    """Monitor GPU memory usage during extraction"""

    def __init__(self, poll_interval: float = 0.1):
        self.poll_interval = poll_interval
        self.memory_log = []
        self.monitoring = False
        self.monitor_thread = None
        self.start_timestamp = None

    def start_monitoring(self):
        """Start background thread to poll GPU memory every 0.1 sec"""
        self.monitoring = True
        self.memory_log = []
        self.start_timestamp = time.time()
        self.monitor_thread = threading.Thread(target=self._poll_gpu_memory)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logger.info("GPU monitoring started")

    def stop_monitoring(self) -> Dict:
        """
        Stop monitoring and return results.

        Returns:
            {
                'max_gpu_memory_mb': float,
                'memory_log': pd.DataFrame,
                'cpu_only_verified': bool
            }
        """
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)

        # Compute max GPU usage
        if self.memory_log:
            max_gpu_memory_mb = max(log['gpu_memory_mb'] for log in self.memory_log)
        else:
            max_gpu_memory_mb = 0.0

        cpu_only_verified = (max_gpu_memory_mb == 0.0)

        memory_df = pd.DataFrame(self.memory_log) if self.memory_log else pd.DataFrame(columns=['timestamp', 'gpu_memory_mb'])

        logger.info(f"GPU monitoring stopped. Max GPU memory: {max_gpu_memory_mb:.2f} MB, CPU-only: {cpu_only_verified}")

        return {
            'max_gpu_memory_mb': max_gpu_memory_mb,
            'memory_log': memory_df,
            'cpu_only_verified': cpu_only_verified
        }

    def _poll_gpu_memory(self):
        """Background thread function: continuously poll GPU memory"""
        while self.monitoring:
            if torch.cuda.is_available():
                memory_mb = torch.cuda.memory_allocated() / 1e6
            else:
                memory_mb = 0.0

            timestamp = time.time() - self.start_timestamp
            self.memory_log.append({
                'timestamp': timestamp,
                'gpu_memory_mb': memory_mb
            })

            time.sleep(self.poll_interval)

    def save_memory_log(self, output_path: str):
        """Save memory log to CSV"""
        if self.memory_log:
            df = pd.DataFrame(self.memory_log)
            df.to_csv(output_path, index=False)
            logger.info(f"Memory log saved to {output_path}")
