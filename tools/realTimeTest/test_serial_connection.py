#!/usr/bin/env python3
import serial
import time

def test_serial_connection():
    try:
        print("Testing COM4 connection...")
        ser = serial.Serial("COM4", 115200, timeout=2)
        print("✓ Serial port opened successfully")
        
        # Reset board
        try:
            ser.setDTR(False)
            time.sleep(0.1)
            ser.setDTR(True)
            print("✓ DTR reset sent")
        except Exception as e:
            print(f"Warning: DTR reset failed: {e}")
        
        time.sleep(2)
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        print("✓ Buffers cleared")
        
        # Test menu command
        print("Sending 'menu' command...")
        ser.write(b"menu\n")
        time.sleep(1)
        
        # Read response
        response = ""
        start_time = time.time()
        while time.time() - start_time < 3:
            if ser.in_waiting > 0:
                data = ser.readline().decode(errors="ignore").strip()
                if data:
                    response += data + "\n"
                    print(f"Received: {data}")
        
        if not response:
            print("❌ No response received from device")
        else:
            print(f"✓ Total response:\n{response}")
        
        ser.close()
        print("✓ Serial port closed")
        
    except serial.SerialException as e:
        print(f"❌ Serial connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_serial_connection()
