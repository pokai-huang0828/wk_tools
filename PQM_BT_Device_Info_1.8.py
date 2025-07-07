#!/usr/bin/env python
import os
import time
import re
import subprocess
import threading
import platform

def path():
    return os.path.join(os.path.expanduser("~"), 'Desktop') + "/"

def model(sn):
    model_cmd = "adb -s " + sn + " shell getprop ro.build.product"
    model_name = (os.popen(model_cmd)).readline().rstrip()
    return model_name

def devices(n):
    device = os.popen("adb devices").readlines()
    devdict = {}
    devlist = []
    for d in device:
        devlist.append(d.strip('\n').replace('\tdevice', ''))
    del devlist[0]
    del devlist[-1]
    for d in device:
        for dlist in devlist:
            device_id = str(devlist.index(dlist) + 1)
            devdict[device_id] = dlist
    if n == "0":
        for i in devdict:
            print("Device ID-%s ==>> %s %s\n" % (i, devdict[i], model(devdict[i])))
    else:
        return devdict[n]

def get_BT_status(sn):
    bt_manager = ["adb", "-s", sn, "shell", "dumpsys", "bluetooth_manager"]
    bt_manager_logs = subprocess.check_output(bt_manager).decode("utf-8")
    match = re.findall(r'(Bluetooth Status[^}]*)BluetoothManagerService', bt_manager_logs)
    return match[0]

def get_BT_chip_firmware_information(sn):
    _reset_bt_status(sn)

    ls_out = _run_command(
        sn,
        "ls /vendor/firmware | grep fw_bcmdhd && echo YES || echo NO",
    )
    ls_out = ls_out.strip()

    if model(sn) == "tangorpro":
        output = _run_command(
            sn,
            "lshal debug android.hardware.bluetooth@1.1::IBluetoothHci | grep \"BCM.*\" ",
        )
        if output:
            return output.splitlines()[0]

    if "YES" in ls_out:
        output = _run_command(
            sn,
            "dumpsys android.hardware.bluetooth.IBluetoothHci/default | grep \"FW\"",
        )
        if output:
            return output.splitlines()[0]

    output = _run_command(sn, "logcat | grep SoC")
    if output:
        ptn = re.compile(r'BT SoC FW SU Build info: (.*),')
        match = ptn.search(output)
        if match:
            return match.group(1)

    raise BaseException("Please check your device, can't match BRCM or QCOM")


def _reset_bt_status(sn):
    os.system(f"adb -s {sn} root")
    os.system(f"adb -s {sn} shell svc bluetooth disable ")
    time.sleep(0.5)
    os.system(f"adb -s {sn} shell svc bluetooth enable ")
    time.sleep(2)

def _run_command(sn, command, timeout=5, is_reg=False):
    if platform.system() == "windows" and "grep" in command:
        if is_reg:
            command.replace("grep", "findstr /r")
        else:
            command.replace("grep", "find")
    cmd_list = ["adb", "-s", sn, "shell"] + command.split(' ')
    process = subprocess.Popen(
        cmd_list,
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
    out, _ = process.communicate()
    if timer is not None:
        timer.cancel()
    if timer_triggered.is_set():
        out, _ = process.communicate()
        return out.decode('utf-8')
    return out.decode('utf-8')

if __name__ == "__main__":
    devices(n="0")
    time.sleep(0.5)
    n = input("Choose the ID-Number of devices(1,2,3...): ")
    sn = devices(n)
    chip_info = get_BT_chip_firmware_information(sn)
    buildnumber = os.popen("adb -s " + sn + " shell getprop ro.build.description").read()
    project = os.popen("adb -s " + sn + " shell getprop ro.revision").read()

    print("\n\n**Paste Test Enviromation in the bug description**")
    print("**TEST ENVIRONMENT**")
    print("======================================")
    print("- <Phone Model>: " + model(sn))
    print("- <SN>: " + sn)
    print("- <Hardware Version>: " + project.strip())
    print("- <Android BuildID>: " + buildnumber.strip())
    print("- <Chip Info & FW Info>: " + chip_info.strip())
    print("======================================\n")
    print("**LOG**")
    print("```\n" + get_BT_status(sn) + "\n```")
