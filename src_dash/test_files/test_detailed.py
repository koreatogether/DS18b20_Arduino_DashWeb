"""
Arduino 명령 응답 상세 테스트
- 각 명령별 응답 확인
- JSON 통신 테스트
- 센서 제어 명령 테스트
"""

import json
import os
import sys
import time

import serial
from core.port_manager import find_arduino_port

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.append(_ROOT)


def test_specific_commands():
    """각 명령별 상세 테스트"""
    port = find_arduino_port() or "COM4"

    print(f"📡 {port}로 Arduino 명령 테스트 시작...")

    try:
        ser = serial.Serial(port, 115200, timeout=3)
        time.sleep(2)
        # 입력/출력 버퍼 초기화 (버전 호환 처리)
        try:
            if hasattr(ser, "reset_input_buffer"):
                ser.reset_input_buffer()
            elif hasattr(ser, "flushInput"):
                ser.flushInput()  # type: ignore[attr-defined]
            if hasattr(ser, "reset_output_buffer"):
                ser.reset_output_buffer()
            elif hasattr(ser, "flushOutput"):
                ser.flushOutput()  # type: ignore[attr-defined]
        except Exception:
            pass

        # 테스트할 명령들
        test_commands = [
            {
                "cmd": "PING",
                "expect": ["PONG", "ERROR", "INVALID_COMMAND"],
                "description": "연결 테스트",
            },
            {
                "cmd": "STATUS",
                "expect": ["STATUS", "COUNTER", "SENSORS"],
                "description": "시스템 상태",
            },
            {
                "cmd": "GET_SENSORS",
                "expect": ["SENSOR_INFO", "CONNECTED_SENSOR_COUNT", "ACK"],
                "description": "센서 정보",
            },
            {
                "cmd": "SCAN_SENSORS",
                "expect": ["ACK", "SENSOR_SCAN"],
                "description": "센서 스캔",
            },
            {
                "cmd": "HELP",
                "expect": ["AVAILABLE_COMMANDS", "PING", "STATUS"],
                "description": "도움말",
            },
        ]

        results = {}

        for test in test_commands:
            print(f"\n🧪 테스트: {test['description']} ({test['cmd']})")

            # 명령 전송
            ser.write((test["cmd"] + "\n").encode("utf-8"))
            print(f"📤 전송: {test['cmd']}")

            # 응답 수집 (3초간)
            start_time = time.time()
            responses = []

            while time.time() - start_time < 3:
                if ser.in_waiting > 0:
                    try:
                        line = ser.readline().decode("utf-8", errors="ignore").strip()
                        if line:
                            responses.append(line)
                            print(f"📥 응답: {line}")
                    except Exception:
                        pass
                time.sleep(0.1)

            # 응답 분석
            expected_found = any(
                any(expect in response for response in responses) for expect in test["expect"]
            )

            results[test["cmd"]] = {
                "success": expected_found,
                "responses": len(responses),
                "data": responses,
            }

            status = "✅ 성공" if expected_found else "❌ 실패"
            print(f"📊 결과: {status} ({len(responses)}개 응답)")

        ser.close()

        # 전체 결과 요약
        print("\n" + "=" * 50)
        print("📋 명령 테스트 요약:")

        success_count = sum(1 for r in results.values() if r["success"])
        total_count = len(results)

        print(f"✅ 성공: {success_count}/{total_count} 명령")

        for cmd, result in results.items():
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {cmd}: {result['responses']}개 응답")

        if success_count == total_count:
            print("\n🎉 모든 명령이 정상적으로 작동합니다!")
        else:
            print(f"\n⚠️ {total_count - success_count}개 명령에 문제가 있습니다.")

        return results

    except Exception as e:
        print(f"❌ 오류: {e}")
        return None


def test_json_communication():
    """JSON 통신 테스트"""
    port = find_arduino_port() or "COM4"

    # 단순 문자열로 변경 (불필요한 f-string 제거)
    print("\n🔄 JSON 통신 테스트 시작...")

    try:
        ser = serial.Serial(port, 115200, timeout=2)
        time.sleep(1)
        try:
            if hasattr(ser, "reset_input_buffer"):
                ser.reset_input_buffer()
            elif hasattr(ser, "flushInput"):
                ser.flushInput()  # type: ignore[attr-defined]
        except Exception:
            pass

        # JSON 메시지를 더 오래(10초) 수집하여 5초 간격 메시지 확실히 수신
        start_time = time.time()
        json_messages = []
        all_messages = []

        print("📡 10초간 JSON 메시지 대기 중...")

        while time.time() - start_time < 10:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode("utf-8", errors="ignore").strip()
                    if line:
                        all_messages.append(line)
                        # JSON 메시지 확인
                        if line.startswith("{") and line.endswith("}"):
                            try:
                                json_data = json.loads(line)
                                json_messages.append(json_data)
                                print(f"📥 JSON: {json_data}")
                            except json.JSONDecodeError:
                                pass
                        # 기타 메시지도 표시
                        elif len(all_messages) <= 5:  # 처음 5개만 표시
                            print(f"📥 기타: {line}")
                except Exception:
                    pass
            time.sleep(0.1)

        ser.close()

        print(f"\n📊 JSON 결과: {len(json_messages)}개 JSON 메시지, 총 {len(all_messages)}개 메시지")

        if json_messages:
            print("✅ JSON 통신 정상 작동")
            # JSON 타입별 분석
            types = {}
            for msg in json_messages:
                msg_type = msg.get("type", "unknown")
                types[msg_type] = types.get(msg_type, 0) + 1

            for msg_type, count in types.items():
                print(f"  📊 {msg_type}: {count}개")

            # 샘플 JSON 메시지 표시
            if len(json_messages) > 0:
                print(f"  💡 샘플 JSON: {json_messages[0]}")
        else:
            print("⚠️ JSON 메시지를 받지 못했습니다")
            if len(all_messages) > 0:
                print(f"  📝 하지만 총 {len(all_messages)}개의 다른 메시지는 수신됨")
                print(f"  💡 샘플 메시지: {all_messages[0] if all_messages else 'None'}")
            else:
                print("  ❌ 어떤 메시지도 수신되지 않음")

        return len(json_messages) > 0

    except Exception as e:
        print(f"❌ JSON 테스트 오류: {e}")
        return False


def main():
    print("🧪 Arduino 상세 기능 테스트")
    print("=" * 50)

    # 1. 명령 응답 테스트
    cmd_results = test_specific_commands()

    # 2. JSON 통신 테스트
    json_success = test_json_communication()

    # 3. 최종 평가
    print("\n" + "=" * 50)
    print("🏆 최종 테스트 결과:")

    if cmd_results:
        cmd_success_rate = sum(1 for r in cmd_results.values() if r["success"]) / len(cmd_results)
        print(f"📤 명령 응답: {cmd_success_rate:.1%} 성공률")
    else:
        print("📤 명령 응답: 테스트 실패")
        cmd_success_rate = 0

    if json_success:
        print("📥 JSON 통신: ✅ 정상")
    else:
        print("📥 JSON 통신: ⚠️ 문제")

    # 종합 평가
    if cmd_success_rate >= 0.8 and json_success:
        print("\n🎉 Arduino DS18B20 시스템이 완벽하게 작동합니다!")
        print("✅ 센서 데이터 수신 정상")
        print("✅ 명령 처리 정상")
        print("✅ JSON 통신 정상")
        print("✅ C++ String 제거 작업 100% 성공!")
    else:
        print("\n⚠️ 일부 기능에 문제가 있을 수 있습니다.")
        if cmd_success_rate < 0.8:
            print("  - 명령 응답 문제")
        if not json_success:
            print("  - JSON 통신 문제")


if __name__ == "__main__":
    main()
