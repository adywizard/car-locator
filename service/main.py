from time import sleep
from jnius import autoclass, cast
from os import environ

from blue.blue import BroadcastReceiver

Intent = autoclass('android.content.Intent')
BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
PythonActivity = autoclass('org.kivy.android.PythonActivity')
mService = autoclass('org.kivy.android.PythonService').mService
PendingIntent = autoclass('android.app.PendingIntent')
NotificationCompat = autoclass('androidx.core.app.NotificationCompat')
Builder = autoclass('androidx.core.app.NotificationCompat$Builder')
NotificationManager = autoclass('android.app.NotificationManager')
NotificationChannel = autoclass('android.app.NotificationChannel')
Context = autoclass('android.content.Context')
AndroidString = autoclass('java.lang.String')
Drawable = autoclass("org.locator.locator.R$drawable")


class KivyService:
    def __init__(self):
        self.br = None
        self.connected = True
        self.CHANNEL_ID = AndroidString("locator")
        self.device = environ.get('PYTHON_SERVICE_ARGUMENT', '')

    def create_notification_channel(self, context):

        name = cast('java.lang.CharSequence', AndroidString('Locator service'))
        description = AndroidString("Location ready")

        importance = NotificationManager.IMPORTANCE_HIGH
        channel = NotificationChannel(self.CHANNEL_ID, name, importance)
        channel.setDescription(description)
        notificationManager = context.getSystemService(NotificationManager)
        notificationManager.createNotificationChannel(channel)

    def notify(self, context):
        self.create_notification_channel(context)

        icon = Drawable.icon

        getLocation = AndroidString("getLocation")
        true = AndroidString("true")

        fullScreenIntent = Intent(context, PythonActivity)
        fullScreenIntent.putExtra(getLocation, true)
        fullScreenPendingIntent = PendingIntent.getActivity(
            context, 0, fullScreenIntent, PendingIntent.FLAG_UPDATE_CURRENT)

        title = cast(
            'java.lang.CharSequence', AndroidString('Locator service')
            )

        text = cast(
            'java.lang.CharSequence', AndroidString(
                'Location ready! Tap to save it'
                )
            )

        builder = Builder(context, self.CHANNEL_ID)
        builder.setSmallIcon(icon)
        builder.setContentTitle(title)
        builder.setContentText(text)
        builder.setPriority(NotificationCompat.PRIORITY_HIGH)
        builder.setFullScreenIntent(fullScreenPendingIntent, True)
        builder.setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
        builder.setAutoCancel(True)
        fullScreenNotification = builder.build()
        systemService = context.getSystemService(Context.NOTIFICATION_SERVICE)
        notificationManager = cast(NotificationManager, systemService)
        notificationManager.notify(1111, fullScreenNotification)

    def on_receive(self, context, intent):

        name = ''
        action = intent.getAction()
        parcable = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE)
        device = cast(BluetoothDevice, parcable)
        name = device.getName()

        if action == BluetoothDevice.ACTION_ACL_DISCONNECTED:

            if name == self.device:
                self.connected = False
                self.unregister_broadcast_receiver()
                self.notify(context)
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
