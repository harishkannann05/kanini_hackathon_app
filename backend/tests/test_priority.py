import pytest
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.queue_service import compute_priority_score


def test_priority_scores():
    assert compute_priority_score('High', 90, True) == 100
    assert compute_priority_score('High', 80, False) >= 80
    assert compute_priority_score('Medium', 50, False) >= 50
    assert compute_priority_score('Low', 10, False) >= 20
