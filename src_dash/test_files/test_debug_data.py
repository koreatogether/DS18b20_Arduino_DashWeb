"""
Arduino 데이터 수신 및 저장 상태 디버그
"""

import os
import sys
import time

from core.serial_json_communication import ArduinoJSONSerial

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.append(_ROOT)


def debug_arduino_data():
    print("🔍 Arduino 데이터 디버그 시작")

    # Arduino 연결
    arduino = ArduinoJSONSerial(port="COM4", baudrate=115200)

    if not arduino.connect():
        print("❌ Arduino 연결 실패")
        return

    if not arduino.start_reading():
        print("❌ 데이터 읽기 시작 실패")
        return

    print("✅ Arduino 연결 및 데이터 읽기 시작")
    print("📡 10초간 데이터 수집 중...")

    # 10초간 데이터 수집
    for i in range(10):
        time.sleep(1)

        # 현재 상태 확인
        stats = arduino.get_connection_stats()
        current_temps = arduino.get_current_temperatures()
        latest_data = arduino.get_latest_sensor_data(count=5)

        print(
            f"[{i+1:2d}초] 연결={stats['is_connected']}, "
            f"건강={arduino.is_healthy()}, "
            f"센서데이터={stats['sensor_data_count']}개, "
            f"현재온도={len(current_temps)}개"
        )

        # 최신 데이터 출력
        if latest_data:
            latest = latest_data[-1]
            print(
                f"      최신: ID={latest['sensor_id']}, "
                f"온도={latest['temperature']}°C, "
                f"시간={latest['timestamp'].strftime('%H:%M:%S')}"
            )

        # 현재 온도 출력
        if current_temps:
            temp_str = ", ".join([f"ID{k}:{v['temperature']:.1f}°C" for k, v in current_temps.items()])
            print(f"      현재온도: {temp_str}")

    # 최종 결과
    print("\n📊 최종 결과:")
    final_stats = arduino.get_connection_stats()
    final_temps = arduino.get_current_temperatures()

    print(f"   총 센서 데이터: {final_stats['sensor_data_count']}개")
    print(f"   현재 온도 센서: {len(final_temps)}개")
    print(f"   연결 상태: {'✅ 건강' if arduino.is_healthy() else '❌ 불량'}")

    if final_temps:
        print("   센서별 현재 온도:")
        for sensor_id, info in final_temps.items():
            print(f"     센서 {sensor_id}: {info['temperature']:.1f}°C ({info['status']})")
    else:
        print("   ⚠️ 현재 온도 데이터 없음")

    arduino.disconnect()
    print("🔌 연결 종료")


if __name__ == "__main__":
    debug_arduino_data()
