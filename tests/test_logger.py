from toolops.logger import ToolOpsLogger


def test_logger_all_levels(capsys):
    """Test that all logger levels emit JSON."""
    l = ToolOpsLogger(name="test_logger", level="DEBUG")

    l.info("i", val=1)
    l.warning("w", val=2)
    l.error("e", val=3)
    l.debug("d", val=4)

    out = capsys.readouterr().out.splitlines()
    assert len(out) == 4
    assert '"event": "i"' in out[0]
    assert '"event": "w"' in out[1]
    assert '"event": "e"' in out[2]
    assert '"event": "d"' in out[3]
