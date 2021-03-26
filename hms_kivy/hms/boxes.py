# -*- coding: utf-8 -*-
""" HMS Kiosk (HMS Boxes module)

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

__all__ = ("Boxes",)
import json
from http import HTTPStatus

from kivy.logger import Logger


class Boxes:
    hms = None

    # states
    INUSE = 10
    REMOVED = 20
    ABANDONED = 30

    _audit_URL = "api/boxes/audit"  # GET
    _mark_in_use_URL = "api/boxes/{box}/markInUse"  # PATCH
    _mark_abandoned_URL = "api/boxes/{box}/markAbandoned"  # PATCH
    _mark_removed_URL = "api/boxes/{box}/markRemoved"  # PATCH
    _print_URL = "api/boxes/{box}/print"  # POST
    _index_URL = "api/boxes"  # GET
    # _store_URL = "api/projects"  # POST
    _show_URL = "api/boxes/{box}"  # GET

    # [
    #     {
    #         "id": 1,
    #         "boughtDate": "2021-03-26T03:13:39.000000Z",
    #         "removedDate": null,
    #         "state": 10,
    #         "stateString": "In Use",
    #         "userId": 953
    #     }
    # ]
    boxes = []

    def __init__(self, hms):
        self.hms = hms

    def index(self, callback):
        Logger.debug("Boxes: index")

        return self.hms.get_request(
            self._index_URL,
            lambda request, result, callback=callback: self._index_cb(
                request, result, callback
            ),
        )

    def _index_cb(self, request, result, callback):
        Logger.debug(f"Boxes: _index_cb {request.url} {request.resp_status}")
        Logger.debug(f"Boxes: _index_cb {result}")

        if self._index_URL in request.url and request.resp_status == HTTPStatus.OK:
            self.boxes = result["data"]
            callback()

    def show(self, box, callback):
        Logger.debug(f"Boxes: show {box}")

        return self.hms.get_request(
            self._show_URL.format(box=box),
            lambda request, result, callback=callback: self._index_cb(
                request, result, callback
            ),
        )

    def _show_cb(self, request, result, callback):
        Logger.debug(f"Boxes: _show_cb {request.url} {request.resp_status}")
        Logger.debug(f"Boxes: _show_cb {result}")

        if self._show_URL in request.url and request.resp_status == HTTPStatus.OK:
            self.boxs = result["data"]
            callback()

    def print(self, box, callback):
        Logger.debug(f"Boxes: print {box}")

        return self.hms.patch_request(
            self._print_URL.format(box=box),
            lambda request, result, callback=callback: self._index_cb(
                request, result, callback
            ),
        )

    def _print_cb(self, request, result, callback):
        Logger.debug(f"Boxes: _print_cb {request.url} {request.resp_status}")
        Logger.debug(f"Boxes: _print_cb {result}")

        if self._print_URL in request.url and request.resp_status == HTTPStatus.OK:
            self.boxs = result["data"]
            callback()

    def mark_in_use(self, box, callback):
        Logger.debug(f"Boxes: mark_in_use {box}")

        return self.hms.patch_request(
            self._mark_in_use_URL.format(box=box),
            lambda request, result, callback=callback: self._index_cb(
                request, result, callback
            ),
        )

    def _mark_in_use_cb(self, request, result, callback):
        Logger.debug(f"Boxes: _mark_in_use_cb {request.url} {request.resp_status}")
        Logger.debug(f"Boxes: _mark_in_use_cb {result}")

        if (
            self._mark_in_use_URL in request.url
            and request.resp_status == HTTPStatus.OK
        ):
            self.boxs = result["data"]
            callback()

    def mark_abandoned(self, box, callback):
        Logger.debug(f"Boxes: mark_abandoned {box}")

        return self.hms.patch_request(
            self._show_Umark_abandonedormat(box=box),
            lambda request, result, callback=callback: self._index_cb(
                request, result, callback
            ),
        )

    def _mark_abandoned_cb(self, request, result, callback):
        Logger.debug(f"Boxes: _mark_abandoned_cb {request.url} {request.resp_status}")
        Logger.debug(f"Boxes: _mark_abandoned_cb {result}")

        if (
            self._mark_abandoned_URL in request.url
            and request.resp_status == HTTPStatus.OK
        ):
            self.boxs = result["data"]
            callback()

    def mark_removed(self, box, callback):
        Logger.debug(f"Boxes: mark_removed {box}")

        return self.hms.patch_request(
            self._showmark_removed.format(box=box),
            lambda request, result, callback=callback: self._index_cb(
                request, result, callback
            ),
        )

    def _mark_removed_cb(self, request, result, callback):
        Logger.debug(f"Boxes: _mark_removed_cb {request.url} {request.resp_status}")
        Logger.debug(f"Boxes: _mark_removed_cb {result}")

        if (
            self._mark_removed_URL in request.url
            and request.resp_status == HTTPStatus.OK
        ):
            self.boxs = result["data"]
            callback()
