import json
import time

from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen

Config.set('input', 'mouse', 'mouse,disable_multitouch')

from functions import *

global sidebar_buttons
sidebar_buttons = ["Audio", "Keyboard", "Install location", "Kernel", "ZRAM", "About", "Help"]


def read_package_version(package_name: str) -> str:
    # Read eupnea.json to get distro info
    with open("/etc/eupnea.json", "r") as f:
        distro_info = json.load(f)

    match distro_info["distro_name"]:
        case "ubuntu" | "popos":
            try:
                raw_dpkg = bash(f"dpkg-query -s {package_name}")
                if raw_dpkg.__contains__("Status: install ok installed"):
                    return raw_dpkg.split("\n")[7][9:]
            except subprocess.CalledProcessError:
                return "Error"
        case "fedora":
            pass
        case "arch":
            pass


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


class Screen1(SettingsScreen):  # audio
    pass


class Screen2(SettingsScreen):  # keyboard
    pass


class Screen3(SettingsScreen):  # install location
    pass


class Screen4(SettingsScreen):  # kernel
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.first_enter = True
        self.kernel_install_in_process = False

    def on_enter(self):
        super().on_enter()  # call original on_enter() method

        if self.first_enter:
            # set spacing for boxlayout
            self.manager.get_screen(self.name).ids.screen_content_box.spacing = 50

            # add gridlayout for kernel version
            temp_grid = GridLayout()
            temp_grid.cols = 2
            temp_grid.size_hint = (1, None)
            # temp_grid.spacing = 10
            # temp_grid.padding = 50
            self.manager.get_screen(self.name).ids.screen_content_box.add_widget(temp_grid)
            self.ids['about_screen_grid_layout'] = temp_grid

            labels = ["Current kernel: ", "", "Kernel package version: ", "", "Modules package version: ", "",
                      "Headers package version: ", ""]

            for text in labels:
                self.new_label = Factory.CustomLabel()
                self.new_label.text = text
                self.new_label.halign = "right" if text == "" else "left"
                self.manager.get_screen(self.name).ids.about_screen_grid_layout.add_widget(self.new_label)

            # Add mainline kernel button
            mainline_kernel_button = Factory.RoundedButton()
            mainline_kernel_button.text = "Switch to Mainline kernel"
            mainline_kernel_button.bind(on_release=self.kernel_button_clicked)
            mainline_kernel_button.size_hint = (0.5, 0.1)
            mainline_kernel_button.pos_hint = {"center_x": 0.5}
            self.ids['mainline_kernel_button'] = mainline_kernel_button
            self.manager.get_screen(self.name).ids.screen_content_box.add_widget(mainline_kernel_button)

            # Add ChromeOS kernel button
            chromeos_kernel_button = Factory.RoundedButton()
            chromeos_kernel_button.text = "Switch to ChromeOS kernel"
            chromeos_kernel_button.bind(on_release=self.kernel_button_clicked)
            chromeos_kernel_button.size_hint = (0.5, 0.1)
            chromeos_kernel_button.pos_hint = {"center_x": 0.5}
            self.ids['chromeos_kernel_button'] = chromeos_kernel_button
            self.manager.get_screen(self.name).ids.screen_content_box.add_widget(chromeos_kernel_button)

            # Add loading gif
            empty_image = Factory.LoadingImage(source="assets/blank_icons/blank.png")
            empty_image.size_hint = (0.1, 0.1)
            empty_image.pos_hint = {"center_x": 0.5, "center_y": 0.5}
            self.ids['loading_image'] = empty_image
            self.manager.get_screen(self.name).ids.screen_content_box.add_widget(empty_image)

            self.first_enter = False

        # Read eupnea.json to get distro info
        with open("/etc/eupnea.json", "r") as f:
            distro_info = json.load(f)

        # read kernel version
        kernel_version = bash("uname -r")

        kernel_type = "chromeos" if kernel_version.startswith("5.") else "mainline"

        image_version = read_package_version(f"eupnea-{kernel_type}-kernel")
        modules_version = read_package_version(f"eupnea-{kernel_type}-kernel-modules")
        headers_version = read_package_version(f"eupnea-{kernel_type}-kernel-headers")

        # Set kernel version labels
        self.manager.get_screen(self.name).ids.about_screen_grid_layout.children[6].text = kernel_version
        self.manager.get_screen(self.name).ids.about_screen_grid_layout.children[4].text = image_version
        self.manager.get_screen(self.name).ids.about_screen_grid_layout.children[2].text = modules_version
        self.manager.get_screen(self.name).ids.about_screen_grid_layout.children[0].text = headers_version

        # Set button text
        self.manager.get_screen(
            self.name).ids.chromeos_kernel_button.text = "Switch to ChromeOS kernel" if kernel_type == "mainline" else "Reinstall ChromeOS kernel"
        self.manager.get_screen(
            self.name).ids.mainline_kernel_button.text = "Switch to Mainline kernel" if kernel_type == "chromeos" else "Reinstall Mainline kernel"

    def kernel_button_clicked(self, instance):
        def rotate_loading_image():
            if self.kernel_install_in_process:
                if self.manager.current == self.name:  # only spin if current screen is visible
                    self.manager.get_screen(self.name).ids.loading_image.angle -= 5
                Clock.schedule_once(lambda dt: rotate_loading_image(), 0.025)

        if not self.kernel_install_in_process:
            print(f"{instance.text} pressed")
            self.kernel_install_in_process = True

            # Disable both kernel buttons
            self.manager.get_screen(self.name).ids.chromeos_kernel_button.disabled = True
            self.manager.get_screen(self.name).ids.chromeos_kernel_button.state = "down"
            self.manager.get_screen(self.name).ids.mainline_kernel_button.disabled = True
            self.manager.get_screen(self.name).ids.mainline_kernel_button.state = "down"

            # Start re/installing kernel
            bash("/usr/lib/eupnea/modify-packages")

            # start spinning gif
            self.manager.get_screen(self.name).ids.loading_image.source = "assets/loading.png"
            Clock.schedule_once(lambda dt: rotate_loading_image())  # start spinning circle in separate thread



class Screen5(SettingsScreen):  # ZRAM
    pass


class Screen6(SettingsScreen):  # about
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
                      "Depthboot version: ", "", "Eupnea utils version: ", "", "Eupnea updater version: ", "",
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
                  read_package_version("eupnea-system"), "", read_package_version("eupnea-utils"), "",
                  "v" + data["depthboot_version"], "",
                  data["de_name"], "",
                  data["distro_version"], "", data["distro_name"].capitalize()]

        for index, label in enumerate(self.manager.get_screen(self.name).ids.help_screen_grid_layout.children):
            if label.text == "":
                label.text = labels[index]


class Screen7(SettingsScreen):  # help
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
