from toolops.logger import ToolOpsLogger


def test_logger_all_levels(capsys):
    """Test that all logger levels emit JSON."""
    logger_obj = ToolOpsLogger(name="test_logger", level="DEBUG")

    logger_obj.info("i", val=1)
    logger_obj.warning("w", val=2)
    logger_obj.error("e", val=3)
    logger_obj.debug("d", val=4)

    out = capsys.readouterr().out.splitlines()
    assert len(out) == 4
    assert '"event": "i"' in out[0]
    assert '"event": "w"' in out[1]
    assert '"event": "e"' in out[2]
    assert '"event": "d"' in out[3]
