"""
안전한 Arduino 데이터 디버그 (Ctrl+C 지원)
"""
import signal
import sys
import time
from serial_json_communication import ArduinoJSONSerial

# 전역 변수
arduino = None
running = True

def signal_handler(sig, frame):
    """Ctrl+C 핸들러"""
    global running, arduino
    print("\n🛑 종료 신호 수신...")
    running = False
    
    if arduino:
        try:
            arduino.disconnect()
            print("🔌 Arduino 연결 해제 완료")
        except Exception as e:
            print(f"⚠️ 연결 해제 중 오류: {e}")
    
    print("✅ 안전하게 종료됨")
    sys.exit(0)

def safe_debug_arduino():
    global arduino, running
    
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🔍 안전한 Arduino 데이터 디버그 시작")
    print("💡 Ctrl+C로 언제든 안전하게 종료 가능")
    
    # Arduino 연결
    arduino = ArduinoJSONSerial(port='COM4', baudrate=115200)
    
    if not arduino.connect():
        print("❌ Arduino 연결 실패")
        return
    
    if not arduino.start_reading():
        print("❌ 데이터 읽기 시작 실패")
        arduino.disconnect()
        return
    
    print("✅ Arduino 연결 및 데이터 읽기 시작")
    print("📡 데이터 수집 중... (Ctrl+C로 종료)")
    
    # 안전한 루프
    counter = 0
    while running:
        try:
            counter += 1
            
            # 5초마다 상태 출력
            if counter % 5 == 0:
                stats = arduino.get_connection_stats()
                current_temps = arduino.get_current_temperatures()
                latest_data = arduino.get_latest_sensor_data(count=3)
                
                print(f"\n[{counter:3d}초] 📊 상태:")
                print(f"   연결: {stats['is_connected']}")
                print(f"   건강: {arduino.is_healthy()}")
                print(f"   총 데이터: {stats['sensor_data_count']}개")
                print(f"   현재 온도: {len(current_temps)}개 센서")
                
                # 최신 데이터 출력
                if latest_data:
                    print("   📥 최신 3개 데이터:")
                    for i, data in enumerate(latest_data[-3:], 1):
                        print(f"      {i}. ID{data['sensor_id']}: {data['temperature']}°C "
                              f"({data['timestamp'].strftime('%H:%M:%S')})")
                else:
                    print("   ⚠️ 수신된 데이터 없음")
                
                # 현재 온도 출력
                if current_temps:
                    temp_list = [f"ID{k}:{v['temperature']:.1f}°C" 
                               for k, v in current_temps.items()]
                    print(f"   🌡️ 현재: {', '.join(temp_list)}")
            
            time.sleep(1)  # 1초 대기
            
        except KeyboardInterrupt:
            # 이중 안전장치
            break
        except Exception as e:
            print(f"⚠️ 루프 중 오류: {e}")
            time.sleep(1)
    
    # 정리
    if arduino:
        arduino.disconnect()
    print("🔌 연결 해제 완료")

if __name__ == "__main__":
    try:
        safe_debug_arduino()
    except Exception as e:
        print(f"❌ 치명적 오류: {e}")
    finally:
        if arduino:
            arduino.disconnect()
        print("✅ 프로그램 종료")