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

# states
INUSE = 10
REMOVED = 20
ABANDONED = 30

# {
#     "id": 1,
#     "boughtDate": "2021-03-26",
#     "removedDate": null,
#     "state": 10,
#     "stateString": "In Use",
#     "userId": 953
# }


class Boxes:
    hms = None
    boxes = []

    _audit_URL = "api/boxes/audit"  # GET
    _index_URL = "api/boxes"  # GET
    _show_URL = "api/boxes/{box}"  # GET
    # _store_URL = "api/projects"  # POST

    def __init__(self, hms):
        self.hms = hms

    def index(self, callback=None):
        Logger.debug("Boxes: index")

        return self.hms.get_request(
            self._index_URL,
            lambda request, result, callback=callback: self._index_cb(
                request, result, callback
            ),
        )

    def _index_cb(self, request, result, callback=None):
        Logger.debug(f"Boxes: _index_cb {request.url} {request.resp_status}")
        Logger.debug(f"Boxes: _index_cb {result}")

        if self._index_URL in request.url and request.resp_status == HTTPStatus.OK:
            # self.boxes = result["data"]
            self.boxes = []
            for box in result["data"]:
                self.boxes.append(Box(self.hms, box))
            if callback is not None:
                callback(self.boxes)

    def show(self, box, callback=None):
        Logger.debug(f"Boxes: show {box}")

        return self.hms.get_request(
            self._show_URL.format(box=box),
            lambda request, result, box=box, callback=callback: self._show_cb(
                request, result, callback
            ),
        )

    def _show_cb(self, request, result, box, callback=None):
        Logger.debug(f"Boxes: _show_cb {request.url} {request.resp_status}")
        Logger.debug(f"Boxes: _show_cb {result}")

        if (
            self._show_URL.format(box=box) in request.url
            and request.resp_status == HTTPStatus.OK
        ):
            # if Box of this id is in boxes update it and return that instance
            # else add a new one to boxes and return it
            box = Box(self.hms, result["data"])
            if callback is not None:
                callback(box)


class Box:
    hms = None
    id = None
    bought_date = None
    removed_date = None
    state = None
    state_string = None
    user_id = None

    _mark_in_use_URL = "api/boxes/{box}/markInUse"  # PATCH
    _mark_abandoned_URL = "api/boxes/{box}/markAbandoned"  # PATCH
    _mark_removed_URL = "api/boxes/{box}/markRemoved"  # PATCH
    _print_URL = "api/boxes/{box}/print"  # POST

    def __init__(self, hms, box):
        self.hms = hms
        self._populate_from_box(box)

    def _populate_from_box(self, box):
        self.id = box["id"]
        self.bought_date = box["boughtDate"]
        self.removed_date = box["removedDate"]
        self.state = box["state"]
        self.state_string = box["stateString"]
        self.user_id = box["userId"]

    def mark_string(self):
        """Which mark function can be called for this box
        Removed
        Abandoned
        In Use
        """

        if self.state == INUSE:
            return "Mark Removed"
        else:
            return "Mark In Use"

    def mark(self, callback=None):
        """call the correct mark function based on current state
        Removed
        Abandoned
        In Use
        """

        if self.state == INUSE:
            return self.mark_removed(callback)
        else:
            return self.mark_in_use(callback)

    def print(self, callback=None):
        Logger.debug(f"Box ({self.id}): print")

        return self.hms.patch_request(
            self._print_URL.format(box=box),
            lambda request, result, callback=callback: self._print_cb(
                request, result, callback
            ),
        )

    def _print_cb(self, request, result, callback=None):
        Logger.debug(f"Box ({self.id}): _print_cb {request.url} {request.resp_status}")
        Logger.debug(f"Box ({self.id}): _print_cb {result}")

        if (
            self._print_URL.format(box=box) in request.url
            and request.resp_status == HTTPStatus.ACCEPTED
        ):
            if callback is not None:
                callback()

    def mark_in_use(self, callback=None):
        Logger.debug(f"Box ({self.id}): mark_in_use")

        return self.hms.patch_request(
            self._mark_in_use_URL.format(box=self.id),
            lambda request, result, callback=callback: self._mark_in_use_cb(
                request, result, callback
            ),
        )

    def _mark_in_use_cb(self, request, result, callback=None):
        Logger.debug(
            f"Box ({self.id}): _mark_in_use_cb {request.url} {request.resp_status}"
        )
        Logger.debug(f"Box ({self.id}): _mark_in_use_cb {result}")

        if (
            self._mark_in_use_URL.format(box=self.id) in request.url
            and request.resp_status == HTTPStatus.OK
        ):
            self._populate_from_box(result["data"])
            if callback is not None:
                callback()
        elif (
            self._mark_in_use_URL.format(box=self.id) in request.url
            and request.resp_status == HTTPStatus.FORBIDDEN
        ):
            if callback is not None:
                callback(result["errors"][0]["detail"])

    def mark_abandoned(self, callback=None):
        Logger.debug(f"Box ({self.id}): mark_abandoned")

        return self.hms.patch_request(
            self._mark_abandoned_URL.format(box=self.id),
            lambda request, result, callback=callback: self._mark_abandoned_cb(
                request, result, callback
            ),
        )

    def _mark_abandoned_cb(self, request, result, callback=None):
        Logger.debug(
            f"Box ({self.id}): _mark_abandoned_cb {request.url} {request.resp_status}"
        )
        Logger.debug(f"Box ({self.id}): _mark_abandoned_cb {result}")

        if (
            self._mark_abandoned_URL.format(box=self.id) in request.url
            and request.resp_status == HTTPStatus.OK
        ):
            self._populate_from_box(result["data"])
            if callback is not None:
                callback()
        elif (
            self._mark_abandoned_URL.format(box=self.id) in request.url
            and request.resp_status == HTTPStatus.FORBIDDEN
        ):
            if callback is not None:
                callback(result["errors"][0]["detail"])

    def mark_removed(self, callback=None):
        Logger.debug(f"Box ({self.id}): mark_removed")

        return self.hms.patch_request(
            self._mark_removed_URL.format(box=self.id),
            lambda request, result, callback=callback: self._mark_removed_cb(
                request, result, callback
            ),
        )

    def _mark_removed_cb(self, request, result, callback=None):
        Logger.debug(
            f"Box ({self.id}): _mark_removed_cb {request.url} {request.resp_status}"
        )
        Logger.debug(f"Box ({self.id}): _mark_removed_cb {result}")

        if (
            self._mark_removed_URL.format(box=self.id) in request.url
            and request.resp_status == HTTPStatus.OK
        ):
            self._populate_from_box(result["data"])
            if callback is not None:
                callback()
        elif (
            self._mark_removed_URL.format(box=self.id) in request.url
            and request.resp_status == HTTPStatus.FORBIDDEN
        ):
            if callback is not None:
                callback(result["errors"][0]["detail"])
