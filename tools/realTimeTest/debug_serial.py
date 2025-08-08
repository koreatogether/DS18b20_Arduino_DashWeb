#!/usr/bin/env python3
import serial
import time
import sys

def test_serial_connection():
    """Test serial connection and capture initial board output"""
    print("=== Serial Connection Debug Test ===")
    
    try:
        # Open serial port
        print(f"Opening COM4 at 115200 baud...")
        ser = serial.Serial('COM4', 115200, timeout=2)
        print("✓ Port opened successfully")
        
        # Reset board via DTR
        print("Resetting board via DTR...")
        ser.setDTR(False)
        time.sleep(0.1)
        ser.setDTR(True)
        print("✓ DTR reset completed")

        # Wait for boot (5초 이상 대기)
        print("Waiting for board boot (5 seconds)...")
        time.sleep(5)

        # Clear any buffered data
        ser.reset_input_buffer()
        print("✓ Input buffer cleared")

        # Capture initial output
        print("Capturing initial output for 5 seconds...")
        start_time = time.time()
        all_data = b""
        line_count = 0
        appstate0_detected = False

        while time.time() - start_time < 5:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                all_data += data
                # Print each line as it comes
                for line in data.decode('utf-8', errors='ignore').split('\n'):
                    if line.strip():
                        line_count += 1
                        print(f"Line {line_count}: {repr(line)}")
                        if '[DEBUG] appState: 0' in line:
                            appstate0_detected = True
            time.sleep(0.1)

        print(f"\n=== Summary ===")
        print(f"Total bytes received: {len(all_data)}")
        print(f"Total lines: {line_count}")
        print(f"Raw data (first 500 chars): {repr(all_data[:500])}")

        # Check for specific Korean text
        text = all_data.decode('utf-8', errors='ignore')
        print(f"\n=== Korean Text Detection ===")
        print(f"Contains '번호': {'번호' in text}")
        print(f"Contains 'ID': {'ID' in text}")
        print(f"Contains '| 번호': {'| 번호' in text}")
        print(f"Contains '센서 제어 메뉴': {'센서 제어 메뉴' in text}")

        # Check for appState: 0
        print(f"\n=== AppState 0 Detection ===")
        print(f"Contains '[DEBUG] appState: 0': {appstate0_detected}")

        # Test sending 'menu' command
        print(f"\n=== Testing 'menu' command ===")
        ser.write(b'menu\n')
        time.sleep(1)
        response = ser.read(1000)
        print(f"Response to 'menu': {repr(response.decode('utf-8', errors='ignore'))}")

        ser.close()
        print("✓ Port closed")

        return text, all_data
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return None, None

if __name__ == "__main__":
    test_serial_connection()
