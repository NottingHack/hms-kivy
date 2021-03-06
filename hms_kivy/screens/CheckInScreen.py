# -*- coding: utf-8 -*-
""" HMS Kiosk CheckInScreen

    Author: Matt Lloyd
    Copyright (c) 2021 Nottingham Hackspace

    The MIT License (MIT)

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

__all__ = ("CheckInScreen",)

import queue
import json

from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.screenmanager import Screen

from ..utils import load_kv


class CheckInScreen(Screen):
    currentMembers = StringProperty("?")
    votingMembers = StringProperty("?")
    quorum = StringProperty("?")
    attendees = StringProperty("?")
    proxies = StringProperty("?")
    representedProxies = StringProperty("?")
    checkInCount = StringProperty("?")
    quorumMetState = BooleanProperty(False)
    statusMessage = StringProperty("")

    _app = None

    def __init__(self, **kwargs):
        super(CheckInScreen, self).__init__(**kwargs)
        # hms.checkInScreen = self

    def on_enter(self):
        Logger.debug("CheckInScreen@on_enter")
        self._app = App.get_running_app()
        self._app.update_title("Finding Next Meeting")

    def on_leave(self):
        Logger.debug("CheckInScreen@on_leave")

    def updateCheckInCounts(self, counts):
        Logger.debug("CheckInScreen@updateCheckInCounts")

        self.checkInScreen.currentMembers = str(counts["currentMembers"])
        self.checkInScreen.votingMembers = str(counts["votingMembers"])
        self.checkInScreen.quorum = str(counts["quorum"])
        self.checkInScreen.attendees = str(counts["attendees"])
        self.checkInScreen.proxies = str(counts["proxies"])
        self.checkInScreen.representedProxies = str(counts["representedProxies"])
        self.checkInScreen.checkInCount = str(counts["checkInCount"])
        self.checkInScreen.quorumMetState = (
            True if counts["checkInCount"] >= counts["quorum"] else False
        )


load_kv()
