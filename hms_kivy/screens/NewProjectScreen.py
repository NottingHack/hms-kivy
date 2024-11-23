__all__ = ("NewProjectScreen",)
import json

from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import (
    ObjectProperty,
    ListProperty,
    StringProperty,
    NumericProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label

from ..utils import load_kv
from ..hms import Projects


class NewProjectScreen(Screen):
    _app = None
    projects = None

    project_name = ObjectProperty(None)
    project_description = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(NewProjectScreen, self).__init__(**kwargs)

    def on_enter(self):
        Logger.debug("NewProjectScreen: on_enter")
        self._app = App.get_running_app()
        self.user = self._app.user
        self._app.set_home_button("Home")
        self._app.update_title("Create a new project")
        self._app.home_button.bind(on_release=self.on_home_pressed)
        self.project_name.text = ""
        self.project_description.text = ""
        self.projects = Projects(self._app.hms)

    def on_leave(self):
        Logger.debug("NewProjectScreen: on_leave")
        self._app.home_button.unbind(on_release=self.on_home_pressed)

    def on_home_pressed(self, *args):
        Logger.debug("NewProjectScreen: on_home_pressed")
        self._app.set_screen("home")

    def create_project(self, *args):
        Logger.debug("NewProjectScreen: create_project ({}, {})".format(
            self.project_name.text,
            self.project_description.text
        ))
        self.projects.store(
            self.project_name.text,
            self.project_description.text,
            self.create_project_cb)

    def create_project_cb(self):
        Logger.debug("NewProjectScreen: create_project_cb")
        self._app.set_screen("projects")


load_kv()
