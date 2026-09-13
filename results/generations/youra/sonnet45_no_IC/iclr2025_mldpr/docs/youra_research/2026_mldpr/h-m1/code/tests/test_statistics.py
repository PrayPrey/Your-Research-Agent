"""
Tests for StatisticalAnalyzer module.
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from analysis.statistics import StatisticalAnalyzer


def test_analyzer_initialization():
    """Test analyzer initialization."""
    analyzer = StatisticalAnalyzer(effect_size=0.57, alpha=0.05, power=0.80)
    assert analyzer.effect_size == 0.57
    assert analyzer.alpha == 0.05
    assert analyzer.power == 0.80


def test_calculate_required_n():
    """Test power calculation."""
    analyzer = StatisticalAnalyzer(effect_size=0.57, alpha=0.05, power=0.80)
    required_n = analyzer.calculate_required_n()

    # For Cohen's d = 0.57, alpha = 0.05, power = 0.80
    # Expected N ≈ 49 per group * 2 = 98 total (from Phase 2B)
    # But code returns per-group, not total
    assert 45 <= required_n <= 55


def test_check_power_sufficiency():
    """Test power sufficiency check."""
    analyzer = StatisticalAnalyzer(effect_size=0.57, alpha=0.05, power=0.80)

    result = analyzer.check_power_sufficiency(actual_n=150)

    assert result['actual_n'] == 150
    assert result['power_sufficient'] == True


def test_analyze_domain_coverage():
    """Test domain coverage analysis."""
    analyzer = StatisticalAnalyzer()

    df = pd.DataFrame({
        'task': ['CV', 'CV', 'NLP', 'CV', 'NLP']
    })

    result = analyzer.analyze_domain_coverage(df)

    assert result['domain_count'] == 2
    assert result['distribution']['CV'] == 3
    assert result['distribution']['NLP'] == 2


def test_analyze_reproduction_depth():
    """Test reproduction depth analysis."""
    analyzer = StatisticalAnalyzer()

    df = pd.DataFrame({
        'result_count': [5, 10, 15, 20, 25]
    })

    result = analyzer.analyze_reproduction_depth(df)

    assert result['median'] == 15
    assert result['min'] == 5
    assert result['max'] == 25
