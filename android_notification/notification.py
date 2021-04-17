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
# Drawable = autoclass('org.locator.locator.R$drawable')
ActionBuilder = autoclass(
    'androidx.core.app.NotificationCompat$Action$Builder'
    )
Action = autoclass('androidx.core.app.NotificationCompat$Action')
R = autoclass('android.R$drawable')
ID = 11


def create_action_intent(context):
    i = Intent(context, PythonActivity)
    i.putExtra(AndroidString("start"), AndroidString("start"))

    pendingIntent = PendingIntent.getActivity(
        context, 321321, i, PendingIntent.FLAG_UPDATE_CURRENT)
    title = cast('java.lang.CharSequence', AndroidString("start"))

    action = ActionBuilder(R.ic_menu_mylocation, title, pendingIntent)

    return action.build()


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

    if channel_id == 'CAR_LOCATOR':
        ID = 123123
    elif channel_id == 'CAR_LOCATOR_HEADS_UP':
        ID = 121212
        action = create_action_intent(context)

    if flag == 'update':
        flag = PendingIntent.FLAG_UPDATE_CURRENT
    elif flag == 'cancel':
        flag = PendingIntent.FLAG_CANCEL_CURRENT
    elif flag == 'one':
        flag = PendingIntent.FLAG_ONE_SHOT

    intent = Intent(context, PythonActivity)

    if extras:

        for extra in extras:
            intent.putExtra(AndroidString(extra[0]), AndroidString(extra[1]))

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
    builder.setSmallIcon(context.getApplicationInfo().icon)
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
        builder.addAction(action)

    notification = builder.build()

    systemService = context.getSystemService(Context.NOTIFICATION_SERVICE)
    notificationManager = cast(NotificationManager, systemService)
    notificationManager.notify(1111, notification)
