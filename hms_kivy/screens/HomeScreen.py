# -*- coding: utf-8 -*-
""" HMS Kiosk HomeScreen

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

__all__ = ("HomeScreen",)
import json

from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen

from ..utils import load_kv


class HomeScreen(Screen):
    status_message = StringProperty("hello")
    balance = StringProperty("")
    register_rfid_allowed = BooleanProperty(False)
    meeting_check_in_allowed = BooleanProperty(False)
    _app = None
    user = None

    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)

    def on_enter(self):
        Logger.debug("HomeScreen: on_enter")
        self.status_message = ""
        self._app = App.get_running_app()
        self.user = self._app.user
        self._app.update_title(f"Welcome {self.user.get_name()}")
        self.balance = f"Snackspace balance: £{(2000 / 100):.2f}"

        # self.register_rfid_allowed = self.user.can("search.users") and self.user.can("pins.reactivate")
        # self.meeting_check_in_allowed = self.user.can("governance.meeting.checkIn") # and next agm?

    def on_leave(self):
        Logger.debug("HomeScreen: on_leave")

    def on_projects(self):
        Logger.debug("HomeScreen: on_projects")

    def on_boxes(self):
        Logger.debug("HomeScreen: on_boxes")

    def on_register_rfid(self):
        Logger.debug("HomeScreen: on_register_rfid")

    def on_meeting_check_in(self):
        Logger.debug("HomeScreen: on_meeting_check_in")


load_kv()
