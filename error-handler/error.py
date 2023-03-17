from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup

import os


class ExportDialog(FloatLayout):
    export = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)


class ErrorScreen(BoxLayout):
    # read all logs from the log dir and sort them naturally
    error_log_file = f"/{os.getenv('HOME')}/.config/eupnea-settings/logs/" + \
                     sorted(os.listdir(f"/{os.getenv('HOME')}/.config/eupnea-settings/logs/"),
                            key=lambda x: int(x.split('_')[-1].split('.')[0]))[1]

    def load_log_file(self):
        with open(self.error_log_file, 'r') as f:
            log_content = f.read()
        return log_content

    def dismiss_export_popup(self):
        self._popup.dismiss()

    def show_export(self):
        content = ExportDialog(export=self.export, cancel=self.dismiss_export_popup)
        self._popup = Popup(title="Export error log", content=content,
                            size_hint=(0.9, 0.9)).open()

    def export(self, path):
        os.system(f"cp {self.error_log_file} {path}")

        self._popup.dismiss()


class ErrorApp(App):
    def build(self):
        return ErrorScreen()


if __name__ == '__main__':
    ErrorApp().run()
