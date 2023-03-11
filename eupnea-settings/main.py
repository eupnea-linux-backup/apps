import atexit
import json

from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen

Config.set('input', 'mouse', 'mouse,disable_multitouch')

from functions import *

global sidebar_buttons
sidebar_buttons = ["Audio", "Keyboard", "Install location", "Kernel", "ZRAM", "About", "Help"]


def exit_handler():
    # show error popup somehow
    pass


def read_package_version(package_name: str) -> str:
    # Read eupnea.json to get distro info
    with open("/etc/eupnea.json", "r") as f:
        distro_info = json.load(f)

    match distro_info["distro_name"]:
        case "ubuntu" | "popos":
            try:
                raw_dpkg = bash(f"dpkg-query -s {package_name}")
                if raw_dpkg.__contains__("Status: install ok installed"):
                    return raw_dpkg.split("\n")[7][9:].strip()
            except subprocess.CalledProcessError:
                return "Error"
        case "fedora":
            try:
                raw_dnf = bash(f"dnf list -C {package_name}")
                if raw_dnf.__contains__("Installed Packages"):
                    return raw_dnf.split("                  ")[1].strip()
            except subprocess.CalledProcessError:
                return "Error"
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
        self.current_cmdline = ""
        self.first_enter = True
        self.kernel_install_in_process = False
        self.applying_cmdline = False

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

            # Add cmdline button
            cmdline_button = Factory.RoundedButton()
            cmdline_button.text = "Edit cmdline"
            cmdline_button.bind(on_release=self.show_cmdline_popup)
            cmdline_button.size_hint = (0.5, 0.5)
            cmdline_button.pos_hint = {"center_x": 0.5}
            self.ids['cmdline_button'] = cmdline_button
            self.manager.get_screen(self.name).ids.screen_content_box.add_widget(cmdline_button)

            # # Add empty image
            # empty_image = Factory.LoadingImage(source="assets/blank_icons/blank_green.png")
            # empty_image.size_hint = (0.05, 0.05)
            # self.manager.get_screen(self.name).ids.screen_content_box.add_widget(empty_image)

            # Gridlayout makes the buttons way too big -> use 2 horizontal boxlayouts
            # add Boxlayouts for kernel buttons
            temp_box = BoxLayout()
            temp_box.size_hint = (1, 1)
            # temp_box.spacing = 10
            self.ids['mainline_box'] = temp_box
            self.manager.get_screen(self.name).ids.screen_content_box.add_widget(temp_box)

            temp_box = BoxLayout()
            temp_box.size_hint = (1, 1)
            # temp_box.spacing = 10
            self.ids['chromeos_box'] = temp_box
            self.manager.get_screen(self.name).ids.screen_content_box.add_widget(temp_box)

            # Add mainline kernel button
            mainline_kernel_button = Factory.RoundedButton()
            mainline_kernel_button.text = "Switch to Mainline kernel"
            mainline_kernel_button.bind(on_release=self.kernel_button_clicked)
            mainline_kernel_button.size_hint = (0.5, 0.5)
            mainline_kernel_button.pos_hint = {"center_x": 0.5, "center_y": 0.5}
            self.ids['mainline_kernel_button'] = mainline_kernel_button
            self.manager.get_screen(self.name).ids.mainline_box.add_widget(mainline_kernel_button)

            # Add loading gif
            loading_image = Factory.LoadingImage(source="assets/blank_icons/blank.png")
            loading_image.size_hint = (0.5, 0.5)
            loading_image.pos_hint = {"center_x": 0.5, "center_y": 0.5}
            self.ids['mainline_loading_image'] = loading_image
            self.manager.get_screen(self.name).ids.mainline_box.add_widget(loading_image)

            # Add ChromeOS kernel button
            chromeos_kernel_button = Factory.RoundedButton()
            chromeos_kernel_button.text = "Switch to ChromeOS kernel"
            chromeos_kernel_button.bind(on_release=self.kernel_button_clicked)
            chromeos_kernel_button.size_hint = (0.5, 0.5)
            chromeos_kernel_button.pos_hint = {"center_x": 0.5, "center_y": 0.5}
            self.ids['chromeos_kernel_button'] = chromeos_kernel_button
            self.manager.get_screen(self.name).ids.chromeos_box.add_widget(chromeos_kernel_button)

            # Add loading gif
            loading_image = Factory.LoadingImage(source="assets/blank_icons/blank.png")
            loading_image.size_hint = (0.5, 0.5)
            loading_image.pos_hint = {"center_x": 1, "center_y": 0.5}
            self.ids['chromeos_loading_image'] = loading_image
            self.manager.get_screen(self.name).ids.chromeos_box.add_widget(loading_image)

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

    def show_cmdline_popup(self, instance):
        # Create cmdline popup
        cmdline_popup = Factory.CMDLinePopUp()
        self.ids['cmdline_popup'] = cmdline_popup

        try:
            with open("/proc/cmdline", "r") as f:
                self.current_cmdline = f.read()
            print(self.current_cmdline)
            cmdline_popup.ids.cmdline_input.text = self.current_cmdline
        except subprocess.CalledProcessError:
            cmdline_popup.ids.cmdline_input.text = "Error reading cmdline"
        cmdline_popup.open()

    # This function is called from kv only
    def apply_cmdline(self, instance):
        def rotate_loading_image():
            if self.applying_cmdline:
                self.manager.get_screen(self.name).ids.cmdline_popup.ids.cmdline_loading_image.angle -= 5
                Clock.schedule_once(lambda dt: rotate_loading_image(), 0.025)

        def __apply_cmdline():
            # Start rotating loading image
            Clock.schedule_once(lambda dt: rotate_loading_image())

            # The error popup needs a function as the code cannot wait in kivy
            def __dismiss_popups(instance):
                self.applying_cmdline = False
                with contextlib.suppress(NameError):
                    error_popup.dismiss()  # error popup doesnt exist if there was no error
                self.manager.get_screen(self.name).ids.cmdline_popup.dismiss()

            # Create new cmdline file
            with open("/tmp/new_cmdline", "w") as f:
                f.write(self.manager.get_screen(self.name).ids.cmdline_popup.ids.cmdline_input.text)
            # Start install-kernel script
            try:
                bash("/usr/lib/eupnea/install-kernel --kernel-flags /tmp/new_cmdline")
            except subprocess.CalledProcessError as e:
                if e.returncode == 65:
                    print_error("System is pending reboot. Please reboot and try again.")
                    # Show error popup
                    error_popup = Popup(title="Error", title_align="center", title_size="20", auto_dismiss=False)
                    error_popup.size_hint = (0.5, 0.5)
                    error_popup.add_widget(BoxLayout(orientation="vertical", size_hint=(1, 1), spacing=100))
                    error_popup.children[0].add_widget(
                        Label(text="System is pending a reboot. Reboot and try again.", valign="top"))
                    # add empty image to center text
                    error_popup.children[0].add_widget(Image(size_hint=(1, 1), source="assets/blank_icons/blank.png"))
                    error_popup.children[0].add_widget(Factory.RoundedButton(text="OK", on_press=__dismiss_popups))
                    error_popup.open()
                else:
                    raise e
            __dismiss_popups(None)

        print("Checking if cmdline changed")
        print(self.manager.get_screen(self.name).ids.cmdline_popup.ids.cmdline_input.text)
        if self.manager.get_screen(self.name).ids.cmdline_popup.ids.cmdline_input.text != self.current_cmdline:
            print("Changing cmdline")
            self.applying_cmdline = True

            # grey out apply button
            self.manager.get_screen(self.name).ids.cmdline_popup.ids.apply_button.state = "down"
            self.manager.get_screen(self.name).ids.cmdline_popup.ids.apply_button.disabled = True
            # Disable text input
            self.manager.get_screen(self.name).ids.cmdline_popup.ids.cmdline_input.disabled = True

            # Set button text
            self.manager.get_screen(self.name).ids.cmdline_popup.ids.apply_button.text = "Applying cmdline..."

            # Start spinning circle
            self.manager.get_screen(self.name).ids.cmdline_popup.ids.cmdline_loading_image.source = "assets/loading.png"
            # Clock passes an argument to the function, but we don't need it -> use lambda to ignore the argument
            print(self)
            Clock.schedule_once(lambda dt: __apply_cmdline())


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
    def __init__(self, **kwargs):
        super(WindowManager, self).__init__(**kwargs)
        # Override keyboard controls
        Window.bind(on_keyboard=self.keyboard)

    # Do not exit when escape is pressed
    def keyboard(self, window, key, *args):
        if key == 27:  # ESC
            return True  # Do nothing


class MainApp(App):
    def build(self):
        self.title = 'Audio'
        Window.clearcolor = (30 / 255, 32 / 255, 36 / 255, 1)  # color between transitions
        self.window_manager = WindowManager()
        self.window_manager.transition.duration = 0
        self.window_manager.current = 'screen_4'
        return self.window_manager


if __name__ == '__main__':
    atexit.register(exit_handler)
    MainApp().run()
