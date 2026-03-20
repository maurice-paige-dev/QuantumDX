def test_setup_telemetry_initializes():
    from observability.telemetry import setup_telemetry, metrics_state

    state = setup_telemetry("quantumdx-test")

    assert state.initialized is True
    assert state.meter is not None
    assert state.requests_counter is not None
    assert state.duration_histogram is not None


def test_monitored_decorator_runs():
    from observability.decorators import monitored

    calls = {"count": 0}

    @monitored("TestAgent", "do_work")
    def do_work(trace_id=None):
        calls["count"] += 1
        return "ok"

    result = do_work(trace_id="trace-1")

    assert result == "ok"
    assert calls["count"] == 1


def test_monitored_decorator_raises():
    import pytest
    from observability.decorators import monitored

    @monitored("TestAgent", "explode")
    def explode(trace_id=None):
        raise ValueError("boom")

    with pytest.raises(ValueError):
        explode(trace_id="trace-2")