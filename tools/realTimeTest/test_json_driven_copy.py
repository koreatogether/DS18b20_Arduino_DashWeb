import os, json, time, sys
import pytest
from conftest import read_output

def list_scenarios(scenario_dir):
    return [f for f in os.listdir(scenario_dir) if f.endswith('.json')]

def select_scenario(scenario_dir):
    # 환경변수에서 시나리오 지정 확인
    env_scenario = os.environ.get('PYTEST_SCENARIO')
    if env_scenario:
        scenario_path = os.path.join(scenario_dir, env_scenario)
        if os.path.exists(scenario_path):
            print(f"Using specified scenario: {env_scenario}")
            return env_scenario
        else:
            print(f"Specified scenario '{env_scenario}' not found. Showing available scenarios.")
    
    scenarios = list_scenarios(scenario_dir)
    print("Available scenarios:")
    print("** 0 is cancel **")
    print("0. cancel")
    for idx, name in enumerate(scenarios):
        print(f"{idx+1}. {name}")
    sel = input("Select scenario number: ")
    try:
        sel_idx = int(sel)
        if sel_idx == 0:
            import pytest
            pytest.skip("Canceled by user.")
        sel_idx -= 1
        if 0 <= sel_idx < len(scenarios):
            return scenarios[sel_idx]
    except ValueError:
        pass
    print("Invalid selection.")
    import pytest
    pytest.skip("Invalid selection.")

@pytest.mark.parametrize("specfile", [None])
def test_flow(ser, specfile):
    scenario_dir = os.path.join(os.path.dirname(__file__), "scenarioJson")
    
    # 환경 변수에서 시나리오 파일명 가져오기
    env_scenario = os.environ.get('PYTEST_SCENARIO')
    if env_scenario:
        specfile = env_scenario
        print(f"Using specified scenario: {specfile}")

    if specfile is None:
        specfile = select_scenario(scenario_dir)
        
    path = os.path.join(scenario_dir, specfile)
    spec = json.load(open(path, "r", encoding="utf-8"))
    time.sleep(1)
    initial_output = read_output(ser, timeout=5)
    print(f"[INFO] Initial board output: {initial_output[:100]}...")
    
    # 보드 상태 확인 및 강제 Normal 상태로 리셋
    print("[INFO] Forcing board to Normal state...")
    ser.write(b"reset\n")
    time.sleep(2)
    reset_output = read_output(ser, timeout=3)
    print(f"[INFO] Reset output: {reset_output[:100]}...")
    
    # 추가 안전장치: 여러 번 리셋 시도
    for i in range(3):
        ser.write(b"reset\n")
        time.sleep(1)
        output = read_output(ser, timeout=2)
        if "[시스템 준비 완료 - Normal 모드에서 대기 중]" in output or "Normal" in output:
            print(f"[INFO] Board successfully reset to Normal state (attempt {i+1})")
            break
        print(f"[INFO] Reset attempt {i+1} - output: {output[:50]}...")
    
    print(f"[INFO] Running scenario: {specfile}")
    import threading
    import itertools
    import sys
    stop_spinner = False
    def spinner():
        info = '\tPress CTRL+C twice to force terminate PROCESS.'
        for c in itertools.cycle(['|', '/', '-', '\\']):
            if stop_spinner:
                break
            sys.stdout.write(f'\r[진행 중] {c}{info}')
            sys.stdout.flush()
            time.sleep(0.2)
        sys.stdout.write('\r')
        sys.stdout.flush()
    spin_thread = threading.Thread(target=spinner)
    spin_thread.start()
    try:
        for step in spec["steps"]:
            # 조건 분기 step 지원
            if "if" in step:
                cond = step["if"].get("condition", "")
                # 간단한 조건 해석: appState==2 && response.contains('에러')
                # 실제 조건 해석은 필요에 따라 확장 가능
                last_out = ""
                if "response" in step["if"]:
                    last_out = step["if"]["response"]
                else:
                    try:
                        ser.reset_input_buffer()
                    except Exception:
                        pass
                    time.sleep(1)
                    last_out = read_output(ser, timeout=3)
                cond_true = False
                # 예시: appState==2 && response.contains('에러')
                if "appState==2" in cond:
                    if "[DEBUG] appState: 2" in last_out:
                        cond_true = True
                if "response.contains('에러')" in cond:
                    if "에러" in last_out:
                        cond_true = cond_true and True
                if cond_true:
                    for then_step in step["if"].get("then", []):
                        ser.write(then_step["send"].encode())
                        time.sleep(1)
                        out = read_output(ser, timeout=3)
                        expects = then_step["expect"]
                        if isinstance(expects, list):
                            for expect_line in expects:
                                assert expect_line.strip() in out.replace('\r', '').replace('\n', ''), f"'{expect_line.strip()}' not in\n{out}"
                        else:
                            for expect_line in expects.split('\n'):
                                assert expect_line.strip() in out.replace('\r', '').replace('\n', ''), f"'{expect_line.strip()}' not in\n{out}"
                else:
                    for else_step in step["if"].get("else", []):
                        ser.write(else_step["send"].encode())
                        time.sleep(1)
                        out = read_output(ser, timeout=3)
                        expects = else_step["expect"]
                        if isinstance(expects, list):
                            for expect_line in expects:
                                assert expect_line.strip() in out.replace('\r', '').replace('\n', ''), f"'{expect_line.strip()}' not in\n{out}"
                        else:
                            for expect_line in expects.split('\n'):
                                assert expect_line.strip() in out.replace('\r', '').replace('\n', ''), f"'{expect_line.strip()}' not in\n{out}"
            else:
                try:
                    ser.reset_input_buffer()
                except Exception:
                    pass
                ser.write(step["send"].encode())
                time.sleep(1)
                out = read_output(ser, timeout=3)
                expects = step["expect"]
                if isinstance(expects, list):
                    for expect_line in expects:
                        assert expect_line.strip() in out.replace('\r', '').replace('\n', ''), f"'{expect_line.strip()}' not in\n{out}"
                else:
                    for expect_line in expects.split('\n'):
                        assert expect_line.strip() in out.replace('\r', '').replace('\n', ''), f"'{expect_line.strip()}' not in\n{out}"
    finally:
        stop_spinner = True
        spin_thread.join()
        print("[시나리오 완료]")

if __name__ == "__main__":
    import pytest
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    pytest.main([os.path.basename(__file__)])
