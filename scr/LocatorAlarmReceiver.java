package org.org.locator;

import android.content.BroadcastReceiver;
import android.content.Intent;
import android.content.Context;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import androidx.core.app.NotificationCompat;
import androidx.core.app.NotificationManagerCompat;
import android.os.Build;
import org.kivy.android.PythonActivity;
import org.locator.locator.R.drawable;
import android.media.RingtoneManager;
import android.net.Uri;
import android.media.AudioAttributes;


public class LocatorAlarmReceiver extends BroadcastReceiver{

    private void createNotificationChannel(Context context) {

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            Uri sound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);

            AudioAttributes att = new AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_NOTIFICATION)
                    .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                    .build();

            CharSequence name = "CAR_LOCATOR_ALARM";
            String description = "Parking alarm";
            int importance = NotificationManager.IMPORTANCE_HIGH;
            NotificationChannel channel = new NotificationChannel("CAR_LOCATOR_ALARM", name, importance);
            channel.setDescription(description);
            channel.setSound(sound, att);
            channel.enableLights(true);
            channel.enableVibration(true);
            NotificationManager notificationManager = context.getSystemService(NotificationManager.class);
            notificationManager.createNotificationChannel(channel);
        }
    }
    
    private void sendNotification(Context context) {
        Intent fullScreenIntent = new Intent(context, PythonActivity.class);
        PendingIntent fullScreenPendingIntent = PendingIntent.getActivity(context, 654321,
                fullScreenIntent, PendingIntent.FLAG_UPDATE_CURRENT);

        Uri uri= RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);

        NotificationCompat.Builder builder = new NotificationCompat.Builder(context, "CAR_LOCATOR_ALARM")
                .setSmallIcon(drawable.icon)
                .setContentTitle("Parking alarm")
                .setContentText("Parking is expired!")
                .setTicker("Parking is expired!")
                .setVibrate(new long[]{0, 300, 0, 400, 0, 500})
                .setSound(uri)
                .setAutoCancel(true)
                .setOnlyAlertOnce(true)
                .setPriority(NotificationCompat.PRIORITY_HIGH)
                .setFullScreenIntent(fullScreenPendingIntent, true);

        NotificationManagerCompat notificationManager = NotificationManagerCompat.from(context);
        notificationManager.notify(192837, builder.build());
    }

    @Override
    public void onReceive(Context context, Intent intent) {
        this.createNotificationChannel(context);
        this.sendNotification(context);
    }
}