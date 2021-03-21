#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" HMS Kiosk

    Requirements (pi only)
    pi-rc522 (https://github.com/kevinvalk/pi-rc522.git)

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
import time
import queue
import json

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.logger import Logger, LOG_LEVELS
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.settings import SettingsWithTabbedPanel

from .hms import HMS
from .rfid import RFID
from .screens import SettingsPasswordScreen, LogInScreen

Logger.setLevel(LOG_LEVELS["debug"])


class ScreenSwitcher(ScreenManager):
    # The screens can be added on the __init__ method like this or on the .kv file
    def __init__(self, **kwargs):
        super(ScreenSwitcher, self).__init__(**kwargs)
        self.add_widget(LogInScreen())
        self.add_widget(SettingsPasswordScreen())


# TopBar Digital Clock
class ClockLabel(ButtonBehavior, Label):
    def __init__(self, **kwargs):
        super(ClockLabel, self).__init__(**kwargs)
        Clock.schedule_interval(self.update, 1)

    def update(self, *args):
        self.text = time.strftime("%H:%M:%S")


class KioskApp(App):
    # use_kivy_settings = False
    settings_cls = SettingsWithTabbedPanel
    userToken = None
    rfid = RFID()
    hms = HMS()
    previousScreen = None

    def build_config(self, config):
        config.setdefaults("Kiosk", {"settings_password": "1234"})
        self.hms.build_config(config)
        self.rfid.build_config(config)

    def build_settings(self, settings):
        jsondata = json.dumps(
            [
                {
                    "type": "string",
                    "title": "Settings password",
                    "section": "Kiosk",
                    "key": "settings_password",
                },
            ]
        )
        settings.add_json_panel("Kiosk", self.config, data=jsondata)
        self.hms.build_settings(settings, self.config)
        self.rfid.build_settings(settings, self.config)

    def on_config_change(self, config, section, key, value):
        pass

    def on_start(self, *args):
        pass

    def on_stop(self, *args):
        self.rfid.stop_RFID_read()

    def updateTitle(self, text=""):
        self.root.ids.title.text = text

    def open_settings_password(self):
        self.setScreen("settingsPassword")

    def setScreen(self, screen):
        self.previousScreen = self.root.ids.manager.current
        self.root.ids.manager.current = screen

    def restorePreviousScreen(self):
        previousScreen = self.root.ids.manager.current
        self.root.ids.manager.current = self.previousScreen
        self.previousScreen = previousScreen

    def login(self, userToken):
        Logger.debug("login")
        self.root.ids.logout.disabled = False
        self.userToken = userToken

    def logout(self):
        Logger.debug("logout")
        self.root.ids.logout.disabled = True
        self.userToken = None
        self.updateTitle()
        self.root.ids.manager.current = "login"


def main():
    Window.size = (800, 480)
    try:
        KioskApp().run()
    except KeyboardInterrupt:
        KioskApp().stop()


if __name__ == "__main__":
    main()
