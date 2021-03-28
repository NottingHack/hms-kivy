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


# states
ACTIVE = 10
COMPLETE = 20
ABANDONED = 30

# {
#     "id": 1,
#     "projectName": "ytest",
#     "description": "kjgkjg",
#     "startDate": "2021-03-26T03:21:08.000000Z",
#     "completeDate": null,
#     "state": 10,
#     "stateString": "Active",
#     "userId": 953
# }


class Projects:
    hms = None
    projects = []

    _index_URL = "api/projects"  # GET
    _store_URL = "api/projects"  # POST
    _show_URL = "api/projects/{project}"  # GET

    def __init__(self, hms):
        self.hms = hms

    def index(self, callback=None):
        Logger.debug("Projects: index")

        return self.hms.get_request(
            self._index_URL,
            lambda request, result, callback=callback: self._index_cb(
                request, result, callback
            ),
        )

    def _index_cb(self, request, result, callback=None):
        Logger.debug(f"Projects: _index_cb {request.url} {request.resp_status}")
        Logger.debug(f"Projects: _index_cb {result}")

        if self._index_URL in request.url and request.resp_status == HTTPStatus.OK:

            self.projects = []
            for project in result["data"]:
                self.projects.append(Project(self.hms, project))
            if callback is not None:
                callback(self.projects)

    def show(self, project, callback=None):
        Logger.debug(f"Projects: show {project}")

        return self.hms.get_request(
            self._show_URL.format(project=project),
            lambda request, result, project=project, callback=callback: self._show_cb(
                request, result, callback
            ),
        )

    def _show_cb(self, request, result, project, callback=None):
        Logger.debug(f"Projects: _show_cb {request.url} {request.resp_status}")
        Logger.debug(f"Projects: _show_cb {result}")

        if (
            self._show_URL.format(project=project) in request.url
            and request.resp_status == HTTPStatus.OK
        ):
            self.projects = result["data"]
            callback()

    def store(self, project_name, description, callback=None):
        Logger.debug(f"Projects: store {project_name}")

        data = json.dumps({"projectName": project_name, "description": description})
        return self.hms.post_request(
            self._store_URL,
            lambda request, result, callback=callback: self._store_cb(
                request, result, callback
            ),
        )

    def _store_cb(self, request, result, callback=None):
        Logger.debug(f"Projects: _store_cb {request.url} {request.resp_status}")
        Logger.debug(f"Projects: _store_cb {result}")

        if self._store_URL in request.url and request.resp_status == HTTPStatus.OK:
            self.projects = result["data"]
            callback()


class Project:
    hms = None
    id = None
    project_name = None
    description = None
    start_date = None
    complete_date = None
    state = None
    state_string = None
    user_id = None

    _mark_active_URL = "api/projects/{project}/markActive"  # PACTH
    _mark_abandoned_URL = "api/projects/{project}/markAbandoned"  # PATCH
    _mark_complete_URL = "api/projects/{project}/markComplete"  # PATCH
    _print_URL = "api/projects/{project}/print"  # POST
    _update_URL = "api/projects/{project}"  # PATCH

    def __init__(self, hms, project):
        self.hms = hms
        self._populate_from_project(project)

    def _populate_from_project(self, project):
        self.id = project["id"]
        self.project_name = project["projectName"]
        self.description = project["description"]
        self.start_date = project["startDate"]
        self.complete_date = project["completeDate"]
        self.state = project["state"]
        self.state_string = project["stateString"]
        self.user_id = project["userId"]

    def update(self, project_name, description, callback=None):
        Logger.debug("Project ({self.id}): update")

        data = json.dumps({"projectName": project_name, "description": description})
        return self.hms.post_request(
            self._update_URL.format(project=self.id),
            lambda request, result, callback=callback: self._update_cb(
                request, result, callback
            ),
        )

    def _update_cb(self, request, result, callback=None):
        Logger.debug(
            f"Project ({self.id}): _update_cb {request.url} {request.resp_status}"
        )
        Logger.debug(f"Project ({self.id}): _update_cb {result}")

        if (
            self._update_URL.format(project=self.id) in request.url
            and request.resp_status == HTTPStatus.OK
        ):
            self.projects = result["data"]
            callback()

    def print(self, callback=None):
        Logger.debug(f"Project ({self.id}): print")

        return self.hms.patch_request(
            self._print_URL.format(project=self.id),
            lambda request, result, callback=callback: self._print_cb(
                request, result, callback
            ),
        )

    def _print_cb(self, request, result, callback=None):
        Logger.debug(
            f"Project ({self.id}): _print_cb {request.url} {request.resp_status}"
        )
        Logger.debug(f"Project ({self.id}): _print_cb {result}")

        if (
            self._print_URL.format(project=self.id) in request.url
            and request.resp_status == HTTPStatus.OK
        ):
            self.projects = result["data"]
            callback()

    def mark_active(self, callback=None):
        Logger.debug(f"Project ({self.id}): mark_active")

        return self.hms.patch_request(
            self._mark_active_URL.format(project=self.id),
            lambda request, result, callback=callback: self._mark_active_cb(
                request, result, callback
            ),
        )

    def _mark_active_cb(self, request, result, callback=None):
        Logger.debug(
            f"Project ({self.id}): _mark_active_cb {request.url} {request.resp_status}"
        )
        Logger.debug(f"Project ({self.id}): _mark_active_cb {result}")

        if (
            self._mark_active_URL.format(project=self.id) in request.url
            and request.resp_status == HTTPStatus.OK
        ):
            self.projects = result["data"]
            callback()

    def mark_abandoned(sect, callback=None):
        Logger.debug(f"Project ({self.id}): mark_abandoned")

        return self.hms.patch_request(
            self._mark_abandoned_URL.format(project=self.id),
            lambda request, result, callback=callback: self._mark_abandoned_cb(
                request, result, callback
            ),
        )

    def _mark_abandoned_cb(self, request, result, callback=None):
        Logger.debug(
            f"Project ({self.id}): _mark_abandoned_cb {request.url} {request.resp_status}"
        )
        Logger.debug(f"Project ({self.id}): _mark_abandoned_cb {result}")

        if (
            self._mark_abandoned_URL.format(project=self.id) in request.url
            and request.resp_status == HTTPStatus.OK
        ):
            self.projects = result["data"]
            callback()

    def mark_complete(sect, callback=None):
        Logger.debug(f"Project ({self.id}): mark_complete")

        return self.hms.patch_request(
            self._mark_complete_URL.format(project=self.id),
            lambda request, result, callback=callback: self._mark_complete_cb(
                request, result, callback
            ),
        )

    def _mark_complete_cb(self, request, result, callback=None):
        Logger.debug(
            f"Project ({self.id}): _mark_complete_cb {request.url} {request.resp_status}"
        )
        Logger.debug(f"Project ({self.id}): _mark_complete_cb {result}")

        if (
            self._mark_complete_URL.format(project=self.id) in request.url
            and request.resp_status == HTTPStatus.OK
        ):
            self.projects = result["data"]
            callback()
