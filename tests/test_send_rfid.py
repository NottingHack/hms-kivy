import pytest

from hms_kivy.send_rfid import send_rfid

## https://github.com/mindflayer/python-mocket?


def test_send_rfid():
    assert send_rfid("12ed89a5".encode())
