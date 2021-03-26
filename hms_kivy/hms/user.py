# -*- coding: utf-8 -*-
""" HMS Kiosk (HMS User module)

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

__all__ = ("User",)
import json
from http import HTTPStatus

from kivy.logger import Logger


class User:
    hms = None
    _user_URL = "api/users"
    _can_check_URL = "api/can"

    # initial permissions to check when first doing a user login
    _initial_permissions_to_check = {
        "permissions": [
            "project.create.self",
            "project.view.self",
            "project.edit.self",
            "project.printLabel.self",
            "box.buy.self",
            "box.view.self",
            "box.edit.self",
            "box.printLabel.self",
            "rfidTags.view.self",
            "rfidTags.edit.self",
            "snackspace.transaction.view.self",
            "governance.meeting.checkIn",
            "search.users",
            "pins.reactivate",
        ]
    }

    uid = None
    user = None
    permissions = None

    def __init__(self, hms):
        self.hms = hms

    def login(self, uid, on_success, on_fail):
        """Login into HMS using a given RFIDTag UID"""
        Logger.debug(f'User: login: "{uid}"')
        if self.uid != uid:
            self.hms.forget_rfid_token()

        self.uid = uid
        self._get_rfid_token(uid, on_success, on_fail)

    def _get_rfid_token(self, uid, on_success, on_fail):
        Logger.debug("User: _get_rfid_token")
        return self.hms.get_rfid_token(
            uid,
            lambda request, result, on_success=on_success, on_fail=on_fail: self._rfid_token_success_cb(
                request, result, on_success, on_fail
            ),
            lambda request, result, on_success=on_success, on_fail=on_fail: self._rfid_token_fail_cb(
                request, result, on_success, on_fail
            ),
        )

    def _rfid_token_success_cb(self, request, result, on_success, on_fail):
        Logger.debug("User: _rfid_token_success_cb")
        # good rfid login ok, move onto getting user
        self._get_user(on_success, on_fail)

    def _rfid_token_fail_cb(self, request, result, on_success, on_fail):
        Logger.debug(f"User: _rfid_token_fail_cb: {result}")
        # good rfid login ok, move onto getting user
        on_fail(result)

    def _get_user(self, on_success, on_fail):
        Logger.debug("User: _get_user")
        return self.hms.get_request(
            self._user_URL,
            lambda request, result, on_success=on_success, on_fail=on_fail: self._get_user_cb(
                request, result, on_success, on_fail
            ),
        )

    def _get_user_cb(self, request, result, on_success, on_fail):
        Logger.debug(f"User: _get_user_cb {request.url} {request.resp_status}")
        Logger.debug(f"User: _get_user_cb {result}")

        if self._user_URL in request.url and request.resp_status == HTTPStatus.OK:
            self.user = result["data"]
            on_success(self.uid)
            self._get_permissions(on_success, on_fail)

        if self._user_URL not in request.url:
            on_fail(result)

    def _get_permissions(self, on_success, on_fail):
        Logger.debug("User: _get_permissions")
        params = json.dumps(self._initial_permissions_to_check)

        return self.hms.post_request(
            self._can_check_URL,
            lambda request, result, on_success=on_success, on_fail=on_fail: self._get_permissions_cb(
                request, result, on_success, on_fail
            ),
            data=params,
        )

    def _get_permissions_cb(self, request, result, on_success, on_fail):
        Logger.debug(f"User: _get_permissions_cb {request.url} {request.resp_status}")
        Logger.debug(f"User: _get_permissions_cb {result}")

        if self._can_check_URL in request.url and request.resp_status == HTTPStatus.OK:
            self.permissions = result
            on_success(self.uid)

    def get_name(self):
        if self.user:
            return self.user["name"]

        return None

    def get_username(self):
        if self.user:
            return self.user["username"]

        return None

    def get_email(self):
        if self.user:
            return self.user["email"]

        return None

    def get_fullname(self):
        if self.user:
            return self.user["fullname"]

        return None

    def get_balance(self):
        if self.user:
            return self.user["profile"]["balance"]

        return None

    def can(self, permission):
        if self.permissions and permission in self.permissions:
            return self.permissions[permission]

        return False
