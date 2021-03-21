# -*- coding: utf-8 -*-
""" HMS Kiosk SettingsPasswordScreen

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

__all__ = ("SettingsPasswordScreen",)

from kivy.app import App
from kivy.logger import Logger
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen

from ..utils import load_kv


class SettingsPasswordScreen(Screen):
    statusMessage = StringProperty("")
    password = ObjectProperty(None)

    _app = None

    def __init__(self, **kwargs):
        super(SettingsPasswordScreen, self).__init__(**kwargs)

    def on_enter(self):
        self.statusMessage = ""
        self._app = App.get_running_app()
        self._app.updateTitle("Settings Locked")

    def on_leave(self):
        self._app.updateTitle("")

    def on_confirm(self):
        Logger.info(self.password.text)
        Logger.info(self._app.config.get("Kiosk", "settings_password"))
        if self.password.text == self._app.config.get("Kiosk", "settings_password"):
            self._app.open_settings()
            self.password.text = ""
            self._app.restorePreviousScreen()

    def on_cancel(self):
        self.password.text = ""
        self._app.restorePreviousScreen()


load_kv()
