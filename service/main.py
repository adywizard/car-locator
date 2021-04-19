from time import sleep
from jnius import autoclass, cast
from os import environ

from blue.blue import BroadcastReceiver
from android_notification.notification import notify
from plyer import gps

BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
mService = autoclass('org.kivy.android.PythonService').mService
AndroidString = autoclass('java.lang.String')


class KivyService:
    def __init__(self):
        self.br = None
        self.connected = True
        self.device = environ.get('PYTHON_SERVICE_ARGUMENT', '')
        self.last_coordinates = []
        gps.configure(on_location=self.on_location)
        self.context = None
        self.extras = []
        self.stopped = False

    def on_location(self, **kwargs):

        lat = kwargs.get('lat')
        lon = kwargs.get('lon')
        self.last_coordinates = [
            str(lat), str(lon)
            ]
        print(f'lat: {lat}, lon: {lon}')

    def on_receive(self, context, intent):

        self.context = context

        name = ''
        action = intent.getAction()
        parcable = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE)
        device = cast(BluetoothDevice, parcable)
        name = device.getName()

        if action == BluetoothDevice.ACTION_ACL_DISCONNECTED:
            # print('started')
            if name == self.device:
                print('disconected')
                self.unregister_broadcast_receiver()
                gps.stop()
                self.stop_service()

    def unregister_broadcast_receiver(self):
        if self.br:
            self.br.stop()
            self.br = None

    def register_broadcats_receiver(self):

        if not self.br:
            self.br = BroadcastReceiver(
                self.on_receive, actions=[
                    # 'ACTION_ACL_CONNECTED',
                    'ACTION_ACL_DISCONNECTED'
                    ])
            self.br.start()

    def stop_service(self):
        if not self.stopped:
            self.stopped = True
            self.extras = [
                [
                    'gotLocation', 'true'
                    ],
                [
                    'lat', str(self.last_coordinates[0])
                    ],
                [
                    'lon', str(self.last_coordinates[1])
                    ]
                ]
            notify(
                context=self.context,
                channel_id='CAR_LOCATOR',
                text='Location ready!',
                title='Car locator location service',
                name='Car locator',
                description='Car locator service',
                extras=self.extras,
                flag='update',
                n_type='full',
                autocancel=True
                )
        # self.connected = False
        # mService.stopSelf()

    def start(self):
        gps.start(1000, 0)
        self.register_broadcats_receiver()
        while self.connected:
            print('waiting for disconnection')
            sleep(1)


if __name__ == '__main__':
    service = KivyService()
    service.start()
