import pytest

from hms_kivy.rfid import RFID


class TestRfidClass:
    def test_rfid(self):
        rfid = RFID()

        assert rfid

    def test_clear_queue(self):
        rfid = RFID()

        rfid.q_RFID.put_nowait("12ed89a5")
        rfid.q_RFID.put_nowait("39e8990f")
        rfid.q_RFID.put_nowait("46a46635")
        assert rfid.q_RFID.empty() == False

        rfid.clear_queue()
        assert rfid.q_RFID.empty() == True
