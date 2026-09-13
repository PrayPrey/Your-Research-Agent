"""Multi-agent orchestrator with checkpointing."""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from agents import PlannerAgent, CoderAgent, InstrumentedDebugger, ReviewerAgent


class AgentMeshOrchestrator:
    """Orchestrate multi-agent execution with checkpointing."""

    def __init__(self, model, tokenizer, config: Dict):
        self.model = model
        self.tokenizer = tokenizer
        self.config = config

        # Initialize agents
        self.planner = PlannerAgent(model, tokenizer)
        self.coder = CoderAgent(model, tokenizer)
        self.debugger = InstrumentedDebugger(
            model, tokenizer,
            analyzer_name='bandit',
            max_iterations=config.get('max_debugger_iterations', 5)
        )
        self.reviewer = ReviewerAgent(model, tokenizer)

    def execute_task(self, task: Dict) -> Dict:
        """Execute single task through agent pipeline."""
        task_id = task['task_id']
        task_description = task['problem_statement']

        try:
            # Plan
            plan = self.planner.plan(task_description)

            # Code
            initial_code = self.coder.generate_code(plan, task_description)

            # Debug (instrumented)
            final_code = self.debugger.debug(initial_code, task_description, task_id)

            # Review
            review = self.reviewer.review(final_code)

            # Get revision log
            revision_log = self.debugger.get_revision_log()

            return {
                'task_id': task_id,
                'solution_code': final_code,
                'revision_log': revision_log,
                'success': review['approved']
            }
        except Exception as e:
            print(f"Task {task_id} failed: {e}")
            return {
                'task_id': task_id,
                'solution_code': '',
                'revision_log': self.debugger.get_revision_log(),
                'success': False,
                'error': str(e)
            }

    def save_trace(self, task_id: str, trace: List[Dict], output_dir: str):
        """Save revision trace to JSONL."""
        os.makedirs(output_dir, exist_ok=True)
        trace_file = os.path.join(output_dir, f'task_{task_id}_trace.jsonl')

        with open(trace_file, 'w') as f:
            for revision in trace:
                f.write(json.dumps(revision) + '\n')

    def load_checkpoint(self, checkpoint_path: str) -> Dict:
        """Load checkpoint if exists."""
        if os.path.exists(checkpoint_path):
            with open(checkpoint_path, 'r') as f:
                return json.load(f)
        return None

    def save_checkpoint(self, state: Dict, checkpoint_path: str):
        """Save checkpoint."""
        os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
        with open(checkpoint_path, 'w') as f:
            json.dump(state, f, indent=2)
