# Introduction

## Overview

This repository contains a suite of Python scripts designed to automate various tasks on Android devices using ADB (Android Debug Bridge). These scripts can perform a variety of functions including retrieving device information, extracting clipboard data, listening for tap events, and enabling developer mode. The scripts are particularly useful for developers and testers who need to interact with Android devices programmatically.

## Scripts

### `find_imei.py`

This script retrieves the IMEI (International Mobile Equipment Identity) number of the connected Android device.

#### Key Functions:
- **`run_adb_command(command)`**: Executes an ADB shell command and returns the output.
- **`is_phone_awake()`**: Checks if the phone is awake.
- **`wake_up_phone()`**: Sends a command to wake up the phone.
- **`swipe_up_to_unlock()`**: Swipes up to unlock the phone.
- **`is_home_screen()`**: Checks if the current activity is the home screen.
- **`go_to_home_screen()`**: Sends a command to navigate to the home screen.
- **`open_dialer_and_input_code(coordinates)`**: Opens the dialer and inputs a code using tap coordinates.
- **`get_coordinates_for_phone(phone_model)`**: Returns predefined coordinates for different phone models.

### `get_copy_data.py`

This script fetches clipboard data from the connected Android device.

#### Key Functions:
- **`run_adb_command(command)`**: Executes an ADB shell command and returns the output.
- **`get_clipboard_data()`**: Retrieves the clipboard data from the device.

### `get_infor.py`

This script retrieves general information about the connected Android device.

#### Key Functions:
- **`run_adb_command(command)`**: Executes an ADB shell command and returns the output.
- **`get_device_property(device, prop)`**: Retrieves a specific property from the device.
- **`get_device_info(device)`**: Retrieves comprehensive information about the device including manufacturer, model, Android version, kernel version, serial number, IMEI numbers, and Android ID.

### `get_tap_coordinates.py`

This script listens for tap events on the connected Android device and extracts the touch coordinates.

#### Key Functions:
- **`run_adb_command(command)`**: Executes an ADB shell command and returns the output.
- **`get_event_number()`**: Identifies the event number for the touchscreen.
- **`listen_for_tap_events(event_number)`**: Listens for touch events and extracts coordinates.

### `test.py`

This script performs a variety of tasks including enabling developer mode, retrieving device properties, and displaying device information. It serves as a comprehensive tool for interacting with Android devices.

#### Key Functions:
- **`run_command(command)`**: Executes a shell command and returns the output.
- **`run_adb_command(command)`**: Executes an ADB shell command and returns the output.
- **`verify_adb()`**: Verifies if ADB is available and configures the environment.
- **`start_adb_server()`**: Starts the ADB server.
- **`get_device_list()`**: Retrieves a list of connected devices.
- **`get_device_property(device, prop)`**: Retrieves a specific property from the device.
- **`get_imei(device, slot)`**: Retrieves the IMEI number from the device.
- **`get_device_info(device)`**: Retrieves comprehensive information about the device.
- **`enable_developer_mode(device)`**: Enables developer mode on the device.
- **`display_info(info)`**: Displays the retrieved device information.

## Usage

1. **Clone the repository:**

    ```sh
    git clone https://github.com/yourusername/android-testing-tool.git
    cd android-testing-tool
    ```

2. **Install the required Python packages (if any, otherwise skip this step):**

    ```sh
    pip install -r requirements.txt
    ```

3. **Connect your Android device to your computer via USB and ensure that ADB is working by running:**

    ```sh
    adb devices
    ```

4. **Run the desired script:**

    - To find the IMEI:

        ```sh
        python find_imei.py
        ```

    - To get clipboard data:

        ```sh
        python get_copy_data.py
        ```

    - To get device information:

        ```sh
        python get_infor.py
        ```

    - To get tap coordinates:

        ```sh
        python get_tap_coordinates.py
        ```

    - To perform various tasks and display device information:

        ```sh
        python test.py
        ```

## Conclusion

These scripts provide a robust set of tools for automating tasks on Android devices using ADB. They can be particularly useful for developers and testers who need to interact with Android devices programmatically. By leveraging these scripts, you can streamline your workflow and enhance your productivity.

