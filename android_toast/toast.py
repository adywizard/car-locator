
from android.runnable import run_on_ui_thread
from jnius import autoclass, cast

mActivity = autoclass("org.kivy.android.PythonActivity").mActivity
Toast = autoclass("android.widget.Toast")
CharSequence = autoclass("java.lang.CharSequence")
String = autoclass("java.lang.String")


@run_on_ui_thread
def android_toast(text, long=False):

    duration = Toast.LENGTH_SHORT if long else Toast.LENGTH_LONG
    text = cast(CharSequence, String(text))
    Toast.makeText(
        mActivity.getApplicationContext(), text, duration
        ).show()
