from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.uix.screenmanager import ScreenManager, Screen

import system_functions

Config.set('input', 'mouse', 'mouse,disable_multitouch')


class BlankScreen(Screen):
    pass


class SetupScreen1(Screen):
    pass


class SetupScreen2(Screen):
    def button_clicked(self, instance):
        install_type = instance.install_type
        print("Install type selected: " + instance.install_type)


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
        if instance.collide_point(*touch.pos):
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

            print("basic layout selected: " + instance.text)
            # Show advanced layouts in second scrollview
            self.manager.get_screen("setup_screen_3").ids.advanced_layout_list.clear_widgets()

            # Get layout short name from dict
            self.short_name = self.dictionaries[0][instance.text]
            print("basic layout selected short name: " + self.short_name)

            # get advanced layouts for selected basic layout
            advanced_list = []
            try:
                for key, value in self.dictionaries[1][self.short_name].items():
                    advanced_list.append(key)
                    advanced_list.sort()
            except KeyError:
                # Layout doesn't have advanced layouts
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
        if instance.collide_point(*touch.pos):
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

            print("advanced layout selected: " + instance.text)
            self.selected_layout = self.dictionaries[1][self.short_name][instance.text]
            print("selected layout short name: " + self.selected_layout)
            self.manager.get_screen("setup_screen_3").ids.next_button_3.disabled = False
            self.manager.get_screen("setup_screen_3").ids.next_button_3.state = "normal"

    def button_clicked(self, instance):
        system_functions.set_keyboard_layout(self.selected_layout)


class SetupScreen4(Screen):
    pass


class WindowManager(ScreenManager):
    pass


class MainApp(App):
    def build(self):
        Window.clearcolor = (30 / 255, 32 / 255, 36 / 255, 1)  # color between transitions
        # Window.size = (1920, 1080)
        Window.size = (1280, 720)
        Window.borderless = True
        window_manager = WindowManager()
        # Window.fullscreen = True
        window_manager.current = 'setup_screen_1'
        return window_manager


if __name__ == '__main__':
    MainApp().run()
