# car-locator
Car locator android app created with kivy/kivymd

before building this app; go to:
'.buildozer\android\platform\python-for-android\recipes\sdl2_ttf' and
in __init__.py  file change version  = '2.0.14' to version  = '2.0.15'
this will allow you to correctly diplay icons in app, this is necessary due to the bug in the version = '2.0.14' of sdl2_ttf.

Requirements in buildozer.spec
