"""
Version History

1.1:
   Fixed script issue with error `unsupported operand type(s)`
"""

import logging
import time
import os
import subprocess
import platform
import threading

SERIAL_NUMBER = None
PRINT_LENGTH = 35

# =================
#  Script Functions
# =================

logging.basicConfig(
    filename="command_history.log",
    format="[%(asctime)s]%(message)s",
    filemode="a",
)
_logging = logging.getLogger("Main")
_logging.setLevel(logging.DEBUG)


def _run_command(command, timeout=30, is_reg=False):
    if platform.system() == "windows" and "grep" in command:
        if is_reg:
            command.replace("grep", "findstr /r")
        else:
            command.replace("grep", "find")
    process = subprocess.Popen(
        command.split(" "),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
        universal_newlines=False,
    )
    timer = None
    timer_triggered = threading.Event()
    if timeout and timeout > 0:
        # The wait method on process will hang when used with PIPEs with large
        # outputs, so use a timer thread instead.
        def timeout_expired():
            timer_triggered.set()
            process.terminate()

        timer = threading.Timer(timeout, timeout_expired)
        timer.start()
    # If the command takes longer than the timeout, then the timer thread
    # will kill the subprocess, which will make it terminate.
    out, err = process.communicate()
    if timer is not None:
        timer.cancel()
    if timer_triggered.is_set():
        out, err = process.communicate()
        return out.decode("utf-8").strip(), err.decode("utf-8").strip()
    return out.decode("utf-8").strip(), err.decode("utf-8").strip()


def send_adb_command(command, sn=None, without_shell=False):
    if not sn:
        sn = SERIAL_NUMBER

    adb_command = f"adb -s {sn} shell {command}"
    if without_shell:
        adb_command = adb_command.replace(" shell", "")
    out, err = _run_command(adb_command)
    if err:
        _logging.debug("command=[%s], output=[%s]", adb_command, err)
        return err
    _logging.debug("command=[%s], output=[%s]", adb_command, out)
    return out


def print_with_dot(title):
    print(title.ljust(PRINT_LENGTH, "."), end="")


def format_output(func):
    def outer():
        output = func()
        if output:
            print("\x1b[32m \u2713 \x1b[0m")
        else:
            print("\x1b[31m \u2717 \x1b[0m")
        return output

    return outer


# =================
#  ADB Functions
# =================


@format_output
def adb_root():
    print_with_dot("Root ADB.")

    send_adb_command("root", without_shell=True)
    # Add buffer times for root adb.
    send_adb_command("wait-for-device", without_shell=True)
    return True


@format_output
def adb_reboot():
    print_with_dot("Reboot device.")

    send_adb_command("reboot", without_shell=True)
    send_adb_command("wait-for-device", without_shell=True)

    for _ in range(5):
        completed = send_adb_command("getprop sys.boot_completed")
        if completed == "1":
            send_adb_command("input keyevent 82")
            return True
        time.sleep(5)
    return False


# =================
#  Clock
# =================


@format_output
def clock_enable_seconds():
    print_with_dot("Enable Clock Seconds.")

    send_adb_command("settings put secure clock_seconds 1")

    clock_seconds = send_adb_command("settings get secure clock_seconds")
    if clock_seconds == "1":
        return True
    return False


# =================
#  Bugreport
# =================


@format_output
def set_bugreport_keyboard_shortcut():
    print_with_dot("Enable Bugreport Keyboard Shortcut.")

    send_adb_command("settings put secure bugreport_in_power_menu 1")

    power_menu = send_adb_command("settings get secure bugreport_in_power_menu")
    if power_menu == "1":
        return True
    return False


@format_output
def set_bugreport_enable_snoop_log():
    print_with_dot("Enable Bugreport Snoop Log.")

    send_adb_command("setprop persist.bluetooth.btsnooplogmode full")

    snoop_log_mode = send_adb_command(
        "getprop persist.bluetooth.btsnooplogmode"
    )
    if snoop_log_mode == "full":
        return True
    return False


@format_output
def set_bugreport_enable_for_all():
    print_with_dot("Enable Bugreport All Debug Log.")

    send_adb_command(
        "device_config put bluetooth INIT_logging_debug_enabled_for_all true"
    )

    debug_for_all = send_adb_command(
        "device_config get bluetooth INIT_logging_debug_enabled_for_all"
    )
    if debug_for_all == "true":
        return True
    return False


@format_output
def set_bugreport_log_level():
    print_with_dot("Set Bugreport Log Level To Verbose")

    send_adb_command("device_config set_sync_disabled_for_tests persistent")
    send_adb_command(
        "device_config put bluetooth INIT_default_log_level_str LOG_VERBOSE"
    )
    send_adb_command("setprop persist.log.tag.bluetooth verbose")

    log_level = send_adb_command("getprop persist.log.tag.bluetooth")
    if log_level == "verbose":
        return True
    return False


@format_output
def set_bugreport_to_default():
    print_with_dot("Set Bugreport Handler to Default.")

    send_adb_command(
        "settings put secure custom_bugreport_handler_app com.android.shell"
    )
    time.sleep(1)
    send_adb_command(
        "am start -a com.android.settings.APPLICATION_DEVELOPMENT_SETTINGS"
    )
    time.sleep(1)

    handler_app = send_adb_command(
        "settings get secure custom_bugreport_handler_app"
    )
    if handler_app == "com.android.shell":
        return True

    # Fixed sometime handler will change back to betterbug after first time open
    # dev page.
    send_adb_command(
        "settings put secure custom_bugreport_handler_app com.android.shell"
    )
    time.sleep(1)

    handler_app = send_adb_command(
        "settings get secure custom_bugreport_handler_app"
    )
    if handler_app != "com.android.shell":
        return False
    return True


@format_output
def set_bugreport_logcat_buffer_size():
    print_with_dot("Set Bugreport Logcat Buffer Size.")

    buffer_list = [
        "main",
        "system",
        "crash",
        "radio",
        "events",
        "kernel",
    ]
    for buffer_name in buffer_list:
        send_adb_command(f"logcat -b {buffer_name} -G 16M")
    send_adb_command("setprop persist.logd.size 8388608")

    logd_size = send_adb_command("getprop persist.logd.size")
    if logd_size == "8388608":
        return True
    return False


# =================
#  OOBE
# =================


@format_output
def skip_oobe():
    print_with_dot("Skip OOBE.")

    send_adb_command("am start -a com.android.setupwizard.FOUR_CORNER_EXIT")
    time.sleep(0.5)
    send_adb_command("input keyevent 3")
    time.sleep(0.5)
    send_adb_command("settings put system system_locales en-US")
    return True


# =================
#  Pixel Logger
# =================


# def open_pixel_logger():
#     send_adb_command(
#         "am start -n com.android.pixellogger/.ui.main.MainActivity"
#     )

# def auido_dump_encode():
#     pass


# @format_output
# def make_pixel_logger_visible_in_menu() -> bool:
#     print("Show Pixel Logger APP Icon" )

#     send_adb_command("input swipe 500 1600 500 400")
#     cmd = (
#         "am broadcast -a com.android.pixellogger.ACTION_SHOW_ICON -n "
#         "com.android.pixellogger/com.android.pixellogger.receiver.BootReceiver"
#     )
#     for _ in range(2):
#         send_adb_command(cmd)
#     time.sleep(5)
#     return True


# =================
#   dev settings
# =================


@format_output
def show_dev_settings():
    print_with_dot("Show Dev Option In Setting.")

    send_adb_command("settings put global development_settings_enabled 1")

    dev_setting = send_adb_command(
        "settings get global development_settings_enabled"
    )
    if dev_setting == "1":
        return True
    return False


@format_output
def set_stay_awake_while_charging():
    print_with_dot("Set Stay Awake While Charging.")

    send_adb_command("settings put global stay_on_while_plugged_in 15")

    dev_setting = send_adb_command(
        "settings get global stay_on_while_plugged_in"
    )
    if dev_setting == "15":
        return True
    return False


# =================
#   Others
# =================


def model(sn):
    return send_adb_command("getprop ro.build.product", sn=sn)


def device_init_setup():
    """Pre-setting for Pixel phone.

    Steps:
        1. Skip OOBE.
        2. Enable clock show seconds.
        3. Enable dev option in setting.
        4. Enable stay awake option in dev setting.
        5. Enable bugreport power menu shortcut.
        6. Enable snoop log.
        7. Set bugreport log level to verbose.
        8. Set max size for buffer size.
        9. Enable bugreport all log for debug.
        10.Set bugreport handler to Android System.
    """
    adb_root()

    skip_oobe()

    clock_enable_seconds()

    show_dev_settings()
    set_stay_awake_while_charging()

    set_bugreport_keyboard_shortcut()
    set_bugreport_enable_snoop_log()
    set_bugreport_log_level()
    set_bugreport_logcat_buffer_size()
    set_bugreport_enable_for_all()
    set_bugreport_to_default()

    adb_reboot()
    adb_root()

    print("Finished.")


def get_devices():
    devices_from_command = os.popen("adb devices").readlines()[1:-1]
    if not devices_from_command or len(devices_from_command) == 0:
        return []

    output_devices = [None]
    for index, device in enumerate(devices_from_command):
        sn = device.split("\t")[0]
        print(f"Device ID-{index + 1} ==>> {sn} {model(sn)}\n")
        output_devices.append(sn)
    return output_devices


if __name__ == "__main__":
    devices = get_devices()
    if devices:
        time.sleep(0.5)
        n = input("Choose the ID-Number of devices(1,2,3...): ")
        try:
            SERIAL_NUMBER = devices[int(n)]
            device_init_setup()
        except IndexError:
            print("Number not in list.")
    else:
        print("Can't found any devices from 'adb devices'.")
