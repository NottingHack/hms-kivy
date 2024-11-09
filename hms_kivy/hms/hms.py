# -*- coding: utf-8 -*-

""" HMS Kiosk (HMS module)

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
import json
from time import time
from http import HTTPStatus

from kivy.app import App
from kivy.cache import Cache
from kivy.clock import Clock

# from kivy.config import Config
from kivy.logger import Logger
from kivy.network.urlrequest import UrlRequest
from kivy.storage.jsonstore import JsonStore


class HMS:
    _config = None
    _store = JsonStore("hms.json")
    _token_URL = "oauth/token"
    _rfid_token_URL = "api/cc/rfid-token"

    _rfid_tag_register_URL = "api/cc/rfid-tags/register"

    _client_token_request = None
    _rfid_token_request = None

    _json_headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
    }

    def __init__(self):
        Cache.register("HMS")
        if self._store.exists("client_token"):
            client_token = self._store.get("client_token")
            if client_token["expires_at"] > time():
                Logger.debug("HMS: __init__: loaded client_token from JsonStore")
                Cache.append(
                    "HMS",
                    "client_token",
                    client_token,
                    client_token["expires_at"] - time(),
                )

    def __del__(self):
        client_token = Cache.get("HMS", "client_token")
        if client_token is not None:
            self._store.put("client_token", **client_token)
            Logger.debug("HMS: __del__: put client_token in JsonStore")

    def build_config(self, config):
        Logger.debug("HMS: build_config")
        config.setdefaults(
            "HMS",
            {
                "url": "https://hms.nottinghack.org.uk/",
                "client_id": "",
                "client_secret": "",
                "verify_ssl": True,
                "ca_file": "",
            },
        )

        self._config = config

    def build_settings(self, settings, config):
        Logger.debug("HMS: build_settings")
        jsondata = json.dumps(
            [
                {
                    "type": "string",
                    "title": "URL",
                    "desc": "URL to HMS, include the schema & trailing slash",
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
                {
                    "type": "bool",
                    "title": "Verify SSL",
                    "desc": "If False, disables SSL CA certificate verification",
                    "section": "HMS",
                    "key": "verify_ssl",
                },
                {
                    "type": "path",
                    "title": "CA certificate",
                    "desc": "SSL CA file path to validate HTTPS certificates against",
                    "section": "HMS",
                    "key": "ca_file",
                },
            ]
        )
        settings.add_json_panel("HMS", config, data=jsondata)

    def on_config_change(self, config, section, key, value):
        Logger.debug("HMS: on_config_change")
        if section != "HMS":
            return

        if key == "client_id" or key == "client_secret":
            Cache.remove("HMS", "client_token")
            self._get_client_token()

    def start(self):
        Logger.debug("HMS: start")
        self._get_client_token()

    def stop(self):
        Logger.debug("HMS: stop")

        client_token = Cache.get("HMS", "client_token")
        if client_token is not None:
            self._store.put("client_token", **client_token)
            Logger.debug("HMS: stop: put client_token in JsonStore")

    def _get_client_token(self):
        """Get the client token from the Cache or fetch a new on if needed"""
        Logger.debug("HMS: _get_client_token")

        client_token = Cache.get("HMS", "client_token")
        if client_token is not None:
            return client_token

        # did not find a token in the Cache so start request to get a new one

        # are we already in the middle of a request
        if (
            self._client_token_request is not None
            and self._client_token_request.is_finished == False
        ):
            return None

        Logger.debug("HMS: _get_client_token: fetching new client token")

        def _got_client_token(request, result):
            Logger.debug("HMS: _get_client_token: got new client token")

            result["expires_at"] = time() + result["expires_in"]
            Cache.append("HMS", "client_token", result, result["expires_in"])
            self._client_token_request = None

        def _client_token_failure(request, result):
            Logger.warning("HMS: _get_client_token: failed to get new client token")
            Logger.warning(request)
            Logger.warning(result)
            self._client_token_request = None
            # try again in a few? maybe count attempts
            Clock.schedule_once(self._get_client_token(), 5)
            # raise an error on the UI?

        params = json.dumps(
            {
                "grant_type": "client_credentials",
                "client_id": self._config.get("HMS", "client_id"),
                "client_secret": self._config.get("HMS", "client_secret"),
            }
        )

        self._client_token_request = UrlRequest(
            url=self._config.get("HMS", "url") + self._token_URL,
            req_body=params,
            req_headers=self._json_headers,
            on_error=_client_token_failure,
            on_failure=_client_token_failure,
            on_success=_got_client_token,
            timeout=5,
            ca_file=self._config.get("HMS", "ca_file"),
            verify=self._config.getboolean("HMS", "verify_ssl"),
        )

    def get_rfid_token(self, uid=None, on_success=None, on_fail=None):
        """Login into HMS using a given RFIDTag UID"""
        Logger.debug(f'HMS: get_rfid_token: "{uid}"')

        rfid_token = Cache.get("HMS", "rfid_token")
        if rfid_token is not None:
            return rfid_token

        if uid is None:
            return None

        # are we already in the middle of a request
        if (
            self._rfid_token_request is not None
            and self._rfid_token_request.is_finished == False
        ):
            # should we cancel it or what?
            self._rfid_token_request.cancel()
            self._rfid_token_request = None

        # get client token
        client_token = self._get_client_token()
        if client_token is None:
            # was not in the Cache recursive call
            Clock.schedule_once(
                lambda dt: self.get_rfid_token(
                    uid, on_success=on_success, on_fail=on_fail
                ),
                0.5,
            )
            return

        # if good, get the user _user_URL and the permissions _can_check_URL
        #   pass user and permission to on_success
        def _got_rfid_token(request, result):
            Logger.debug("HMS: get_rfid_token: got new rfid token")
            self._rfid_token_request = None

            result["expires_at"] = time() + result["expires_in"]
            Cache.append("HMS", "rfid_token", result, result["expires_in"])
            if on_success:
                on_success(request, result)

        # if error parse reason and pass back to on_fail
        def _rfid_token_error(request, error):
            Logger.warning("HMS: get_rfid_token: error getting new rfid token")
            self._rfid_token_request = None
            Logger.warning(request.resp_status)
            Logger.warning(error)
            if on_fail:
                on_fail(request, "Request failed")

        # if fail parse reason and pass back to on_fail
        def _rfid_token_failure(request, result):
            Logger.warning("HMS: get_rfid_token: failed to get new rfid token")
            self._rfid_token_request = None

            if request.resp_status == HTTPStatus.UNPROCESSABLE_ENTITY:
                # validation error
                if on_fail:
                    on_fail(request, result["errors"]["rfidSerial"][0])
            if request.resp_status == HTTPStatus.NOT_FOUND:
                # RFID not found
                if on_fail:
                    on_fail(request, result["errors"][0]["detail"])
            elif request.resp_status == HTTPStatus.FORBIDDEN:
                # RFID not active
                if on_fail:
                    on_fail(request, result["errors"][0]["detail"])
            else:
                Logger.warning(request.resp_status)
                Logger.warning(result)
                if on_fail:
                    on_fail(request, "Unknown Error")

        # prep headers with the client_token
        headers = self._json_headers
        headers[
            "Authorization"
        ] = f'{client_token["token_type"]} {client_token["access_token"]}'

        # the request body
        params = json.dumps({"rfidSerial": uid})

        self._rfid_token_request = UrlRequest(
            url=self._config.get("HMS", "url") + self._rfid_token_URL,
            req_body=params,
            req_headers=headers,
            on_error=_rfid_token_error,
            on_failure=_rfid_token_failure,
            on_success=_got_rfid_token,
            timeout=5,
            ca_file=self._config.get("HMS", "ca_file"),
            verify=self._config.getboolean("HMS", "verify_ssl"),
        )

        return None

    def _handle_request(self, method, url, callback, data=None):
        # get rfid token
        rfid_token = self.get_rfid_token()
        if rfid_token is None:
            # was not in the Cache
            return None

        # prep headers with the rfid_token
        headers = self._json_headers
        headers[
            "Authorization"
        ] = f'{rfid_token["token_type"]} {rfid_token["access_token"]}'

        return UrlRequest(
            url=self._config.get("HMS", "url") + url,
            method=method,
            req_headers=headers,
            req_body=data,
            on_success=callback,
            on_error=callback,
            on_failure=callback,
            timeout=5,
            ca_file=self._config.get("HMS", "ca_file"),
            verify=self._config.getboolean("HMS", "verify_ssl"),
        )

    def get_request(self, url, callback, data=None):
        return self._handle_request("GET", url, callback, data)

    def post_request(self, url, callback, data=None):
        return self._handle_request("POST", url, callback, data)

    def patch_request(self, url, callback, data=None):
        return self._handle_request("PATCH", url, callback, data)

    def delete_request(self, url, callback, data=None):
        return self._handle_request("DELETE", url, callback, data)

    def forget_rfid_token(self):
        Cache.remove("HMS", "rfid_token")
