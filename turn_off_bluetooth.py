import subprocess

def run_adb_command(command):
    """Run an ADB command and return the output."""
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"Error: {result.stderr.strip()}")
            return None
    except FileNotFoundError:
        print("ADB not found. Make sure ADB is installed and added to your PATH.")
        return None

def check_device():
    """Check if any device is connected via ADB."""
    devices = run_adb_command(["adb", "devices"])
    if devices:
        lines = devices.splitlines()
        if len(lines) > 1:  # The first line is the header
            for line in lines[1:]:
                if line.strip() and "device" in line:
                    print(f"Device connected: {line.split()[0]}")
                    return True
    print("No device connected. Please connect your device and enable USB debugging.")
    return False

def turn_off_bluetooth():
    """Turn off Bluetooth on the connected device."""
    print("Turning off Bluetooth...")
    result = run_adb_command(["adb", "shell", "service", "call", "bluetooth_manager", "8"])
    if result:
        print("Bluetooth turned off successfully.")
    else:
        print("Failed to turn off Bluetooth.")

def main():
    """Main function to check device and turn off Bluetooth."""
    if check_device():
        turn_off_bluetooth()

if __name__ == "__main__":
    main()
