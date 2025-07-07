import yaml
import os
import sys

def analyze_file(file_path: str):
    """
    Analyzes a single YAML file for devices with non-'apims' scopes
    and reports the line number where the device ID is found.

    Args:
        file_path: The full path to the YAML file to be analyzed.
    """
    print("-" * 50)
    print(f"--- Analyzing file: {file_path} ---")

    # --- Step 1: Read the entire file into a list of lines ---
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
    except Exception as e:
        print(f"\nError reading file: {e}")
        return

    # --- Step 2: Parse the data structure ---
    try:
        data = yaml.safe_load("".join(all_lines))
    except yaml.YAMLError as e:
        print(f"\nError: Failed to parse YAML: {e}")
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

            other_scopes = [s for s in scope_list if s != 'apims']

            if other_scopes:
                found_issues = True
                device_id = device.get('id', 'Undefined ID')
                
                print(f"\n Found non-'apims' scopes in device ID '{device_id}': {', '.join(other_scopes)}")

                # --- Step 4: Find the line number of the device ID ---
                line_number = -1
                search_strings = [f"id: {device_id}", f"id: '{device_id}'", f'id: "{device_id}"']
                for i, line_text in enumerate(all_lines):
                    if any(s in line_text for s in search_strings):
                        line_number = i
                        break

                if line_number != -1:
                    print(f"  -> Found at line: {line_number + 1}")
                else:
                    print(f"  (Warning: Could not locate the line for device ID '{device_id}')")

    if not found_issues:
        print("\n Check complete. No devices with scopes other than 'apims' were found.")

def main():
    """
    Main function: Scans a directory for YAML files, lets the user choose one,
    and then analyzes it.
    """
    target_directory = '/usr/local/google/mobileharness/testbeds'
    print(f"--- Scanning for YAML files in: {target_directory} ---")

    try:
        all_entries = os.listdir(target_directory)
        # Filter for files ending with .yaml or .yml (case-insensitive) and sort them
        yaml_files = sorted([f for f in all_entries if f.lower().endswith(('.yaml', '.yml')) and os.path.isfile(os.path.join(target_directory, f))])
    except FileNotFoundError:
        print(f"\nError: The specified directory was not found: '{target_directory}'.")
        print("Please ensure the path is correct.")
        return
    except Exception as e:
        print(f"An error occurred while scanning the directory: {e}")
        return

    if not yaml_files:
        print("\nNo YAML (.yaml or .yml) files were found in this directory.")
        return

    # --- Display files and prompt for user's choice ---
    print("\nPlease select a file from the list below to analyze:")
    for i, filename in enumerate(yaml_files):
        print(f"  [{i + 1}] {filename}")

    selected_file = None
    while True:
        try:
            choice_str = input(f"\nEnter a number (1-{len(yaml_files)}), or 'q' to quit: ")
            if choice_str.lower() == 'q':
                print("User chose to quit.")
                return

            choice_num = int(choice_str)
            if 1 <= choice_num <= len(yaml_files):
                selected_file = yaml_files[choice_num - 1]
                break
            else:
                print(f"Invalid choice. Please enter a number between 1 and {len(yaml_files)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            return
            
    # --- Construct full path and start analysis ---
    full_path_to_analyze = os.path.join(target_directory, selected_file)
    analyze_file(full_path_to_analyze)


if __name__ == '__main__':
    main()