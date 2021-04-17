from jnius import autoclass, cast


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

ID = 11


def create_notification_channel(context, channel_id, name, description):

    name = cast('java.lang.CharSequence', AndroidString(name))
    description = AndroidString(description)
    channel_id = AndroidString(channel_id)

    importance = NotificationManager.IMPORTANCE_HIGH
    channel = NotificationChannel(channel_id, name, importance)
    channel.setDescription(description)
    notificationManager = context.getSystemService(NotificationManager)
    notificationManager.createNotificationChannel(channel)


def notify(
        context, channel_id='',
        text='', title='', name='',
        description='', extras=[],
        flag='update', n_type='full', autocancel=False):

    create_notification_channel(context, channel_id, name, description)

    icon = Drawable.icon

    if channel_id == 'CAR_LOCATOR':
        ID = 123123
    elif channel_id == 'CAR_LOCATOR_HEADS_UP':
        ID = 121212

    if flag == 'update':
        flag = PendingIntent.FLAG_UPDATE_CURRENT
    elif flag == 'cancel':
        flag = PendingIntent.FLAG_CANCEL_CURRENT
    elif flag == 'one':
        flag = PendingIntent.FLAG_ONE_SHOT

    intent = Intent(context, PythonActivity)

    if extras:

        for extra in extras:
            intent.putExtra(extra[0], extra[1])

    pendingIntent = PendingIntent.getActivity(
        context, ID, intent, flag)

    title = cast(
        'java.lang.CharSequence', AndroidString(title)
        )

    text = cast(
        'java.lang.CharSequence', AndroidString(
            text
            )
        )

    builder = Builder(context, channel_id)
    builder.setSmallIcon(icon)
    builder.setContentTitle(title)
    builder.setContentText(text)
    builder.setPriority(NotificationCompat.PRIORITY_HIGH)
    builder.setVisibility(NotificationCompat.VISIBILITY_PUBLIC)

    if autocancel:
        builder.setAutoCancel(True)

    if n_type == 'full':
        builder.setFullScreenIntent(pendingIntent, True)
    elif n_type == 'head':
        builder.setContentIntent(pendingIntent)
        builder.setVibrate([0])

    notification = builder.build()

    systemService = context.getSystemService(Context.NOTIFICATION_SERVICE)
    notificationManager = cast(NotificationManager, systemService)
    notificationManager.notify(1111, notification)
