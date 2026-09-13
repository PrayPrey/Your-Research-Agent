"""Load miniF2F problems from Test.lean."""
import re
from dataclasses import dataclass
from typing import List


@dataclass
class Problem:
    """miniF2F problem."""
    id: str
    statement: str
    source: str


def load_minif2f_problems(filepath: str) -> List[Problem]:
    """Load problems from Test.lean."""
    with open(filepath, 'r') as f:
        content = f.read()

    problems = []
    pattern = r'theorem\s+(\w+)\s*:(.+?)(?=theorem|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)

    for name, stmt in matches:
        problems.append(Problem(
            id=name,
            statement=stmt.strip(),
            source=extract_source(name)
        ))

    return problems


def extract_source(name: str) -> str:
    """Extract source from theorem name."""
    name_lower = name.lower()
    if 'amc' in name_lower:
        return 'AMC'
    elif 'aime' in name_lower:
        return 'AIME'
    elif 'imo' in name_lower:
        return 'IMO'
    elif 'usamo' in name_lower:
        return 'USAMO'
    else:
        return 'OTHER'
