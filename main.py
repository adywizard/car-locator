"""Find my car"""
__author__ = 'Ady Wizard'
from functools import partial
from random import choice
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
# from kivymd.toast import toast
from kivy.properties import StringProperty, ListProperty,\
    ObjectProperty, NumericProperty, ColorProperty

from kivy.uix.screenmanager import (
    Screen, SlideTransition,
    FallOutTransition, RiseInTransition
    )

from kivy.lang import Builder
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


BUBBLE_COLORS = [
    [214/255, 131/255, 54/255, 1],
    [56/255, 126/255, 217/255, 1],
    [119/255, 93/255, 186/255, 1],
    [207/255, 64/255, 142/255, 1],
    [83/255, 194/255, 111/255, 1],
    [235/255, 217/255, 138/255, 1],
    [131/255, 138/255, 242/255, 1],
    [182/255, 40/255, 247/255, 1],
    [79/255, 247/255, 180/255, 1],
    [176255, 181/255, 80/255, 1],
    [67/255, 57/255, 145/255, 1]
    ]

URL = "https://www.google.com/maps/search/@"

if platform == 'android':
    from jnius import autoclass, cast
    from android.runnable import run_on_ui_thread
    from android import activity
    from android_toast.toast import android_toast

    from blue.blue import BroadcastReceiver
    from android_notification.notification import notify

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
else:
    import webbrowser

    def run_on_ui_thread(*args):
        return


MAIL = "developer.mail@here.com"


header = '''
$HEADER$
uniform vec2 resolution;
uniform float time;
uniform vec2 mouse;
'''


shader_watter_bubble = header + '''
void main(void)
{
    vec2 halfres = resolution.xy / 2.0;
    vec2 cpos = vec4(frag_modelview_mat * gl_FragCoord).xy;

    vec2 sinres = vec2(tan(resolution.x * time), -sin(resolution * time));

    cpos.x -= 0.5 * halfres.x * sin(time/2.0) + \
        0.3 * halfres.x * cos(time) + halfres.x;

    cpos.y -= 0.5 * halfres.y * sin(time/5.0) + \
        0.3 * halfres.y * sin(time) + halfres.y;

    float cLength = length(cpos);

    vec2 uv = \
        tex_coord0 + (cpos / cLength) * \
            sin(cLength / 50.0 - time * 2.0) / 15.0;

    vec3 col = texture2D(texture0, uv).xyz;
    gl_FragColor = vec4(col, 1.0);
}
'''


KV = """
#: import colors kivymd.color_definitions.colors
#: import Clock kivy.clock.Clock
#: import p kivy.utils.platform
#: import SE kivy.effects.scroll.ScrollEffect
#: import MapView kivy_garden.mapview.MapView
#: import w kivy.core.window.Window
#: import BlueDevicesScreen blue_devices_screen.devices.BlueDevicesScreen


<SemiCircle>
    canvas.before:

        Color:
            rgba: self.color

        Ellipse:
            angle_start: self.angle_start
            angle_end: self.angle_end
            size: self.size
            pos: self.pos


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
        # app.close_dialog(self.parent.parent.parent.parent)
        self.parent.parent.parent.parent.dismiss()
        app.hide_banner()

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
        app.theme_dialog_helper()
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

    MDNavigationLayout:
        ScreenManager:
            id: sm
            MDScreen:
                md_bg_color: 0, 0, 0, 1
            Screen:
                name: 'scr 1'
                id: scr1

                ShaderWidget:
                    id: shader_widget
                    size_hint: 1, 1

                    LayoutWidget
                        id: r
                        size_hint: 1, 1
                        canvas.before:
                            Color:
                                rgba: self.color
                            Rectangle:
                                size: self.size
                                pos: self.pos
                            PushMatrix
                            Scale:
                                x: self.x_scale
                                y: self.y_scale
                                z: self.z_scale
                            Rotate:
                                angle: self.angle
                                origin: self.center
                        canvas.after:
                            PopMatrix

                        SemiCircle
                            id: se_half
                            color: app.theme_cls.primary_color
                            angle_start: 0
                            angle_end: 360
                            center: root.x + dp(25), root.y + dp(25),
                            size_hint: None, None
                            size: dp(250), dp(250)

                        SemiCircle
                            id: e_half
                            color: app.theme_cls.primary_color
                            angle_start: 0
                            angle_end: 360

                            center: root.width - dp(100), \
                                root.height - dp(150)

                            size_hint: None, None
                            size: dp(250), dp(250)

                        SemiCircle
                            id: s_half
                            color: app.theme_cls.primary_color
                            angle_start: 0
                            angle_end: 360

                            center:
                                root.center_x - dp(200), \
                                    root.center_y - dp(100)

                            size_hint: None, None
                            size: dp(100), dp(100)

                        SemiCircle
                            id: ft_half
                            color: app.theme_cls.primary_dark
                            angle_start: 0
                            angle_end: 360

                            center: root.center_x - dp(200), \
                                root.center_y + dp(250)

                            size_hint: None, None
                            size: dp(100), dp(100)

                        SemiCircle
                            id: f_half
                            color: app.theme_cls.primary_light
                            angle_start: 0
                            angle_end: 360

                            center: root.center_x + dp(150), \
                                root.center_y - dp(250)

                            size_hint: None, None
                            size: dp(50), dp(50)

                        SemiCircle
                            id: t_half
                            color: app.theme_cls.primary_color
                            angle_start: 0
                            angle_end: 360

                            center: root.center_x + dp(200), \
                                root.center_y + dp(200)

                            size_hint: None, None
                            size: dp(50), dp(50)

                        SemiCircle
                            id: first_half
                            color: app.theme_cls.primary_dark
                            angle_start: 0
                            angle_end: 360
                            center: root.center_x, root.center_y - dp(150)
                            size_hint: None, None
                            size: dp(150), dp(150)

                        SemiCircle
                            id: second_half
                            color: app.theme_cls.primary_light
                            angle_start: 0
                            angle_end: 360
                            center: root.center_x, root.center_y + dp(150)
                            size_hint: None, None
                            size: dp(100), dp(100)

                MDFloatLayout:
                    id: banner
                    opacity: 0
                    size_hint_y: None
                    height: dp(64)
                    pos: scr1.x, scr1.height
                    md_bg_color: 1, 1, 1, 1
                    Label:
                        id: b_lbl
                        color: 0, 0, 0, 1
                        text: 'Fetching current coordinates'
                        pos_hint: {'center_x':.4, 'center_y':.5}
                        halign: 'center'
                        opacity: 0
                    MDSpinner:
                        id: spinner
                        size_hint: None, None
                        size: dp(32), dp(32)
                        pos_hint: {'center_x':.85, 'center_y':.5}
                        active: False


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
                                    if p in ('windows', 'linux', 'macos')\
                                        else app.add_mark(\
                                            52.506761, 13.2843075)
                                
                                sm.current = 'scr 2'

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

            BlueDevicesScreen:
                name: 'blue'
                id: blue

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

    w_count = 0
    upper_left = False
    lower_right = False

    transition = None

    br = None

    paired_car = ""
    is_car_paired = False

    def on_new_intent(self, intent):
        get_location = intent.getStringExtra("getLocation")
        if get_location == "true":
            self.stop_service()

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
                self.start_service(name)
                notify(
                    context,
                    'CAR LOCATOR',
                    'Car paired, will listen for diconnection',
                    'Location service',
                    'Car locator',
                    'Car locator service',
                    )

    def unregister_broadcast_receiver(self):
        if self.br and platform == 'android':
            self.br.stop()
            self.br = None

    @mainthread
    def stop_service(self):
        mActivity.stop_service()
        activity.unbind(on_new_intent=self.on_new_intent)
        self.start(1000, 0)

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

        self.root.ids.sm.transition = FallOutTransition() \
            if self.theme_cls.theme_style == 'Dark' else RiseInTransition()

        self.set_decorations()
        self.root.ids.sm.current = 'scr 1'

        self.root.ids.sm.transition = SlideTransition()
        self.root.ids.sm.transition.direction = 'up'

    def request_android_permissions(self):

        from android.permissions import request_permissions, Permission

        def callback(permissions, results):

            if all([res for res in results]):

                self.permit = True
            else:
                android_toast("Permessions denied", True)
                self.permit = False
                android_toast("This app can't work without GPS", True)

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

        elif self.root.ids.sm.current == 'blue':
            self.root.ids.sm.current = 'scr 1'

        elif self.root.ids.sm.current == 'scr 1':
            mActivity.moveTaskToBack(True)

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
            self.show_banner()
        elif platform == 'android' and not self.permit:
            self.request_android_permissions()

    def stop(self):
        if platform == 'android':
            gps.stop()

    def open_gps_settings(self, *_):
        self.turn_on_gps('start')

    def is_location_enabled(self):
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

    def save_current_loc(self, *_):

        if not self.is_location_enabled():
            self.saved = False
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
        Clock.schedule_once(self.allowe_scanning, 2.5)

    def allowe_scanning(self, _):
        self.saved = False

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
        self.root.ids.b_lbl.opacity = 0
        self.root.ids.banner.opacity = 0
        self.stop()
        if not self.saved and self.is_location_enabled():
            android_toast("Current location saved", True)
            self.saved = True

            Clock.schedule_once(self.save_current_loc, 0)
            # self.save_current_loc()

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
        window.setStatusBarColor(AColor.parseColor(color_s))
        window.setNavigationBarColor(AColor.parseColor(color_n))
        if self.green:
            window.getDecorView().setSystemUiVisibility(
                LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS |
                View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR |
                View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR)
        else:
            window.getDecorView().setSystemUiVisibility(0)

    def on_start(self):
        self.set_theme()
        self.create_content_drawer()
        self.create_dialogs()
        self.get_last_location()
        self.create_history()
        self.configure_gps()

        self.register_broadcats_receiver()

        Clock.schedule_once(self.animate_colors, 3)
        Clock.schedule_once(self.animate_lower_pos, 3)
        # encreased to 3 seconds because of some older devices
        # need more time for loading
        Clock.schedule_once(self.first_start, 2.5)

    def on_pause(self, *_):

        files = glob.glob('/cache/*.png')
        for f in files:
            try:
                os.remove(f)
            except OSError as e:
                Logger.info('Chache not removed: ' + str(e))
        self.unregister_broadcast_receiver()
        return True

    def on_resume(self):
        self.get_last_location()
        self.register_broadcats_receiver()

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

        if icon == 'history':
            Clock.schedule_once(partial(self.change_screen, 'scr 3'), .25)
            # self.root.ids.sm.current = 'scr 3'
        elif icon == 'bluetooth':
            Clock.schedule_once(partial(self.change_screen, 'blue'), .25)
            # self.root.ids.sm.current = 'blue'
            return
        elif icon == 'palette':
            Clock.schedule_once(self.theme_color_cahnge, .3)
            # self.theme_dialog.open()
        elif icon == 'set-left-right':
            app.anchor = 'right' if app.anchor == 'left' else 'left'

        elif icon == 'car':
            self.plate_dialog.open()

    def change_screen(self, screen, _):
        self.root.ids.sm.current = screen

    def theme_dialog_helper(self):
        a = Animation(_scale_x=0, _scale_y=0, d=1, t='in_out_bounce')
        a.bind(on_complete=self.close_dialog)
        a.start(self.theme_dialog)

    def close_dialog(self, *_):
        self.theme_dialog.dismiss()
        # Clock.schedule_once(self.dialog_restore, 1)

    def dialog_restore(self, _):
        self.theme_dialog._scale_x = 1
        self.theme_dialog._scale_y = 1

    def theme_color_cahnge(self, *_):
        self.theme_dialog.open()
        a = Animation(_scale_x=1, _scale_y=1, d=1, t='in_out_bounce')
        # a.bind(on_complete=self.close_dialog)
        a.start(self.theme_dialog)

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
                _scale_x=0,
                _scale_y=0,
                overlay_color=[0, 0, 0, 0],
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
                title="Set the plate",
                type="custom",
                content_cls=PltContent(),
                buttons=[
                    Cancel(text="CANCEL"),
                    Ok(text="OK")
                ]
            )

    def get_last_location(self):
        with open(
            'locations/loc.json', 'r'
        ) as f:
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
                "theme_style": app.theme_cls.theme_style,
                "primary_palette": app.theme_cls.primary_palette,
                "alpha": self.root.alpha,
                "mark": self.mark_img,
                "car": self.car_image,
                "drawer": self.anchor,
                "plate": self.plate,
                "device": self.paired_car
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
        self.paired_car = sett["device"]
        app.root.ids.content_drawer.md_bg_color = [1, 1, 1, 1]
        if sett["theme_style"] == 'Dark':
            self.root.ids.r.color = [0, 0, 0, 1]
        else:
            self.root.ids.r.color = [1, 1, 1, 1]

        sett = None

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
            "history": "Cronology",
            "palette": "Change the color",
            "theme-light-dark": "Change the style",
            "set-left-right": "Drawer to right",
            "car": "Set the plate",
            'bluetooth': self.paired_car if self.paired_car else 'Choose car'
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
