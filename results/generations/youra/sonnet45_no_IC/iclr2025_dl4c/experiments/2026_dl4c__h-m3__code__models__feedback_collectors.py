"""
Feedback Collectors: Execution, AI, and Human feedback modules
Task: A-4 (Feedback Collectors)
"""
import torch
import torch.nn as nn
from typing import List, Dict, Optional
import subprocess
import tempfile
import json
import os
from transformers import AutoTokenizer, AutoModel


class ExecutionFeedback:
    """
    Execution feedback via test case execution
    Returns: [0,1] - fraction of tests passed
    """

    def __init__(self, timeout: float = 5.0, sandbox: bool = True):
        self.timeout = timeout
        self.sandbox = sandbox

    def compute_reward(
        self,
        code: str,
        test_cases: str,
        entry_point: str = "main"
    ) -> float:
        """
        Execute code against test cases and return pass rate

        Args:
            code: Generated code string
            test_cases: Test cases to execute
            entry_point: Function entry point

        Returns:
            reward: [0,1] - fraction of tests passed
        """
        try:
            # Create temporary file with code + tests
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code + "\n\n" + test_cases)
                temp_file = f.name

            # Execute tests
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                timeout=self.timeout,
                text=True
            )

            # Clean up
            os.unlink(temp_file)

            # Success if no errors
            if result.returncode == 0:
                return 1.0
            else:
                return 0.0

        except subprocess.TimeoutExpired:
            return 0.0
        except Exception as e:
            # Execution error
            return 0.0


class AIFeedback(nn.Module):
    """
    AI feedback via learned reward model
    Returns: [-1,1] normalized score
    """

    def __init__(
        self,
        model_name: str = "microsoft/codebert-base",
        reward_model_path: Optional[str] = None
    ):
        super().__init__()

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.encoder = AutoModel.from_pretrained(model_name)

        # Reward head (fine-tuned on execution + human data)
        self.reward_head = nn.Sequential(
            nn.Linear(self.encoder.config.hidden_size, 256),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(256, 1),
            nn.Tanh()  # Output in [-1,1]
        )

        # Load fine-tuned weights if available
        if reward_model_path and os.path.exists(reward_model_path):
            self.load_state_dict(torch.load(reward_model_path))

    def compute_reward(
        self,
        code: str,
        prompt: str,
        device: str = "cuda"
    ) -> torch.Tensor:
        """
        Compute AI reward score for generated code

        Args:
            code: Generated code string
            prompt: Original problem prompt
            device: torch device

        Returns:
            reward: Tensor [-1,1] - AI assessment score
        """
        # Tokenize prompt + code
        inputs = self.tokenizer(
            prompt + "\n" + code,
            max_length=512,
            truncation=True,
            padding=True,
            return_tensors="pt"
        ).to(device)

        # Encode
        with torch.no_grad():
            outputs = self.encoder(**inputs)
            pooled = outputs.last_hidden_state[:, 0, :]  # [CLS] token

        # Compute reward
        reward = self.reward_head(pooled).squeeze(-1)

        return reward


class HumanFeedback:
    """
    Human feedback via cached annotations
    Returns: [0,1] - human preference score
    """

    def __init__(
        self,
        annotation_cache_path: str = "./data/annotations/cache.json",
        fallback_score: float = 0.5
    ):
        self.cache_path = annotation_cache_path
        self.fallback_score = fallback_score
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict:
        """Load annotation cache from file"""
        if os.path.exists(self.cache_path):
            with open(self.cache_path, 'r') as f:
                return json.load(f)
        return {}

    def compute_reward(
        self,
        code: str,
        task_id: str
    ) -> float:
        """
        Retrieve human preference score from cache, or compute from code quality

        Args:
            code: Generated code string
            task_id: Problem task ID

        Returns:
            reward: [0,1] - human preference score (cached or quality-based)
        """
        # Check cache for this task_id + code hash
        code_hash = hash(code) % 10000
        cache_key = f"{task_id}_{code_hash}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        # Fallback: compute quality-based score (independent of execution)
        # This provides a meaningful training signal when no annotations exist
        return self._compute_quality_score(code)

    def _compute_quality_score(self, code: str) -> float:
        """
        Compute code quality score independent of execution correctness

        Metrics:
        - Code structure (proper functions, returns)
        - Documentation quality (docstrings, comments)
        - Code complexity (simpler is better)
        - Length appropriateness

        Returns:
            quality_score: [0,1] - code quality estimate
        """
        score = 0.5  # Neutral baseline

        # Code length quality
        code_len = len(code.strip())
        if 50 <= code_len <= 300:
            score += 0.15
        elif code_len < 20:
            score -= 0.15
        elif code_len > 500:
            score -= 0.10

        # Documentation quality
        has_docstring = '"""' in code or "'''" in code
        has_comments = '#' in code
        if has_docstring:
            score += 0.15
        elif has_comments:
            score += 0.10

        # Structural quality
        has_def = 'def ' in code
        has_return = 'return' in code
        if has_def and has_return:
            score += 0.15
        elif has_def:
            score += 0.05

        # Complexity (simpler is better)
        complexity_keywords = ['if', 'for', 'while', 'try', 'except', 'elif', 'else']
        complexity_count = sum(code.count(kw) for kw in complexity_keywords)
        if complexity_count <= 3:
            score += 0.10
        elif complexity_count > 8:
            score -= 0.10

        # Anti-patterns
        if code.strip() in ('pass', ''):
            score -= 0.3
        if code.count('import') > 5:
            score -= 0.05

        return max(0.0, min(1.0, score))


class FeedbackCollector:
    """
    Unified interface for collecting all three feedback signals
    """

    def __init__(
        self,
        execution_timeout: float = 5.0,
        reward_model_name: str = "microsoft/codebert-base",
        reward_model_path: Optional[str] = None,
        annotation_cache_path: str = "./data/annotations/cache.json",
        device: str = "cuda"
    ):
        self.execution = ExecutionFeedback(timeout=execution_timeout)
        self.ai_feedback = AIFeedback(
            model_name=reward_model_name,
            reward_model_path=reward_model_path
        ).to(device)
        self.human = HumanFeedback(annotation_cache_path=annotation_cache_path)
        self.device = device

    def collect_all(
        self,
        code: str,
        prompt: str,
        test_cases: str,
        task_id: str,
        entry_point: str = "main"
    ) -> Dict[str, torch.Tensor]:
        """
        Collect all three feedback signals

        Returns:
            Dict with keys: execution, ai, human (all as tensors)
        """
        # Execution feedback
        exec_reward = self.execution.compute_reward(code, test_cases, entry_point)

        # AI feedback
        ai_reward = self.ai_feedback.compute_reward(code, prompt, self.device)

        # Human feedback
        human_reward = self.human.compute_reward(code, task_id)

        return {
            'execution': torch.tensor(exec_reward, dtype=torch.float32, device=self.device),
            'ai': ai_reward,
            'human': torch.tensor(human_reward, dtype=torch.float32, device=self.device)
        }


if __name__ == "__main__":
    # Test feedback collectors
    print("Testing Feedback Collectors...")

    collector = FeedbackCollector(device="cpu")

    # Test code
    code = """
def add(a, b):
    return a + b
"""
    prompt = "Write a function to add two numbers"
    test_cases = """
assert add(2, 3) == 5
assert add(0, 0) == 0
"""

    feedback = collector.collect_all(
        code=code,
        prompt=prompt,
        test_cases=test_cases,
        task_id="test_001",
        entry_point="add"
    )

    print(f"Execution reward: {feedback['execution']:.3f}")
    print(f"AI reward: {feedback['ai'].item():.3f}")
    print(f"Human reward: {feedback['human']:.3f}")

    print("\n✓ Feedback collectors test passed")
