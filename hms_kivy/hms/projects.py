# -*- coding: utf-8 -*-
""" HMS Kiosk (HMS Projects module)

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

__all__ = ("Projects",)
import json
from http import HTTPStatus

from kivy.logger import Logger


class Projects:
    hms = None

    # states
    ACTIVE = 10
    COMPLETE = 20
    ABANDONED = 30

    _mark_active_URL = "api/projects/{project}/markActive"  # PACTH
    _mark_abandoned_URL = "api/projects/{project}/markAbandoned"  # PATCH
    _mark_complete_URL = "api/projects/{project}/markComplete"  # PATCH
    _print_URL = "api/projects/{project}/print"  # POST
    _index_URL = "api/projects"  # GET
    _store_URL = "api/projects"  # POST
    _show_URL = "api/projects/{project}"  # GET
    _update_URL = "api/projects/{project}"  # PATCH

    # [
    #     {
    #         "id": 1,
    #         "projectName": "ytest",
    #         "description": "kjgkjg",
    #         "startDate": "2021-03-26T03:21:08.000000Z",
    #         "completeDate": null,
    #         "state": 10,
    #         "stateString": "Active",
    #         "userId": 953
    #     }
    # ]
    projects = []

    def __init__(self, hms):
        self.hms = hms

    def index(self, callback):
        Logger.debug("Projects: index")

        return self.hms.get_request(
            self._index_URL,
            lambda request, result, callback=callback: self._index_cb(
                request, result, callback
            ),
        )

    def _index_cb(self, request, result, callback):
        Logger.debug(f"Projects: _index_cb {request.url} {request.resp_status}")
        Logger.debug(f"Projects: _index_cb {result}")

        if self._index_URL in request.url and request.resp_status == HTTPStatus.OK:
            self.projects = result["data"]
            callback()

    def store(self, project_name, description, callback):
        Logger.debug("Projects: store")

        data = json.dumps({"projectName": project_name, "description": description})
        return self.hms.post_request(
            self._store_URL,
            lambda request, result, callback=callback: self._index_cb(
                request, result, callback
            ),
        )

    def _store_cb(self, request, result, callback):
        Logger.debug(f"Projects: _store_cb {request.url} {request.resp_status}")
        Logger.debug(f"Projects: _store_cb {result}")

        if self._store_URL in request.url and request.resp_status == HTTPStatus.OK:
            self.projects = result["data"]
            callback()

    def show(self, project, callback):
        Logger.debug(f"Projects: show {project}")

        return self.hms.get_request(
            self._show_URL.format(project=project),
            lambda request, result, callback=callback: self._index_cb(
                request, result, callback
            ),
        )

    def _show_cb(self, request, result, callback):
        Logger.debug(f"Projects: _show_cb {request.url} {request.resp_status}")
        Logger.debug(f"Projects: _show_cb {result}")

        if self._show_URL in request.url and request.resp_status == HTTPStatus.OK:
            self.projects = result["data"]
            callback()

    def update(self, project_name, description, callback):
        Logger.debug("Projects: update")

        data = json.dumps({"projectName": project_name, "description": description})
        return self.hms.post_request(
            self._update_URL,
            lambda request, result, callback=callback: self._index_cb(
                request, result, callback
            ),
        )

    def _update_cb(self, request, result, callback):
        Logger.debug(f"Projects: _update_cb {request.url} {request.resp_status}")
        Logger.debug(f"Projects: _update_cb {result}")

        if self._update_URL in request.url and request.resp_status == HTTPStatus.OK:
            self.projects = result["data"]
            callback()

    def print(self, project, callback):
        Logger.debug(f"Projects: print {project}")

        return self.hms.patch_request(
            self._print_URL.format(project=project),
            lambda request, result, callback=callback: self._index_cb(
                request, result, callback
            ),
        )

    def _print_cb(self, request, result, callback):
        Logger.debug(f"Projects: _print_cb {request.url} {request.resp_status}")
        Logger.debug(f"Projects: _print_cb {result}")

        if self._print_URL in request.url and request.resp_status == HTTPStatus.OK:
            self.projects = result["data"]
            callback()

    def mark_active(self, project, callback):
        Logger.debug(f"Projects: mark_active {project}")

        return self.hms.patch_request(
            self._mark_active_URL.format(project=project),
            lambda request, result, callback=callback: self._index_cb(
                request, result, callback
            ),
        )

    def _mark_active_cb(self, request, result, callback):
        Logger.debug(f"Projects: _mark_active_cb {request.url} {request.resp_status}")
        Logger.debug(f"Projects: _mark_active_cb {result}")

        if (
            self._mark_active_URL in request.url
            and request.resp_status == HTTPStatus.OK
        ):
            self.projects = result["data"]
            callback()

    def mark_abandoned(self, project, callback):
        Logger.debug(f"Projects: mark_abandoned {project}")

        return self.hms.patch_request(
            self._show_Umark_abandonedormat(project=project),
            lambda request, result, callback=callback: self._index_cb(
                request, result, callback
            ),
        )

    def _mark_abandoned_cb(self, request, result, callback):
        Logger.debug(
            f"Projects: _mark_abandoned_cb {request.url} {request.resp_status}"
        )
        Logger.debug(f"Projects: _mark_abandoned_cb {result}")

        if (
            self._mark_abandoned_URL in request.url
            and request.resp_status == HTTPStatus.OK
        ):
            self.projects = result["data"]
            callback()

    def mark_complete(self, project, callback):
        Logger.debug(f"Projects: mark_complete {project}")

        return self.hms.patch_request(
            self._showmark_complete.format(project=project),
            lambda request, result, callback=callback: self._index_cb(
                request, result, callback
            ),
        )

    def _mark_complete_cb(self, request, result, callback):
        Logger.debug(f"Projects: _mark_complete_cb {request.url} {request.resp_status}")
        Logger.debug(f"Projects: _mark_complete_cb {result}")

        if (
            self._mark_complete_URL in request.url
            and request.resp_status == HTTPStatus.OK
        ):
            self.projects = result["data"]
            callback()
