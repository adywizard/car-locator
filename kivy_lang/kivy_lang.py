
KV = """
#: import colors kivymd.color_definitions.colors
#: import Clock kivy.clock.Clock
#: import p kivy.utils.platform
#: import SE kivy.effects.scroll.ScrollEffect
#: import MapView kivy_garden.mapview.MapView
#: import w kivy.core.window.Window
#: import BlueDevicesScreen blue_devices_screen.devices.BlueDevicesScreen
#: import AlarmScreen parking_alarm.alarm_screen.AlarmScreen
#: import partial functools.partial


<TiltedButton@MDFillRoundFlatIconButton>
    angle: 5
    canvas.before:
        PushMatrix
        Rotate:
            angle: self.angle
            origin: self.center
    canvas.after:
        PopMatrix



<ChronologyScreen>
    canvas.before:
        Color:
            rgba: app.theme_cls.primary_color

        Ellipse:
            angle_start: 0
            angle_end: 360
            size: dp(300), dp(300)
            pos: root.x - dp(100), root.height - dp(250)

        Ellipse:
            angle_start: 0
            angle_end: 360
            size: dp(250), dp(250)
            pos: root.width - dp(150), root.y - dp(100)

        Ellipse:
            angle_start: 0
            angle_end: 360
            size: dp(50), dp(50)
            pos: root.x + dp(50), root.height / 2 - dp(100)

        Ellipse:
            angle_start: 0
            angle_end: 360
            size: dp(25), dp(25)
            pos: root.width - dp(75), root.height / 2 + dp(100)


<ContentLocationReady>
    MDLabel:
        pos_hint: {'center_x': .5, 'center_y': .5}
        size_hint: .7, .7
        text: 'Do yo want to crate parking alarm?'

<ContentTimeError>
    MDLabel:
        pos_hint: {'center_x': .5, 'center_y': .5}
        size_hint: .7, .7
        text: 'Can be more then 12h or less then 1 minute'

<WarnDialogContent>
    txt: txt
    size_hint_y: None
    height: dp(150)

    ScrollView:
        effect_cls: SE
        do_scroll_x: False
        do_scroll_y: True

        MDLabel:
            id: txt
            halign: 'left'
            size_hint_y: None
            height: self.texture_size[1]
            text_size: self.width, None
            padding: 10, 10


<SemiCircle>
    canvas.before:

        Color:
            rgba: self.color

        Ellipse:
            angle_start: self.angle_start
            angle_end: self.angle_end
            size: self.size
            pos: self.pos


<PltContent>

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
        app.animation_dialog_helper(self.parent.parent.parent.parent)
        app.hide_banner()

<Accept>:
    text_color: app.theme_cls.primary_color
    on_release:
        app.animation_dialog_helper(self.parent.parent.parent.parent)
        Clock.schedule_once(app.enable, .5)

<Ok>
    text_color: app.theme_cls.primary_color
    on_release:
        app.animation_dialog_helper(self.parent.parent.parent.parent)
        app.get_background_permission_option_label()\
            if self.parent.parent.parent.parent.title == 'Background location'\
                else app.set_plate_number()

<ItemConfirm>
    on_release:
        theme_text_color: 'Primary'
        root.set_icon(check)
        app.animation_dialog_helper(app.map_dialog)
        # app.map_dialog.dismiss()
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
        app.animation_dialog_helper(self.parent.parent.parent.parent)
        app.update_theme_color(self.text)


    CheckboxLeftWidget:
        id: check_c
        group: "check"
        theme_text_color: 'Custom'
        selected_color: app.theme_cls.primary_color
        unselected_color: [1, 1, 1, 1]\
            if app.theme_cls.theme_style == 'Dark'\
                else [0, 0, 0, 1]

<ItemDrawer>
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

<ContentNavigationDrawer>
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
            size_hint_x: .6
            pos_hint: {'center_x': .6, 'center_y': .5}

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
                        right_action_items:
                            [['parking',\
                                lambda x: app.open_time_picker(False)]]

                    MDFloatLayout:

                        TiltedButton:
                            angle: 2

                            icon: 'location-enter'
                            text: 'TURN ON GPS'
                            theme_text_color: 'Custom'
                            text_color: toolbar.specific_text_color
                            md_bg_color: app.theme_cls.primary_color[:3]\
                                + root.alpha
                            pos_hint: {'center_x': .5, 'center_y': .75}
                            on_release:

                                app.turn_on_gps()

                        TiltedButton:
                            angle: -2

                            icon: 'map-marker-plus'
                            text: 'SAVE THE LOCATION'
                            theme_text_color: 'Custom'
                            text_color: toolbar.specific_text_color
                            md_bg_color: app.theme_cls.primary_color[:3]\
                                + root.alpha
                            pos_hint: {'center_x': .5, 'center_y': .575}
                            on_release:
                                app.start(1000, 0)

                        TiltedButton:
                            angle: 1.5

                            icon: 'map-search-outline'
                            text: 'FIND MY CAR'
                            theme_text_color: 'Custom'
                            text_color: toolbar.specific_text_color
                            md_bg_color: app.theme_cls.primary_color[:3]\
                                + root.alpha
                            pos_hint: {'center_x': .5, 'center_y': .425}
                            on_release:
                                app.add_mark(52.506761, 13.2843075)\
                                    if p in ('windows', 'linux', 'macos')\
                                        else app.add_mark(\
                                            app.loca[0], app.loca[1])

                                sm.current = 'scr 2'

                        TiltedButton:
                            angle: -3

                            icon: 'map-marker-remove-outline'
                            text: 'GO TO CHRONOLOGY'
                            theme_text_color: 'Custom'
                            text_color: toolbar.specific_text_color
                            md_bg_color: app.theme_cls.primary_color[:3]\
                                + root.alpha
                            pos_hint: {'center_x': .5, 'center_y': .25}
                            on_release:
                                sm.current = 'scr 3'

                        # MDLabel:
                        #     id: lbl
                        #     pos_hint: {'center_x': .5, 'center_y': .2}
                        #     halign: 'center'

            BlueDevicesScreen:
                name: 'blue'
                id: blue

            Screen:
                name: 'scr 2'
                on_enter:
                    app.center_mapview(mapview)
                id: scr2
                zoom_on: 12

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
                                Clock.schedule_once(\
                                    partial(\
                                        app.open_animate_dialog,\
                                            app.map_dialog), .3\
                                        )

            ChronologyScreen:
                name: 'scr 3'

                MDBoxLayout:
                    orientation: 'vertical'
                    MDToolbar:
                        title: 'Chronology'
                        elevation: 10
                        left_action_items:
                            [['menu', lambda x: nav_drawer.set_state()]]
                        right_action_items:
                            [['reload', lambda x: app.clear_history()]]

                    ScrollView:
                        id: sv
                        effect_cls: SE
                        smooth_scroll_end: 120

                        MDList:
                            id: md_list
                            padding: [0, dp(6), 0, 0]
                            spacing: dp(6)

            AlarmScreen:
                id: alarm_screen
                name: 'alarm_screen'

        MDNavigationDrawer:
            id: nav_drawer
            anchor: app.anchor
            elevation: 1
            md_bg_color: 1, 1, 1, 1

            ContentNavigationDrawer:
                id: content_drawer
"""
