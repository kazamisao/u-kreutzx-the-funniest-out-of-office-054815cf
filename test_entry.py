"""Tests for the funniest out-of-office entry program (main.py).

Behavior: running `python3 main.py` with MAKEFUN_OUTPUT_DIR set writes
exactly one out-of-office line to $MAKEFUN_OUTPUT_DIR/entry.txt:
1-140 characters, a single line, not only whitespace, deterministic
(two runs produce identical bytes), no network.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent
MAIN = REPO / "main.py"


def run_program(out_dir: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["MAKEFUN_OUTPUT_DIR"] = str(out_dir)
    return subprocess.run(
        [sys.executable, str(MAIN)],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_entry_file_exists_and_is_valid():
    """entry.txt exists, is 1-140 chars, one line, not only whitespace."""
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        result = run_program(out)
        assert result.returncode == 0, f"main.py failed: {result.stderr}"
        entry = out / "entry.txt"
        assert entry.exists(), "entry.txt was not written"
        text = entry.read_text(encoding="utf-8")
        assert 1 <= len(text) <= 140, f"length {len(text)} outside 1-140"
        assert text.strip(), "entry is only whitespace"
        assert "\n" not in text.strip(), "entry must be a single line"


def test_deterministic_two_runs_identical():
    """Two runs write byte-identical entry.txt."""
    with tempfile.TemporaryDirectory() as tmp1, tempfile.TemporaryDirectory() as tmp2:
        out1, out2 = Path(tmp1), Path(tmp2)
        assert run_program(out1).returncode == 0
        assert run_program(out2).returncode == 0
        b1 = (out1 / "entry.txt").read_bytes()
        b2 = (out2 / "entry.txt").read_bytes()
        assert b1 == b2, "two runs produced different entry.txt bytes"


def test_no_trailing_newline_inflates_length():
    """The written text has no trailing newline (length counts the reply only)."""
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        assert run_program(out).returncode == 0
        text = (out / "entry.txt").read_text(encoding="utf-8")
        assert text == text.strip(), "entry has leading/trailing whitespace"


def test_reply_is_an_out_of_office_with_a_twist():
    """The line reads as an out-of-office reply with a real twist.

    The brief wants a reply a real person would set, turning on a
    surprise: field trip, snack treasurer, and a nine-year-old's
    audit queue for the sender's urgent email.
    """
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        assert run_program(out).returncode == 0
        text = (out / "entry.txt").read_text(encoding="utf-8")
        assert text.startswith("Out of office"), "reply does not open as out-of-office"
        assert "field trip" in text, "reply never says where they are"
        assert "snack treasurer" in text, "reply never names the twist job"
        assert "nine-year-old" in text, "reply never names the auditor"


def test_program_uses_stdlib_only():
    """main.py imports only the standard library (os, pathlib)."""
    import ast

    tree = ast.parse(MAIN.read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert imports <= {"os", "pathlib"}, f"non-stdlib imports: {imports}"
