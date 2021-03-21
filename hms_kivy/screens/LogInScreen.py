# -*- coding: utf-8 -*-
""" HMS Kiosk LogInScreen

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

__all__ = ("LogInScreen",)

import queue
import json

from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen

from ..utils import load_kv


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


load_kv()
