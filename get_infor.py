import subprocess
import logging

# Configure logging to display messages with timestamp, log level, and message
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()])

def run_adb_command(command):
    try:
        # Run the ADB command and capture the output
        result = subprocess.run(["adb"] + command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            # Log an error if the command fails
            logging.error(f"ADB command failed: {command}")
            logging.error(result.stderr)
            return ""
        return result.stdout.strip()
    except Exception as e:
        # Log any exceptions that occur during command execution
        logging.error(f"Error executing ADB command: {command}")
        logging.error(str(e))
        return ""

def enable_developer_mode():
    # Check if developer mode is enabled
    developer_mode_status = run_adb_command("shell settings get global development_settings_enabled")
    if developer_mode_status != '1':
        # Enable developer mode if it is not already enabled
        run_adb_command("shell settings put global development_settings_enabled 1")
        logging.info("Developer mode enabled")
    else:
        logging.info("Developer mode is already enabled")

def get_device_info():
    
    device_info = {
        "Serial Number": run_adb_command("shell getprop ro.serialno"),
        "IMEI1": run_adb_command("shell service call iphonesubinfo 1 s16 com.android.shell | cut -c 50-66 | tr -d \".[:space:]'\""),
        "IMEI2": run_adb_command("shell service call iphonesubinfo 2 s16 com.android.shell | cut -c 50-66 | tr -d \".[:space:]'\"")
    }
    return device_info

def check_info_completeness(info):
    
    for key, value in info.items():
        if not value:
            # Log a warning if any data is missing
            logging.warning(f"{key} data is missing")
        else:
            # Log info if the data is complete
            logging.info(f"{key} data is complete")

def main():
    logging.info("Starting to check and enable developer mode")
    enable_developer_mode()
    
    logging.info("Fetching device details")
    device_info = get_device_info()
    
    logging.info("Checking data completeness")
    check_info_completeness(device_info)
    
    logging.info("Outputting data in UTF-8 encoding")
    for key, value in device_info.items():
        # Ensuring the output is in UTF-8 encoding
        print(f"{key}: {value.encode('utf-8').decode('utf-8')}")

if __name__ == "__main__":
    main()
