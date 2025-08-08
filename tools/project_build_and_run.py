import subprocess
import sys
import os
import time
import traceback
from datetime import datetime

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN_PY = os.path.join(REPO_ROOT, 'src_dash', 'app.py')  # 메인 파일 절대경로

# Python 실행 파일 경로 (가상환경 우선, 없으면 시스템 Python)
def get_python_executable():
    venv_python = os.path.join(os.getcwd(), '.venv', 'Scripts', 'python.exe')
    if os.path.exists(venv_python):
        return venv_python
    else:
        return sys.executable  # 시스템 Python 사용

VENV_PYTHON = get_python_executable()

# exe 파일명 및 저장 경로
def get_exe_path():
    now = datetime.now().strftime('%Y%m%d_%H%M%S')
    exe_dir = os.path.join(REPO_ROOT, 'src_dash', 'exe')
    os.makedirs(exe_dir, exist_ok=True)
    exe_name = f'{now}_18b20DashBoard.exe'
    return os.path.join(exe_dir, exe_name)

# 1. 코드 품질 검사 (flake8, pylint) - 선택적 실행
def run_code_quality():
    print('--- 코드 품질 검사 시작 ---')
    # flake8 검사
    try:
        print('--- flake8 검사 ---')
        flake8_result = subprocess.run(
            [VENV_PYTHON, '-m', 'flake8', os.path.join(REPO_ROOT, 'src_dash')],
            capture_output=True, text=True, timeout=30
        )
        if flake8_result.stdout:
            print(flake8_result.stdout)
        if flake8_result.stderr:
            print("flake8 stderr:", flake8_result.stderr)
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"flake8 검사 건너뜀: {e}")
        flake8_result = None

    # pylint 검사
    try:
        print('--- pylint 검사 ---')
        pylint_result = subprocess.run(
            [VENV_PYTHON, '-m', 'pylint', MAIN_PY],
            capture_output=True, text=True, timeout=30
        )
        if pylint_result.stdout:
            print(pylint_result.stdout)
        if pylint_result.stderr:
            print("pylint stderr:", pylint_result.stderr)
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"pylint 검사 건너뜀: {e}")
        pylint_result = None

    return flake8_result, pylint_result

# 2. pyinstaller로 exe 변환
def build_exe():
    print('--- pyinstaller 빌드 ---')
    pyinstaller_path = r'C:\Users\h\AppData\Roaming\Python\Python313\Scripts\pyinstaller.exe'
    exe_path = get_exe_path()
    cmd = [
        pyinstaller_path, '--onefile', '--windowed', MAIN_PY,
        '--distpath', os.path.dirname(exe_path), '--name', os.path.splitext(os.path.basename(exe_path))[0]
    ]
    print(f'실행 명령: {" ".join(cmd)}')
    build_result = subprocess.run(cmd, capture_output=True, text=True)
    print('stdout:', build_result.stdout)
    print('stderr:', build_result.stderr)
    return build_result, exe_path, cmd

# 3. exe 파일 실행
def run_exe(exe_path):
    if os.path.exists(exe_path):
        print(f'--- {exe_path} 실행 ---')
        subprocess.run([exe_path], check=False)
    else:
        print(f'실행 파일({exe_path})이 존재하지 않습니다.')

def save_error_log(error_title, error_content, extra_info=None):
    log_dir = os.path.join(REPO_ROOT, 'docs_dash', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    now = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{now}_{error_title}.md'
    filepath = os.path.join(log_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f'# {error_title} 에러 로그\n\n')
        f.write('## 에러 상황\n')
        f.write(error_content)
        if extra_info:
            f.write('\n\n## 추가 정보\n')
            f.write(extra_info)
    print(f'에러 로그 저장: {filepath}')

def run_serial_preview(max_iters=5, interval_sec=0.5):
    """시리얼 통신 관련 출력 미리보기 (5회 제한, 구분선 표시)

    하드웨어 미연결 시에도 안전하게 종료되며, 오류는 로그로 남김.
    """
    print('--- 시리얼 통신 미리보기 시작 ---')
    try:
        # src_dash 모듈 임포트 경로 보장
        root_dir = REPO_ROOT
        if root_dir not in sys.path:
            sys.path.insert(0, root_dir)

        from src_dash.serial_json_communication import ArduinoJSONSerial as ArduinoSerial
        try:
            from src_dash.port_manager import find_arduino_port
            detected = find_arduino_port()
        except Exception:
            detected = None

        ard = ArduinoSerial(port=detected or 'COM4', baudrate=115200)
        if ard.connect():
            ard.start_reading()
            for i in range(max_iters):
                time.sleep(interval_sec)
                stats = ard.get_connection_stats()
                temps = ard.get_current_temperatures()
                print(f"[{i+1}/{max_iters}] 연결={stats['is_connected']}, 건강={stats['is_healthy']}, 수신={stats['total_received']}개, 센서={len(temps)}개")
                if i < max_iters - 1:
                    print('----')
            ard.disconnect()
        else:
            print('연결 실패: 하드웨어 미연결이거나 포트 점유 상태일 수 있습니다.')
            # 그래도 5회 형식 출력 유지
            for i in range(max_iters):
                print(f"[{i+1}/{max_iters}] 연결=False, 건강=False, 수신=0개, 센서=0개")
                if i < max_iters - 1:
                    print('----')
    except Exception as e:
        tb = traceback.format_exc()
        save_error_log('serial_preview', f'{e}\n\n{tb}')
    finally:
        print('--- 시리얼 통신 미리보기 종료 ---')

if __name__ == '__main__':
    flake8_result, pylint_result = run_code_quality()
    if flake8_result is not None and flake8_result.returncode != 0:
        save_error_log('flake8', (flake8_result.stdout or '') + '\n' + (flake8_result.stderr or ''))
    if pylint_result is not None and pylint_result.returncode != 0:
        save_error_log('pylint', (pylint_result.stdout or '') + '\n' + (pylint_result.stderr or ''))
    
    # exe 패키징 과정 - 시간이 오래 걸리므로 주석 처리
    # build_result, exe_path, build_cmd = build_exe()
    # if build_result.returncode != 0 or not os.path.exists(exe_path):
    #     extra = f'실행 명령: {" ".join(build_cmd)}\n\n파일 존재 여부: {os.path.exists(exe_path)}\n경로: {exe_path}'
    #     save_error_log('pyinstaller', build_result.stdout + '\n' + build_result.stderr, extra_info=extra)
    # run_exe(exe_path)
    
    print("코드 품질 검사 완료. exe 패키징은 주석 처리됨.")
    print("exe 패키징이 필요하면 위의 주석을 해제하세요.")

    # 앱 실행 전 간단한 시리얼 미리보기 (5회)
    run_serial_preview(max_iters=5, interval_sec=0.5)

    # 코드 검사 후 app.py 자동 실행 (출력 압축 + 장애 시 상세 출력)
    print("app.py를 실행합니다...")
    app_path = MAIN_PY
    try:
        env = os.environ.copy()
        env.setdefault('PYTHONIOENCODING', 'utf-8')
        env.setdefault('PYTHONUTF8', '1')

        import threading
        import queue

        def run_app_with_buffered_output(cmd, env):
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    text=True, encoding='utf-8', errors='replace', env=env)
            out_q = queue.Queue()
            err_q = queue.Queue()

            def enqueue_output(stream, q):
                for line in iter(stream.readline, ''):
                    q.put(line)
                stream.close()

            t_out = threading.Thread(target=enqueue_output, args=(proc.stdout, out_q), daemon=True)
            t_err = threading.Thread(target=enqueue_output, args=(proc.stderr, err_q), daemon=True)
            t_out.start()
            t_err.start()

            buffer = []
            last_flush = time.time()
            detailed_mode = False
            error_keywords = [
                '연결 끊김', '연결 상태 불량', '시뮬레이션 모드',
                'PermissionError', '에러', '오류', 'error', 'exception',
                'Traceback', 'KeyboardInterrupt', 'could not open port', 'Permission denied'
            ]
            recovery_keywords = [
                '🟢 Arduino 연결됨', '연결됨', '재연결 성공',
                '✅ 수동 재연결 성공', '✅ Arduino 연결 및 데이터 읽기 시작 성공',
                '✅ Arduino 연결 성공', '실제 데이터 사용', 'Dash is running'
            ]

            def flush_buffer():
                nonlocal buffer, last_flush
                if buffer:
                    print(''.join(buffer), end='')
                    buffer.clear()
                    last_flush = time.time()

            try:
                while proc.poll() is None:
                    now = time.time()
                    while not out_q.empty():
                        line = out_q.get()
                        buffer.append(line)
                        if any(k in line for k in error_keywords):
                            flush_buffer()
                            detailed_mode = True
                        elif detailed_mode and any(k in line for k in recovery_keywords):
                            flush_buffer()
                            detailed_mode = False
                    while not err_q.empty():
                        line = err_q.get()
                        buffer.append(line)
                        if any(k in line for k in error_keywords):
                            flush_buffer()
                            detailed_mode = True
                        elif detailed_mode and any(k in line for k in recovery_keywords):
                            flush_buffer()
                            detailed_mode = False

                    if not detailed_mode and buffer and (now - last_flush > 5):
                        flush_buffer()
                    if detailed_mode and buffer and (now - last_flush > 2):
                        flush_buffer()

                    time.sleep(0.1)

                while not out_q.empty():
                    buffer.append(out_q.get())
                while not err_q.empty():
                    buffer.append(err_q.get())
                flush_buffer()
            except Exception as e:
                print(f'출력 처리 중 오류: {e}')
            return proc.returncode

        cmd = [VENV_PYTHON, app_path]
        retcode = run_app_with_buffered_output(cmd, env)
        if retcode != 0:
            save_error_log('app_run', '앱 실행 오류 또는 비정상 종료')
        else:
            print('app.py 정상 종료')
    except Exception as e:
        tb = traceback.format_exc()
        save_error_log('app_run_exception', f'{e}\n\n{tb}')
