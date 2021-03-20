import pytest

from hms_kivy.hms import HMS


class TestHmsClass:
    def test_hms(self):
        hms = HMS()

        assert hms
