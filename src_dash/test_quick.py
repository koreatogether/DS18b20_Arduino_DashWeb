"""
빠른 Arduino 연결 테스트 (5초 제한)
"""
import serial
import time
import threading

def test_arduino_quick():
    print("🧪 빠른 Arduino 테스트 (5초 제한)")
    
    try:
        # 짧은 타임아웃으로 연결
        ser = serial.Serial('COM4', 115200, timeout=0.5)
        print("✅ Arduino 연결 성공")
        
        # 5초간만 데이터 수집
        start_time = time.time()
        data_count = 0
        
        while time.time() - start_time < 5:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        data_count += 1
                        print(f"[{data_count:2d}] {line}")
                except:
                    pass
            time.sleep(0.1)
        
        ser.close()
        print(f"\n📊 결과: {data_count}개 데이터 수신")
        
        if data_count > 0:
            print("✅ Arduino가 데이터를 정상적으로 전송하고 있습니다!")
        else:
            print("❌ Arduino에서 데이터를 받지 못했습니다")
            
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    print("🔌 테스트 완료")

if __name__ == "__main__":
    test_arduino_quick()