from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen

Config.set('input', 'mouse', 'mouse,disable_multitouch')

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
                button.background_color = (0, 0, 0, 1)
            else:
                button.disabled = True
                # button.state = "down"
                button.background_color = (1, 1, 1, 1)

    def button_clicked(self, instance):
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


class Screen5(SettingsScreen):
    pass


class Screen6(SettingsScreen):
    pass


class WindowManager(ScreenManager):
    pass


class MainApp(App):
    def build(self):
        self.title = 'Eupnea settings'
        Window.clearcolor = (30 / 255, 32 / 255, 36 / 255, 1)  # color between transitions
        window_manager = WindowManager()
        window_manager.current = 'screen_1'
        return window_manager


if __name__ == '__main__':
    MainApp().run()
