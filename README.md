# Car-locator

Car locator android app created with kivy/kivymd

### This app is not meant for the desktop use even if it runs on desktop it will not produce desirable effect.

![](gifs/screen.gif)

## How to build

If you want to build this app (last version) your self, you'll have to set p4a = develop in buildozer.spec if it doesen't compile is due to https://github.com/kivy/kivy/issues/7398 and likely you'll have to make changes at your own. (Manually add lottie support to your project).

Else if you want to build previus version of the app just rename main.py to something else and main_with_circle_animation.py to main.py
then buildozer android build.

Otherwise already built app can be found in the bin folder.

### requirements:

The app in the bin folder was built with kivy==2.0.0 and kivymd==0.104.2.dev0 and modifyed version of python for android because of the above issue.


All other requirements can be found in buildozer.spec file

## Version 0.1.2

Added shader animation instead of simple circles and lottie animation instead of static preplash image

![](gifs/screen2.gif)
