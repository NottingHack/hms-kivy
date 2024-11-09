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

Builder.load_file(os.path.join(os.path.dirname(__file__), "style.kv"))

from .hms import HMS, User
from .rfid.rfid import RFID
from .screens import (
    SettingsPasswordScreen,
    LogInScreen,
    HomeScreen,
    ProjectsScreen,
    BoxesScreen,
    RfidRegistrationScreen,
    NewProjectScreen,
)


class ScreenSwitcher(ScreenManager):
    # The screens can be added on the __init__ method like this or on the .kv file
    def __init__(self, **kwargs):
        super(ScreenSwitcher, self).__init__(**kwargs)
        self.add_widget(LogInScreen())
        self.add_widget(SettingsPasswordScreen())
        self.add_widget(HomeScreen())
        self.add_widget(ProjectsScreen())
        self.add_widget(BoxesScreen())
        self.add_widget(RfidRegistrationScreen())
        self.add_widget(NewProjectScreen())


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

    home_label = StringProperty("Present Card")
    title_label = StringProperty("")
    manager = None
    home_button = None

    rfid = RFID()
    hms = HMS()

    _previous_screen = None
    _logout_clock = None
    _remove_card_clock = None

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
        Logger.debug("Kiosk: on_start")

        # pull out the manager and home_button
        self.manager = self.root.ids.manager
        self.home_button = self.root.ids.home_button
        # warm up hms
        self.hms.start()
        # start the rfid reader
        self.rfid.start_RFID_read()
        self.rfid.bind(on_remove=self.on_rfid_remove)
        # and enable login
        self.enable_login()

    def on_stop(self, *args):
        Logger.debug("Kiosk: on_stop")
        self.rfid.stop_RFID_read()
        self.hms.stop()

    def update_title(self, text=""):
        self.title_label = text

    def open_settings_password(self):
        self.set_screen("settingsPassword")

    def get_screen(self, screen):
        return self.manager.get_screen(screen)

    def set_screen(self, screen):
        self._previous_screen = self.manager.current
        self.manager.current = screen

    def restore_previous_screen(self):
        previous_screen = self.manager.current
        self.manager.current = self._previous_screen
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
            self.set_home_button("Logged in", True)

        if self._uid == uid:
            # we are likely already logged in with this user
            self.set_home_button("Logged in", True)
            return

        if self.user is not None:
            # we have a user already logged in and now have a new one?
            # should not get here anyway
            self.logout()

        self._uid = uid

        if self.manager.current != "login":
            self.set_screen("login")

        self.set_home_button("Logging in...", True)
        self.user = User(self.hms)
        self.user.login(
            uid, on_success=self.login_success_cb, on_fail=self.login_failed_cb
        )

    def login_success_cb(self, uid):
        Logger.debug(f"Kiosk: login_success_cb")
        if self.user.user and self.user.permissions:
            self.set_home_button("Logged in", True)
            # move to the next screen
            self.set_screen("home")

    def login_failed_cb(self, reason):
        Logger.debug(f"Kiosk: login_failed_cb: {reason}")
        #  login failed for some reason need to flash on the login screen
        self.set_home_button("Login fail", True)
        self.get_screen("login").set_status_message(reason)
        self._uid = None

        # clock to clear message?
        self._remove_card_clock = Clock.schedule_once(
            lambda dt: self.get_screen("login").set_status_message("Remove Card"),
            5,
        )
        # or swap to say remove card

    def on_rfid_remove(self, *args, **kwargs):
        Logger.debug("Kiosk: on_rfid_remove")
        if self.manager.current == "checkIn":
            return

        if self._remove_card_clock:
            self._remove_card_clock.cancel()
            self._remove_card_clock = None

        # start logout count down
        if self._logout_clock is None:
            self.logout(self.config.getint("Kiosk", "logout_delay"))

    def logout(self, count=0):
        Logger.debug(f"Kiosk: logout {count}")
        if self.manager.current == "checkIn":
            return

        if count == 0 or self._uid == None or self.user == None:
            self._logout_clock = None
            self._uid = None
            self.user = None
            self.permissions = None
            self.update_title()
            # bypass normal set_screen logic
            self._previous_screen = "login"
            self.root.ids.manager.current = "login"

            self.set_home_button("Present Card", True)
        else:
            # display the count
            self.set_home_button(f"Logout in {count}", True)
            self._logout_clock = Clock.schedule_once(
                lambda dt: self.logout(count - 1), 1
            )

    def set_home_button(self, label, disabled=False):
        self.home_label = label
        self.home_button.disabled = disabled

    def on_home_pressed(self, *args):
        Logger.debug("Kiosk: on_home_pressed")


def main():
    Window.size = (800, 480)
    try:
        KioskApp().run()
    except KeyboardInterrupt:
        KioskApp().stop()


if __name__ == "__main__":
    main()
