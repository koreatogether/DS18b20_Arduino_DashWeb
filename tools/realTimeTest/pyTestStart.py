import subprocess
import sys
import os
import argparse
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='Run DS18B20 real-time test scenarios')
    parser.add_argument('scenario', nargs='?', help='Scenario JSON file name (e.g., 02_multi_id_change_scenario.json)')
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)  # 작업 디렉터리 이동

    # 로그 디렉터리 생성
    logs_dir = os.path.join(script_dir, 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # 로그 파일명 생성 (현재 시간 기반)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(logs_dir, f'pyTest_logs_{timestamp}.log')

    test_file = os.path.join(script_dir, 'test_json_driven_copy.py')

    # 시나리오가 지정된 경우 환경변수로 전달
    env = os.environ.copy()
    if args.scenario:
        env['PYTEST_SCENARIO'] = args.scenario
        print(f"Running specific scenario: {args.scenario}")
    env['PYTHONIOENCODING'] = 'utf-8'

    cmd = [sys.executable, '-m', 'pytest', '-s', test_file]
    print(f"Running: {' '.join(cmd)}")
    print(f"Log will be saved to: {log_file}")

    # 테스트 시작 전 보드 하드 리셋(DTR 신호) 및 5초 대기, 시리얼 버퍼 완전 비우기
    try:
        import time
        import serial
        port = os.environ.get('PYTEST_SERIAL_PORT', 'COM4')
        ser = serial.Serial(port, 115200, timeout=2)
        ser.setDTR(False)
        time.sleep(0.1)
        ser.setDTR(True)
        print(f"[INFO] Board hard reset (DTR) on {port}, waiting 5 seconds...")
        time.sleep(5)  # 리셋 후 MCU 부팅 충분히 대기
        # 시리얼 버퍼 완전 비우기: 남아있는 모든 데이터 읽어서 버림
        ser.reset_input_buffer()
        time.sleep(0.2)
        flushed = 0
        while ser.in_waiting:
            _ = ser.read(ser.in_waiting)
            flushed += 1
            time.sleep(0.05)
            if flushed > 20:
                break
        ser.close()
        print(f"[INFO] Serial buffer flushed before test start.")
    except Exception as e:
        print(f"[WARN] Board reset/buffer flush skipped: {e}")

    # 로그 파일에 출력 저장하면서 동시에 콘솔에도 출력
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            # 실시간으로 출력을 읽어서 처리 (errors='replace'로 디코딩 에러 방지)
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     text=True, encoding='utf-8', errors='replace', env=env, bufsize=1, universal_newlines=True)

            output_lines = []
            for line in iter(process.stdout.readline, ''):
                print(line, end='')  # 콘솔 출력
                f.write(line)        # 파일 출력
                f.flush()            # 즉시 디스크에 저장
                output_lines.append(line)

            process.wait()
            result_code = process.returncode

    except Exception as e:
        print(f"Error during test execution: {e}")
        result_code = 1

    print(f"\nTest completed. Log saved to: {log_file}")
    sys.exit(result_code)

if __name__ == "__main__":
    main()
