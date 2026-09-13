"""User Workload Simulator - h-m4 Module 6"""
import random
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta


class UserWorkloadSimulator:
    """Simulate user dataset load operations over time."""

    def __init__(
        self,
        extended_loader: 'ExtendedInstrumentedLoader',
        num_users: int = 1000,
        simulation_days: int = 30,
        loads_per_user: int = 8,
        deprecated_encounter_rate: float = 0.4,
        adoption_rate: float = 0.5,
        seed: int = 42
    ):
        """
        Initialize simulator.

        Args:
            extended_loader: ExtendedInstrumentedLoader instance
            num_users: total users to simulate
            simulation_days: simulation duration in days
            loads_per_user: loads per user over simulation period
            deprecated_encounter_rate: % users encountering deprecated datasets
            adoption_rate: % of users who adopt successor within 30 days
            seed: random seed
        """
        self.extended_loader = extended_loader
        self.num_users = num_users
        self.simulation_days = simulation_days
        self.loads_per_user = loads_per_user
        self.deprecated_encounter_rate = deprecated_encounter_rate
        self.adoption_rate = adoption_rate

        random.seed(seed)

    def run_simulation(
        self,
        datasets: List[str],
        deprecation_registry: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Run workload simulation.

        Args:
            datasets: list of dataset names to load
            deprecation_registry: {deprecated_name: successor_name}

        Returns:
            {
                'total_loads': int,
                'deprecated_encounters': int,
                'adoption_events': int,
                'elapsed_seconds': float
            }
        """
        start_time = time.time()

        total_loads = 0
        deprecated_encounters = 0
        adoption_events = 0

        deprecated_datasets = list(deprecation_registry.keys())

        for user_id in range(self.num_users):
            user_str = f"user_{user_id:05d}"

            # Determine if user encounters deprecated dataset
            encounters_deprecated = random.random() < self.deprecated_encounter_rate

            for load_num in range(self.loads_per_user):
                # Select dataset
                if encounters_deprecated and load_num == 0:
                    # First load: deprecated dataset
                    dataset_name = random.choice(deprecated_datasets)
                    deprecated_encounters += 1
                elif encounters_deprecated and load_num < self.loads_per_user // 2:
                    # Early loads: mix of deprecated and normal
                    dataset_name = random.choice(datasets)
                elif encounters_deprecated and load_num >= self.loads_per_user // 2:
                    # Late loads: check if adopts successor
                    if random.random() < self.adoption_rate:
                        # Adopt successor
                        deprecated_name = random.choice(deprecated_datasets)
                        dataset_name = deprecation_registry[deprecated_name]
                        adoption_events += 1
                    else:
                        dataset_name = random.choice(datasets)
                else:
                    # Normal user
                    dataset_name = random.choice(datasets)

                # Load dataset (triggers telemetry)
                self.extended_loader.load_dataset_with_tracking(
                    dataset_name,
                    user_str
                )

                total_loads += 1

        elapsed = time.time() - start_time

        return {
            'total_loads': total_loads,
            'deprecated_encounters': deprecated_encounters,
            'adoption_events': adoption_events,
            'elapsed_seconds': elapsed,
            'throughput_loads_per_sec': total_loads / elapsed if elapsed > 0 else 0
        }
