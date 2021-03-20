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
from kivy.network.urlrequest import UrlRequest
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty

from .hms import HMS
from .rfid import RFID


class ScreenSwitcher(ScreenManager):
    # The screens can be added on the __init__ method like this or on the .kv file
    def __init__(self, **kwargs):
        super(ScreenSwitcher, self).__init__(**kwargs)
        self.add_widget(LogInScreen())


# TopBar Digital Clock
class ClockLabel(Label):
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
            #     url         = self._meetingCheckInRfidURL.format(baseURL=self._baseURLProd if self.production else self._baseURLDev, meeting=self._meetinId),
            #     req_body    = params,
            #     req_headers = headers,
            #     on_error    = self.checkInError,
            #     on_failure  = self.checkInFailure,
            #     on_progress = None,
            #     on_redirect = self.checkInRedirect,
            #     on_success  = self.checkInSuccess,
            #     timeout     = 5,
            #     verify      = self.production,
            #     )


class KioskApp(App):
    userToken = None
    rfid = RFID()

    def build_config(self, config):
        config.setdefaults(
            "HMS",
            {
                "url": "https://lspace.nottinghack.org.uk",
                "clientId": "9",
                "clientSecret": "ctYIiYVX1oIVrOSXroPn2jRIkxCb4FsMEVpjoVYb",
            },
        )

    def build_settings(self, settings):
        jsondata = """... put the json data here ..."""
        settings.add_json_panel("Test application", self.config, data=jsondata)

    def on_config_change(self, config, section, key, value):
        pass

    def on_start(self, *args):
        pass

    def on_stop(self, *args):
        self.rfid.stop_RFID_read()

    def updateTitle(self, text=""):
        self.root.ids.title.text = text

    def login(self, userToken):
        print("login")
        self.root.ids.logout.disabled = False
        self.userToken = userToken

    def logout(self):
        print("logout")
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
