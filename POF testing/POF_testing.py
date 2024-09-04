import time
import random

class DeviceUnderTest:
    def __init__(self):
        self.powered_on = True
        self.finder_enabled = False
        self.ble_key = None
        self.last_key_change = 0

    def power_off(self):
        self.powered_on = False
        print("DUT powered off manually.")

    def enable_power_off_finder(self):
        self.finder_enabled = True
        print("Power off finder enabled.")

    def check_finder_function(self):
        if not self.powered_on and self.finder_enabled:
            current_time = time.time()
            if current_time - self.last_key_change >= 1024:
                self.ble_key = random.randint(1000, 9999)
                self.last_key_change = current_time
            print(f"Finder function working. Current BLE key: {self.ble_key}")
            return True
        else:
            print("Finder function not working.")
            return False

def run_test():
    dut = DeviceUnderTest()

    # Pre-condition
    dut.enable_power_off_finder()

    # Procedure
    dut.power_off()

    check_times = [600, 1500, 600]  # 10 minutes, 25 minutes, 35 minutes
    for i, wait_time in enumerate(check_times, 1):
        print(f"\nStep {i*2-1}: Waiting for {wait_time} seconds...")
        time.sleep(wait_time)
        
        print(f"Step {i*2}: Checking finder function...")
        if not dut.check_finder_function():
            print("Test failed: Finder function not working as expected.")
            return False

    # Verification
    print("\nVerification:")
    initial_key = dut.ble_key
    for i in range(3):  # Check for key changes over 3 periods
        time.sleep(1024)  # Wait for 1024 seconds
        dut.check_finder_function()
        if dut.ble_key == initial_key:
            print(f"Test failed: BLE key did not change after {(i+1)*1024} seconds.")
            return False
        initial_key = dut.ble_key

    print("Test passed: DUT sends BLE advertising data with different keys changed every 1024s.")
    return True

if __name__ == "__main__":
    start_time = time.time()
    test_result = run_test()
    end_time = time.time()
    
    print(f"\nTest {'passed' if test_result else 'failed'}.")
    print(f"Total test duration: {end_time - start_time:.2f} seconds.")
