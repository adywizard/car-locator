from datetime import datetime

from kivymd.uix.picker import MDTimePicker
from kivymd.app import MDApp
from kivy.animation import Animation


class CustomTimePicker(MDTimePicker):

    def __init__(self, **kwargs):
        self.app = MDApp.get_running_app()
        super().__init__(**kwargs)

    def on_cancel(self, *args):
        self.animate()
        return

    def on_save(self, *args):
        self.app.alarm_time = self.time
        self.animate()
        return

    def close(self, *_):
        self.dismiss()

    def animate(self):
        a = Animation(opacity=0, d=.4)
        a.bind(on_complete=self.close)
        a.start(self)

    def on_pre_open(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        time = datetime.strptime(current_time, '%H:%M:%S').time()
        self.set_time(time)
        return super().on_pre_open()
