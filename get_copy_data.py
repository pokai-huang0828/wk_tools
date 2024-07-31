import subprocess
import re

def run_adb_command(command):
    result = subprocess.run(['adb', 'shell'] + command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.stderr:
        print("Error:", result.stderr)
    return result.stdout.strip()

def get_clipboard_data():
    # Use service call clipboard to get the clipboard content
    result = run_adb_command(['service', 'call', 'clipboard', '1'])
    
    if result:
        # Extract the hexadecimal values (32-bit words)
        hex_values = re.findall(r'0x[0-9A-Fa-f]+', result)
        
        # Convert hex values to bytes
        byte_array = bytearray()
        for hex_value in hex_values:
            int_value = int(hex_value, 16)
            byte_array.extend(int_value.to_bytes(4, byteorder='big'))
        
        # Remove trailing null bytes
        byte_array = byte_array.rstrip(b'\x00')
        
        return byte_array
    return None

def decode_clipboard_data(byte_array, encodings):
    decoded_texts = {}
    for encoding in encodings:
        try:
            # Decode bytes to string using the specified encoding, ignoring errors
            clipboard_text = byte_array.decode(encoding, errors='ignore')
            
            # Filter out non-printable characters
            clipboard_text = ''.join(c for c in clipboard_text if c.isprintable())
            
            decoded_texts[encoding] = clipboard_text.strip()
        except Exception as e:
            decoded_texts[encoding] = f"Decoding failed: {str(e)}"
    return decoded_texts

def main():
    encodings = [
        'utf-8',
        'latin1',  # Try other common encodings
        'utf-16',
        'utf-32'
    ]
    
    print("Retrieving the copied data...")
    byte_array = get_clipboard_data()
    
    if byte_array:
        print("Decoding the copied data with different encodings...")
        decoded_texts = decode_clipboard_data(byte_array, encodings)
        for encoding, text in decoded_texts.items():
            print(f"Copied text with {encoding}: {text}")
    else:
        print("No clipboard data found")

if __name__ == "__main__":
    main()
