"""Find my car"""

__author__ = 'Ady Wizard'

from functools import partial
from random import choice
from datetime import datetime, date
import os
import glob
import json

from kivymd.color_definitions import colors
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.app import MDApp
from kivymd.uix.card import MDCardSwipe
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.theming import ThemableBehavior
from kivymd.uix.list import MDList, OneLineIconListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import OneLineAvatarIconListItem

from kivy.properties import StringProperty, ListProperty,\
    ObjectProperty, NumericProperty, ColorProperty

from kivy.uix.screenmanager import (
    Screen, SlideTransition,
    RiseInTransition  # ,FallOutTransition
    )

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform
from kivy.core.window import Window
from kivy.clock import mainthread
from plyer import gps
from kivy_garden.mapview import MapMarker
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.graphics import (
    RenderContext, Fbo, Color,
    ClearColor, ClearBuffers, Rectangle
)
from kivy.uix.floatlayout import FloatLayout
from kivy.metrics import dp

from time_picker.picker import CustomTimePicker
from constants.texts import first_warn_text, background_text
from constants.colors import BUBBLE_COLORS
from constants.urls import URL, MAIL
from opengl_shader.bubbleshader import shader_watter_bubble
from kivy_lang.kivy_lang import KV


if platform == 'android':
    from jnius import autoclass, cast, JavaException
    from android.runnable import run_on_ui_thread
    from android import activity
    from android.permissions import request_permissions, Permission

    from blue.blue import BroadcastReceiver
    from android_notification.notification import notify, cancel_notification
    from alarm_manager.alarm import ParkAlarmManager
    from android_toast.toast import android_toast
    from android_vibrator.vibrator import AndroidVibrator

    Intent = autoclass('android.content.Intent')
    BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
    Uri = autoclass('android.net.Uri')
    Context = autoclass('android.content.Context')
    String = autoclass('java.lang.String')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    mActivity = PythonActivity.mActivity
    WindowManager = autoclass('android.view.WindowManager')
    AColor = autoclass("android.graphics.Color")
    LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
    Settings = autoclass('android.provider.Settings')
    LocationManager = autoclass('android.location.LocationManager')
    Calendar = autoclass('java.util.Calendar')
    SimpleDateFormat = autoclass('java.text.SimpleDateFormat')
    View = autoclass('android.view.View')
    String = autoclass('java.lang.String')
    Boolean = autoclass('java.lang.Boolean')
    ActivityCompat = autoclass('androidx.core.app.ActivityCompat')
    Manifest = autoclass('android.Manifest$permission')
    PackageManager = autoclass('android.content.pm.PackageManager')
    ContextCompat = autoclass('androidx.core.content.ContextCompat')
    NotificationManager = autoclass('android.app.NotificationManager')
    BuildVersion = autoclass('android.os.Build$VERSION')
    BuildVersion_CODES = autoclass('android.os.Build$VERSION_CODES')
    PowerManager = autoclass('android.os.PowerManager')
    Configuration = autoclass('android.content.res.Configuration')
else:
    import webbrowser

    def run_on_ui_thread(*args, **kwargs):
        return


class WarnDialogContent(BoxLayout):
    txt = ObjectProperty()


class ContentTimeError(FloatLayout):
    pass


class ContentLocationReady(FloatLayout):
    pass


class LayoutWidget(FloatLayout):
    angle = NumericProperty()
    color = ColorProperty([0, 0, 0, 0])
    x_scale = NumericProperty(1)
    y_scale = NumericProperty(1)
    z_scale = NumericProperty(1)


class SemiCircle(FloatLayout):
    color = ColorProperty([1, 1, 1, 1])
    angle_start = NumericProperty()
    angle_end = NumericProperty()


class ShaderWidget(FloatLayout):

    mouse_pos = ListProperty([100, 100])

    fs = StringProperty(None)

    texture = ObjectProperty(None)

    def __init__(self, **kwargs):

        Window.bind(mouse_pos=self.get_mouse_pos)

        self.canvas = RenderContext(use_parent_projection=True,
                                    use_parent_modelview=True,
                                    use_parent_frag_modelview=True)

        with self.canvas:
            self.fbo = Fbo(size=self.size)
            self.fbo_color = Color(1, 1, 1, 1)
            self.fbo_rect = Rectangle(size=self.size, pos=self.pos)

        with self.fbo:
            ClearColor(0, 0, 0, 0)
            ClearBuffers()

        super(ShaderWidget, self).__init__(**kwargs)

        self.fs = shader_watter_bubble
        Clock.schedule_interval(self.update_glsl, 0)

    def get_mouse_pos(self, w, pos):
        self.canvas['mouse'] = pos
        self.mouse_pos = pos

    def update_glsl(self, *largs):
        self.canvas['time'] = Clock.get_boottime()
        self.canvas['resolution'] = [float(v) for v in self.size]

    def on_fs(self, instance, value):

        shader = self.canvas.shader
        old_value = shader.fs
        shader.fs = value
        if not shader.success:
            shader.fs = old_value
            raise Exception('compilation failed')

    def add_widget(self, *args, **kwargs):
        c = self.canvas
        self.canvas = self.fbo
        super(ShaderWidget, self).add_widget(*args, **kwargs)
        self.canvas = c

    def remove_widget(self, *args, **kwargs):
        c = self.canvas
        self.canvas = self.fbo
        super(ShaderWidget, self).remove_widget(*args, **kwargs)
        self.canvas = c

    def on_size(self, instance, value):
        self.fbo.size = value
        self.texture = self.fbo.texture
        self.fbo_rect.size = value

    def on_pos(self, instance, value):
        self.fbo_rect.pos = value

    def on_texture(self, instance, value):
        self.fbo_rect.texture = value


class PltContent(MDFloatLayout):
    pass


class ItemSettings(MDFloatLayout):
    icon = StringProperty()
    text_color = StringProperty('Primary')
    color = ListProperty([1, 1, 1, 1])
    text = StringProperty()


class ChronologyScreen(Screen):
    ellipse_top = ListProperty([0, 0])
    ellipse_bottom = ListProperty([0, 0])
    ellipse_middle_bottom = ListProperty([0, 0])
    ellipse_middle_top = ListProperty([0, 0])

    def on_enter(self):
        self.animate()

    def animate(self):
        a = Animation(
            ellipse_top=[dp(300), dp(300)], d=.4, t='in_out_elastic'
        )
        a += Animation(
            ellipse_bottom=[dp(250), dp(250)], d=.4, t='in_out_elastic'
        )
        a += Animation(
            ellipse_middle_top=[dp(25), dp(25)], d=.4, t='in_out_elastic'
        )
        a += Animation(
            ellipse_middle_bottom=[dp(50), dp(50)], d=.4, t='in_out_elastic'
        )
        a.start(self)


class SettingsScreen(Screen):
    def jump(self):
        app.root.ids.sm.transition.direction = 'up'
        app.root.ids.sm.current = 'scr 1'


class ColorMark(MapMarker):
    pass


class RootWidget(Screen):

    mapview = ObjectProperty()
    alpha = ListProperty([1])


class SwipeToDeleteItem(MDCardSwipe):
    text = StringProperty()
    secondary_text = StringProperty()
    tertiary_text = StringProperty()

    def set_location(self, location):
        loc = location.split(' ')
        lo = float(loc[1])
        la = float(loc[3])
        app.loca.clear()
        app.loca = [lo, la]
        app.root.ids.mapview.center_on(lo, la)
        app.add_mark(lo, la)
        app.root.ids.sm.current = 'scr 2'


class ItemConfirm(OneLineAvatarIconListItem):

    map_type = StringProperty()

    def set_icon(self, instance_check):
        instance_check.active = True
        check_list = instance_check.get_widgets(instance_check.group)
        for check in check_list:
            if check != instance_check:
                check.active = False


class ItemColor(OneLineAvatarIconListItem):

    def set_icon(self, instance_check):
        instance_check.active = True
        check_list = instance_check.get_widgets(instance_check.group)
        for check in check_list:
            if check != instance_check:
                check.active = False


class Cancel(MDFlatButton):
    pass


class Accept(MDFlatButton):
    pass


class Ok(MDFlatButton):
    pass


class ContentNavigationDrawer(MDBoxLayout):
    pass


class ItemDrawer(OneLineIconListItem):
    icon = StringProperty()

    def set_name(self):
        if self.text == 'Drawer to right':
            self.text = 'Drawer to left'
        elif self.text == 'Drawer to left':
            self.text = 'Drawer to right'


class DrawerList(ThemableBehavior, MDList):
    type_way = ''

    def set_color_item(self, instance_item):
        if instance_item == 'theme-light-dark':
            if app.theme_cls.theme_style == 'Dark':
                app.root.alpha = [1]
                app.theme_cls.theme_style = 'Light'
                app.root.ids.r.color = [1, 1, 1, 1]
            elif app.theme_cls.theme_style == 'Light':
                app.root.alpha = [1]
                app.theme_cls.theme_style = 'Dark'
                app.root.ids.content_drawer.md_bg_color = [1, 1, 1, 1]
                app.root.ids.r.color = [0, 0, 0, 1]
            app.save_theme()


class CarPos(MDApp):

    gps_location = StringProperty()
    gps_status = StringProperty()
    loca = ListProperty()
    permit = False
    mark = None

    dialog = None
    map_dialog = None
    plate_dialog = None
    a_11_background_permit = None
    automatic_ready_dialog = None
    time_picker = None
    time_dialog_warn = None

    lat_lon = []
    accur = []
    saved = False
    gps_is_on = False
    theme_dialog = None
    mark_img = StringProperty()
    car_image = StringProperty()
    anchor = StringProperty('left')
    w = None
    h = None
    plate = StringProperty('')
    green = False

    w_count = 0
    upper_left = False
    lower_right = False

    transition = None

    br = None

    paired_car = ""
    is_car_paired = False

    is_first_time = None

    is_removing = False

    is_gathering = False

    alarm_time = ObjectProperty(allownone=True)

    vibrator = None

    activity_alarm = False

    @run_on_ui_thread
    def regain_focus(self):
        mActivity.onWindowFocusChanged(False)
        mActivity.onWindowFocusChanged(True)
        # FIX for SDLActivity window loses focus

    def button_animation(self, *_):
        if platform != 'android':
            Clock.schedule_once(self.button_animation_cancel, 5)
        ang = 8 if self.root.ids.sl.angle == -2 else -2
        a = Animation(angle=ang, d=.7, t='out_bounce')
        a.bind(on_complete=self.button_animation)
        a.start(self.root.ids.sl)

    def button_animation_cancel(self, *_):
        Animation.cancel_all(self.root.ids.sl)
        self.root.ids.sl.disabled = False
        self.root.ids.sl.angle == -2

    def on_alarm_time(self, *_):

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        time = datetime.strptime(current_time, '%H:%M:%S').time()
        t = datetime.combine(
            date.today(), self.alarm_time
            ) - datetime.combine(date.today(), time)

        if t.seconds < 60 or t.seconds > 43200:
            self.open_animate_dialog(self.time_dialog_warn, None)
            return

        alarm = ParkAlarmManager()
        alarm.start(t.seconds)
        if not self.activity_alarm:
            activity.bind(on_new_intent=self.on_alarm_intent)
            self.activity_alarm = True

    def center_mapview(self, mapview):
        mapview.center_on(app.loca[0], app.loca[1]) \
                if app.loca[0] != 0 and app.loca[1] != 0 \
                else mapview.center_on(52.5065133, 13.1445545)

    def on_alarm_intent(self, intent):
        start_alarm = intent.getBooleanExtra("startAlarm", False)
        if start_alarm:
            self.show_alarm_screen(None)
        if self.activity_alarm:
            activity.unbind(on_new_intent=self.on_alarm_intent)
            self.activity_alarm = False

    def on_new_intent(self, intent):
        cancel = intent.getStringExtra("cancel")
        if cancel == "cancel":
            self.stop_service(0, 0)
            self.start(1000, 0)
            return

        got_location = intent.getStringExtra("gotLocation")
        lat = intent.getStringExtra("lat")
        lon = intent.getStringExtra("lon")

        start = intent.getStringExtra("start")
        if start == "start":
            self.start_service(self.paired_car)
            self.turn_on_gps('start')
            cancel_notification()
            return

        if lat or lon:
            lat = float(lat)
            lon = float(lon)

        if got_location == "true":
            self.stop_service(lat, lon)

    def on_receive(self, context, intent):
        name = ''
        action = intent.getAction()
        parcable = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE)
        device = cast(BluetoothDevice, parcable)
        name = device.getName()

        if action == BluetoothDevice.ACTION_ACL_CONNECTED:

            if name == self.paired_car and not self.is_car_paired:
                # android_toast(f'connected to {name} Starting service', True)
                activity.bind(on_new_intent=self.on_new_intent)
                # self.start_service(name)
                notify(
                    context,
                    'CAR_LOCATOR_HEADS_UP',
                    'CAR CONNECTED PRESS TO START LISTEN',
                    'Location service',
                    'Car locator',
                    'Car locator service',
                    flag='update',
                    n_type='head',
                    autocancel=False
                    )

    def unregister_broadcast_receiver(self):
        try:
            if self.br and platform == 'android':
                self.br.stop()
                self.br = None
        except JavaException as e:
            Logger.error(str(e))

    @mainthread
    def stop_service(self, lat, lon):
        mActivity.stop_service()
        activity.unbind(on_new_intent=self.on_new_intent)

        if lat == 0 and lon == 0:
            return

        now = self.get_datetime()

        with open('locations/loc.json', 'r+') as f:
            loc = json.load(f)
            loc["datetime"].append(now)

            number_of_locations = len(loc['loc'])

            if number_of_locations >= 20:
                loc['loc'].pop(0)

            loc['loc'].append([lat, lon])
            f.seek(0)
            json.dump(loc, f)

        self.root.ids.md_list.add_widget(
                SwipeToDeleteItem(
                    text="Automatic Location",
                    secondary_text=now,
                    tertiary_text=f"longitude {lat} latitude {lon}"
                    )
            )
        self.open_animate_dialog(self.automatic_ready_dialog, None)

    @mainthread
    def start_service(self, device):
        mActivity.start_service(
                'waiting for disconnection',
                'location service',
                device
                )

    def register_broadcats_receiver(self):
        if not self.br and platform == 'android':

            ''' 'SCAN_RESULTS_AVAILABLE_ACTION',
                    'ACTION_STATE_CHANGED',
                    'ACTION_ACL_CONNECTED',
                    'ACTION_ACL_DISCONNECTED',
                    'ACTION_BOND_STATE_CHANGED',
                    'ACTION_ACL_DISCONNECT_REQUESTED' '''

            self.br = BroadcastReceiver(
                self.on_receive, actions=[
                    'ACTION_ACL_CONNECTED',
                    'ACTION_ACL_DISCONNECTED'
                    ])
            self.br.start()

    def first_start(self, *_):

        self.root.ids.sm.transition = RiseInTransition()
        # FallOutTransition()\
        # if self.theme_cls.theme_style == 'Dark' else RiseInTransition()

        self.root.ids.sm.current = 'scr 1'

        self.root.ids.sm.transition = SlideTransition()
        self.root.ids.sm.transition.direction = 'up'
        self.set_decorations()

    def get_background_permission_option_label(self):
        '''this is yet to be implemented with newer API'''
        PackageManager.getBackgroundPermissionOptionLabel()

    def check_background(self, *_):

        if self.permit and BuildVersion.SDK_INT >= 29:

            if ContextCompat.checkSelfPermission(
                    mActivity.getApplicationContext(),
                    Manifest.ACCESS_BACKGROUND_LOCATION
                    ) == PackageManager.PERMISSION_GRANTED:
                return True

            if ContextCompat.checkSelfPermission(
                    mActivity.getApplicationContext(),
                    Manifest.ACCESS_BACKGROUND_LOCATION
                    ) != PackageManager.PERMISSION_GRANTED:
                ActivityCompat.requestPermissions(
                    mActivity, [Manifest.ACCESS_BACKGROUND_LOCATION], 1)

            if ContextCompat.checkSelfPermission(
                    mActivity.getApplicationContext(),
                    Manifest.ACCESS_BACKGROUND_LOCATION
                    ) == PackageManager.PERMISSION_DENIED:

                if ActivityCompat.shouldShowRequestPermissionRationale(
                            mActivity,
                            Manifest.ACCESS_BACKGROUND_LOCATION
                            ):
                    Clock.schedule_once(
                        partial(
                            self.open_animate_dialog,
                            self.a_11_background_permit
                            ), 0)

        return True

    def explain_need_for_backgraund(self, *_):
        if self.is_firs_time and platform == 'android':
            Clock.schedule_once(partial(
                self.open_animate_dialog, self.explain_dialog), 0)

    def request_android_permissions(self):

        def callback(permissions, results):

            if all([res for res in results]):

                self.permit = True
            else:
                android_toast("Permessions denied", True)
                self.permit = False
                android_toast("This app can't work without GPS", True)

            return self.permit

        request_permissions([Permission.ACCESS_COARSE_LOCATION,
                             Permission.ACCESS_FINE_LOCATION], callback)

    def build(self):
        Window.bind(on_keyboard=self.back_key_handler)
        Builder.load_string(KV)
        self.root = RootWidget()

    def set_plate_number(self):
        if self.plate_dialog.content_cls.ids.txt_field.text:
            self.plate = self.plate_dialog.content_cls.ids.txt_field.text
            # Clock.schedule_once(self.save_theme, .05)

    def handle_screens(self):

        if self.root.ids.sm.current == 'scr 2':
            self.root.ids.sm.current = 'scr 1'

        elif self.root.ids.sm.current == 'scr 3'\
                or self.root.ids.sm.current == 'scr 4':

            self.root.ids.sm.current = 'scr 1'

        elif self.root.ids.sm.current == 'blue':
            self.root.ids.sm.current = 'scr 1'

        elif self.root.ids.sm.current == 'scr 1' and platform == 'android':
            mActivity.moveTaskToBack(True)
            self.on_pause()
            self.stop()

    def back_key_handler(self, window, keycode1, keycode2, text, modifiers):
        if keycode1 in [27, 1001]:
            self.handle_screens()
        return True

    def add_mark(self, lat, lon):
        if not self.mark:
            self.mark = ColorMark(lat=lat, lon=lon)
            self.root.mapview.add_widget(self.mark)
        else:
            self.mark.lat = lat
            self.mark.lon = lon

    def start(self, minTime, minDistance):
        if platform == 'android' and self.permit and not self.is_gathering:
            self.is_gathering = True
            self.turn_on_gps('start')
            gps.start(minTime, minDistance)
            self.show_banner()
        elif platform == 'android' and not self.permit:
            self.request_android_permissions()

    def gps_stop(self):
        if platform == 'android':
            gps.stop()

    def open_gps_settings(self, *_):
        self.turn_on_gps('start')

    def is_location_enabled(self, *args):
        if platform != 'android':
            return

        context = cast(
                'android.content.Context',
                mActivity.getApplicationContext())

        locationManager = cast(
                'android.location.LocationManager',
                context.getSystemService(Context.LOCATION_SERVICE))

        return locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER)

    @mainthread
    def turn_on_gps(self, caller=''):
        if platform == 'android':

            if self.is_location_enabled():
                if not caller:
                    android_toast('GPS already on', True)
            else:
                Clock.schedule_once(
                    partial(self.open_animate_dialog, self.dialog), .3)
                Clock.schedule_once(self.safety_check, 15)

    @mainthread
    def enable(self, _):
        gpsIntent = Intent(Settings.ACTION_LOCATION_SOURCE_SETTINGS)
        mActivity.startActivity(gpsIntent)

    def get_datetime(self):
        cal = Calendar.getInstance()
        y, m, d, h, mi = (
            cal.get(Calendar.YEAR),
            cal.get(Calendar.MONTH),
            cal.get(Calendar.DAY_OF_MONTH),
            cal.get(Calendar.HOUR_OF_DAY),
            cal.get(Calendar.MINUTE)
        )
        if h < 10:
            h = f"0{h}"
        if mi < 10:
            mi = f"0{mi}"
        if d < 10:
            d = f"0{d}"
        if m < 10:
            m = f"0{m}"
        now = f"{d}/{m}/{y} {h}:{mi}"
        return now

    def clear_history(self):
        now = self.get_datetime()
        loc = {'loc': [[0, 0]], 'datetime': [now]}

        with open('locations/loc.json', 'w') as f:
            json.dump(loc, f)

        self.loca = [0, 0]
        self.remove_all_items()

    def safety_check(self, *_):
        if not self.is_location_enabled():
            self.saved = False
            self.is_gathering = False
            self.hide_banner()
            Animation.cancel_all(self.root.ids.sl)
            self.root.ids.sl.disabled = False
            self.root.ids.sl.angle == -2
            return

    def save_current_loc(self, *args):

        if not self.is_location_enabled():
            self.saved = False
            self.is_gathering = False
            Animation.cancel_all(self.root.ids.sl)
            self.root.ids.sl.disabled = False
            self.root.ids.sl.angle == -2
            return

        idx = self.accur.index(min(self.accur))
        self.loca = self.lat_lon[idx]
        now = self.get_datetime()
        number_of_locations = 0
        with open('locations/loc.json', 'r+') as f:
            loc = json.load(f)
            loc["datetime"].append(now)
            number_of_locations = len(loc['loc'])
            if number_of_locations < 20:
                loc['loc'].append(self.loca)
            else:
                loc['loc'].pop(0)
                loc['loc'].append(self.loca)

            f.seek(0)
            json.dump(loc, f)

        if number_of_locations >= 20:
            w = self.root.ids.md_list.children[0]
            self.root.ids.md_list.remove_widget(w)
        t_text = f"longitude {self.loca[0]} latitude {self.loca[1]}"
        self.root.ids.md_list.add_widget(
                SwipeToDeleteItem(
                    text="Location",
                    secondary_text=now,
                    tertiary_text=t_text
                    )
            )

        Clock.schedule_once(self.allow_scanning, 2.5)

    def allow_scanning(self, _):
        self.saved = False
        self.accur.clear()
        self.lat_lon.clear()
        Animation.cancel_all(self.root.ids.sl)
        self.root.ids.sl.disabled = False
        self.root.ids.sl.angle == -2

    def show_banner(self):
        self.root.ids.spinner.active = True
        self.root.ids.banner.opacity = 1
        self.root.ids.b_lbl.opacity = 1
        a = Animation(
            y=(
                self.root.height
                - self.root.ids.toolbar.height
                - self.root.ids.banner.height
            ),
            d=.25, t='in_out_back'
            )
        a.start(self.root.ids.banner)

    def hide_banner(self):
        if self.root.ids.banner.y == self.root.height:
            return
        a = Animation(y=self.root.height, d=.5, t='out_back')
        a.bind(on_complete=self.stop_and_save)
        a.start(self.root.ids.banner)

    @mainthread
    def on_location(self, **kwargs):
        loc = []
        if len(self.lat_lon) <= 5:
            for k, v in kwargs.items():
                if k == 'lat' or k == 'lon':
                    loc.append(v)
                elif k == 'accuracy':
                    self.accur.append(v)
                self.lat_lon.append(loc)
        else:
            self.hide_banner()

    def stop_and_save(self, *_):
        self.root.ids.spinner.active = False
        self.is_gathering = False
        self.root.ids.b_lbl.opacity = 0
        self.root.ids.banner.opacity = 0
        self.gps_stop()
        if not self.saved and self.is_location_enabled():
            android_toast("Current location saved", True)
            self.saved = True

            Clock.schedule_once(self.save_current_loc, 0)
            # self.save_current_loc()

    def remove_item(self, instance):
        self.root.ids.md_list.remove_widget(instance)

    def animate_remove_locations(self, *args):
        if args:
            self.root.ids.md_list.remove_widget(args[1])

        if self.root.ids.md_list.children:
            a = Animation(
                x=-self.root.width, opacity=.2, d=.45, t='in_elastic'
                )
            a.bind(on_complete=self.animate_remove_locations)
            a.start(
                self.root.ids.md_list.children[0]
                )
        else:
            self.is_removing = False
        self.root.ids.sv._trigger_update_from_scroll()

    def remove_all_items(self):
        if not self.is_removing:
            self.is_removing = True
            if self.root.ids.md_list.children:
                self.animate_remove_locations()
        # self.root.ids.md_list.clear_widgets()

    @mainthread
    def on_status(self, stype, status):
        self.gps_status = f'type={stype}\n{status}'

    @run_on_ui_thread
    def clear_statusbar(self):

        window = mActivity.getWindow()
        window.setFlags(
            LayoutParams.FLAG_LAYOUT_NO_LIMITS,
            LayoutParams.FLAG_LAYOUT_NO_LIMITS)

    def normal_statusbar(self):
        self.set_decorations()

    @run_on_ui_thread
    def statusbar(self, color_s, color_n):

        window = mActivity.getWindow()
        window.clearFlags(LayoutParams.FLAG_LAYOUT_NO_LIMITS)
        window.clearFlags(LayoutParams.FLAG_TRANSLUCENT_STATUS)
        window.addFlags(LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS)
        window.setStatusBarColor(AColor.parseColor(color_s))
        window.setNavigationBarColor(AColor.parseColor(color_n))
        if self.green:
            window.getDecorView().setSystemUiVisibility(
                LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS |
                View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR |
                View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR)
        else:
            window.getDecorView().setSystemUiVisibility(0)

    @mainthread
    def show_alarm_screen(self, dt):
        self.root.ids.sm.current = 'alarm_screen'
        self.vibrator = AndroidVibrator()
        self.vibrator.vibrate()

    def get_intent(self):
        if platform != 'android':
            return
        intent = mActivity.getIntent()
        start = intent.getBooleanExtra("startAlarm", False)

        if start:
            Clock.schedule_once(self.show_alarm_screen, 2)

    def is_dark_theme_on(self):
        return (
            mActivity.getResources().getConfiguration().uiMode
            & Configuration.UI_MODE_NIGHT_MASK
            ) == Configuration.UI_MODE_NIGHT_YES

    def on_start(self):
        self.dark_on = self.is_dark_theme_on()
        self.set_theme()
        self.create_content_drawer()
        self.create_dialogs()
        self.get_last_location()
        self.create_history()
        self.configure_gps()
        # self.set_decorations()
        self.register_broadcats_receiver()

        Clock.schedule_once(self.animate_colors, 3)
        Clock.schedule_once(self.animate_lower_pos, 3)
        # encreased to 3 seconds because of some older devices
        # need more time for loading
        Clock.schedule_once(self.first_start, 2.25)
        self.get_intent()

    def on_pause(self, *_):
        self.save_theme()
        files = glob.glob('/cache/*.png')
        for f in files:
            try:
                os.remove(f)
            except OSError as e:
                Logger.info('Chache not removed: ' + str(e))
        self.unregister_broadcast_receiver()

        if self.activity_alarm:
            activity.unbind(on_new_intent=self.on_alarm_intent)
            self.activity_alarm = False
        return True

    def on_resume(self):
        self.register_broadcats_receiver()
        self.get_intent()
        Clock.schedule_once(self.get_last_location, .1)

    def on_stop(self, *_):
        try:
            gps.stop()
        except Exception:
            Logger.info('On_pause: %s', exc_info=1)
        files = glob.glob('/cache/*.png')
        for f in files:
            try:
                os.remove(f)
            except OSError as e:
                Logger.info('Chache not removed: ' + str(e))

    def select_intent(self, icon, lon=None, lat=None, mode=None):

        if platform in ('win', 'linux', 'macos', 'linux2') \
                and icon == 'walk':
            url = \
                f"{URL}52.506761,13.2843075,11z"

            webbrowser.open(url)
            return

        elif platform == 'android' and\
            icon != 'palette' and\
                icon != 'set-left-right':
            if icon == 'mail':
                Clock.schedule_once(self.contact_developer, .5)
                return

            elif icon == 'walk':
                self.open_navigation(lon, lat, mode)
                Clock.schedule_once(partial(
                    self.open_navigation, lon, lat, mode), 0.5)
                return True

            elif icon == 'share-variant':
                Clock.schedule_once(self.helper, .5)
                return

            elif icon == 'battery':
                Clock.schedule_once(
                    self.allowe_opt_out_battery_optimazation, .3
                )
                return

        if icon == 'history':
            Clock.schedule_once(partial(self.change_screen, 'scr 3'), .3)
            # self.root.ids.sm.current = 'scr 3'
        elif icon == 'bluetooth':
            Clock.schedule_once(partial(self.change_screen, 'blue'), .3)
            # self.root.ids.sm.current = 'blue'
            return
        elif icon == 'palette':
            Clock.schedule_once(
                partial(self.open_animate_dialog, self.theme_dialog), .3)

        elif icon == 'set-left-right':
            app.anchor = 'right' if app.anchor == 'left' else 'left'

        elif icon == 'car':
            Clock.schedule_once(partial(
                self.open_animate_dialog, self.plate_dialog), .3)
            # self.plate_dialog.open()

    def change_screen(self, screen, _):
        self.root.ids.sm.current = screen

    def animation_dialog_helper(self, dialog):
        a = Animation(_scale_x=0, _scale_y=0, d=.75, t='out_bounce')
        a.bind(on_complete=self.close_dialog)
        a.start(dialog)
        dialog.overlay_color = [0, 0, 0, 0]

    def close_dialog(self, *args):
        args[1].overlay_color = [0, 0, 0, 0]
        args[1].dismiss()

        if args[1].title == "Location permissions" and platform == 'android':
            self.is_first_time = False
            Clock.schedule_once(self.save_theme, 0)
            self.request_android_permissions()

    def open_animate_dialog(self, dialog, _):

        dialog.open()
        a = Animation(_scale_x=1, _scale_y=1, d=.75, t='out_bounce')
        a.bind(on_complete=self.animate_overlay)
        a.start(dialog)

    def animate_overlay(self, *args):
        a = Animation(overlay_color=[0, 0, 0, .7], d=.15)
        # a.bind(on_complete=self.animate_overlay)
        a.start(args[1])

    def doze_opt_out(self):
        if platform != 'android':
            return
        context = mActivity.getApplicationContext()
        powerManager = cast(
            PowerManager, context.getSystemService(Context.POWER_SERVICE)
            )
        return powerManager.isIgnoringBatteryOptimizations(
            mActivity.getPackageName()
            )

    def allowe_opt_out_battery_optimazation(self, *_):
        is_opt_out = self.doze_opt_out()
        if not is_opt_out:
            mActivity.startActivity(
                Intent(
                    Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,
                    Uri.parse("package:"+mActivity.getPackageName())
                    )
                )

    def contact_developer(self, *largs):

        intent = Intent(Intent.ACTION_SENDTO)
        intent.setData(Uri.parse("mailto:"))
        intent.putExtra(Intent.EXTRA_EMAIL, [MAIL])
        intent.putExtra(Intent.EXTRA_SUBJECT, String("Bug report"))
        if intent.resolveActivity(mActivity.getPackageManager()):
            mActivity.startActivity(intent)
        else:
            android_toast('No mail app found!', True)

    @mainthread
    def open_navigation(self, lon, lat, mode, *largs):

        s = f'google.navigation:q={lon},{lat}&mode={mode}'
        intent = Intent(Intent.ACTION_VIEW, Uri.parse(s))
        intent.setPackage("com.google.android.apps.maps")

        if intent.resolveActivity(mActivity.getPackageManager()):
            mActivity.startActivity(intent)
        else:
            android_toast(
                'No google maps found!\nInstall it from Play Store',
                True
                )

    @mainthread
    def helper(self, *_):
        self.share()

    @run_on_ui_thread
    def share(self):
        if self.loca:
            url = f"{URL}{self.loca[0]},{self.loca[1]},10z/"
            sendIntent = Intent()
            sendIntent.setAction(Intent.ACTION_SEND)
            sendIntent.putExtra(Intent.EXTRA_TEXT, String(url))
            sendIntent.setType("text/plain")

            shareIntent = Intent.createChooser(
                sendIntent, String('Share with...')
                )

            mActivity.startActivity(shareIntent)
        else:
            android_toast('No location', True)

    def create_dialogs(self):
        if not self.map_dialog:
            self.map_dialog = MDDialog(
                title='How do you go there?',
                type='confirmation',
                overlay_color=[0, 0, 0, 0],
                _scale_x=0,
                _scale_y=0,
                auto_dismiss=False,
                items=[
                    ItemConfirm(text='Walk', map_type='w'),
                    ItemConfirm(text='Bike', map_type='b'),
                    ItemConfirm(text='Car', map_type='d'),
                ],
                buttons=[
                    Cancel(
                        text='CANCEL'),
                ],
                # size_hint_x=.75
            )
        if not self.dialog:
            self.dialog = MDDialog(
                overlay_color=[0, 0, 0, 0],
                _scale_x=0,
                _scale_y=0,
                auto_dismiss=False,
                text="Turn on gps?",
                size_hint_x=.8,
                buttons=[
                    Accept(
                        text='OK'),
                    Cancel(
                        text='CANCEL'),
                ],
            )
        if not self.theme_dialog:
            self.theme_dialog = MDDialog(
                overlay_color=[0, 0, 0, 0],
                _scale_x=0,
                _scale_y=0,
                auto_dismiss=False,
                title='Choose the color',
                type='confirmation',
                items=[
                    ItemColor(text='Indigo'),
                    ItemColor(text='Blue'),
                    ItemColor(text='Red'),
                    ItemColor(text='Green')
                ],
                buttons=[
                    Cancel(
                        text='CANCEL'),
                ],
            )
        if not self.plate_dialog:
            self.plate_dialog = MDDialog(
                overlay_color=[0, 0, 0, 0],
                _scale_x=0,
                _scale_y=0,
                title="Set the plate",
                type="custom",
                auto_dismiss=False,
                content_cls=PltContent(size_hint_y=None, height=dp(100)),
                buttons=[
                    Cancel(text="CANCEL"),
                    Ok(text="OK")
                ]
            )

        if not self.a_11_background_permit:
            self.a_11_background_permit = MDDialog(
                overlay_color=[0, 0, 0, 0],
                _scale_x=0,
                _scale_y=0,
                title="Automatic location saving",
                type="custom",
                auto_dismiss=False,
                content_cls=WarnDialogContent(),
                buttons=[
                    Ok(text="OK")
                ]
            )
            self.a_11_background_permit.content_cls.txt.text = background_text

        if not self.time_picker:
            self.time_picker = CustomTimePicker(
                auto_dismiss=False,
                opacity=0,
                )

        if not self.time_dialog_warn:
            ok = MDFlatButton(text="OK")
            self.time_dialog_warn = MDDialog(
                overlay_color=[0, 0, 0, 0],
                _scale_x=0,
                _scale_y=0,
                title="Time error",
                type="custom",
                auto_dismiss=False,
                content_cls=ContentTimeError(
                    size_hint_y=None, height=dp(100)
                    ),
                buttons=[ok]
            )
            ok.bind(
                on_release=lambda x: self.animation_dialog_helper(
                    self.time_dialog_warn
                    )
                )

        if not self.automatic_ready_dialog:
            dismiss = MDFlatButton(text="DISMISS")
            yes = MDFlatButton(text="YES")

            self.automatic_ready_dialog = MDDialog(
                overlay_color=[0, 0, 0, 0],
                _scale_x=0,
                _scale_y=0,
                title="Location ready",
                type="custom",
                auto_dismiss=False,
                content_cls=ContentLocationReady(
                    size_hint_y=None, height=dp(100)
                    ),
                buttons=[yes, dismiss]
            )
            dismiss.bind(
                on_release=lambda x: self.animation_dialog_helper(
                    self.automatic_ready_dialog
                    )
                )
            yes.bind(on_release=lambda x: self.open_time_picker())

    def open_time_picker(self, close=True):
        if close:
            self.animation_dialog_helper(self.automatic_ready_dialog)
        Clock.schedule_once(self.animate_time_picker, .3)
        self.time_picker.open()

    def animate_time_picker(self, *_):
        a = Animation(opacity=1, d=.4)
        a.start(self.time_picker)

    def get_time(self, instance, time):
        self.alarm_time = time

    def get_last_location(self, *_):
        with open('locations/loc.json', 'r') as f:
            loc = json.load(f)
        self.loca = loc['loc'][-1]

    def update_theme_color(self, color):

        self.theme_cls.primary_palette = color
        self.mark_img = f'imgs/{color}.png'
        self.car_image = f'imgs/{color}-car.png'
        self.set_decorations()
        self.save_theme()

    def on_anchor(self, *_):
        Clock.schedule_once(self.save_theme, 0)

    def save_theme(self, *_):
        sett = {
                "theme_style": self.theme_cls.theme_style,
                "primary_palette": self.theme_cls.primary_palette,
                "alpha": self.root.alpha,
                "mark": self.mark_img,
                "car": self.car_image,
                "drawer": self.anchor,
                "plate": self.plate,
                "device": self.paired_car,
                "first_run": False
                }
        with open('settings/sett.json', 'w') as f:
            json.dump(sett, f, indent=4)

    def set_theme(self):
        with open('settings/sett.json') as f:
            sett = json.load(f)
        self.theme_cls.theme_style = sett["theme_style"]
        # if not self.dark_on else 'Dark'
        self.theme_cls.primary_palette = sett["primary_palette"]
        self.root.alpha = sett["alpha"]
        self.mark_img = sett["mark"]
        self.car_image = sett["car"]
        self.anchor = sett["drawer"]
        self.plate = sett["plate"]
        self.paired_car = sett["device"]
        self.is_first_time = sett["first_run"]
        app.root.ids.content_drawer.md_bg_color = [1, 1, 1, 1]
        if self.theme_cls.theme_style == 'Dark':
            self.root.ids.r.color = [0, 0, 0, 1]
        else:
            self.root.ids.r.color = [1, 1, 1, 1]

        if self.is_first_time and platform == 'android':
            self.create_explain_dialog()
        if not self.is_first_time:
            self.explain_dialog = None
            if platform == 'android':
                self.request_android_permissions()
        sett = None

    def create_explain_dialog(self):
        self.explain_dialog = MDDialog(
            overlay_color=[0, 0, 0, 0],
            _scale_x=0,
            _scale_y=0,
            title="Location permissions",
            type="custom",
            auto_dismiss=False,
            content_cls=WarnDialogContent(),
            # text=first_warn_text,
            buttons=[
                Ok(text="OK")
            ]
        )
        self.explain_dialog.content_cls.txt.text = first_warn_text

        Clock.schedule_once(
            partial(self.open_animate_dialog, self.explain_dialog), 2)

    def set_decorations(self):
        if platform == "android":
            if self.theme_cls.primary_palette == 'Green':
                self.green = True
            else:
                self.green = False
            color_s = '#'+colors[self.theme_cls.primary_palette]['700']
            color_n = '#'+colors[self.theme_cls.primary_palette]['500']
            self.statusbar(color_s, color_n)

    def configure_gps(self):
        if platform == "android":
            try:
                gps.configure(
                    on_location=self.on_location, on_status=self.on_status)
            except NotImplementedError:
                self.gps_status = 'GPS not available'
                android_toast(self.gps_status, True)

    def create_content_drawer(self):
        icons_item = {
            "mail": "Report the bug",
            "share-variant": "Share your position",
            "history": "Chronology",
            "palette": "Change the color",
            "theme-light-dark": "Change the style",
            "set-left-right": "Drawer to right",
            "car": "Set the plate",
            'battery': 'Allowe exact alarms'
            if not self.doze_opt_out() else 'Exact alarms allowed',
            'bluetooth': self.paired_car if self.paired_car else 'Choose car',
        }
        for icon_name in icons_item:
            item = ItemDrawer(icon=icon_name, text=icons_item[icon_name])
            self.root.ids.content_drawer.ids.md_list.add_widget(
                item
            )

    def create_history(self):
        self.root.ids.md_list.clear_widgets()
        with open('locations/loc.json') as f:
            loc = json.load(f)
        if loc['loc'][0][0] == 0 and loc['loc'][0][1] == 0:
            locations = loc['loc'][1:]
            datetime = list(loc["datetime"])[1:]
        else:
            locations = loc['loc']
            datetime = list(loc["datetime"])

        for idx, i in enumerate(locations):
            self.root.ids.md_list.add_widget(
                SwipeToDeleteItem(
                    text="Location",
                    secondary_text=datetime[idx],
                    tertiary_text=f"longitude {i[0]} latitude {i[1]}"
                    )
            )

    def animate_colors(self, *_):

        if self.w_count == 0:
            w = self.root.ids.first_half
        elif self.w_count == 1:
            w = self.root.ids.second_half
        elif self.w_count == 2:
            w = self.root.ids.t_half
        elif self.w_count == 3:
            w = self.root.ids.f_half
        elif self.w_count == 4:
            w = self.root.ids.ft_half
        elif self.w_count == 5:
            w = self.root.ids.s_half
        elif self.w_count == 6:
            w = self.root.ids.se_half
        elif self.w_count == 7:
            w = self.root.ids.e_half

        a = Animation(color=choice(BUBBLE_COLORS), d=4, t='in_out_bounce')
        a.bind(on_complete=self.animate_colors)
        a.start(w)

        if self.w_count == 7:
            self.w_count = 0
        else:
            self.w_count += 1

    def animate_lower_pos(self, *_):

        if not self.lower_right:
            x = self.root.width - self.root.ids.se_half.width
        else:
            x = self.root.x

        self.lower_right = not self.lower_right

        a = Animation(
            x=x,
            d=8, t='out_bounce')

        a.bind(on_complete=self.animate_upper_pos)
        a.start(self.root.ids.se_half)

    def animate_upper_pos(self, *_):

        if not self.upper_left:
            x = self.root.x
        else:
            x = self.root.width - self.root.ids.e_half.width

        self.upper_left = not self.upper_left

        a = Animation(
            x=x,
            d=8, t='in_bounce')

        a.bind(on_complete=self.animate_lower_pos)
        a.start(self.root.ids.e_half)


if __name__ == '__main__':
    app = CarPos()
    app.run()
