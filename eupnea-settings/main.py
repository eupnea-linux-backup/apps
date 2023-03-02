import json

from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen

Config.set('input', 'mouse', 'mouse,disable_multitouch')

from functions import *

global sidebar_buttons
sidebar_buttons = ["Audio", "Install location", "Kernel", "ZRAM", "About", "Help"]


class BlankScreen(Screen):
    pass


class SettingsScreen(Screen):
    # This function will be called every time the screen is displayed
    def on_enter(self):
        self.manager.get_screen(self.name).ids.side_bar.remove_widget(
            self.manager.get_screen(self.name).ids.side_bar_fake_button)

        for button in self.manager.get_screen(self.name).ids.side_bar.children:
            if button.text != sidebar_buttons[int(self.name[7:]) - 1]:
                button.disabled = False
                button.state = "normal"
            else:
                button.disabled = True
                button.state = "down"
                App.get_running_app().title = button.text

    def side_bar_button_clicked(self, instance):
        # install_type = instance.install_type
        print(f"Sidebar selected: {instance.text}")
        self.manager.transition.duration = 0
        self.manager.current = f"screen_{sidebar_buttons.index(instance.text) + 1}"


class Screen1(SettingsScreen):
    pass


class Screen2(SettingsScreen):
    pass


class Screen3(SettingsScreen):
    pass


class Screen4(SettingsScreen):
    pass


class Screen5(SettingsScreen):  # about
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.first_enter = True

    def on_enter(self):
        super().on_enter()  # call original on_enter() method
        if self.first_enter:
            # Add Depthboot/EupneaOS logo
            eupnea_image = Image(source="assets/eupneaos.png")
            eupnea_image.size_hint = (0.3, 0.3)
            eupnea_image.pos_hint = {"center_x": 0.5, "center_y": 0.5}
            self.manager.get_screen(self.name).ids.screen_content_box.add_widget(eupnea_image)

            # set spacing for boxlayout
            self.manager.get_screen(self.name).ids.screen_content_box.spacing = 50

            # add gridlayout to the screen
            temp_grid = GridLayout()
            temp_grid.cols = 2
            temp_grid.size_hint = (1, 1)
            temp_grid.spacing = 10
            # temp_grid.padding = 50
            self.manager.get_screen(self.name).ids.screen_content_box.add_widget(temp_grid)
            self.ids['help_screen_grid_layout'] = temp_grid
            # add labels to the screen
            # The empty strings are filled each time the screen is displayed
            # TODO: Differentiate between depthboot and eupneaOS
            labels = ["Distribution: ", "", "Distribution version: ", "", "Desktop environment: ", "",
                      "Depthboot version: ", "", "Eupnea utils version: ", "", "Eupnea update version: ", "",
                      "Install type: ", "", "Windowing system", "", "Firmware payload: ", ""]

            for text in labels:
                self.new_label = Factory.CustomLabel()
                self.new_label.text = text
                self.new_label.halign = "right" if text == "" else "left"
                self.manager.get_screen(self.name).ids.help_screen_grid_layout.add_widget(self.new_label)

            self.first_enter = False

        # Read /etc/eupnea.json
        with open("/etc/eupnea.json") as f:
            data = json.load(f)

        try:
            session_type = bash("echo $XDG_SESSION_TYPE")
        except subprocess.CalledProcessError:
            session_type = "Unknown"

        labels = [data["firmware_payload"].capitalize(), "", session_type.capitalize(), "", data["install_type"], "",
                  "Unknown", "", "Unknown", "", "v" + data["depthboot_version"], "", data["de_name"], "",
                  data["distro_version"], "", data["distro_name"].capitalize()]

        for index, label in enumerate(self.manager.get_screen(self.name).ids.help_screen_grid_layout.children):
            print(index, label.text)
            if label.text == "":
                label.text = labels[index]


class Screen6(SettingsScreen):
    pass


class WindowManager(ScreenManager):
    pass


class MainApp(App):
    def build(self):
        self.title = 'Audio'
        Window.clearcolor = (30 / 255, 32 / 255, 36 / 255, 1)  # color between transitions
        window_manager = WindowManager()
        window_manager.transition.duration = 0
        window_manager.current = 'screen_1'
        return window_manager


if __name__ == '__main__':
    MainApp().run()
