"""
Arduino 연결 및 데이터 수신 테스트
"""

import time

import serial


def test_arduino_connection():
    try:
        # COM4 포트로 연결
        ser = serial.Serial("COM4", 115200, timeout=2)
        print("✅ Arduino 연결 성공!")

        # 연결 안정화 대기
        time.sleep(2)

        # 버퍼 클리어
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        print("📡 Arduino에서 데이터 수신 대기 중...")

        # 10초간 데이터 수신 시도
        start_time = time.time()
        received_data = []

        while time.time() - start_time < 10:
            if ser.in_waiting > 0:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if line:
                    print(f"📥 수신: {line}")
                    received_data.append(line)
            time.sleep(0.1)

        if not received_data:
            print("⚠️ Arduino에서 데이터를 받지 못했습니다")
            print("🔧 테스트 명령을 Arduino에 전송합니다...")

            # JSON 명령 전송
            test_commands = [
                '{"type":"request","action":"get_stats"}',
                '{"type":"config","action":"toggle_json_mode"}',
                "GET_STATUS",  # CSV 명령
                "HELP",  # CSV 명령
            ]

            for cmd in test_commands:
                print(f"📤 전송: {cmd}")
                ser.write((cmd + "\n").encode("utf-8"))
                time.sleep(1)

                # 응답 확인
                if ser.in_waiting > 0:
                    response = ser.readline().decode("utf-8", errors="ignore").strip()
                    if response:
                        print(f"📥 응답: {response}")

        ser.close()
        print("🔌 연결 종료")

        return len(received_data) > 0

    except Exception as e:
        print(f"❌ 오류: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Arduino 연결 테스트 시작")
    success = test_arduino_connection()

    if success:
        print("✅ 테스트 성공: Arduino가 데이터를 전송하고 있습니다!")
    else:
        print("❌ 테스트 실패: Arduino에서 데이터를 받지 못했습니다")
        print("💡 해결 방법:")
        print("   1. Arduino 코드가 업로드되었는지 확인")
        print("   2. 시리얼 모니터에서 Arduino 출력 확인")
        print("   3. DS18B20 센서 연결 확인")
