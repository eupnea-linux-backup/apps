import contextlib
import os
import threading

# overwrite default kivy home
os.environ["KIVY_HOME"] = "~/.config/eupnea-settings"

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
from kivy.uix.screenmanager import Screen, ScreenManager

import backend

Config.set("input", "mouse", "mouse,disable_multitouch")


class BlankScreen(Screen):
    pass


class SettingsScreen(Screen):
    # This function will be called every time the screen is displayed
    def on_enter(self):
        # TODO: kill all running threads
        # print(multiprocessing.active_children())
        # for process in multiprocessing.active_children():
        #     process.kill()

        self.manager.get_screen(self.name).ids.side_bar.remove_widget(
            self.manager.get_screen(self.name).ids.side_bar_fake_button)

        # remove extra buttons from sidebar if they should not be there
        if "Install to disk" not in sidebar_buttons:
            self.manager.get_screen(self.name).ids.side_bar.remove_widget(
                self.manager.get_screen(self.name).ids.side_bar_button_3)
        if "Fedora extras" not in sidebar_buttons:
            self.manager.get_screen(self.name).ids.side_bar.remove_widget(
                self.manager.get_screen(self.name).ids.side_bar_button_6)

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
            self.ids["about_screen_grid_layout"] = temp_grid

            labels = [
                "Current kernel: ",
                "",
                "Kernel package version: ",
                "",
                "Modules package version: ",
                "",
                "Headers package version: ",
                "",
            ]

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
            self.ids["cmdline_button"] = cmdline_button
            self.manager.get_screen(self.name).ids.screen_content_box.add_widget(cmdline_button)

            # Add sleep fix button
            sleep_fix_button = Factory.RoundedButton()
            if backend.deep_sleep_enabled():
                sleep_fix_button.text = "Re-enable deep sleep"
            else:
                sleep_fix_button.text = "Disable deep sleep"
            sleep_fix_button.bind(on_release=lambda dt: backend.toggle_deep_sleep())
            sleep_fix_button.size_hint = (0.5, 0.5)
            sleep_fix_button.pos_hint = {"center_x": 0.5, "center_y": 0.5}
            self.ids["sleep_fix_button"] = sleep_fix_button
            self.manager.get_screen(self.name).ids.screen_content_box.add_widget(sleep_fix_button)

            # # Add empty image
            # empty_image = Factory.LoadingImage(source="assets/blank_icons/blank_green.png")
            # empty_image.size_hint = (0.05, 0.05)
            # self.manager.get_screen(self.name).ids.screen_content_box.add_widget(empty_image)

            # Gridlayout makes the buttons way too big -> use 2 horizontal boxlayouts
            # add Boxlayouts for kernel buttons
            temp_box = BoxLayout()
            temp_box.size_hint = (1, 1)
            # temp_box.spacing = 10
            self.ids["mainline_box"] = temp_box
            self.manager.get_screen(self.name).ids.screen_content_box.add_widget(temp_box)

            temp_box = BoxLayout()
            temp_box.size_hint = (1, 1)
            # temp_box.spacing = 10
            self.ids["chromeos_box"] = temp_box
            self.manager.get_screen(self.name).ids.screen_content_box.add_widget(temp_box)

            # Add mainline kernel button
            mainline_kernel_button = Factory.RoundedButton()
            mainline_kernel_button.text = "Switch to Mainline kernel"
            mainline_kernel_button.bind(on_release=self.kernel_button_clicked)
            mainline_kernel_button.size_hint = (0.5, 0.5)
            mainline_kernel_button.pos_hint = {"center_x": 0.5, "center_y": 0.5}
            self.ids["mainline_kernel_button"] = mainline_kernel_button
            self.manager.get_screen(self.name).ids.mainline_box.add_widget(mainline_kernel_button)

            # Add loading gif
            loading_image = Factory.LoadingImage(source="assets/blank_icons/blank.png")
            loading_image.size_hint = (0.5, 0.5)
            loading_image.pos_hint = {"center_x": 0.5, "center_y": 0.5}
            self.ids["mainline_loading_image"] = loading_image
            self.manager.get_screen(self.name).ids.mainline_box.add_widget(loading_image)

            # Add ChromeOS kernel button
            chromeos_kernel_button = Factory.RoundedButton()
            chromeos_kernel_button.text = "Switch to ChromeOS kernel"
            chromeos_kernel_button.bind(on_release=self.kernel_button_clicked)
            chromeos_kernel_button.size_hint = (0.5, 0.5)
            chromeos_kernel_button.pos_hint = {"center_x": 0.5, "center_y": 0.5}
            self.ids["chromeos_kernel_button"] = chromeos_kernel_button
            self.manager.get_screen(self.name).ids.chromeos_box.add_widget(chromeos_kernel_button)

            # Add loading gif
            loading_image = Factory.LoadingImage(source="assets/blank_icons/blank.png")
            loading_image.size_hint = (0.5, 0.5)
            loading_image.pos_hint = {"center_x": 1, "center_y": 0.5}
            self.ids["chromeos_loading_image"] = loading_image
            self.manager.get_screen(self.name).ids.chromeos_box.add_widget(loading_image)

            self.first_enter = False

        # disable kernel buttons while async task is running
        self.manager.get_screen(self.name).ids.mainline_kernel_button.disabled = True
        self.manager.get_screen(self.name).ids.chromeos_kernel_button.disabled = True

        def _background_load(self):
            # read kernel version
            kernel_version = backend.get_kernel_version()

            kernel_type = "chromeos" if kernel_version.startswith("5.") else "mainline"

            # Set kernel version labels
            self.manager.get_screen(self.name).ids.about_screen_grid_layout.children[6].text = kernel_version
            image_version = backend.read_package_version(f"eupnea-{kernel_type}-kernel")
            self.manager.get_screen(self.name).ids.about_screen_grid_layout.children[4].text = image_version
            modules_version = backend.read_package_version(f"eupnea-{kernel_type}-kernel-modules")
            self.manager.get_screen(self.name).ids.about_screen_grid_layout.children[2].text = modules_version
            headers_version = backend.read_package_version(f"eupnea-{kernel_type}-kernel-headers")
            self.manager.get_screen(self.name).ids.about_screen_grid_layout.children[0].text = headers_version

            # Set button text
            self.manager.get_screen(self.name).ids.chromeos_kernel_button.text = (
                "Switch to ChromeOS kernel" if kernel_type == "mainline" else "Reinstall ChromeOS kernel")
            self.manager.get_screen(self.name).ids.mainline_kernel_button.text = (
                "Switch to Mainline kernel" if kernel_type == "chromeos" else "Reinstall Mainline kernel")

            # Re-enable kernel buttons
            print(self.manager.get_screen(self.name).ids.mainline_kernel_button.disabled)
            self.manager.get_screen(self.name).ids.mainline_kernel_button.disabled = False
            print(self.manager.get_screen(self.name).ids.mainline_kernel_button.disabled)
            self.manager.get_screen(self.name).ids.chromeos_kernel_button.disabled = False

        # start _background_load in a thread
        threading.Thread(target=_background_load, args=(self,)).start()

    def kernel_button_clicked(self, instance):
        def rotate_loading_image(kernel_type):
            if self.kernel_install_in_process:
                if self.manager.current == self.name:  # only spin if current screen is visible
                    if kernel_type == "mainline":
                        self.manager.get_screen(self.name).ids.mainline_loading_image.angle -= 5
                    else:
                        self.manager.get_screen(self.name).ids.chromeos_loading_image.angle -= 5
                Clock.schedule_once(lambda dt: rotate_loading_image(kernel_type), 0.025)

        def __process_kernel(instance_text):
            backend.install_kernel(instance_text.startswith("Reinstall"))  # Pass True if reinstalling

            # re-enable kernel buttons when done
            self.manager.get_screen(self.name).ids.chromeos_kernel_button.disabled = False
            self.manager.get_screen(self.name).ids.chromeos_kernel_button.state = "down"
            self.manager.get_screen(self.name).ids.mainline_kernel_button.disabled = False
            self.manager.get_screen(self.name).ids.mainline_kernel_button.state = "down"
            self.kernel_install_in_process = False

        print(f"{instance.text} pressed")
        self.kernel_install_in_process = True

        # Disable both kernel buttons
        self.manager.get_screen(self.name).ids.chromeos_kernel_button.disabled = True
        self.manager.get_screen(self.name).ids.chromeos_kernel_button.state = "down"
        self.manager.get_screen(self.name).ids.mainline_kernel_button.disabled = True
        self.manager.get_screen(self.name).ids.mainline_kernel_button.state = "down"

        # start spinning gif
        if instance.text.__contains__("Mainline"):
            self.manager.get_screen(self.name).ids.mainline_loading_image.source = "assets/loading.png"
            # start rotating loading image
            Clock.schedule_once(lambda dt: rotate_loading_image("mainline"))
        else:
            self.manager.get_screen(self.name).ids.chromeos_loading_image.source = "assets/loading.png"
            # start rotating loading image
            Clock.schedule_once(lambda dt: rotate_loading_image("chromeos"))

        # start kernel install in a thread
        Clock.schedule_once(lambda dt: __process_kernel(instance.text))

    def show_cmdline_popup(self, instance):
        # Create cmdline popup
        cmdline_popup = Factory.CMDLinePopUp()
        self.ids["cmdline_popup"] = cmdline_popup

        error, self.current_cmdline = backend.get_current_cmdline()
        cmdline_popup.ids.cmdline_input.text = error or self.current_cmdline
        cmdline_popup.open()

    # This function is called from kv only
    def apply_cmdline(self, _):
        def rotate_loading_image():
            if self.applying_cmdline:
                self.manager.get_screen(self.name).ids.cmdline_loading_image.angle -= 5
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

            error = backend.apply_kernel(self.manager.get_screen(self.name).ids.cmdline_popup.ids.cmdline_input.text)
            if error == "PENDING_REBOOT":
                # Show error popup
                error_popup = Popup(title="Error", title_align="center", title_size="20", auto_dismiss=False)
                error_popup.size_hint = (0.5, 0.5)
                error_popup.add_widget(BoxLayout(orientation="vertical", size_hint=(1, 1), spacing=100))
                error_popup.children[0].add_widget(Label(text=error, valign="top"))
                # add empty image to center text
                error_popup.children[0].add_widget(Image(size_hint=(1, 1), source="assets/blank_icons/blank.png"))
                error_popup.children[0].add_widget(Factory.RoundedButton(text="OK", on_press=__dismiss_popups))
                error_popup.open()
            elif error:
                # TODO: Show generic error popup
                pass
            __dismiss_popups(None)

        print("Checking if cmdline changed")
        print(self.manager.get_screen(self.name).ids.cmdline_popup.ids.cmdline_input.text)
        if self.manager.get_screen(self.name).ids.cmdline_popup.ids.cmdline_input.text != self.current_cmdline:
            print("Changing cmdline")
            self.applying_cmdline = True

            # grey out buttons
            self.manager.get_screen(self.name).ids.cmdline_popup.ids.apply_button.state = "down"
            self.manager.get_screen(self.name).ids.cmdline_popup.ids.cancel_button.state = "down"
            self.manager.get_screen(self.name).ids.cmdline_popup.ids.apply_button.disabled = True
            self.manager.get_screen(self.name).ids.cmdline_popup.ids.cancel_button.disabled = True
            # Disable text input
            self.manager.get_screen(self.name).ids.cmdline_popup.ids.cmdline_input.disabled = True

            # Add loading image
            temp_image = Factory.LoadingImage(source="assets/loading.png", size_hint=(1, 0.3))
            self.ids["cmdline_loading_image"] = temp_image
            self.manager.get_screen(self.name).ids.cmdline_popup.ids.popup_boxlayout.add_widget(temp_image)

            # Set button text
            self.manager.get_screen(self.name).ids.cmdline_popup.ids.apply_button.text = "Applying cmdline..."

            # Start spinning circle
            # Clock passes an argument to the function, but we don't need it -> use lambda to ignore the argument
            print(self)
            Clock.schedule_once(lambda dt: __apply_cmdline())
        else:
            self.manager.get_screen(self.name).ids.cmdline_popup.dismiss()


class Screen5(SettingsScreen):  # ZRAM
    pass


class Screen6(SettingsScreen):  # Fedora extras
    pass


class Screen7(SettingsScreen):  # about
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
            self.ids["help_screen_grid_layout"] = temp_grid
            # add labels to the screen
            # The empty strings are filled each time the screen is displayed
            # TODO: Differentiate between depthboot and eupneaOS
            labels = [
                "Distribution:",
                "",
                "Distribution version:",
                "",
                "Desktop environment:",
                "",
                "Depthboot version:",
                "",
                "Eupnea utils version:",
                "",
                "Eupnea updater version:",
                "",
                "Install type:",
                "",
                "Windowing system:",
                "",
                "Firmware payload:",
                "",
            ]

            for text in labels:
                self.new_label = Factory.CustomLabel()
                self.new_label.text = text
                self.new_label.halign = "right" if text == "" else "left"
                self.manager.get_screen(self.name).ids.help_screen_grid_layout.add_widget(self.new_label)

            self.first_enter = False

        def _background_load(self):
            print(self)
            # threaded function to fill fields to prevent freezing of the ui

            data = backend.read_eupnea_json()  # Read eupnea configuration
            session_type = backend.get_session_type()  # Get session type

            labels = [
                data["firmware_payload"].capitalize(),
                "",
                session_type.capitalize(),
                "",
                data["install_type"],
                "",
                backend.read_package_version("eupnea-system"),
                "",
                backend.read_package_version("eupnea-utils"),
                "",
                "v" + data["depthboot_version"],
                "",
                data["de_name"],
                "",
                data["distro_version"],
                "",
                data["distro_name"].capitalize(),
            ]

            for index, label in enumerate(self.manager.get_screen(self.name).ids.help_screen_grid_layout.children):
                if label.text == "":
                    label.text = labels[index]

        # start _background_load in a thread
        print(self)
        threading.Thread(target=_background_load, args=(self,)).start()


class Screen8(SettingsScreen):  # help
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
        self.title = "Audio"
        Window.clearcolor = (30 / 255, 32 / 255, 36 / 255, 1)  # color between transitions
        self.window_manager = WindowManager()
        self.window_manager.transition.duration = 0
        self.window_manager.current = "screen_4"
        return self.window_manager


if __name__ == "__main__":
    # determine which screens should be shown
    sidebar_buttons = ["Audio", "Keyboard", "Install to disk", "Kernel", "ZRAM", "Fedora extras", "About", "Help"]
    eupnea_json = backend.read_eupnea_json()
    if eupnea_json["install_type"] in ["internal", "expanded-internal"]:
        sidebar_buttons.remove("Install to disk")
    if eupnea_json["distro_name"] != "fedora":
        sidebar_buttons.remove("Fedora extras")

    MainApp().run()
