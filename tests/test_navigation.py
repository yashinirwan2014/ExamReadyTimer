import sys
from pathlib import Path

from navigation import dashboard_command

def test_source_dashboard_command_uses_main_entrypoint(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "executable", "/usr/bin/python-test")
    assert dashboard_command(tmp_path, frozen=False) == ["/usr/bin/python-test", str(tmp_path / "main.py")]

def test_windows_packaged_dashboard_command(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32")
    assert dashboard_command(tmp_path, frozen=True) == [str(tmp_path / "ExamReadyTimer.exe")]

def test_unix_packaged_dashboard_command(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    assert dashboard_command(tmp_path, frozen=True) == [str(tmp_path / "ExamReadyTimer")]
