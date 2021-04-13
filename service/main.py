from time import sleep
from jnius import autoclass, cast
from os import environ

from blue.blue import BroadcastReceiver
from android_notification.notification import notify

# Intent = autoclass('android.content.Intent')
BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
# PythonActivity = autoclass('org.kivy.android.PythonActivity')
mService = autoclass('org.kivy.android.PythonService').mService
# PendingIntent = autoclass('android.app.PendingIntent')
# NotificationCompat = autoclass('androidx.core.app.NotificationCompat')
# Builder = autoclass('androidx.core.app.NotificationCompat$Builder')
# NotificationManager = autoclass('android.app.NotificationManager')
# NotificationChannel = autoclass('android.app.NotificationChannel')
# Context = autoclass('android.content.Context')
AndroidString = autoclass('java.lang.String')
# Drawable = autoclass("org.locator.locator.R$drawable")


class KivyService:
    def __init__(self):
        self.br = None
        self.connected = True
        self.device = environ.get('PYTHON_SERVICE_ARGUMENT', '')

    def on_receive(self, context, intent):

        name = ''
        action = intent.getAction()
        parcable = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE)
        device = cast(BluetoothDevice, parcable)
        name = device.getName()
        extras = [[AndroidString("getLocation"), AndroidString("true")]]

        if action == BluetoothDevice.ACTION_ACL_DISCONNECTED:

            if name == self.device:
                self.connected = False
                self.unregister_broadcast_receiver()
                notify(
                    context,
                    'CAR LOCATOR',
                    'Tap to save current location',
                    'Location service',
                    'Car locator',
                    'Car locator service',
                    extras
                    )
                mService.stopSelf()

    def unregister_broadcast_receiver(self):

        if self.br:
            self.br.stop()
            self.br = None

    def register_broadcats_receiver(self):

        if not self.br:
            self.br = BroadcastReceiver(
                self.on_receive, actions=[
                    'ACTION_ACL_CONNECTED',
                    'ACTION_ACL_DISCONNECTED'
                    ])
            self.br.start()

    def start(self):
        self.register_broadcats_receiver()
        while self.connected:
            print('waiting for disconnection')
            sleep(2)


if __name__ == '__main__':
    service = KivyService()
    service.start()
