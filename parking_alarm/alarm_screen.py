from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.animation import Animation

from kivymd.app import MDApp
from kivymd.uix.button import MDFloatingActionButton

from jnius import autoclass

mActivity = autoclass('org.kivy.android.PythonActivity').mActivity


class AlarmScreen(Screen):
    def __init__(self, **kw):
        self.app = MDApp.get_running_app()
        Clock.schedule_once(self.post_init, 0)
        super().__init__(**kw)

    def post_init(self, dt):
        self.btn = MDFloatingActionButton(
            icon='alarm-off',
            pos_hint={'center_x': .5, 'center_y': .1}
        )
        self.btn.md_bg_color = self.app.theme_cls.primary_color
        self.btn.bind(on_release=self.close)
        self.image = Image(
            source=self.app.car_image,
            pos_hint={'center_x': .5, 'center_y': .5},
            size_hint=[None, None],
            size=[200, 200]
        )
        self.add_widget(self.image)
        self.add_widget(self.btn)

    def on_enter(self, *args):
        self.start_animation()
        return super().on_enter(*args)

    def on_pre_leave(self, *args):
        Animation.cancel_all(self.image)
        return super().on_pre_leave(*args)

    def start_animation(self, *_):
        a = Animation(size=[300, 300], d=1., t='in_out_elastic')
        a.bind(on_complete=self.back_aniamte)
        a.start(self.image)

    def back_aniamte(self, *_):
        a = Animation(size=[150, 150], d=1., t='in_out_elastic')
        a.bind(on_complete=self.start_animation)
        a.start(self.image)

    def close(self, *_):
        self.app.root.ids.sm.current = 'scr 1'
        if self.app.vibrator:
            self.app.vibrator.stop()
            self.app.vibrator = None
        Clock.schedule_once(self.move_close, .3)

    def move_close(self, _):
        mActivity.moveTaskToBack(True)
