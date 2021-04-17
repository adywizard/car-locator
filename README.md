# Car-locator

***Car locator android app created with kivy/kivymd***

#### This app is not meant for the desktop use even if it runs on desktop it will not produce desirable effect.

#### This app was tested on Android 11 on Xiaomi mi 10 phone and on Android 9 OnePlus 5t phone.


## Version 0.1.3

Added more animations and cleaned all unnecessary files from build, added automatic location saving.



## Version 0.1.2

Added shader animation instead of simple circles and lottie animation instead of static preplash image,

(experimental) added automatic location save on bluetooth unpaired from choosen device.

![](gifs/screen2.gif)



## Version 0.1

![](gifs/screen.gif)

## How to build

If you want to build this app (last version) your self, you'll have to set p4a = develop in buildozer.spec if it crash after compilation is due to https://github.com/kivy/kivy/issues/7398 and likely you'll have to add lottie support to your project at your own.

Also there's some manipulation of the Java code involved:

Inside onCreate method of the PythonActivity.java this needs to be added

```
setShowWhenLocked(true);
setTurnScreenOn(true);
```

should look like this:

```java

protected void onCreate(Bundle savedInstanceState) {
        Log.v(TAG, "PythonActivity onCreate running");
        resourceManager = new ResourceManager(this);

        Log.v(TAG, "About to do super onCreate");
        super.onCreate(savedInstanceState);
        Log.v(TAG, "Did super onCreate");

        this.mActivity = this;

        this.showLoadingScreen(this.getLoadingScreen());

        setShowWhenLocked(true);
        setTurnScreenOn(true);

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
