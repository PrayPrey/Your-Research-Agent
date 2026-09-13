"""
Model interface for code generation and repair
"""
import openai
from typing import Dict, List
import time
import config

class CodeGenerationModel:
    """Interface for LLM-based code generation"""

    def __init__(self, model_name: str = None, api_key: str = None):
        self.model_name = model_name or config.LLM_MODEL
        self.api_key = api_key or config.OPENAI_API_KEY
        openai.api_key = self.api_key

    def generate_code(self, specification: str, function_signature: str) -> str:
        """Generate initial code from specification"""
        prompt = f"""You are an expert Python programmer. Generate a complete, correct Python function based on the following specification.

Specification:
{specification}

Function Signature:
{function_signature}

Requirements:
- Include all necessary imports (e.g., from typing import List, Optional)
- The function should be correct and handle edge cases
- Use proper Python syntax and best practices
- Do not include any explanations, only output the complete function code

Code:"""

        try:
            response = openai.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert Python programmer. Generate only code without explanations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.TEMPERATURE,
                max_tokens=1000
            )
            code = response.choices[0].message.content.strip()
            # Extract code from markdown if present
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0].strip()
            elif "```" in code:
                code = code.split("```")[1].split("```")[0].strip()
            return code
        except Exception as e:
            print(f"Error generating code: {e}")
            return ""

    def repair_code(self, code: str, feedback: str, specification: str) -> str:
        """Repair code based on feedback"""
        prompt = f"""You are an expert Python programmer. The following code has issues that need to be fixed.

Original Specification:
{specification}

Current Code:
{code}

Verification Feedback:
{feedback}

Please provide a corrected version of the code that addresses all the issues mentioned in the feedback.
Requirements:
- Fix all errors and issues
- Maintain the original function signature
- Ensure all test cases will pass
- Do not include any explanations, only output the complete corrected function code

Corrected Code:"""

        try:
            response = openai.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert Python programmer. Generate only code without explanations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.TEMPERATURE,
                max_tokens=1000
            )
            code = response.choices[0].message.content.strip()
            # Extract code from markdown if present
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0].strip()
            elif "```" in code:
                code = code.split("```")[1].split("```")[0].strip()
            return code
        except Exception as e:
            print(f"Error repairing code: {e}")
            return code  # Return original if repair fails

class FeedbackSynthesizer:
    """Synthesize formal verification feedback into natural language"""

    def __init__(self, model_name: str = None, api_key: str = None):
        self.model_name = model_name or config.FEEDBACK_MODEL
        self.api_key = api_key or config.OPENAI_API_KEY
        openai.api_key = self.api_key

    def synthesize_feedback(self, raw_feedback: str, code: str, specification: str) -> str:
        """Transform raw verification output into structured repair prompts"""
        prompt = f"""You are an expert in program analysis and debugging. Transform the following raw verification feedback into clear, actionable guidance.

Code:
{code}

Specification:
{specification}

Raw Verification Output:
{raw_feedback}

Generate structured feedback that includes:
1. Clear explanation of each error in natural language
2. Specific location in the code
3. Concrete repair suggestions
4. Examples of how to fix the issue

Synthesized Feedback:"""

        try:
            response = openai.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert in program analysis. Provide clear, actionable feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error synthesizing feedback: {e}")
            return raw_feedback  # Return raw feedback if synthesis fails
