import sys

def decimal_to_hex(decimal):
    return f"{decimal:02X}"

def convert_list_to_hex(decimal_list):
    return " ".join(map(decimal_to_hex, decimal_list))

def get_user_input():
    default_list = []
    
    print("Enter decimal numbers separated by commas (or press Enter to use default list):")
    input_string = input().strip()
    
    if not input_string:
        print(f"Using default list: {default_list}")
        return default_list
    
    try:
        numbers = [int(x.strip()) for x in input_string.split(',')]
        if not numbers:
            raise ValueError("No valid numbers entered.")
        return numbers
    except ValueError as e:
        print(f"Error: {e}. Using default list.")
        return default_list

def process_numbers(numbers, start=7, end=26):
    if len(numbers) < end:
        print(f"Warning: Input list has fewer than {end} numbers. Processing all available numbers.")
        end = len(numbers)
    
    target_numbers = numbers[start-1:end]
    hex_string = convert_list_to_hex(target_numbers)
    
    print(f"\nProcessing numbers {start} to {end}:")
    print("\nDecimal numbers:")
    print(target_numbers)
    
    print("\nHexadecimal representation:")
    print(hex_string)

def main():
    print("Decimal to Hexadecimal Converter (optimized for 7th to 26th numbers)")
    print("------------------------------------------------------------------")

    while True:
        decimal_numbers = get_user_input()
        process_numbers(decimal_numbers)
        
        if input("\nConvert another set of numbers? (y/n): ").lower() != 'y':
            break

    print("Thank you for using the converter!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting...")
        sys.exit(0)
