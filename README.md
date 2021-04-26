# Car-locator

***Car locator android app created with kivy/kivymd***

#### This app is not meant for the desktop use even if it runs on desktop it will not produce desirable effect.

#### This app was tested on Android 11 on Xiaomi mi 10 phone, on Android 8.1 OnePlus 5t phone, Motorola Edge phone with Android 10, Huawei Honor 9 phone with Android 9 and will not work below android version 8 API 26 as it uses androidx as a dependency.


## Version 0.1.3

Added more animations and cleaned all unnecessary files from build, added automatic location saving after
bluetooth disconnection with choosen device, and automatic parking alarm reminder.
 ***Do not rely too much on those two new features***, on newer versions of Android,
alarms are not very precise depending on how much vendor try to optimize the battery life, on some devices 
exact alarm might work without issues as well as being fiered after 3 hours on some other brands, there's an option which exclude this app from battery optimizations if granted, app can fire exact alarms at any given time.

 ***Do not rely to much on those two new features***, on newer versions of Android,
alarms are not very precise depending on how much vendor try too optimize the battery life, on some devices 
exact alarm might work without issues as well as being fiered after 3 houres on some other brands. 

Also gathering location in the background isn't very reliable when screen is off as android constantly tries to trottle
location access which is easily visible while debugging with background location on, so the best option is to have screen on

***In order to schedule exact alarms app needs REQUEST_IGNORE_BATTERY_OPTIMIZATIONS permission, latest apk has it built in, there's new item in the drawer "Allowe exact alarms", that will ensure correct alarm firing when parking alarm is set.***



## Version 0.1.2

Added shader animation instead of simple circles and lottie animation instead of static preplash image,

(experimental) added automatic location save on bluetooth unpaired from choosen device.

![](gifs/screen2.gif)



## Version 0.1

![](gifs/screen.gif)

## How to build

If you want to build this app (last version) your self, you'll have to set p4a = develop in buildozer.spec if it crash after compilation is due to https://github.com/kivy/kivy/issues/7398 and likely you'll have to add lottie support to your project at your own.

In gradle tamlate should be added androidx support.

```
ext {
    useAndroidX=true
    enableJetifier=true
}
```

Also there's some manipulation of the Java code involved:

Inside onCreate method of the PythonActivity.java this needs to be added

```
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O_MR1) {
            setShowWhenLocked(true);
            setTurnScreenOn(true);
        }
else {                
    this.getWindow().addFlags(
        WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED |
        WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON
        );
}
```

should look like this:

```java

@Override
protected void onCreate(Bundle savedInstanceState) {
    Log.v(TAG, "PythonActivity onCreate running");
    resourceManager = new ResourceManager(this);

    Log.v(TAG, "About to do super onCreate");
    super.onCreate(savedInstanceState);
    Log.v(TAG, "Did super onCreate");

    this.mActivity = this;

    this.showLoadingScreen(this.getLoadingScreen());

    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O_MR1) {
        setShowWhenLocked(true);
        setTurnScreenOn(true);
    }
    else {                
        this.getWindow().addFlags(
            WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED |
            WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON
            );
    }
    new UnpackFilesTask().execute(getAppRoot());

}

```

Inside doStartForeground method in PythonService.java this should be added:

```

Intent i = new Intent(context, PythonActivity.class);
i.putExtra("cancel", "cancel");
PendingIntent pi = PendingIntent.getActivity(context, 123123, i, PendingIntent.FLAG_UPDATE_CURRENT);

```

and also this: 

```
builder.addAction(context.getApplicationInfo().icon, "Force diconnection and save", pi);
```

looks like this:

```java

builder.setContentTitle(serviceTitle);
builder.setContentText(serviceDescription);
builder.setContentIntent(pIntent);
builder.addAction(context.getApplicationInfo().icon, "Force diconnection and save", pi);
builder.setSmallIcon(context.getApplicationInfo().icon);
notification = builder.build();

```


In the AndroidManifest.tmpl.xml

```
android:foregroundServiceType="location"
``` 
has to be added

it looks like this:

```xml

{% if service or args.launcher %}
<service android:name="org.kivy.android.PythonService"
            android:foregroundServiceType="location"
            android:process=":pythonservice" />
{% endif %}

```

If you want to build previus version of the app just rename main.py to something else and main_with_circle_animation.py from old_builds folder to main.py
then buildozer android build.

Otherwise already built app can be found in the bin folder.

### requirements:

The app in the bin folder was built with kivy==2.0.0 and kivymd==0.104.2.dev0 and modifyed version of python for android because of the above issue.


All other requirements can be found in buildozer.spec file.
