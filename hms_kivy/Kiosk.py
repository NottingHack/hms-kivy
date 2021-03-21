#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" HMS Kiosk

    Requirements (pi only)
    pi-rc522 (https://github.com/kevinvalk/pi-rc522.git)

    Author: Matt Lloyd
    Copyright (c) 2020 Nottingham Hackspace

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
from binascii import hexlify
import urllib.request, urllib.parse, urllib.error
import time
import queue
import threading
import socket
import select
import json

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.logger import Logger, LOG_LEVELS
from kivy.network.urlrequest import UrlRequest
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.settings import SettingsWithTabbedPanel

from .hms import HMS
from .rfid import RFID

# Logger.setLevel(LOG_LEVELS["debug"])


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


class LogInScreen(Screen):
    statusMessage = StringProperty("")

    _app = None

    def __init__(self, **kwargs):
        super(LogInScreen, self).__init__(**kwargs)

    def on_enter(self):
        self.statusMessage = ""
        self._app = App.get_running_app()
        # start checking RFID's
        self._app.rfid.start_RFID_read()
        self.eventCheckRFID = Clock.schedule_interval(self.checkForRFID, 0.5)

    def on_leave(self):
        self.statusMessage = ""
        # start checking RFID's
        self._app.rfid.stop_RFID_read()
        try:
            self.eventCheckRFID.cancel()
        except:
            pass

    def checkForRFID(self, *args):
        try:
            uid = self._app.rfid.q_RFID.get_nowait()
        except queue.Empty:
            pass
        else:
            # get/refresh clientToken first
            self.statusMessage = "Checking Card"
            self._app.login([])
            params = json.dumps(
                {
                    "rfidSerial": uid.decode("utf-8"),
                }
            )

            # headers = {
            #     "Content-type": "application/json",
            #     "Accept": "application/json",
            #     "Authorization": "{} {}".format(
            #         self._token["token_type"], self._token["access_token"]
            #     ),
            # }

            # UrlRequest(
            #     url=self._meetingCheckInRfidURL.format(
            #         baseURL=self._baseURLProd if self.production else self._baseURLDev,
            #         meeting=self._meetinId,
            #     ),
            #     req_body=params,
            #     req_headers=headers,
            #     on_error=self.checkInError,
            #     on_failure=self.checkInFailure,
            #     on_progress=None,
            #     on_redirect=self.checkInRedirect,
            #     on_success=self.checkInSuccess,
            #     timeout=5,
            #     verify=self.production,
            # )


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
        if self.password.text == self._app.config.get("Kiosk", "settings_password"):
            self._app.open_settings()
            self.password.text = ""
            self._app.restorePreviousScreen()

    def on_cancel(self):
        self.password.text = ""
        self._app.restorePreviousScreen()


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
        self.previousScreen = self.root.ids.manager.current
        self.root.ids.manager.current = "settingsPassword"

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
