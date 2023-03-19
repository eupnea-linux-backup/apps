import os
from pathlib import Path

os.environ["KIVY_HOME"] = "/tmp/eupnea-apps-crash-handler"

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup


class SuccessfulExportPopup(Popup):
    export_path = ObjectProperty()


class CrashScreen(BoxLayout):
    def __init__(self, **kwargs):
        log_dirs = {
            "Eupnea Settings": "~/.config/eupnea-settings/logs",
            "Eupnea Initial Setup": "~/.config/eupnea-setup/logs",
        }

        export_dir = Path(os.path.expanduser("~/Downloads"))
        export_dir.mkdir(parents=True, exist_ok=True)

        log_files = []
        for app_name, log_dir in log_dirs.items():
            full_log_dir = Path(os.path.expanduser(log_dir))
            if full_log_dir.exists():
                log_files += [(app_name, f) for f in full_log_dir.glob("*") if f.is_file()]

        log_files.sort(key=lambda x: os.path.getmtime(x[1]), reverse=True)

        self.crashed_app, self.crash_log = log_files[0]
        self.export_path = export_dir / self.crash_log.name

        super().__init__(**kwargs)

    def load_log(self):
        with open(self.crash_log, "r") as f:
            log_content = f.read()
        return log_content

    def export(self):
        Path(self.export_path).write_text(self.load_log())
        SuccessfulExportPopup(export_path=str(self.export_path)).open()


class CrashApp(App):
    def build(self):
        return CrashScreen()


if __name__ == "__main__":
    CrashApp().run()
