from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition

import system_functions

Config.set('input', 'mouse', 'mouse,disable_multitouch')


class BlankScreen(Screen):
    pass


class SetupScreen1(Screen):
    pass


class SetupScreen2(Screen):
    def button_clicked(self, instance):
        install_type = instance.install_type
        print(f"Install type selected: {instance.install_type}")


class SetupScreen3(Screen):
    dictionaries = system_functions.parse_keyboard_layouts()
    prev_basic_label = None
    prev_advanced_label = None

    # This function will be called every time the screen is displayed
    def on_enter(self):
        # Generate layouts dictionaries
        # Parse into list
        basic_list = []
        for key, value in self.dictionaries[0].items():
            basic_list.append(key)
        basic_list.sort()

        # Add basic layouts labels to the scrollview
        for layout in basic_list:
            self.new_label = Factory.CustomLabel()
            self.new_label.text = layout
            self.new_label.bind(on_touch_down=self.manager.get_screen("setup_screen_3").basic_layout_selected)
            self.manager.get_screen("setup_screen_3").ids.basic_layout_list.add_widget(self.new_label)

    def basic_layout_selected(self, instance, touch):
        if not instance.collide_point(*touch.pos):
            return
        # Disable button, no matter what
        self.manager.get_screen("setup_screen_3").ids.next_button_3.disabled = True
        self.manager.get_screen("setup_screen_3").ids.next_button_3.state = "down"

        # Reset background color of previous label
        if self.prev_basic_label is not None:
            self.prev_basic_label.background_color = (0, 0, 0, 0)
        # Change background color of selected label
        instance.background_color = (1, 1, 1, 0.3)
        # Save selected label
        self.prev_basic_label = instance

        print(f"basic layout selected: {instance.text}")
        # Show advanced layouts in second scrollview
        self.manager.get_screen("setup_screen_3").ids.advanced_layout_list.clear_widgets()

        # Get layout short name from dict
        self.short_name = self.dictionaries[0][instance.text]
        print(f"basic layout selected short name: {self.short_name}")

        # get advanced layouts for selected basic layout
        advanced_list = []
        try:
            for key, value in self.dictionaries[1][self.short_name].items():
                advanced_list.append(key)
                advanced_list.sort()
        except KeyError:
            # Layout doesn't have advanced layouts
            self.selected_layout = self.short_name
            # activate next button
            self.manager.get_screen("setup_screen_3").ids.next_button_3.disabled = False
            self.manager.get_screen("setup_screen_3").ids.next_button_3.state = "normal"
            return

        for layout in advanced_list:
            self.new_label = Factory.CustomLabel()
            self.new_label.text = layout
            self.new_label.bind(on_touch_down=self.manager.get_screen("setup_screen_3").advanced_layout_selected)
            self.manager.get_screen("setup_screen_3").ids.advanced_layout_list.add_widget(self.new_label)

    def advanced_layout_selected(self, instance, touch):
        if not instance.collide_point(*touch.pos):
            return
        # Disable button, no matter what
        self.manager.get_screen("setup_screen_3").ids.next_button_3.disabled = True
        self.manager.get_screen("setup_screen_3").ids.next_button_3.state = "down"

        # Reset background color of previous label
        if self.prev_advanced_label is not None:
            self.prev_advanced_label.background_color = (0, 0, 0, 0)
        # Change background color of selected label
        instance.background_color = (1, 1, 1, 0.3)
        # Save selected label
        self.prev_advanced_label = instance

        print(f"advanced layout selected: {instance.text}")
        self.selected_layout = self.dictionaries[1][self.short_name][instance.text]
        print(f"selected layout short name: {self.selected_layout}")
        self.manager.get_screen("setup_screen_3").ids.next_button_3.disabled = False
        self.manager.get_screen("setup_screen_3").ids.next_button_3.state = "normal"

    def button_clicked(self, instance) -> None:
        system_functions.set_keyboard_layout(self.selected_layout)


class SetupScreen4(Screen):

    def clear_username_error(self):
        self.manager.get_screen("setup_screen_4").ids.username_error.text = ""
        self.manager.get_screen("setup_screen_4").ids.username_input.background_normal = "assets/textfield/normal.png"

    def compare_passwords(self) -> None:
        if self.manager.get_screen("setup_screen_4").ids.password_input_1.text != self.manager.get_screen(
                "setup_screen_4").ids.password_input_2.text:
            self.manager.get_screen("setup_screen_4").ids.password_error_1.text = "Passwords don't match"
            self.manager.get_screen(
                "setup_screen_4").ids.password_input_1.background_normal = "assets/textfield/error.png"
            self.manager.get_screen("setup_screen_4").ids.password_error_2.text = "Passwords don't match"
            self.manager.get_screen(
                "setup_screen_4").ids.password_input_2.background_normal = "assets/textfield/error.png"
        else:
            self.manager.get_screen("setup_screen_4").ids.password_error_1.text = ""
            self.manager.get_screen(
                "setup_screen_4").ids.password_input_1.background_normal = "assets/textfield/normal.png"
            self.manager.get_screen("setup_screen_4").ids.password_error_2.text = ""
            self.manager.get_screen(
                "setup_screen_4").ids.password_input_2.background_normal = "assets/textfield/normal.png"

    def check_username(self) -> None:
        # Don't check if username is empty and revert to normal
        if self.manager.get_screen("setup_screen_4").ids.username_input.text == "":
            self.manager.get_screen(
                "setup_screen_4").ids.username_input.background_normal = "assets/textfield/normal.png"
            self.manager.get_screen("setup_screen_4").ids.username_error.text = ""
            return

        # Check for spaces inside username
        if " " in self.manager.get_screen("setup_screen_4").ids.username_input.text:
            self.manager.get_screen("setup_screen_4").ids.username_error.text = "Username cannot contain spaces"
            self.manager.get_screen(
                "setup_screen_4").ids.username_input.background_normal = "assets/textfield/error.png"
            return

        # Don't allow dash at the beginning
        if self.manager.get_screen("setup_screen_4").ids.username_input.text[0] == "-":
            self.manager.get_screen("setup_screen_4").ids.username_error.text = "Username can't start with a dash"
            self.manager.get_screen(
                "setup_screen_4").ids.username_input.background_normal = "assets/textfield/error.png"
            return

        # Don't allow numbers at the beginning
        if self.manager.get_screen("setup_screen_4").ids.username_input.text[0].isdigit():
            self.manager.get_screen("setup_screen_4").ids.username_error.text = "Username can't start with a number"
            self.manager.get_screen(
                "setup_screen_4").ids.username_input.background_normal = "assets/textfield/error.png"
            return

        # Only allow chars from dictionary below
        for char in self.manager.get_screen("setup_screen_4").ids.username_input.text:
            if char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-":
                self.manager.get_screen(
                    "setup_screen_4").ids.username_error.text = f"Username contains invalid character: {char}"
                self.manager.get_screen(
                    "setup_screen_4").ids.username_input.background_normal = "assets/textfield/error.png"
                return
        # if no invalid chars are found revert to normal
        self.manager.get_screen("setup_screen_4").ids.username_input.background_normal = "assets/textfield/normal.png"
        self.manager.get_screen("setup_screen_4").ids.username_error.text = ""


class SetupScreen5(Screen):
    # This function will be called every time the screen is displayed
    def on_enter(self):
        # Read Wi-Fi ssids
        wifi_list = system_functions.get_wifi_list()
        if wifi_list[0] == "Already connected to the internet":
            print("Already connected to the internet")
            # TODO: UNCOMMENT FOR RELEASE
            self.manager.current = "setup_screen_6"  # skip to next screen
            return

        # Add basic layouts labels to the scrollview
        for wifi in wifi_list:
            self.new_label = Factory.CustomLabel()
            self.new_label.text = wifi[0]
            self.new_label.bind(on_touch_down=self.manager.get_screen("setup_screen_5").wifi_selected)
            self.manager.get_screen("setup_screen_5").ids.wifi_list_layout.add_widget(self.new_label)

    def wifi_selected(self, instance, touch):
        if instance.collide_point(*touch.pos):
            pass


class SetupScreen6(Screen):
    pass


class WindowManager(ScreenManager):
    def __init__(self, **kwargs):
        super(WindowManager, self).__init__(**kwargs)
        # Override keyboard controls
        Window.bind(on_keyboard=self.keyboard, on_request_close=self.inhibit_close)

    def inhibit_close(self, *args):
        print("Refusing to close")
        return True

    # def on_touch_down(self, touch):
    #     try:
    #         if touch.button == 'right':
    #             print("Refusing to allow right click")
    #             return True
    #     except AttributeError:
    #         pass
    #     return super().on_touch_down(touch)

    def keyboard(self, window, key, *args):
        print(key)
        if key == 27:  # ESC
            return True  # Do nothing


class MainApp(App):
    def build(self):
        Window.clearcolor = (30 / 255, 32 / 255, 36 / 255, 1)  # color between transitions
        Window.size = (1920, 1080)
        # Window.size = (1280, 720)
        Window.borderless = True
        # Window.fullscreen = True
        window_manager = WindowManager()
        window_manager.current = 'setup_screen_4'
        return window_manager


if __name__ == '__main__':
    MainApp().run()
