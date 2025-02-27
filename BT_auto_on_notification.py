#!/usr/bin/env python3

import time
from datetime import datetime
import subprocess
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bt_test.log')
    ]
)
logger = logging.getLogger(__name__)

class BTAutoOnTest:
    def __init__(self):
        self.adb_cmd = "adb"
        self.verify_adb_connection()
    
    def verify_adb_connection(self):
        try:
            result = subprocess.run(
                [self.adb_cmd, "get-state"], 
                capture_output=True, 
                text=True,
                check=True
            )
            logger.info("ADB connection verified")
        except subprocess.CalledProcessError as e:
            logger.error(f"ADB connection failed: {e}")
            raise Exception("Please check ADB connection")

    def run_adb_command(self, command):
        """執行 ADB 命令並返回結果"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"ADB command failed: {e}")
            logger.error(f"Error output: {e.stderr}")
            raise

    def verify_bt_status(self):
        """檢查藍牙狀態"""
        try:
            cmd = f'{self.adb_cmd} shell settings get global bluetooth_on'
            result = self.run_adb_command(cmd)
            return result == "1"
        except Exception as e:
            logger.error(f"Failed to check BT status: {e}")
            return False

    def turn_off_bt(self):
        """使用 adb shell svc bluetooth disable 關閉藍牙"""
        try:
            # 關閉藍牙
            cmd = f'{self.adb_cmd} shell svc bluetooth disable'
            self.run_adb_command(cmd)
            
            # 等待藍牙關閉
            time.sleep(20)  # 增加等待時間為 20 秒
            
            # 驗證藍牙狀態
            if self.verify_bt_status():
                raise Exception("Bluetooth is still on")
            
            logger.info("Successfully turned off Bluetooth")
            return True
        except Exception as e:
            logger.error(f"Failed to turn off Bluetooth: {e}")
            return False

    def set_datetime(self, date_str, time_str="04:59:50"):
        """設置手機日期時間"""
        try:
            # 組合完整日期時間
            current_year = "2025"
            date_time_str = f"{date_str} {current_year} {time_str}"
            date_obj = datetime.strptime(date_time_str, "%b %d %Y %H:%M:%S")
            
            # 格式化為 adb 命令格式
            formatted_date = date_obj.strftime("%m%d%H%M%Y.%S")
            
            # 設置系統時間
            cmd = f'{self.adb_cmd} shell "su 0 date {formatted_date}"'
            self.run_adb_command(cmd)
            
            # 等待時間設置生效
            time.sleep(1)
            
            # 驗證時間設置
            current_time = self.get_device_time()
            logger.info(f"Device time set to: {current_time}")
            
            return self.verify_datetime(date_obj)
        except Exception as e:
            logger.error(f"Failed to set datetime: {e}")
            return False

    def get_device_time(self):
        """獲取設備當前時間"""
        try:
            cmd = f'{self.adb_cmd} shell date'
            return self.run_adb_command(cmd)
        except Exception:
            return "Unknown time"

    def verify_datetime(self, expected_datetime):
        """驗證設備時間是否正確設置"""
        try:
            cmd = f'{self.adb_cmd} shell date'
            current_time_str = self.run_adb_command(cmd)
            current_time = datetime.strptime(current_time_str, "%Y-%m-%d %H:%M:%S")
            
            time_diff = abs((current_time - expected_datetime).total_seconds())
            
            if time_diff > 5:
                logger.warning(f"Time difference too large: {time_diff} seconds")
                return False
                
            return True
        except Exception as e:
            logger.error(f"DateTime verification failed: {e}")
            return False

    def check_notification_dialog(self):
        """檢查通知對話框"""
        try:
            # 使用 UI Automator 檢查通知
            cmd = (f'{self.adb_cmd} shell uiautomator dump && '
                  f'{self.adb_cmd} shell cat /sdcard/window_dump.xml')
            result = self.run_adb_command(cmd)
            
            # 檢查是否包含藍牙自動開啟的相關文字
            return "bluetooth" in result.lower() and "auto" in result.lower()
        except Exception as e:
            logger.error(f"Failed to check notification: {e}")
            return False

    def wait_and_check(self, timeout=180):
        """等待並檢查結果"""
        start_time = time.time()
        dialog_found = False
        bt_turned_on = False
        
        while time.time() - start_time < timeout:
            current_time = self.get_device_time()
            logger.info(f"Checking at: {current_time}")
            
            # 檢查通知對話框
            if not dialog_found and self.check_notification_dialog():
                dialog_found = True
                logger.info("Notification dialog found")
            
            # 檢查藍牙狀態
            if not bt_turned_on and self.verify_bt_status():
                bt_turned_on = True
                logger.info("Bluetooth turned on automatically")
            
            # 如果都完成了就退出
            if dialog_found and bt_turned_on:
                break
            
            time.sleep(5)
        
        elapsed_time = time.time() - start_time
        return dialog_found, bt_turned_on, elapsed_time

    def run_factory_reset(self):
        """執行 Factory Reset"""
        try:
            logger.info("Performing factory reset...")
            cmd = f'{self.adb_cmd} shell "am broadcast -a android.intent.action.MASTER_CLEAR"'
            self.run_adb_command(cmd)
            logger.info("Factory reset initiated successfully")
        except Exception as e:
            logger.error(f"Failed to perform factory reset: {e}")

    def run_test_cases(self):
        """執行所有測試案例"""
        test_dates = [
            "Feb 12",
            "Feb 13",
            "Feb 14"
        ]
        
        results = []
        for test_date in test_dates:
            logger.info(f"\n=== Starting test for {test_date} 2025 ===")
            
            try:
                # 關閉藍牙
                if not self.turn_off_bt():
                    raise Exception("Failed to turn off Bluetooth")
                
                # 設置時間
                if not self.set_datetime(test_date):
                    raise Exception("Failed to set date and time")
                
                # 等待並檢查結果
                dialog_found, bt_turned_on, elapsed_time = self.wait_and_check()
                
                # 記錄結果
                test_passed = dialog_found and bt_turned_on
                result_msg = (
                    f"Test results for {test_date} 2025:\n"
                    f"- Device time: {self.get_device_time()}\n"
                    f"- Notification dialog appeared: {'Yes' if dialog_found else 'No'}\n"
                    f"- Bluetooth auto turned on: {'Yes' if bt_turned_on else 'No'}\n"
                    f"- Time taken: {elapsed_time:.1f} seconds"
                )
                
                results.append({
                    'date': f"{test_date} 2025",
                    'passed': test_passed,
                    'message': result_msg
                })
                
            except Exception as e:
                logger.error(f"Test failed: {e}")
                results.append({
                    'date': f"{test_date} 2025",
                    'passed': False,
                    'message': f"Test failed: {str(e)}"
                })
            
            # 測試間隔
            time.sleep(5)
        
        self.print_test_report(results)

        # 測試完成後執行 Factory Reset
        self.run_factory_reset()

    def print_test_report(self, results):
        """輸出測試報告"""
        logger.info("\n====== Test Report ======")
        
        for result in results:
            status = "PASS" if result['passed'] else "FAIL"
            logger.info(f"\nTest Date: {result['date']}")
            logger.info(f"Status: {status}")
            logger.info(result['message'])
        
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r['passed'])
        
        logger.info(f"\nSummary:")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

def main():
    try:
        tester = BTAutoOnTest()
        tester.run_test_cases()
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
