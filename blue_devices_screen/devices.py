from random import choice

from kivymd.uix.screen import MDScreen
from kivymd.uix.list import OneLineListItem
from kivymd.uix.list import MDList
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.button import MDFloatingActionButton
from kivymd.app import MDApp
# from kivymd.toast import toast

from kivy.utils import platform, get_hex_from_color
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp

# from kivymd.icon_definitions import md_icons

COLORS = [
    [153/255, 69/255, 255/255, 1],
    [187/255, 100/255, 217/255, 1],
    [255/255, 69/255, 150/255, 1],
    [255/255, 69/255, 69/255, 1],
    [100/255, 160/255, 217/255, 1],
    [255/255, 115/255, 69/255, 1],
    [217/255, 100/255, 166/255, 1]
]


if platform == 'android':
    from jnius import autoclass

    BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
    BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
    Intent = autoclass('android.content.Intent')
    mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
    from android_toast.toast import android_toast


class BlueDevicesScreen(MDScreen):
    def __init__(self, **kw):
        self.devices = []
        self.list_of_devices = None
        self.toolbar = None
        self.choosen_color = None
        self.app = MDApp.get_running_app()

        if platform == 'android':
            self.bluetoothAdapter = BluetoothAdapter.getDefaultAdapter()
            if not self.bluetoothAdapter:
                android_toast("This device doesn't support bluetooth", True)
        else:
            self.bluetoothAdapter = None

        Clock.schedule_once(self.post_init, 0)
        super().__init__(**kw)

    def post_init(self, dt):

        scroll = ScrollView(always_overscroll=False)
        self.list_of_devices = MDList()
        scroll.add_widget(self.list_of_devices)
        box = BoxLayout()
        box.add_widget(scroll)

        self.refresh_btn = MDFloatingActionButton(
            icon='refresh',
            pos_hint={'center_x': .5, 'center_y': .5},
            md_bg_color=self.app.theme_cls.primary_color,
            opacity=0
        )
        self.refresh_btn.bind(on_release=self.get_bluetooth_devices)
        btn_layout = FloatLayout(size_hint_y=None, height=dp(100))
        btn_layout.add_widget(self.refresh_btn)

        self.container = BoxLayout(orientation='vertical')
        self.toolbar = MDToolbar(pos_hint={'top': 1})
        self.toolbar.left_action_items = [
            'chevron-left', lambda x: self.switch_screen()
        ],
        self.toolbar.right_action_items = [
            'bluetooth-off', lambda x: self.clear_device()
        ],
        self.container.add_widget(self.toolbar)
        self.container.add_widget(box)
        self.container.add_widget(btn_layout)

        self.add_widget(self.container)

    def enable_bluetooth(self):
        enableAdapter = Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE)
        mActivity.startActivityForResult(enableAdapter, 0)

    def on_enter(self, *args):
        if self.bluetoothAdapter:
            if not self.bluetoothAdapter.isEnabled():
                self.enable_bluetooth()
            self.get_bluetooth_devices()
        Clock.schedule_once(self.animate_button_colors, 0)
        return super().on_enter(*args)

    def on_leave(self, *args):
        self.devices = []
        self.list_of_devices.clear_widgets()
        Clock.schedule_once(self.app.save_theme, 0)
        Animation.cancel_all(self.refresh_btn)
        Animation.cancel_all(self.toolbar)
        self.toolbar.md_bg_color = self.app.theme_cls.primary_color
        self.refresh_btn.md_bg_color = self.app.theme_cls.primary_color
        return super().on_leave(*args)

    def on_pre_enter(self, *args):
        Animation(opacity=1, d=1.5).start(self.refresh_btn)
        return super().on_pre_enter(*args)

    def on_pre_leave(self, *args):
        self.app.set_decorations()
        self.refresh_btn.opacity = 0
        return super().on_pre_leave(*args)

    def get_bluetooth_devices(self, *_):

        if self.bluetoothAdapter:
            if self.bluetoothAdapter.isEnabled():
                results = self.bluetoothAdapter.getBondedDevices()
                self.devices = results.toArray()
                self.list_of_devices.clear_widgets()

                for device in self.devices:
                    name = OneLineListItem(text=device.getName())
                    name.bind(on_release=self.save_device_name)
                    self.list_of_devices.add_widget(name)
            else:
                self.enable_bluetooth()

    def save_device_name(self, widget):

        self.app.paired_car = widget.text

        self.app.root.ids.content_drawer\
            .ids.md_list.children[0].text = widget.text

        android_toast(f'Listening for {widget.text}', True)

    def switch_screen(self):
        self.app.root.ids.sm.current = 'scr 1'

    def clear_device(self):
        self.app.paired_car = ''
        self.app.root.ids.content_drawer\
            .ids.md_list.children[0].text = 'Choose car'

    def change_decorations(self, *_):

        if platform == 'android':
            statusbar = get_hex_from_color(self.choosen_color[:-1])
            navbar = get_hex_from_color(self.choosen_color[:-1])
            self.app.statusbar(statusbar, navbar)

    def animate_button_colors(self, *_):
        self.choosen_color = choice(COLORS)
        a = Animation(md_bg_color=self.choosen_color, d=.3)
        b = Animation(md_bg_color=self.choosen_color, d=.3)
        a.bind(on_start=self.change_decorations)
        a.start(self.refresh_btn)
        b.start(self.toolbar)
