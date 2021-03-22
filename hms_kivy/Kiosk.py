#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" HMS Kiosk

    Requirements (pi only)
    pi-rc522 (https://github.com/kevinvalk/pi-rc522.git)

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
import time
import queue
import json
import os

from kivy.logger import Logger, LOG_LEVELS

Logger.setLevel(LOG_LEVELS["debug"])

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.settings import SettingsWithTabbedPanel

from .hms import HMS
from .rfid.rfid import RFID
from .screens import SettingsPasswordScreen, LogInScreen, HomeScreen

Builder.load_file(os.path.join(os.path.dirname(__file__), "style.kv"))


class ScreenSwitcher(ScreenManager):
    # The screens can be added on the __init__ method like this or on the .kv file
    def __init__(self, **kwargs):
        super(ScreenSwitcher, self).__init__(**kwargs)
        self.add_widget(LogInScreen())
        self.add_widget(SettingsPasswordScreen())
        self.add_widget(HomeScreen())


# TopBar Digital Clock
class ClockLabel(ButtonBehavior, Label):
    def __init__(self, **kwargs):
        super(ClockLabel, self).__init__(**kwargs)
        Clock.schedule_interval(self.update, 1)

    def update(self, *args):
        self.text = time.strftime("%H:%M:%S")


class KioskApp(App):
    # use_kivy_settings = False
    settings_cls = SettingsWithTabbedPanel

    status_label = StringProperty("Present Card")

    rfid = RFID()
    hms = HMS()

    _previous_screen = None
    _logout_clock = None

    _uid = None
    user = None
    permissions = None

    def build_config(self, config):
        config.setdefaults("Kiosk", {"settings_password": "1234", "logout_delay": 5})
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
                {
                    "type": "numeric",
                    "title": "Logout delay",
                    "desc": "Count down time before logout",
                    "section": "Kiosk",
                    "key": "logout_delay",
                },
            ]
        )
        settings.add_json_panel("Kiosk", self.config, data=jsondata)
        self.hms.build_settings(settings, self.config)
        self.rfid.build_settings(settings, self.config)

    def on_config_change(self, config, section, key, value):
        self.hms.on_config_change(config, section, key, value)
        self.rfid.on_config_change(config, section, key, value)

    def on_start(self, *args):
        self.rfid.start_RFID_read()
        self.rfid.bind(on_remove=self.on_rfid_remove)

        # done in LogInScreen for now
        # self._app.enable_login()

    def on_stop(self, *args):
        self.rfid.stop_RFID_read()

    def update_title(self, text=""):
        if self.root:
            self.root.ids.title.text = text

    def open_settings_password(self):
        self.set_screen("settingsPassword")

    def set_screen(self, screen):
        self._previous_screen = self.root.ids.manager.current
        self.root.ids.manager.current = screen

    def restore_previous_screen(self):
        previous_screen = self.root.ids.manager.current
        self.root.ids.manager.current = self._previous_screen
        self._previous_screen = previous_screen

    def enable_login(self):
        Logger.debug("Kiosk: enable_login")
        self.rfid.bind(on_present=self.on_rfid_present)

    def disable_login(self):
        Logger.debug("Kiosk: disable_login")
        self.rfid.unbind(on_present=self.on_rfid_present)

    def on_rfid_present(self, obj, uid):
        Logger.debug(f"Kiosk: on_rfid_present: {uid}")
        if self._logout_clock is not None:
            # cancel the
            self._logout_clock.cancel()
            self._logout_clock = None
            self.status_label = "Logged in"

        if self._uid == uid:
            # we are likely already logged in with this user
            self.status_label = "Logged in"
            return

        if self.user is not None:
            # we have a user already logged in and now have a new one?
            # should not get here anyway
            self.logout()

        self._uid = uid

        if self.root.ids.manager.current != "login":
            self.set_screen("login")

        self.status_label = "Logging in..."
        self.hms.login(uid, on_success=self.login_success, on_fail=self.login_failed)

    def login_success(self, user, permissions):
        Logger.debug(f"Kiosk: login_success: {user['name']}")
        self.user = user
        self.permissions = permissions

        self.status_label = "Logged in"
        # self.root.ids.logout.disabled = False
        # move to the next screen
        self.set_screen("home")

    def login_failed(self, reason):
        Logger.debug(f"Kiosk: login_failed: {reason}")
        #  login failed for some reason need to flash on the login screen
        self.root.ids.manager.get_screen("login").status_message = reason
        self._uid = None

    def on_rfid_remove(self, *args, **kwargs):
        Logger.debug("Kiosk: on_rfid_remove")
        if self.root.ids.manager.current == "checkIn":
            return

        # start logout count down
        if self._logout_clock is None:
            self.logout(self.config.getint("Kiosk", "logout_delay"))

    def logout(self, count=0):
        Logger.debug(f"Kiosk: logout {count}")
        if self.root.ids.manager.current == "checkIn":
            return

        if count == 0:
            self._logout_clock = None
            self._uid = None
            self.user = None
            self.permissions = None
            # self.root.ids.logout.disabled = True
            self.update_title()
            # bypass normal set_screen logic
            self._previous_screen = "login"
            self.root.ids.manager.current = "login"

            self.status_label = "Present Card"
        else:
            # display the count
            self.status_label = f"Logout in {count}"
            self._logout_clock = Clock.schedule_once(
                lambda dt: self.logout(count - 1), 1
            )


def main():
    Window.size = (800, 480)
    try:
        KioskApp().run()
    except KeyboardInterrupt:
        KioskApp().stop()


if __name__ == "__main__":
    main()
