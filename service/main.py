from time import sleep
from jnius import autoclass, cast
from os import environ

from blue.blue import BroadcastReceiver
from android_notification.notification import notify
# from plyer import gps

BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
mService = autoclass('org.kivy.android.PythonService').mService
AndroidString = autoclass('java.lang.String')


class KivyService:
    def __init__(self):
        self.br = None
        self.connected = True
        self.device = environ.get('PYTHON_SERVICE_ARGUMENT', '')
        # self.last_coordinates = []
        # gps.configure(on_location=self.on_location)

    # def on_location(self, **kwargs):
    #     lat = kwargs.get('lat')
    #     lon = kwargs.get('lon')
    #     # self.last_coordinates = [str(lat), lon]
    #     print(f'lat: {lat}, lon: {lon}')
    #     notify(
    #         mService.getApplicationContext(),
    #         'CAR_LOCATOR',
    #         f'lat: {lat}, lon: {lon}',
    #         'Location service',
    #         'Car locator',
    #         'Car locator service',
    #     )

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
                    'CAR_LOCATOR',
                    'Location ready',
                    'Location service',
                    'Car locator',
                    'Car locator service',
                    extras
                    )
                # gps.stop()
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
        # gps.start(1000, 5)
        self.register_broadcats_receiver()
        while self.connected:
            print('waiting for disconnection')
            sleep(2)


if __name__ == '__main__':
    service = KivyService()
    service.start()
