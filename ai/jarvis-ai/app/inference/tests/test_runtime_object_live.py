import importlib
import sys
from pathlib import Path
from unittest.mock import MagicMock


APP_ROOT = Path(__file__).resolve().parents[2]
INFERENCE_ROOT = Path(__file__).resolve().parent.parent

for path in (APP_ROOT, INFERENCE_ROOT):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)


mock_logger = MagicMock()
mock_engine = MagicMock()
mock_engine.logger = mock_logger
sys.modules["engine"] = mock_engine
sys.modules["engine.logger"] = mock_engine.logger

import pytest


@pytest.fixture(scope="module")
def runtime_handles():
    runtime_module = importlib.import_module("runtime_object")

    assert hasattr(runtime_module, "RUNTIME_ACCESS"), "RUNTIME_ACCESS missing"

    runtime_access = runtime_module.RUNTIME_ACCESS
    raw_runtime = getattr(runtime_access, "_runtime", runtime_access)

    return runtime_module, runtime_access, raw_runtime


def test_import_integrity(runtime_handles):
    runtime_module, runtime_access, _ = runtime_handles
    reloaded = importlib.reload(runtime_module)

    assert runtime_access is not None
    assert reloaded.RUNTIME_ACCESS is not None
    assert runtime_access.__class__.__name__ == reloaded.RUNTIME_ACCESS.__class__.__name__
    assert hasattr(reloaded.RUNTIME_ACCESS, "read")
    assert hasattr(reloaded.RUNTIME_ACCESS, "write")


def test_state_ownership_guards(runtime_handles):
    _, runtime_access, raw_runtime = runtime_handles

    with pytest.raises(Exception):
        setattr(raw_runtime, "state", "corrupted")

    for attr in ("metrics", "history", "runtime_events"):
        with pytest.raises(Exception):
            setattr(raw_runtime, attr, {})

    with pytest.raises(Exception):
        runtime_access.write("__illegal_key__", "x")


def test_runtime_read_write_smoke(runtime_handles):
    _, runtime_access, _ = runtime_handles

    assert hasattr(runtime_access, "read")
    assert hasattr(runtime_access, "write")

    assert runtime_access.read("state") == "idle"

    runtime_access.write("state", "processing")
    runtime_access.write("busy", True)
    runtime_access.write("current_request", "live-test")
    runtime_access.write("inference_start", runtime_access.read("start_time"))

    assert runtime_access.read("state") == "processing"
    assert runtime_access.read("busy") is True
    assert runtime_access.read("current_request") == "live-test"

    runtime_access.write("busy", False)
    runtime_access.write("current_request", None)
    runtime_access.write("inference_start", None)
    runtime_access.write("state", "idle")

    assert runtime_access.read("state") == "idle"


def test_cycle_snapshot_guards(runtime_handles):
    _, runtime_access, _ = runtime_handles

    now = runtime_access.read("start_time")

    runtime_access.write("cycle_id", "cycle-test")
    runtime_access.write("cycle_state", "OPEN")
    runtime_access.write("cycle_start_ts", now)

    runtime_access.write("cycle_state", "CLOSING")
    runtime_access.write("cycle_end_ts", now)
    runtime_access.write("cycle_finalized", True)

    runtime_access.write("cycle_state", "CLOSED")
    runtime_access.write("snapshot_ts", now)

    snapshot = runtime_access.build_snapshot()
    runtime_access.commit_snapshot(snapshot)

    with pytest.raises(Exception):
        runtime_access.commit_snapshot(snapshot)


def test_consistency_validation(runtime_handles):
    _, runtime_access, _ = runtime_handles

    assert runtime_access.validate_consistency() is True
    assert runtime_access.read("state") == "idle"
