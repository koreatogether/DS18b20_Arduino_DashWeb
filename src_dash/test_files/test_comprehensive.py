"""
포괄적인 Arduino DS18B20 테스트
- 자동 포트 탐지
- 시리얼 통신 확인
- 센서 데이터 수신 확인
- 명령 응답 테스트
"""

import os
import sys
import time

import serial
from core.port_manager import find_arduino_port, list_available_ports

# 테스트 실행 시 패키지 루트 경로 추가 (동적, 단 1회)
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.append(_ROOT)


def test_serial_communication(port_name, duration=10):
    """시리얼 통신 테스트"""
    print(f"📡 {port_name}로 Arduino 연결 시도...")

    try:
        ser = serial.Serial(port_name, 115200, timeout=2)
        print("✅ Arduino 연결 성공!")

        # 연결 안정화
        time.sleep(2)
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        print(f"📊 {duration}초간 데이터 수신 테스트...")

        start_time = time.time()
        received_data = []
        command_responses = []

        # 테스트 명령 전송
        test_commands = ["PING", "STATUS", "GET_SENSORS", "HELP"]
        command_index = 0
        last_command_time = 0

        while time.time() - start_time < duration:
            current_time = time.time()

            # 2초마다 명령 전송
            if current_time - last_command_time > 2 and command_index < len(test_commands):
                cmd = test_commands[command_index]
                print(f"📤 명령 전송: {cmd}")
                ser.write((cmd + "\n").encode("utf-8"))
                command_index += 1
                last_command_time = current_time

            # 데이터 수신 확인
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode("utf-8", errors="ignore").strip()
                    if line:
                        print(f"📥 수신: {line}")
                        received_data.append(line)

                        # 명령 응답 체크
                        if any(keyword in line for keyword in ["PONG", "ACK", "SYSTEM", "STATUS"]):
                            command_responses.append(line)

                except Exception as e:
                    print(f"⚠️ 디코딩 오류: {e}")

            time.sleep(0.1)

        ser.close()
        print("🔌 연결 종료")

        # 결과 분석
        # 정적 문자열: f 제거 (F541 방지)
        print("\n📊 테스트 결과:")
        print(f"  📥 총 수신 데이터: {len(received_data)}개")
        print(f"  📤 명령 응답: {len(command_responses)}개")

        # 데이터 유형 분석
        sensor_data_count = sum(1 for data in received_data if "TEMP" in data or "SENSOR" in data)
        system_messages = sum(1 for data in received_data if "SYSTEM" in data or "TEST" in data)

        print(f"  🌡️ 센서 데이터: {sensor_data_count}개")
        print(f"  🔧 시스템 메시지: {system_messages}개")

        return {
            "success": len(received_data) > 0,
            "total_data": len(received_data),
            "command_responses": len(command_responses),
            "sensor_data": sensor_data_count,
            "system_messages": system_messages,
        }

    except Exception as e:
        print(f"❌ 연결 오류: {e}")
        return {"success": False, "error": str(e)}


def main():
    print("🧪 Arduino DS18B20 포괄적인 테스트 시작")
    print("=" * 50)

    # 1. 포트 목록 확인
    print("\n1️⃣ 사용 가능한 포트 확인:")
    ports = list_available_ports()
    for port in ports:
        print(f"  📍 {port['device']}: {port['description']}")

    if not ports:
        print("❌ 사용 가능한 포트가 없습니다!")
        return

    # 2. Arduino 포트 자동 탐지
    print("\n2️⃣ Arduino 포트 자동 탐지:")
    arduino_port = find_arduino_port()

    if arduino_port:
        print(f"✅ Arduino 발견: {arduino_port}")
        target_port = arduino_port
    else:
        print("⚠️ Arduino 자동 탐지 실패, COM4 시도...")
        target_port = "COM4"

    # 3. 시리얼 통신 테스트
    print(f"\n3️⃣ 시리얼 통신 테스트 ({target_port}):")
    result = test_serial_communication(target_port, duration=15)

    # 4. 결과 요약
    print("\n" + "=" * 50)
    print("📋 테스트 요약:")

    if result["success"]:
        print("✅ 전체 테스트 성공!")
        print(f"  📊 데이터 수신률: {result['total_data']/15:.1f} 메시지/초")

        if result["sensor_data"] > 0:
            print(f"  🌡️ 센서 데이터 정상 수신 (총 {result['sensor_data']}개)")
        else:
            print("  ⚠️ 센서 데이터 미확인 - 센서 연결 상태 점검 필요")

        if result["command_responses"] > 0:
            # 동적으로 응답 개수 포함
            responses = result["command_responses"]
            print(f"  📤 명령 응답 정상 (총 {responses}개)")
        else:
            print("  ⚠️ 명령 응답 미확인 - 펌웨어 상태 점검 필요")

    else:
        print("❌ 테스트 실패!")
        if "error" in result:
            print(f"  💬 오류 내용: {result['error']}")

        print("\n💡 해결 방법:")
        print("  1. Arduino가 컴퓨터에 제대로 연결되었는지 확인")
        print("  2. Arduino IDE에서 펌웨어가 업로드되었는지 확인")
        print("  3. DS18B20 센서가 올바르게 연결되었는지 확인")
        print("  4. 시리얼 모니터에서 Arduino 출력 직접 확인")


if __name__ == "__main__":
    main()
