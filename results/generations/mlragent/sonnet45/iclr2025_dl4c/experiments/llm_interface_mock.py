"""
Mock LLM interface for testing without API keys.
This generates deterministic code solutions based on task patterns.
"""

import random
from typing import Optional


class MockLLMInterface:
    """Mock interface that generates code without API calls."""

    def __init__(self, model_name: str = "mock", temperature: float = 0.7, max_tokens: int = 2048):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.call_count = 0
        random.seed(42)  # For reproducibility

    def generate_code(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate mock code based on prompt patterns."""
        self.call_count += 1

        # Extract function name from prompt
        function_name = self._extract_function_name(prompt)

        # Generate code based on task type
        if "sum" in prompt.lower() and "even" in prompt.lower():
            return self._generate_sum_even(function_name)
        elif "palindrome" in prompt.lower():
            return self._generate_palindrome(function_name)
        elif "maximum" in prompt.lower() or "max" in prompt.lower():
            return self._generate_find_max(function_name)
        elif "reverse" in prompt.lower() and "list" in prompt.lower():
            return self._generate_reverse_list(function_name)
        elif "count" in prompt.lower() and "character" in prompt.lower():
            return self._generate_count_chars(function_name)
        elif "duplicates" in prompt.lower():
            return self._generate_remove_duplicates(function_name)
        elif "fibonacci" in prompt.lower():
            return self._generate_fibonacci(function_name)
        elif "prime" in prompt.lower():
            return self._generate_is_prime(function_name)
        elif "merge" in prompt.lower() and "sorted" in prompt.lower():
            return self._generate_merge_sorted(function_name)
        elif "pairs" in prompt.lower() and "sum" in prompt.lower():
            return self._generate_find_pairs(function_name)
        elif "rotate" in prompt.lower():
            return self._generate_rotate_list(function_name)
        elif "anagram" in prompt.lower():
            return self._generate_anagrams(function_name)
        elif "common prefix" in prompt.lower():
            return self._generate_common_prefix(function_name)
        elif "roman" in prompt.lower():
            return self._generate_roman_to_int(function_name)
        elif "missing number" in prompt.lower():
            return self._generate_missing_number(function_name)
        elif "balanced" in prompt.lower() and "parenthes" in prompt.lower():
            return self._generate_balanced_parens(function_name)
        elif "non-repeating" in prompt.lower():
            return self._generate_first_non_repeating(function_name)
        elif "power set" in prompt.lower():
            return self._generate_power_set(function_name)
        elif "binary search" in prompt.lower():
            return self._generate_binary_search(function_name)
        elif "flatten" in prompt.lower():
            return self._generate_flatten_list(function_name)
        else:
            return f"def {function_name}(*args):\n    pass"

    def generate_fix(self, task_description: str, failed_code: str, error_message: str,
                     test_results: list, method: str = "simple") -> str:
        """Generate a fix for failed code."""
        self.call_count += 1

        # Simulate improvement: with some probability, generate correct code
        # Different methods have different success probabilities
        if method == "simple":
            success_prob = 0.6
        elif method == "reflection":
            success_prob = 0.7
        elif method == "counterfactual":
            success_prob = 0.8
        else:
            success_prob = 0.5

        # Add some variation based on attempt number (encoded in call count)
        success_prob = min(0.95, success_prob + (self.call_count % 5) * 0.05)

        # Generate code with intentional bugs if not "successful"
        prompt = f"Task: {task_description}\nFailed code: {failed_code}"
        base_code = self.generate_code(prompt)

        if random.random() < success_prob:
            return base_code
        else:
            # Introduce a bug
            return self._introduce_bug(base_code)

    def _extract_function_name(self, prompt: str) -> str:
        """Extract function name from prompt."""
        if "named '" in prompt:
            name = prompt.split("named '")[1].split("'")[0]
            return name
        return "solution"

    def _introduce_bug(self, code: str) -> str:
        """Introduce a simple bug into code."""
        lines = code.split('\n')
        if len(lines) > 2:
            # Change a comparison or operator
            for i in range(len(lines)):
                if '<=' in lines[i]:
                    lines[i] = lines[i].replace('<=', '<')
                    break
                elif '==' in lines[i]:
                    lines[i] = lines[i].replace('==', '!=')
                    break
        return '\n'.join(lines)

    # Code generation templates
    def _generate_sum_even(self, name: str) -> str:
        return f"""def {name}(lst):
    return sum(x for x in lst if x % 2 == 0)"""

    def _generate_palindrome(self, name: str) -> str:
        return f"""def {name}(s):
    s_lower = s.lower()
    return s_lower == s_lower[::-1]"""

    def _generate_find_max(self, name: str) -> str:
        return f"""def {name}(lst):
    if not lst:
        return None
    return max(lst)"""

    def _generate_reverse_list(self, name: str) -> str:
        return f"""def {name}(lst):
    result = []
    for i in range(len(lst) - 1, -1, -1):
        result.append(lst[i])
    return result"""

    def _generate_count_chars(self, name: str) -> str:
        return f"""def {name}(s):
    counts = {{}}
    for char in s:
        counts[char] = counts.get(char, 0) + 1
    return counts"""

    def _generate_remove_duplicates(self, name: str) -> str:
        return f"""def {name}(lst):
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result"""

    def _generate_fibonacci(self, name: str) -> str:
        return f"""def {name}(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b"""

    def _generate_is_prime(self, name: str) -> str:
        return f"""def {name}(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True"""

    def _generate_merge_sorted(self, name: str) -> str:
        return f"""def {name}(lst1, lst2):
    result = []
    i, j = 0, 0
    while i < len(lst1) and j < len(lst2):
        if lst1[i] <= lst2[j]:
            result.append(lst1[i])
            i += 1
        else:
            result.append(lst2[j])
            j += 1
    result.extend(lst1[i:])
    result.extend(lst2[j:])
    return result"""

    def _generate_find_pairs(self, name: str) -> str:
        return f"""def {name}(lst, target):
    pairs = []
    for i in range(len(lst)):
        for j in range(i + 1, len(lst)):
            if lst[i] + lst[j] == target:
                pairs.append((lst[i], lst[j]))
    return pairs"""

    def _generate_rotate_list(self, name: str) -> str:
        return f"""def {name}(lst, k):
    if not lst:
        return lst
    k = k % len(lst) if len(lst) > 0 else 0
    return lst[-k:] + lst[:-k] if k > 0 else lst"""

    def _generate_anagrams(self, name: str) -> str:
        return f"""def {name}(s1, s2):
    return sorted(s1.lower()) == sorted(s2.lower())"""

    def _generate_common_prefix(self, name: str) -> str:
        return f"""def {name}(strs):
    if not strs:
        return ""
    prefix = strs[0]
    for s in strs[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix"""

    def _generate_roman_to_int(self, name: str) -> str:
        return f"""def {name}(s):
    values = {{'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}}
    total = 0
    prev = 0
    for char in reversed(s):
        val = values[char]
        if val < prev:
            total -= val
        else:
            total += val
        prev = val
    return total"""

    def _generate_missing_number(self, name: str) -> str:
        return f"""def {name}(lst):
    n = len(lst)
    expected_sum = n * (n + 1) // 2
    actual_sum = sum(lst)
    return expected_sum - actual_sum"""

    def _generate_balanced_parens(self, name: str) -> str:
        return f"""def {name}(s):
    stack = []
    pairs = {{'(': ')', '[': ']', '{{': '}}'}}
    for char in s:
        if char in pairs:
            stack.append(char)
        elif char in pairs.values():
            if not stack:
                return False
            if pairs[stack.pop()] != char:
                return False
    return len(stack) == 0"""

    def _generate_first_non_repeating(self, name: str) -> str:
        return f"""def {name}(s):
    counts = {{}}
    for char in s:
        counts[char] = counts.get(char, 0) + 1
    for char in s:
        if counts[char] == 1:
            return char
    return None"""

    def _generate_power_set(self, name: str) -> str:
        return f"""def {name}(lst):
    result = [[]]
    for item in lst:
        result.extend([subset + [item] for subset in result])
    return result"""

    def _generate_binary_search(self, name: str) -> str:
        return f"""def {name}(lst, target):
    left, right = 0, len(lst) - 1
    while left <= right:
        mid = (left + right) // 2
        if lst[mid] == target:
            return mid
        elif lst[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1"""

    def _generate_flatten_list(self, name: str) -> str:
        return f"""def {name}(lst):
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend({name}(item))
        else:
            result.append(item)
    return result"""
