# -*- coding: utf-8 -*-
""" HMS Kiosk (HMS module)

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
import json
import urllib.request, urllib.parse, urllib.error

from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.logger import Logger
from kivy.network.urlrequest import UrlRequest


class HMS:
    _token_URL = "{baseURL}/oauth/token"
    _rfid_token_URL = "{baseUrl}/api/cc/rfid-token"
    _can_check_URL = "{baseURL}/api/can"
    _client_token = []
    _user_token = []

    def __init__(self):
        pass

    def build_config(self, config):
        Logger.debug("HMS: build_config")
        config.setdefaults(
            "HMS",
            {
                "url": "https://lspace.nottinghack.org.uk",
                "client_id": "",
                "client_secret": "",
            },
        )

    def build_settings(self, settings, config):
        Logger.debug("HMS: build_settings")
        jsondata = json.dumps(
            [
                {
                    "type": "string",
                    "title": "URL",
                    "desc": "URL to HMS, include the schema but no trailing slash",
                    "section": "HMS",
                    "key": "url",
                },
                {
                    "type": "string",
                    "title": "Client ID",
                    "desc": "Passport client credentials ID",
                    "section": "HMS",
                    "key": "client_id",
                },
                {
                    "type": "string",
                    "title": "Client Secret",
                    "desc": "Passport client credentials secret",
                    "section": "HMS",
                    "key": "client_secret",
                },
            ]
        )
        settings.add_json_panel("HMS", config, data=jsondata)

    def on_config_change(self, config, section, key, value):
        Logger.debug("HMS: on_config_change")

    def login(self, uid, on_success, on_fail):
        """Login into HMS using a given RFIDTag UID"""
        Logger.debug(f"HMS: login: {uid}")

        Clock.schedule_once(lambda dt: on_success({"name": "Matt"}, {}), 2)
        # Clock.schedule_once(lambda dt: on_fail("Do'h"), 2)
