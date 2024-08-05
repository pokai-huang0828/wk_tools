import subprocess
import re
import platform

def get_app_version(package_name):
    try:
        if platform.system() == "Windows":
            cmd = f"adb shell dumpsys package {package_name} | findstr versionName"
        else:
            cmd = f"adb shell dumpsys package {package_name} | grep versionName"
        
        result = subprocess.check_output(cmd, shell=True).decode('utf-8')
        version = re.search(r'versionName=([\d\.]+)', result)
        return version.group(1) if version else "Version not found"
    except subprocess.CalledProcessError:
        return "App not found or ADB error"

def check_adb_connection():
    try:
        subprocess.check_output("adb devices", shell=True)
        return True
    except subprocess.CalledProcessError:
        print("Error: ADB is not properly set up or no device is connected.")
        return False

# List of package names
packages = [
    "com.google.android.googlequicksearchbox",  # Google app
    "com.google.android.youtube",               # YouTube
    "com.google.android.apps.youtube.music",    # YouTube Music
    "com.google.android.apps.tachyon",          # Google Meet (updated package name)
    "com.fitbit.FitbitMobile",                  # Fitbit
    "com.huami.watch.hmwatchmanager",           # Zepp
    "jp.naver.line.android",                    # Line
    "com.facebook.orca",                        # Messenger
    "org.videolan.vlc",                         # VLC
    "com.spotify.music"                         # Spotify
]

if check_adb_connection():
    for package in packages:
        version = get_app_version(package)
        print(f"{package}: {version}")
else:
    print("Please ensure your Android device is connected and USB debugging is enabled.")
