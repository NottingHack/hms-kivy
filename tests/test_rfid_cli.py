import pytest
from typer.testing import CliRunner

from hms_kivy.rfid.cli import app, state, DEFAULT_PORT, send_packet

runner = CliRunner(mix_stderr=False)


def test_app():
    assert state["port"] == DEFAULT_PORT
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    # assert "Hello Camila" in result.stdout
    # assert "Let's have a coffee in Berlin" in result.stdout


def test_custom_port_string():
    result = runner.invoke(app, ["--port", "nope"])
    assert result.exit_code == 2
    assert "Invalid value for '--port' / '-p'" in result.stderr


def text_custom_port():
    port = 1234
    result = runner.invoke(app, ["-p", port])
    assert result.exit_code == 0
    assert f"Will use UDP port {port}" in result.stdout


def test_present_no_uid():
    result = runner.invoke(app, "present")
    assert result.exit_code == 2
    assert "Error: Missing argument 'UID'." in result.stderr


def test_present_with_uid():
    uid = "12ed89a5"
    result = runner.invoke(app, ["present", uid])
    assert result.exit_code == 0
    assert f"Presenting RFID {uid}" in result.stdout


def test_remove():
    result = runner.invoke(app, "remove")
    assert result.exit_code == 0
    assert "Removing RFID" in result.stdout


def test_send_packet():
    # TODO: https://github.com/miketheman/pytest-socket
    pass
