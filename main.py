"""Find my car"""
__author__ = 'Ady Wizard'
from functools import partial
from random import randint
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
from kivymd.toast import toast
from kivy.properties import StringProperty, ListProperty,\
    ObjectProperty, NumericProperty
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.utils import platform
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.clock import mainthread
from plyer import gps
from kivy.garden.mapview import MapMarker
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.animation import Animation


if platform == 'android':
    from jnius import autoclass, cast
    from android.runnable import run_on_ui_thread
    from android import mActivity

    Intent = autoclass('android.content.Intent')
    Uri = autoclass('android.net.Uri')
    Context = autoclass('android.content.Context')
    String = autoclass('java.lang.String')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Color = autoclass("android.graphics.Color")
    LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
    Settings = autoclass('android.provider.Settings')
    LocationManager = autoclass('android.location.LocationManager')
    Calendar = autoclass('java.util.Calendar')
    SimpleDateFormat = autoclass('java.text.SimpleDateFormat')
    View = autoclass('android.view.View')
else:
    import webbrowser

    def run_on_ui_thread(*args):
        return


MAIL = "your.mail@here.com"


KV = """
#: import colors kivymd.color_definitions.colors
#: import Clock kivy.clock.Clock
#: import SE kivy.effects.scroll.ScrollEffect
#: import p kivy.utils.platform
#: import MapView kivy.garden.mapview.MapView
#: import randint random.randint
#: import w kivy.core.window.Window

#: set color_s '#'+colors[app.theme_cls.primary_palette]['700']
#: set color_n '#'+colors[app.theme_cls.primary_palette]['500']
#: set bluish 213/255, 221/255, 232/255, 1


<PltContent>:
    Widget:
        size_hint_y: None
        height: dp(40)
    MDTextField:
        id: txt_field
        pos_hint: {'center_x': .5, 'center_y': .5}

<ColorMark>
    source: app.mark_img

<SwipeToDeleteItem>:
    size_hint_y: None
    height: content.height
    swipe_distance: 100
    max_opened_x: "150dp"
    type_swipe: "hand"

    MDCardSwipeLayerBox:
        padding: "8dp"

        MDIconButton:
            icon: "trash-can"
            pos_hint: {"center_y": .5}
            on_release: app.remove_item(root)

    MDCardSwipeFrontBox:

        ThreeLineListItem:
            id: content
            height: dp(75)
            text: root.text
            secondary_text: root.secondary_text
            tertiary_text: root.tertiary_text
            _no_ripple_effect: True
            on_release: root.set_location(self.tertiary_text)

<Cancel>:
    text_color: app.theme_cls.primary_color
    on_release:
        self.parent.parent.parent.parent.dismiss()

<Accept>:
    text_color: app.theme_cls.primary_color
    on_release:
        self.parent.parent.parent.parent.dismiss()
        Clock.schedule_once(app.enable, .5)

<Ok>
    text_color: app.theme_cls.primary_color
    on_release:
        self.parent.parent.parent.parent.dismiss()
        app.plate = app.plate_dialog.content_cls.ids.txt_field.text

<ItemConfirm>
    on_release:
        theme_text_color: 'Primary'
        root.set_icon(check)
        app.map_dialog.dismiss()
        app.select_intent(\
            'walk', app.loca[0],\
                app.loca[1], self.map_type)

    CheckboxLeftWidget:
        id: check
        group: "check"
        selected_color: app.theme_cls.primary_color
        unselected_color: [1, 1, 1, 1]\
            if app.theme_cls.theme_style == 'Dark'\
                else [0, 0, 0, 1]

<ItemColor>
    on_release:
        theme_text_color: 'Primary'
        root.set_icon(check_c)
        app.theme_dialog.dismiss()
        app.update_theme_color(self.text)


    CheckboxLeftWidget:
        id: check_c
        group: "check"
        theme_text_color: 'Custom'
        selected_color: app.theme_cls.primary_color
        unselected_color: [1, 1, 1, 1]\
            if app.theme_cls.theme_style == 'Dark'\
                else [0, 0, 0, 1]

<ItemDrawer>:
    theme_text_color: "Custom"
    on_release:
        self.parent.set_color_item(icon.icon)
        app.root.ids.nav_drawer.set_state()
        app.select_intent(icon.icon)
        self.set_name()
    text_color: 0, 0, 0, 1

    IconLeftWidget:
        id: icon
        icon: root.icon
        theme_text_color: "Custom"
        text_color: 0, 0, 0, 1

<ContentNavigationDrawer>:
    orientation: "vertical"

    MDFloatLayout:
        size_hint_y: .3
        md_bg_color: app.theme_cls.bg_light

        Image:
            id: avatar
            size_hint: None, None
            size: "56dp", "56dp"
            source: app.car_image
            pos_hint: {'center_x': .15, 'center_y': .5}

        MDLabel:
            text: app.plate
            halign: 'center'
            theme_text_color: 'Custom'
            text_color: app.theme_cls.primary_color
            pos_hint: {'center_x': .5, 'center_y': .5}

    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(6)

        MDLabel:
            text: "Find my car"
            font_style: "Button"
            size_hint_y: None
            height: self.texture_size[1]
            theme_text_color: 'Custom'
            text_color: 0, 0, 0, 1

        ScrollView:
            effect_cls: SE
            DrawerList:
                id: md_list

<RootWidget>:
    mapview: mapview

    NavigationLayout:
        ScreenManager:
            id: sm
            Screen:
                canvas.before:
                    Color:
                        rgba: app.theme_cls.primary_color
                    SmoothLine:
                        close: True
                        circle:
                            (root.wx1, root.wy1, root.r1/2, 0, 360)
                    SmoothLine:
                        close: True
                        circle:
                            (root.wx2, root.wy2, root.r2/2, 0, 360)
                    SmoothLine:
                        close: True
                        circle:
                            (root.wx3, root.wy3, root.r3/2, 0, 360)
                    SmoothLine:
                        close: True
                        circle:
                            (root.wx4, root.wy4, root.r4/2, 0, 360)
                    SmoothLine:
                        close: True
                        circle:
                            (root.wx5, root.wy5, root.r5/2, 0, 360)
                    SmoothLine:
                        close: True
                        circle:
                            (root.wx6, root.wy6, root.r6/2, 0, 360)
                    SmoothLine:
                        close: True
                        circle:
                            (root.wx7, root.wy7, root.r7/2, 0, 360)
                    SmoothLine:
                        close: True
                        circle:
                            (root.wx8, root.wy8, root.r8/2, 0, 360)
                    SmoothLine:
                        close: True
                        circle:
                            (root.wx9, root.wy9, root.r9/2, 0, 360)
                    SmoothLine:
                        close: True
                        circle:
                            (root.wx10, root.wy10, root.r10/2, 0, 360)
                    SmoothLine:
                        close: True
                        circle:
                            (root.wx11, root.wy11, root.r11/2, 0, 360)
                    SmoothLine:
                        close: True
                        circle:
                            (root.wx12, root.wy12, root.r12/2, 0, 360)
                    SmoothLine:
                        close: True
                        circle:
                            (root.wx13, root.wy13, root.r13/2, 0, 360)
                    SmoothLine:
                        close: True
                        circle:
                            (root.wx14, root.wy14, root.r14/2, 0, 360)
                name: 'scr 1'

                BoxLayout:
                    orientation: 'vertical'

                    MDToolbar:
                        id: toolbar
                        title: 'Find my car'
                        elevation: 10
                        left_action_items:
                            [['menu', lambda x: nav_drawer.set_state()]]

                    MDFloatLayout:

                        MDFillRoundFlatIconButton:
                            icon: 'location-enter'
                            text: 'TURN ON GPS'
                            theme_text_color: 'Custom'
                            text_color: toolbar.specific_text_color
                            md_bg_color: app.theme_cls.primary_color[:3]\
                                + root.alpha
                            pos_hint: {'center_x': .5, 'center_y': .65}
                            on_release:
                                # sm.current = 'scr 4'
                                app.turn_on_gps()

                        MDFillRoundFlatIconButton:
                            icon: 'map-marker-plus'
                            text: 'SAVE THE LOCATION'
                            theme_text_color: 'Custom'
                            text_color: toolbar.specific_text_color
                            md_bg_color: app.theme_cls.primary_color[:3]\
                                + root.alpha
                            pos_hint: {'center_x': .5, 'center_y': .55}
                            on_release:
                                app.accur.clear()
                                app.lat_lon.clear()
                                app.saved = False
                                app.start(1000, 0)

                        MDFillRoundFlatIconButton:
                            icon: 'map-search-outline'
                            text: 'FIND MY CAR'
                            theme_text_color: 'Custom'
                            text_color: toolbar.specific_text_color
                            md_bg_color: app.theme_cls.primary_color[:3]\
                                + root.alpha
                            pos_hint: {'center_x': .5, 'center_y': .45}
                            on_release:
                                app.add_mark(app.loca[0], app.loca[1])\
                                    if app.loca else None
                                sm.transition.direction = 'up' if app.loca\
                                    else 'down'
                                sm.current = 'scr 2' if app.loca else 'scr 1'

                        MDFillRoundFlatIconButton:
                            icon: 'map-marker-remove-outline'
                            text: 'GO TO CRONOLOGY'
                            theme_text_color: 'Custom'
                            text_color: toolbar.specific_text_color
                            md_bg_color: app.theme_cls.primary_color[:3]\
                                + root.alpha
                            pos_hint: {'center_x': .5, 'center_y': .35}
                            on_release:
                                sm.current = 'scr 3'

                        MDLabel:
                            id: lbl
                            pos_hint: {'center_x': .5, 'center_y': .2}
                            halign: 'center'

            Screen:
                name: 'scr 2'
                on_enter: mapview.center_on(\
                                    app.loca[0], app.loca[1])\
                                        if app.loca else None
                id: scr2
                zoom_on: 16
                RelativeLayout:
                    MapView:
                        id: mapview
                        zoom: 19

                    MDToolbar:
                        pos_hint: {'top': 1}
                        id: tb
                        elevation: 0
                        title: "Car's position"
                        left_action_items:
                            [['menu', lambda x: nav_drawer.set_state()]]
                        right_action_items:
                            [['target',\
                                lambda x: mapview.center_on(\
                                    app.loca[0], app.loca[1])]]

                    MDFloatLayout:
                        size_hint_y: .2

                        MDFloatingActionButton:
                            id: i
                            md_bg_color: app.theme_cls.primary_color
                            icon: 'navigation'
                            elevation_normal: 10
                            text_color: tb.specific_text_color
                            pos_hint: {'center_x': .5, 'center_y': .5}
                            on_release:
                                app.map_dialog.open()

            Screen:
                name: 'scr 3'

                MDBoxLayout:
                    orientation: 'vertical'
                    MDToolbar:
                        title: 'Cronology'
                        elevation: 10
                        left_action_items:
                            [['menu', lambda x: nav_drawer.set_state()]]
                        right_action_items:
                            [['reload', lambda x: app.clear_history()]]

                    ScrollView:
                        effect_cls: SE
                        smooth_scroll_end: 120

                        MDList:
                            id: md_list
                            padding: [0, dp(6), 0, 0]
                            spacing: dp(6)

        MDNavigationDrawer:
            id: nav_drawer
            anchor: app.anchor
            elevation: 1
            md_bg_color: 1, 1, 1, 1

            ContentNavigationDrawer:
                id: content_drawer
"""


class PltContent(MDFloatLayout):
    pass


class ItemSettings(MDFloatLayout):
    icon = StringProperty()
    text_color = StringProperty('Primary')
    color = ListProperty([1, 1, 1, 1])
    text = StringProperty()


class SettingsScreen(Screen):
    def jump(self):
        app.root.ids.sm.transition.direction = 'up'
        app.root.ids.sm.current = 'scr 1'


class ColorMark(MapMarker):
    pass


class RootWidget(Screen):

    mapview = ObjectProperty()
    alpha = ListProperty([1])
    wx1 = NumericProperty(randint(10, Window.width))
    wy1 = NumericProperty(randint(10, Window.height))
    wx2 = NumericProperty(randint(10, Window.width))
    wy2 = NumericProperty(randint(10, Window.height))
    wx3 = NumericProperty(randint(10, Window.width))
    wy3 = NumericProperty(randint(10, Window.height))
    wx4 = NumericProperty(randint(10, Window.width))
    wy4 = NumericProperty(randint(10, Window.height))
    wx5 = NumericProperty(randint(10, Window.width))
    wy5 = NumericProperty(randint(10, Window.height))
    wx6 = NumericProperty(randint(10, Window.width))
    wy6 = NumericProperty(randint(10, Window.height))
    wx7 = NumericProperty(randint(10, Window.width))
    wy7 = NumericProperty(randint(10, Window.height))
    wx8 = NumericProperty(randint(10, Window.width))
    wy8 = NumericProperty(randint(10, Window.height))
    wx9 = NumericProperty(randint(10, Window.width))
    wy9 = NumericProperty(randint(10, Window.height))
    wx10 = NumericProperty(randint(10, Window.width))
    wy10 = NumericProperty(randint(10, Window.height))
    wx11 = NumericProperty(randint(10, Window.width))
    wy11 = NumericProperty(randint(10, Window.height))
    wx12 = NumericProperty(randint(10, Window.width))
    wy12 = NumericProperty(randint(10, Window.height))
    wx13 = NumericProperty(randint(10, Window.width))
    wy13 = NumericProperty(randint(10, Window.height))
    wx14 = NumericProperty(randint(10, Window.width))
    wy14 = NumericProperty(randint(10, Window.height))
    r1 = NumericProperty(randint(10, Window.height//6))
    r2 = NumericProperty(randint(10, Window.height//6))
    r3 = NumericProperty(randint(10, Window.height//6))
    r4 = NumericProperty(randint(10, Window.height//6))
    r5 = NumericProperty(randint(10, Window.height//6))
    r6 = NumericProperty(randint(10, Window.height//6))
    r7 = NumericProperty(randint(10, Window.height//6))
    r8 = NumericProperty(randint(10, Window.height//6))
    r9 = NumericProperty(randint(10, Window.height//6))
    r10 = NumericProperty(randint(10, Window.height//6))
    r11 = NumericProperty(randint(10, Window.height//6))
    r12 = NumericProperty(randint(10, Window.height//6))
    r13 = NumericProperty(randint(10, Window.height//6))
    r14 = NumericProperty(randint(10, Window.height//6))


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
        app.root.ids.sm.transition.direction = 'up'
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
            elif app.theme_cls.theme_style == 'Light':
                app.root.alpha = [1]
                app.theme_cls.theme_style = 'Dark'
                app.root.ids.content_drawer.md_bg_color = [1, 1, 1, 1]
            app.save_theme()


class CarPos(MDApp):

    gps_location = StringProperty()
    gps_status = StringProperty()
    loca = ListProperty()
    permit = False
    dialog = None
    mark = None
    map_dialog = None
    plate_dialog = None
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
    plate = StringProperty()
    green = False

    def request_android_permissions(self):

        from android.permissions import request_permissions, Permission

        def callback(permissions, results):

            if all([res for res in results]):
                # toast("All permitions granted.")
                self.permit = True
            else:
                toast("Permessions denied")
                self.permit = False
                toast("This app can't work without GPS")

        request_permissions([Permission.ACCESS_COARSE_LOCATION,
                             Permission.ACCESS_FINE_LOCATION], callback)

    def build(self):
        Window.bind(on_keyboard=self.back_key_handler)
        if platform == "android":
            self.request_android_permissions()
        Builder.load_string(KV)
        self.root = RootWidget()

    def handle_screens(self):

        if self.root.ids.sm.current == 'scr 2':
            self.root.ids.sm.current = 'scr 1'

        elif self.root.ids.sm.current == 'scr 3'\
                or self.root.ids.sm.current == 'scr 4':

            self.root.ids.sm.current = 'scr 1'

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
        if platform == 'android' and self.permit:
            self.turn_on_gps('start')
            gps.start(minTime, minDistance)
        elif platform == 'android' and not self.permit:
            self.request_android_permissions()

    def stop(self):
        if platform == 'android':
            gps.stop()

    def open_gps_settings(self, *_):
        self.turn_on_gps('start')

    @mainthread
    def turn_on_gps(self, caller=''):
        if platform == 'android':
            context = cast(
                'android.content.Context',
                mActivity.getApplicationContext())
            locationManager = cast(
                'android.location.LocationManager',
                context.getSystemService(Context.LOCATION_SERVICE))
            if locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER):
                if not caller:
                    toast('GPS on', 3)
            else:
                self.dialog.open()

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

    def save_current_loc(self):
        idx = self.accur.index(min(self.accur))
        self.loca = self.lat_lon[idx]
        now = self.get_datetime()
        with open('locations/loc.json', 'r+') as f:
            loc = json.load(f)
            loc["datetime"].append(now)

            if len(loc['loc']) < 20:
                loc['loc'].append(self.loca)
            else:
                loc['loc'].pop(0)
                loc['loc'].append(self.loca)

            f.seek(0)
            json.dump(loc, f)
        self.create_history()
        # Logger.info('accuracy: ' + str(self.accur))
        # Logger.info('current location: ' + str(self.loca))
        # Logger.info('all location values: ' + str(self.lat_lon))
        # Logger.info('saved location: ' + str(loc))

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
            self.stop()
            if not self.saved:
                toast("Current location saved")
                self.saved = True
                self.save_current_loc()

    def remove_item(self, instance):
        self.root.ids.md_list.remove_widget(instance)

    def remove_all_items(self):
        self.root.ids.md_list.clear_widgets()

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
        window.setStatusBarColor(Color.parseColor(color_s))
        window.setNavigationBarColor(Color.parseColor(color_n))
        if self.green:
            window.getDecorView().setSystemUiVisibility(
                LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS |
                View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR |
                View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR)
        else:
            window.getDecorView().setSystemUiVisibility(0)

    def on_start(self):
        self.w = self.root.width
        self.h = self.root.height
        self.set_theme()
        self.set_decorations()

        if platform == 'android':
            mActivity.removeLoadingScreen()

        self.create_content_drawer()
        self.create_dialogs()
        self.get_last_location()
        self.create_history()
        self.configure_gps()
        self.size_animation_one()

    def on_pause(self):
        try:
            gps.stop()
        except Exception:
            Logger.info('On_pause: %s', exc_info=1)
        Animation.cancel_all(self.root)
        files = glob.glob('/cache/*.png')
        for f in files:
            try:
                os.remove(f)
            except OSError as e:
                Logger.info('Chache not removed: ' + str(e))
        return True

    def on_resume(self):
        self.get_last_location()
        # Clock.schedule_once(self.open_gps_settings, 1)
        self.size_animation_one()

    def on_stop(self):
        files = glob.glob('/cache/*.png')
        for f in files:
            try:
                os.remove(f)
            except OSError as e:
                Logger.info('Chache not removed: ' + str(e))
        Animation.cancel_all(self.root)
        return True

    def select_intent(self, icon, lon=None, lat=None, mode=None):

        if platform in ('win', 'linux', 'macos') and icon == 'navigation':
            url = \
                f"https://www.google.com/maps/search/@{lon},{lat},21z/"

            webbrowser.open(url)

        elif platform == 'android' and\
            icon != 'palette' and\
                icon != 'set-left-right':

            if icon == 'mail':
                Clock.schedule_once(self.contact_developer, .5)
            elif icon == 'walk':
                self.open_navigation(lon, lat, mode)
                Clock.schedule_once(partial(
                    self.open_navigation, lon, lat, mode), 0.5)
                return True
            elif icon == 'share-variant':
                Clock.schedule_once(self.helper, .5)
        if icon == 'history':
            self.root.ids.sm.current = 'scr 3'
        elif icon == 'palette':
            Clock.schedule_once(self.theme_color_cahnge, .3)
            # self.theme_dialog.open()
        elif icon == 'set-left-right':
            app.anchor = 'right' if app.anchor == 'left' else 'left'

        elif icon == 'car':
            self.plate_dialog.open()

    def theme_color_cahnge(self, *_):
        self.theme_dialog.open()

    def contact_developer(self, *largs):

        intent = Intent(Intent.ACTION_SENDTO)
        intent.setData(Uri.parse("mailto:"))
        intent.putExtra(Intent.EXTRA_EMAIL, [MAIL])
        intent.putExtra(Intent.EXTRA_SUBJECT, String("Bug report"))
        if intent.resolveActivity(mActivity.getPackageManager()):
            mActivity.startActivity(intent)
        else:
            toast('No mail app found!', 3)

    @mainthread
    def open_navigation(self, lon, lat, mode, *largs):

        s = f'google.navigation:q={lon},{lat}&mode={mode}'
        intent = Intent(Intent.ACTION_VIEW, Uri.parse(s))
        intent.setPackage("com.google.android.apps.maps")

        if intent.resolveActivity(mActivity.getPackageManager()):
            mActivity.startActivity(intent)
        else:
            toast('No google maps found!\nInstall it from Play Store', 3)

    @mainthread
    def helper(self, *_):
        self.share()

    @run_on_ui_thread
    def share(self):
        if self.loca:
            url = f"https://www.google.com/maps/search/@{self.loca[0]},{self.loca[1]},10z/"
            sendIntent = Intent()
            sendIntent.setAction(Intent.ACTION_SEND)
            sendIntent.putExtra(Intent.EXTRA_TEXT, String(url))
            sendIntent.setType("text/plain")
            shareIntent = Intent.createChooser(sendIntent, String('Share...'))
            mActivity.startActivity(shareIntent)
        else:
            toast('No location')

    def size_animation_one(self, *_):
        self.anim_size = Animation(
            wx1=randint(0, int(self.w)), wy1=randint(0, int(self.h)),
            r1=randint(10, Window.height//6), d=5, t='in_bounce')
        self.anim_size.bind(on_complete=self.size_animation_two)
        self.anim_size.start(self.root)

    def size_animation_two(self, ani, wid):
        self.anim_size = Animation(
            wx2=randint(0, int(self.w)), wy2=randint(0, int(self.h)),
            r2=randint(10, Window.height//6), d=5, t='in_bounce')
        self.anim_size.bind(on_complete=self.size_animation_three)
        self.anim_size.start(self.root)

    def size_animation_three(self, ani, wid):
        self.anim_size = Animation(
            wx3=randint(0, int(self.w)), wy3=randint(0, int(self.h)),
            r3=randint(10, Window.height//6), d=5, t='in_bounce')
        self.anim_size.bind(on_complete=self.size_animation_four)
        self.anim_size.start(self.root)

    def size_animation_four(self, ani, wid):
        self.anim_size = Animation(
            wx4=randint(0, int(self.w)), wy4=randint(0, int(self.h)),
            r4=randint(10, Window.height//6), d=5, t='in_bounce')
        self.anim_size.bind(on_complete=self.size_animation_five)
        self.anim_size.start(self.root)

    def size_animation_five(self, ani, wid):
        self.anim_size = Animation(
            wx5=randint(0, int(self.w)), wy5=randint(0, int(self.h)),
            r5=randint(10, Window.height//6), d=5, t='in_bounce')
        self.anim_size.bind(on_complete=self.size_animation_six)
        self.anim_size.start(self.root)

    def size_animation_six(self, ani, wid):
        self.anim_size = Animation(
            wx6=randint(0, int(self.w)), wy6=randint(0, int(self.h)),
            r6=randint(10, Window.height//6), d=5, t='in_bounce')
        self.anim_size.bind(on_complete=self.size_animation_seven)
        self.anim_size.start(self.root)

    def size_animation_seven(self, ani, wid):
        self.anim_size = Animation(
            wx7=randint(0, int(self.w)), wy7=randint(0, int(self.h)),
            r7=randint(10, Window.height//6), d=5, t='in_bounce')
        self.anim_size.bind(on_complete=self.size_animation_eight)
        self.anim_size.start(self.root)

    def size_animation_eight(self, ani, wid):
        self.anim_size = Animation(
            wx8=randint(0, int(self.w)), wy8=randint(0, int(self.h)),
            r8=randint(10, Window.height//6), d=5, t='in_bounce')
        self.anim_size.bind(on_complete=self.size_animation_nine)
        self.anim_size.start(self.root)

    def size_animation_nine(self, ani, wid):
        self.anim_size = Animation(
            wx9=randint(0, int(self.w)), wy9=randint(0, int(self.h)),
            r9=randint(10, Window.height//6), d=5, t='in_bounce')
        self.anim_size.bind(on_complete=self.size_animation_ten)
        self.anim_size.start(self.root)

    def size_animation_ten(self, ani, wid):
        self.anim_size = Animation(
            wx10=randint(0, int(self.w)), wy10=randint(0, int(self.h)),
            r10=randint(10, Window.height//6), d=5, t='in_bounce')
        self.anim_size.bind(on_complete=self.size_animation_eleven)
        self.anim_size.start(self.root)

    def size_animation_eleven(self, ani, wid):
        self.anim_size = Animation(
            wx11=randint(0, int(self.w)), wy11=randint(0, int(self.h)),
            r11=randint(10, Window.height//6), d=5, t='in_bounce')
        self.anim_size.bind(on_complete=self.size_animation_twelve)
        self.anim_size.start(self.root)

    def size_animation_twelve(self, ani, wid):
        self.anim_size = Animation(
            wx12=randint(0, int(self.w)), wy12=randint(0, int(self.h)),
            r12=randint(10, Window.height//6), d=5, t='in_bounce')
        self.anim_size.bind(on_complete=self.size_animation_thirteen)
        self.anim_size.start(self.root)

    def size_animation_thirteen(self, ani, wid):
        self.anim_size = Animation(
            wx13=randint(0, int(self.w)), wy13=randint(0, int(self.h)),
            r13=randint(10, Window.height//6), d=5, t='in_bounce')
        self.anim_size.bind(on_complete=self.size_animation_fourteen)
        self.anim_size.start(self.root)

    def size_animation_fourteen(self, ani, wid):
        self.anim_size = Animation(
            wx14=randint(0, int(self.w)), wy14=randint(0, int(self.h)),
            r14=randint(10, Window.height//6), d=5, t='in_bounce')
        self.anim_size.bind(on_complete=self.size_animation_one)
        self.anim_size.start(self.root)

    def color_animation_back(self, *_):
        self.anim_color = Animation(color=[.5, .5, .5, .5], d=3)
        self.anim_color.bind(on_complete=self.color_animation)
        self.anim_color.start(self.root)

    def create_dialogs(self):
        if not self.map_dialog:
            self.map_dialog = MDDialog(
                title='How do you go there?',
                type='confirmation',
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
                # size_hint_x=.75
            )
        if not self.plate_dialog:
            self.plate_dialog = MDDialog(
                title="Set the plate",
                type="custom",
                content_cls=PltContent(),
                buttons=[
                    Cancel(text="CANCEL"),
                    Ok(text="OK")
                ]
            )

    def get_last_location(self):
        with open('locations/loc.json', 'r+') as f:
            loc = json.load(f)
        self.loca = loc['loc'][-1]

    def update_theme_color(self, color):

        self.theme_cls.primary_palette = color
        self.mark_img = f'imgs/{color}.png'
        self.car_image = f'imgs/{color}-car.png'
        self.set_decorations()
        self.save_theme()

    def on_anchor(self, *_):
        Clock.schedule_once(self.save_theme, .5)

    def save_theme(self, *_):
        sett = {
                "theme_style": app.theme_cls.theme_style,
                "primary_palette": app.theme_cls.primary_palette,
                "alpha": self.root.alpha,
                "mark": self.mark_img,
                "car": self.car_image,
                "drawer": self.anchor,
                "plate": self.plate
                }
        with open('settings/sett.json', 'w') as f:
            json.dump(sett, f, indent=4)

    def set_theme(self):
        with open('settings/sett.json') as f:
            sett = json.load(f)
            self.theme_cls.theme_style = sett["theme_style"]
            self.theme_cls.primary_palette = sett["primary_palette"]
            self.root.alpha = sett["alpha"]
            self.mark_img = sett["mark"]
            self.car_image = sett["car"]
            self.anchor = sett["drawer"]
            self.plate = sett["plate"]
            app.root.ids.content_drawer.md_bg_color = [1, 1, 1, 1]

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
                toast(self.gps_status, 3)

    def create_content_drawer(self):
        icons_item = {
            "mail": "Report the bug",
            "share-variant": "Share your position",
            "history": "Cronology",
            "palette": "Change the color",
            "theme-light-dark": "Change the style",
            "set-left-right": "Drawer to right",
            "car": "Set the plate"
        }
        for icon_name in icons_item:
            self.root.ids.content_drawer.ids.md_list.add_widget(
                ItemDrawer(icon=icon_name, text=icons_item[icon_name])
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
        # Logger.info(f'Creating
        # history Locations are: {locations} datetime is {datetime}')
        for idx, i in enumerate(locations):
            self.root.ids.md_list.add_widget(
                SwipeToDeleteItem(
                    text="Location",
                    secondary_text=datetime[idx],
                    tertiary_text=f"longitude {i[0]} latitude {i[1]}"
                    )
            )


if __name__ == '__main__':
    app = CarPos()
    app.run()
