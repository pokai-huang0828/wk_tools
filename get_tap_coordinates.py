import subprocess
import re

def get_device_event():
    # Get the event number for the touchscreen
    result = subprocess.run(['adb', 'shell', 'getevent', '-il'], stdout=subprocess.PIPE, text=True)
    potential_event_numbers = []
    lines = result.stdout.splitlines()
    
    for i, line in enumerate(lines):
        if 'add device' in line:
            match = re.search(r'event\d+', line)
            if match:
                event_number = match.group(0)
                print(f"Debug: Potential event number found: {event_number}")
                # Print surrounding lines for context
                for j in range(max(0, i-2), min(i+6, len(lines))):
                    print(f"Debug: Line {j}: {lines[j]}")
                # Check the next few lines for ABS_MT_POSITION_X and ABS_MT_POSITION_Y
                for j in range(i+1, min(i+6, len(lines))):
                    if 'ABS_MT_POSITION_X' in lines[j] or 'ABS_MT_POSITION_Y' in lines[j]:
                        print(f"Debug: Touchscreen event number confirmed: {event_number}")
                        return event_number
                potential_event_numbers.append(event_number)
    
    if potential_event_numbers:
        print("Multiple potential event numbers found:")
        for idx, event_number in enumerate(potential_event_numbers):
            print(f"{idx + 1}: {event_number}")
        choice = int(input("Please select the event number (enter the corresponding number): ")) - 1
        return potential_event_numbers[choice]
    
    return None

def listen_for_taps(event_number):
    # Listen for touch events and extract coordinates
    process = subprocess.Popen(['adb', 'shell', 'getevent', '-lt', f'/dev/input/{event_number}'], stdout=subprocess.PIPE, text=True)
    x, y = None, None
    try:
        for line in process.stdout:
            if 'ABS_MT_POSITION_X' in line:
                x = int(line.split()[-1], 16)
            elif 'ABS_MT_POSITION_Y' in line:
                y = int(line.split()[-1], 16)
            if x is not None and y is not None:
                print(f'Tap detected at: x={x}, y={y}')
                x, y = None, None
    except KeyboardInterrupt:
        process.terminate()

if __name__ == "__main__":
    event_number = get_device_event()
    if event_number:
        print(f"Listening for touch events on /dev/input/{event_number}...")
        listen_for_taps(event_number)
    else:
        print("Could not find touchscreen event number.")
