from pathlib import Path
from datetime import datetime
from src.telemetry import TelemetryLogger
from src.benchmark import BenchmarkHarness
from src.simulate import SimulationGenerator
from src.evaluate import Evaluator
from src.visualize import Visualizer
from src.config import INSTRUMENTATION_CONFIG
import json

def main():
    base_dir = Path(__file__).parent

    telemetry = TelemetryLogger(
        db_path=str(base_dir / INSTRUMENTATION_CONFIG["telemetry"]["db_path"])
    )

    print("Starting benchmark...")
    harness = BenchmarkHarness(
        datasets=INSTRUMENTATION_CONFIG["benchmark"]["datasets"],
        runs_per_dataset=INSTRUMENTATION_CONFIG["benchmark"]["runs_per_dataset"],
        telemetry=telemetry
    )
    results_df = harness.run_benchmarks()
    csv_path = base_dir / INSTRUMENTATION_CONFIG["benchmark"]["output_csv_path"]
    harness.save_results(results_df, str(csv_path))
    print(f"Benchmark complete: {csv_path}")

    print("Generating simulation...")
    sim = SimulationGenerator(telemetry, start_date=datetime.now())
    events = sim.generate_events(
        event_count=INSTRUMENTATION_CONFIG["simulation"]["event_count"],
        adoption_rate=INSTRUMENTATION_CONFIG["simulation"]["successor_adoption_rate"]
    )
    json_path = base_dir / INSTRUMENTATION_CONFIG["simulation"]["output_json_path"]
    sim.save_simulation(events, str(json_path))
    print(f"Simulation complete: {json_path}")

    print("Evaluating results...")
    evaluator = Evaluator(str(csv_path), str(json_path))
    report = evaluator.generate_report(telemetry)

    print("Generating visualizations...")
    viz = Visualizer(base_dir / INSTRUMENTATION_CONFIG["visualization"]["figures_dir"])
    viz.plot_gate_metrics(report)
    viz.plot_load_time_comparison(results_df)
    viz.plot_overhead_distribution(results_df)
    viz.plot_capture_rate(events)
    print(f"Figures saved to {base_dir / INSTRUMENTATION_CONFIG['visualization']['figures_dir']}")

    report_path = base_dir / "evaluation_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nGate Status: {report['gate_status']}")
    print(f"  Overhead: {report['overhead_max']:.2f}% (threshold: 10%)")
    print(f"  Capture Rate: {report['capture_rate']:.2f}% (threshold: 95%)")
    print(f"  Event Count: {report['event_count']} (threshold: 100)")
    print(f"\nReport: {report_path}")
    print("EXPERIMENT COMPLETE")

if __name__ == "__main__":
    main()
