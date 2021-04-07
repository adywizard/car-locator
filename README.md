# Car-locator

Car locator android app created with kivy/kivymd

![](screen.gif)

## How to build

If you want to build this app yourself, and icons are not displayed properly:

Go in to the folder:

'.buildozer\android\platform\python-for-android\pythonforandroid\recipes\sdl2_ttf'

and in __init__.py  file change version  = '2.0.14' to version  = '2.0.15'
this will allow you to correctly display icons in app,
this is necessary due to the bug in the version = '2.0.14' of sdl2_ttf.

Otherwise already built app can be found in the bin folder.

### requirements:

The app in the bin folder was built with kivy==2.0.0 and kivymd==0.402.2.dev0.

All other requirements can be found in buildozer.spec file

## Version 0.1.2

Added shader animation instead of simple circles and lottie animation instead of static preplash image


