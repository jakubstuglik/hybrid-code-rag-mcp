"""
Tests for shared/log.py — unified logging library.

Tests cover:
    - configure(): stream redirection
    - log(): timestamped messages, empty call (blank line)
    - log_raw(): raw output without timestamp
    - log_error(): timestamped error messages
    - log_warn(): timestamped warning messages
    - _timestamp(): format correctness
    - Isolation: each test resets module state
    - Flush behavior: output is flushed immediately
    - Edge cases: empty strings, special characters, multiline, unicode
"""

import io
import re
import sys
from unittest.mock import patch

import pytest

import shared.log as log_module
from shared.log import configure, log, log_error, log_raw, log_warn


# ────────────────────────────────────────────────
# Fixtures
# ────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _reset_stream():
    """Reset the log module's _stream to a fresh StringIO before each test,
    and restore sys.stdout after."""
    original = log_module._stream
    buf = io.StringIO()
    log_module._stream = buf
    yield buf
    log_module._stream = original


# Regex that matches the timestamp format [YYYY-MM-DD HH:MM:SS.mmm]
TS_RE = re.compile(r"^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}\]")


# ────────────────────────────────────────────────
# configure()
# ────────────────────────────────────────────────


class TestConfigure:
    """Tests for configure() — stream redirection."""

    def test_configure_changes_stream(self):
        """configure() should replace the output stream."""
        new_stream = io.StringIO()
        configure(new_stream)
        assert log_module._stream is new_stream

    def test_configure_to_stderr(self):
        """configure(sys.stderr) should direct output to stderr."""
        configure(sys.stderr)
        assert log_module._stream is sys.stderr

    def test_configure_output_goes_to_new_stream(self):
        """After configure(), log output should appear in the new stream."""
        new_stream = io.StringIO()
        configure(new_stream)
        log("hello")
        output = new_stream.getvalue()
        assert "hello" in output

    def test_configure_old_stream_receives_nothing(self, _reset_stream):
        """After configure(), the old stream should not receive new output."""
        old_buf = _reset_stream
        new_stream = io.StringIO()
        configure(new_stream)
        log("after redirect")
        # old_buf should have nothing written after configure
        old_output = old_buf.getvalue()
        assert "after redirect" not in old_output


# ────────────────────────────────────────────────
# _timestamp()
# ────────────────────────────────────────────────


class TestTimestamp:
    """Tests for the internal _timestamp() helper."""

    def test_timestamp_format(self):
        """_timestamp() should return YYYY-MM-DD HH:MM:SS format."""
        ts = log_module._timestamp()
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}", ts), (
            f"Bad format: {ts}"
        )

    def test_timestamp_reflects_current_time(self):
        """_timestamp() should match the current clock (to the minute)."""
        from datetime import datetime

        now = datetime.now()
        ts = log_module._timestamp()
        # At minimum, the date and hour:minute should match
        expected_prefix = now.strftime("%Y-%m-%d %H:%M")
        assert ts.startswith(expected_prefix), (
            f"Timestamp {ts} doesn't match current time {expected_prefix}"
        )


# ────────────────────────────────────────────────
# log()
# ────────────────────────────────────────────────


class TestLog:
    """Tests for log() — timestamped messages."""

    def test_log_basic_message(self, _reset_stream):
        """log('msg') should output '[YYYY-MM-DD HH:MM:SS] msg'."""
        log("Starting indexing")
        output = _reset_stream.getvalue()
        assert TS_RE.search(output), f"No timestamp in: {output!r}"
        assert "Starting indexing" in output

    def test_log_message_format(self, _reset_stream):
        """log() output should be exactly '[YYYY-MM-DD HH:MM:SS] msg\\n'."""
        log("test")
        output = _reset_stream.getvalue()
        assert re.fullmatch(
            r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}\] test\n", output
        ), f"Unexpected format: {output!r}"

    def test_log_empty_call_prints_blank_line(self, _reset_stream):
        """log() with no args should print a blank line (no timestamp)."""
        log()
        output = _reset_stream.getvalue()
        assert output == "\n", f"Expected blank line, got: {output!r}"

    def test_log_empty_string_prints_blank_line(self, _reset_stream):
        """log('') should print a blank line (no timestamp)."""
        log("")
        output = _reset_stream.getvalue()
        assert output == "\n", f"Expected blank line, got: {output!r}"

    def test_log_multiple_calls(self, _reset_stream):
        """Multiple log() calls produce multiple timestamped lines."""
        log("first")
        log("second")
        lines = _reset_stream.getvalue().strip().split("\n")
        assert len(lines) == 2
        assert "first" in lines[0]
        assert "second" in lines[1]

    def test_log_special_characters(self, _reset_stream):
        """log() should handle special characters correctly."""
        log("path=C:\\Users\\test & echo 'hello' | grep \"x\"")
        output = _reset_stream.getvalue()
        assert "C:\\Users\\test" in output
        assert "& echo" in output

    def test_log_unicode(self, _reset_stream):
        """log() should handle unicode text."""
        log("Processing: \u0414\u0435\u043b\u044c\u0444\u0438 \u2014 \u2713 done")
        output = _reset_stream.getvalue()
        assert "\u0414\u0435\u043b\u044c\u0444\u0438" in output
        assert "\u2713" in output

    def test_log_multiline_message(self, _reset_stream):
        """log() with a multiline string should output it as-is."""
        log("line1\nline2\nline3")
        output = _reset_stream.getvalue()
        assert "line1\nline2\nline3" in output

    def test_log_very_long_message(self, _reset_stream):
        """log() should handle very long messages without truncation."""
        long_msg = "x" * 10000
        log(long_msg)
        output = _reset_stream.getvalue()
        assert long_msg in output


# ────────────────────────────────────────────────
# log_raw()
# ────────────────────────────────────────────────


class TestLogRaw:
    """Tests for log_raw() — no timestamp output."""

    def test_log_raw_no_timestamp(self, _reset_stream):
        """log_raw() should NOT include a timestamp."""
        log_raw("separator line")
        output = _reset_stream.getvalue()
        assert not TS_RE.search(output), f"Unexpected timestamp in: {output!r}"
        assert "separator line" in output

    def test_log_raw_exact_output(self, _reset_stream):
        """log_raw('text') should output exactly 'text\\n'."""
        log_raw("hello")
        assert _reset_stream.getvalue() == "hello\n"

    def test_log_raw_empty_call(self, _reset_stream):
        """log_raw() with no args should print a blank line."""
        log_raw()
        assert _reset_stream.getvalue() == "\n"

    def test_log_raw_empty_string(self, _reset_stream):
        """log_raw('') should print a blank line."""
        log_raw("")
        assert _reset_stream.getvalue() == "\n"

    def test_log_raw_separator(self, _reset_stream):
        """log_raw() is used for table separators — test that pattern."""
        log_raw("=" * 70)
        output = _reset_stream.getvalue().strip()
        assert output == "=" * 70

    def test_log_raw_table_formatting(self, _reset_stream):
        """log_raw() should preserve table-like formatting."""
        log_raw("  Name         Count")
        log_raw("  ----------   -----")
        log_raw("  .pas         42")
        output = _reset_stream.getvalue()
        assert "  Name         Count\n" in output
        assert "  .pas         42\n" in output


# ────────────────────────────────────────────────
# log_error()
# ────────────────────────────────────────────────


class TestLogError:
    """Tests for log_error() — timestamped error messages."""

    def test_log_error_format(self, _reset_stream):
        """log_error() should produce '[YYYY-MM-DD HH:MM:SS] [ERROR] msg'."""
        log_error("File not found")
        output = _reset_stream.getvalue()
        assert re.fullmatch(
            r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}\] \[ERROR\] File not found\n",
            output,
        ), f"Unexpected format: {output!r}"

    def test_log_error_has_timestamp(self, _reset_stream):
        """log_error() output should start with a timestamp."""
        log_error("bad thing")
        output = _reset_stream.getvalue()
        assert TS_RE.search(output)

    def test_log_error_has_error_tag(self, _reset_stream):
        """log_error() output should contain [ERROR] tag."""
        log_error("something broke")
        output = _reset_stream.getvalue()
        assert "[ERROR]" in output

    def test_log_error_message_content(self, _reset_stream):
        """log_error() should include the full error message."""
        log_error("Connection refused on port 6333")
        output = _reset_stream.getvalue()
        assert "Connection refused on port 6333" in output

    def test_log_error_special_chars(self, _reset_stream):
        """log_error() should handle paths and special characters."""
        log_error("Parse failed for C:\\source\\unit1.pas: unexpected token")
        output = _reset_stream.getvalue()
        assert "C:\\source\\unit1.pas" in output
        assert "unexpected token" in output


# ────────────────────────────────────────────────
# log_warn()
# ────────────────────────────────────────────────


class TestLogWarn:
    """Tests for log_warn() — timestamped warning messages."""

    def test_log_warn_format(self, _reset_stream):
        """log_warn() should produce '[YYYY-MM-DD HH:MM:SS] [WARN] msg'."""
        log_warn("Skipping empty file")
        output = _reset_stream.getvalue()
        assert re.fullmatch(
            r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}\] \[WARN\] Skipping empty file\n",
            output,
        ), f"Unexpected format: {output!r}"

    def test_log_warn_has_timestamp(self, _reset_stream):
        """log_warn() output should start with a timestamp."""
        log_warn("low disk space")
        output = _reset_stream.getvalue()
        assert TS_RE.search(output)

    def test_log_warn_has_warn_tag(self, _reset_stream):
        """log_warn() output should contain [WARN] tag."""
        log_warn("something")
        output = _reset_stream.getvalue()
        assert "[WARN]" in output

    def test_log_warn_message_content(self, _reset_stream):
        """log_warn() should include the full warning message."""
        log_warn("File encoding is not UTF-8: unit2.pas")
        output = _reset_stream.getvalue()
        assert "File encoding is not UTF-8: unit2.pas" in output


# ────────────────────────────────────────────────
# Flush behavior
# ────────────────────────────────────────────────


class TestFlush:
    """Tests that output is flushed immediately (flush=True in print calls)."""

    def test_log_calls_print_with_flush(self):
        """log() should call print with flush=True."""
        buf = io.StringIO()
        configure(buf)
        with patch("builtins.print") as mock_print:
            log("test flush")
            mock_print.assert_called_once()
            _, kwargs = mock_print.call_args
            assert kwargs.get("flush") is True

    def test_log_raw_calls_print_with_flush(self):
        """log_raw() should call print with flush=True."""
        buf = io.StringIO()
        configure(buf)
        with patch("builtins.print") as mock_print:
            log_raw("test flush")
            mock_print.assert_called_once()
            _, kwargs = mock_print.call_args
            assert kwargs.get("flush") is True

    def test_log_error_calls_print_with_flush(self):
        """log_error() should call print with flush=True."""
        buf = io.StringIO()
        configure(buf)
        with patch("builtins.print") as mock_print:
            log_error("test flush")
            mock_print.assert_called_once()
            _, kwargs = mock_print.call_args
            assert kwargs.get("flush") is True

    def test_log_warn_calls_print_with_flush(self):
        """log_warn() should call print with flush=True."""
        buf = io.StringIO()
        configure(buf)
        with patch("builtins.print") as mock_print:
            log_warn("test flush")
            mock_print.assert_called_once()
            _, kwargs = mock_print.call_args
            assert kwargs.get("flush") is True


# ────────────────────────────────────────────────
# Isolation / state management
# ────────────────────────────────────────────────


class TestIsolation:
    """Tests for module-level state isolation."""

    def test_default_stream_is_stdout(self):
        """Before any configure(), _stream should default to sys.stdout."""
        # We need to check the module's default, but our fixture overrides it.
        # Verify the source code default by reimporting.
        import importlib

        fresh = importlib.reload(log_module)
        assert fresh._stream is sys.stdout
        # Restore for other tests
        importlib.reload(log_module)

    def test_configure_does_not_affect_sys_stdout(self):
        """configure() should not mutate sys.stdout itself."""
        original_stdout = sys.stdout
        buf = io.StringIO()
        configure(buf)
        assert sys.stdout is original_stdout

    def test_multiple_configures(self):
        """Multiple configure() calls should each replace the stream."""
        buf1 = io.StringIO()
        buf2 = io.StringIO()
        configure(buf1)
        log("to buf1")
        configure(buf2)
        log("to buf2")
        assert "to buf1" in buf1.getvalue()
        assert "to buf2" in buf2.getvalue()
        assert "to buf2" not in buf1.getvalue()
        assert "to buf1" not in buf2.getvalue()


# ────────────────────────────────────────────────
# Integration: mixed calls
# ────────────────────────────────────────────────


class TestIntegration:
    """Integration tests combining multiple log functions."""

    def test_mixed_log_calls(self, _reset_stream):
        """Mix of log/log_raw/log_error/log_warn produces correct output."""
        log("start")
        log_raw("=" * 20)
        log_warn("caution")
        log_error("failure")
        log()
        log_raw("done")

        lines = _reset_stream.getvalue().split("\n")
        # Remove trailing empty string from final \n
        if lines and lines[-1] == "":
            lines = lines[:-1]

        assert len(lines) == 6
        assert TS_RE.search(lines[0]) and "start" in lines[0]
        assert lines[1] == "=" * 20
        assert "[WARN]" in lines[2] and "caution" in lines[2]
        assert "[ERROR]" in lines[3] and "failure" in lines[3]
        assert lines[4] == ""  # blank line from log()
        assert lines[5] == "done"

    def test_log_then_configure_then_log(self, _reset_stream):
        """Output goes to the correct stream after mid-flow configure()."""
        log("before")
        new_buf = io.StringIO()
        configure(new_buf)
        log("after")

        assert "before" in _reset_stream.getvalue()
        assert "after" not in _reset_stream.getvalue()
        assert "after" in new_buf.getvalue()
        assert "before" not in new_buf.getvalue()
