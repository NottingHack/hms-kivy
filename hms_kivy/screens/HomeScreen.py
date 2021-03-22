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
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen

from ..utils import load_kv


class HomeScreen(Screen):
    _app = None

    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)

    def on_enter(self):
        Logger.debug("HomeScreen: on_enter")
        self.status_message = ""
        self._app = App.get_running_app()
        self._app.update_title(f"Welcome {self._app.user['name']}")

        # check permission to display buttons?

    def on_leave(self):
        Logger.debug("HomeScreen: on_leave")


load_kv()
