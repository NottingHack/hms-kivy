# -*- coding: utf-8 -*-
""" HMS Kiosk BoxesScreen

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

__all__ = ("BoxesScreen",)
import json

from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.uix.screenmanager import Screen

from ..utils import load_kv
from ..hms import Boxes


class BoxesScreen(Screen):
    _app = None
    user = None
    boxes = None

    def __init__(self, **kwargs):
        super(BoxesScreen, self).__init__(**kwargs)

    def on_enter(self):
        Logger.debug("BoxesScreen: on_enter")
        self._app = App.get_running_app()
        self.user = self._app.user
        self._app.set_home_button("Home")
        self._app.update_title(f"{self.user.get_name()}'s Boxes")
        self._app.home_button.bind(on_release=self.on_home_pressed)

        self.boxes = Boxes(self._app.hms)
        self.boxes.index(self.index_cb)

    def on_leave(self):
        Logger.debug("BoxesScreen: on_leave")
        self._app.home_button.unbind(on_release=self.on_home_pressed)

    def on_home_pressed(self, *args):
        Logger.debug("BoxesScreen: on_home_pressed")
        self._app.set_screen("home")

    def index_cb(self):
        Logger.debug("BoxesScreen: index_cb")


load_kv()
