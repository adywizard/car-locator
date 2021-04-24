
from jnius import autoclass, cast

mActivity = autoclass('org.kivy.android.PythonActivity').mActivity

Vibrator = autoclass('android.os.Vibrator')
VibrationEffect = autoclass('android.os.VibrationEffect')
AudioAttributes = autoclass('android.media.AudioAttributes')
AudioManager = autoclass('android.media.AudioManager')
Context = autoclass('android.content.Context')
AudioAttributesBuilder = autoclass('android.media.AudioAttributes$Builder')
AudioAttributes = autoclass('android.media.AudioAttributes')


class AndroidVibrator:
    def __init__(self):
        self.context = mActivity.getApplicationContext()
        self.vibrator = cast(
            Vibrator, self.context.getSystemService(Context.VIBRATOR_SERVICE)
        )
        self.pattern = [1500, 800, 800, 800]

    def vibrate(self):

        ringerMode = cast(
            AudioManager, self.context.getSystemService(Context.AUDIO_SERVICE)
        )
        ringerMode.getRingerMode()

        if ringerMode == AudioManager.RINGER_MODE_SILENT:
            return

        vibe = VibrationEffect.createWaveform(
            self.pattern, 0
        )

        att = AudioAttributesBuilder()
        att.setUsage(AudioAttributes.USAGE_NOTIFICATION)
        att.setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
        att = cast(AudioAttributes, att.build())

        self.vibrator.vibrate(vibe, att)

    def stop(self):
        self.vibrator.cancel()
