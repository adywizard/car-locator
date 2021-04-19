from time import time
from jnius import cast, autoclass


Intent = autoclass('android.content.Intent')
LocatorAlarmReceiver = autoclass('org.org.locator.LocatorAlarmReceiver')
mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
Intent = autoclass('android.content.Intent')
AlarmManager = autoclass('android.app.AlarmManager')
PendingIntent = autoclass('android.app.PendingIntent')
Context = autoclass('android.content.Context')


class ParkAlarmManager:
    def __init__(self):
        pass

    def start(self, time):
        self.create_alarm(time)

    def create_alarm(self, secondes):

        context = mActivity.getApplicationContext()

        alarmSetTime = int(round(time() * 1000)) + 1000 * secondes
        alarmIntent = Intent()
        alarmIntent.setClass(context, LocatorAlarmReceiver)
        alarmIntent.setAction("org.org.locator.ACTION_START_PARKING_ALARM")

        pendingIntent = PendingIntent.getBroadcast(
            context, 181864, alarmIntent, PendingIntent.FLAG_UPDATE_CURRENT)

        alarm = cast(
            AlarmManager, context.getSystemService(Context.ALARM_SERVICE))

        alarm.setExactAndAllowWhileIdle(
            AlarmManager.RTC_WAKEUP, alarmSetTime, pendingIntent)
