import yaml
import os
from typing import Set, Any

def main():
    """
    Main function: Checks a YAML file to find devices with specific 'scope' values
    and prints the line number of the device ID for quick navigation.
    """
    # --- The filename to check (hardcoded in the script) ---
    file_to_check = 'MCS_TE5_yaml_remove_SIM_daily_backup.txt'

    print(f"--- Checking file in standard mode: {file_to_check} ---")

    # --- Step 1: Read the entire file into a list of lines for lookups ---
    try:
        with open(file_to_check, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
    except FileNotFoundError:
        print(f"\nError: File not found at '{file_to_check}'.")
        print("Please ensure this Python script is in the same folder as your YAML file.")
        return
    except Exception as e:
        print(f"\nError reading file: {e}")
        return

    # --- Step 2: Parse the data structure using the standard yaml library ---
    try:
        data = yaml.safe_load("".join(all_lines))
    except yaml.YAMLError as e:
        print(f"\nError: Failed to parse YAML: {e}")
        print("Please check for non-comment text at the beginning of the file or other YAML format errors.")
        return

    found_issues = False
    print("\n--- Analysis Report ---")

    if not isinstance(data, list):
        print("YAML content is not in the expected list format.")
        return

    # --- Step 3: Traverse the data structure to find problematic devices ---
    for testbed in data:
        if not isinstance(testbed, dict) or 'devices' not in testbed:
            continue
        
        devices = testbed.get('devices', [])
        for device in devices:
            dimensions = device.get('dimensions', {})
            if not dimensions or 'scope' not in dimensions:
                continue

            scope_list = dimensions.get('scope', [])
            if not isinstance(scope_list, list):
                continue

            # Check for scopes other than 'apims'
            other_scopes = [s for s in scope_list if s != 'apims']

            # If different scopes are found
            if other_scopes:
                found_issues = True
                device_id = device.get('id', 'Undefined ID')
                
                print(f"\n Found non-'apims' scopes in device ID '{device_id}': {', '.join(other_scopes)}")

                # --- Step 4 (MODIFIED): Find the line number of the device ID to report it ---
                line_number = -1
                search_strings = [f"id: {device_id}", f"id: '{device_id}'", f'id: "{device_id}"']
                for i, line_text in enumerate(all_lines):
                    if any(s in line_text for s in search_strings):
                        line_number = i
                        break

                # MODIFICATION: Instead of finding comments, just print the line number.
                if line_number != -1:
                    # We add 1 because list indices start at 0, but file line numbers start at 1.
                    print(f"  -> Found at line: {line_number + 1}")
                else:
                    print(f"  (Warning: Could not locate the line for device ID '{device_id}')")

    if not found_issues:
        print("\n Check complete. All devices either contain only 'apims' in their scope or have no scope defined.")


if __name__ == '__main__':
    main()