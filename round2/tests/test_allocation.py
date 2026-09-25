import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Fill, Order
from service import AllocationService


def make_service():
    svc = AllocationService()
    svc.submit(Order("o1", "alice", "BLM", 100))
    svc.submit(Order("o2", "bob", "BLM", 100))
    return svc


def test_fill_is_allocated():
    svc = make_service()
    result = svc.on_fill(Fill("f1", "BLM", 100, 5000))
    assert result


def test_position_created():
    svc = make_service()
    svc.on_fill(Fill("f2", "BLM", 100, 5000))
    assert svc.position("alice", "BLM").quantity > 0


def test_cancel_returns_true():
    svc = make_service()
    assert svc.cancel("o1") is True


if __name__ == "__main__":
    test_fill_is_allocated()
    test_position_created()
    test_cancel_returns_true()
    print("all tests passed")