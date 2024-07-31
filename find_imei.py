import subprocess
import time

def run_adb_command(command):
    result = subprocess.run(['adb', 'shell'] + command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.stderr:
        print("Error:", result.stderr)
    return result.stdout

def is_phone_awake():
    # Get the current power state
    result = run_adb_command(['dumpsys', 'power'])
    # Check if the phone is awake
    return 'mWakefulness=Awake' in result

def wake_up_phone():
    # Send the command to wake up the phone
    run_adb_command(['input', 'keyevent', 'KEYCODE_WAKEUP'])
    time.sleep(1)  # Wait for the phone to wake up

def swipe_up_to_unlock():
    # Swipe up to unlock the phone
    run_adb_command(['input', 'swipe', '300', '1000', '300', '500'])
    time.sleep(1)  # Wait for the phone to unlock

def is_home_screen():
    # Get the current activity
    result = run_adb_command(['dumpsys', 'window', 'windows', '|', 'grep', 'mCurrentFocus'])
    # Check if the current activity is the home screen
    return 'Launcher' in result or 'launcher' in result

def go_to_home_screen():
    # Send the command to go to the home screen
    run_adb_command(['input', 'keyevent', 'KEYCODE_HOME'])
    time.sleep(2)  # Wait for the home screen to load

def open_dialer_and_input_code(coordinates):
    # Open the dialer
    run_adb_command(['am', 'start', '-a', 'android.intent.action.DIAL'])
    time.sleep(2)  # Wait for the dialer to open

    # Input *#06# using tap coordinates
    for x, y in coordinates:
        print(f"Tapping at coordinates: ({x}, {y})")  # Print the coordinates being tapped
        run_adb_command(['input', 'tap', str(x), str(y)])
        time.sleep(0.1)  # Add a small delay between taps

def get_coordinates_for_phone(phone_model):
    # Predefined coordinates for different phone models
    phone_coordinates = {
        'CT3': [
            (157, 2091),  # Coordinate for '*'
            (875, 2103),  # Coordinate for '#'
            (582, 2123),  # Coordinate for '0'
            (811, 1714),  # Coordinate for '6'
            (875, 2103)   # Coordinate for '#'
        ],
        'KM4': [
            (232, 1900),  # Coordinate for '*'
            (811, 1900),  # Coordinate for '#'
            (582, 1900),  # Coordinate for '0'
            (811, 1600),  # Coordinate for '6'
            (811, 1900),  # Coordinate for '#'
        ],
        'TK4': [
            (250, 2000),  # Coordinate for '*'
            (800, 2000),  # Coordinate for '#'
            (550, 2000),  # Coordinate for '0'
            (800, 1600),  # Coordinate for '6'
            (800, 2000),  # Coordinate for '#'
        ],
        'CM4': [
            (250, 1800),  # Coordinate for '*'
            (800, 1800),  # Coordinate for '#'
            (550, 1800),  # Coordinate for '0'
            (800, 1500),  # Coordinate for '6'
            (800, 1800),  # Coordinate for '#'
        ]
    }

    return phone_coordinates.get(phone_model)

def is_developer_mode_enabled():
    # Check if developer options are enabled
    result = run_adb_command(['settings', 'get', 'global', 'development_settings_enabled'])
    return result.strip() == '1'

def enable_developer_mode():
    # Enable developer options
    run_adb_command(['settings', 'put', 'global', 'development_settings_enabled', '1'])
    time.sleep(2)  # Wait for the setting to take effect

def main():
    print("Please select your phone model:")
    print("1. CT3")
    print("2. KM4")
    print("3. TK4")
    print("4. CM4")

    choice = input("Enter the number corresponding to your phone model: ")

    if choice == '1':
        coordinates = get_coordinates_for_phone('CT3')
    elif choice == '2':
        coordinates = get_coordinates_for_phone('KM4')
    elif choice == '3':
        coordinates = get_coordinates_for_phone('TK4')
    elif choice == '4':
        coordinates = get_coordinates_for_phone('CM4')
    else:
        print("Invalid choice.")
        return

    # Check if developer mode is enabled
    if not is_developer_mode_enabled():
        print("Developer mode is not enabled. Enabling developer mode...")
        enable_developer_mode()

    # Check if the phone is awake
    if not is_phone_awake():
        print("Phone is not awake. Waking up the phone...")
        wake_up_phone()

    # Swipe up to unlock if necessary
    print("Swiping up to unlock the phone...")
    swipe_up_to_unlock()

    # Check if the phone is on the home screen
    if not is_home_screen():
        print("Phone is not on the home screen. Going back to the home screen...")
        go_to_home_screen()

    open_dialer_and_input_code(coordinates)

if __name__ == "__main__":
    main()
