import subprocess
import os
import sys
import logging
import shutil
import re

# Set UTF-8 encoding
os.environ['LANG'] = 'en_US.UTF-8'
os.environ['PYTHONIOENCODING'] = 'UTF-8'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()])

# Constants
SCRIPT_NAME = 'Android device info extractor'
SCRIPT_VERSION = '2.8'
ANDROID_SDK_ROOT = os.getenv('ANDROID_SDK_ROOT', '')
DEBUG = os.getenv('DEBUG', '0') == '1'
CI = os.getenv('CI', 'false') == 'true'
PRIVACY_MODE = False
OPEN_DEVICE_STATUS_INFO_ONLY = False

def run_command(command):
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        result.check_returncode()
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {command}")
        logging.error(e.stderr)
        return ""
    except Exception as e:
        logging.error(f"Error executing command: {command}")
        logging.error(str(e))
        return ""

def run_adb_command(command):
    return run_command(f"adb {command}")

def verify_adb():
    if not shutil.which("adb"):
        logging.error("adb is NOT available")
        sys.exit(1)
    if os.name == 'nt' and not ANDROID_SDK_ROOT:
        local_app_data = os.getenv('LOCALAPPDATA')
        if local_app_data and os.path.exists(os.path.join(local_app_data, 'Android', 'Sdk')):
            os.environ['ANDROID_SDK_ROOT'] = os.path.join(local_app_data, 'Android', 'Sdk')
    if ANDROID_SDK_ROOT:
        os.environ['PATH'] += os.pathsep + os.path.join(ANDROID_SDK_ROOT, 'platform-tools')
    if not shutil.which("adb"):
        logging.error("adb is NOT available")
        sys.exit(1)

def start_adb_server():
    run_adb_command("start-server")

def get_device_list():
    devices = run_adb_command("devices")
    return [line.split()[0] for line in devices.strip().split('\n')[1:] if line.strip()]

def get_device_property(device, prop):
    return run_adb_command(f"-s {device} shell getprop {prop}")

def get_imei(device, slot):
    output = run_adb_command(f"-s {device} shell service call iphonesubinfo {slot}")
    imei = ''.join(re.findall(r"\d+", output))
    if not imei:
        output = run_adb_command(f"-s {device} shell dumpsys iphonesubinfo")
        imei_match = re.search(r'IMEI\s*=\s*(\d+)', output)
        if imei_match:
            imei = imei_match.group(1)
    return imei

def get_device_info(device):
    info = {
        'Manufacturer': get_device_property(device, 'ro.product.manufacturer'),
        'Model': get_device_property(device, 'ro.product.model'),
        'Device': get_device_property(device, 'ro.product.device'),
        'Android Version': get_device_property(device, 'ro.build.version.release'),
        'Kernel Version': run_adb_command(f"-s {device} shell uname -r"),
        'Serial Number': get_device_property(device, 'ro.serialno'),
        'IMEI1': get_imei(device, 1),
        'IMEI2': get_imei(device, 2),
        'Android ID': run_adb_command(f"-s {device} shell settings get secure android_id")
    }
    return info

def enable_developer_mode(device):
    developer_mode_status = run_adb_command(f"-s {device} shell settings get global development_settings_enabled")
    if developer_mode_status != '1':
        run_adb_command(f"-s {device} shell settings put global development_settings_enabled 1")
        logging.info("Developer mode enabled")
    else:
        logging.info("Developer mode is already enabled")

def display_info(info):
    for key, value in info.items():
        if PRIVACY_MODE and key in ['IMEI1', 'IMEI2', 'Serial Number', 'Android ID']:
            value = anonymize(value)
        logging.info(f"{key}: {value}")

def anonymize(value):
    return ''.join(['*' if c.isalnum() else c for c in value])

def main():
    global PRIVACY_MODE, OPEN_DEVICE_STATUS_INFO_ONLY

    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg in ['-p', '--privacy-mode']:
                PRIVACY_MODE = True
            elif arg == '--open-device-status-info':
                OPEN_DEVICE_STATUS_INFO_ONLY = True
            elif arg in ['-V', '--version']:
                print(f"{SCRIPT_NAME} v{SCRIPT_VERSION}")
                sys.exit(0)
            else:
                logging.error(f"Unrecognized option: {arg}")
                sys.exit(2)

    verify_adb()
    start_adb_server()
    devices = get_device_list()
    if not devices:
        logging.error("No devices/emulators found")
        sys.exit(1)

    for device in devices:
        logging.info(f"Selected device: {device}")
        if OPEN_DEVICE_STATUS_INFO_ONLY:
            # Implement the logic to open device status info if necessary
            continue
        enable_developer_mode(device)
        info = get_device_info(device)
        display_info(info)

if __name__ == "__main__":
    main()
