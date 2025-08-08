# DS18B20 Embedded Application Test Framework Setup

이 문서는 PlatformIO + PyTest + JSON 기반 미니 테스트 프레임워크를 빠르게 설치 및 설정하는 절차를 안내합니다.

## 1. 가상환경 및 의존성 설치

1. 프로젝트 루트에서 가상환경 생성 및 활성화
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. `requirements.txt`에 다음 항목 추가:
   ```txt
   pytest
   pyserial
   jsonschema  # (선택) JSON 스펙 검증용
   ```
3. 의존성 설치
   ```bash
   pip install -r requirements.txt
   ```

## 2. PlatformIO 설정

- `platformio.ini` 수정:
  ```ini
  [env:uno_r4_wifi]
  platform = atmelavr
  board = uno_r4_wifi
  framework = arduino

  [env:test]
  platform = native
  build_flags =
    -DTEST_MODE
  test_build_src = yes
  ```

## 3. JSON 기반 테스트 시나리오 작성

- 테스트 스펙 폴더 생성: `tests/specs`
- 예시: `sensor_id_change.json`
  ```json
  {
    "description": "개별 센서 ID 변경 흐름",
    "steps": [
      {"send": "m\n", "expect": "센서 제어 메뉴"},
      {"send": "1\n", "expect": "센서 ID 조정 메뉴"},
      {"send": "2\n", "expect": "센서 2번을 변경할까요?"}
    ]
  }
  ```

## 4. PyTest 설정 및 헬퍼 작성

- `tests/conftest.py`
  ```python
  import pytest, serial, time

  @pytest.fixture(scope="session")
  def ser():
      port = "COM4"
      s = serial.Serial(port, 115200, timeout=2)
      time.sleep(2)
      yield s
      s.close()

  def read_output(ser, timeout=2):
      end = time.time() + timeout
      buf = ""
      while time.time() < end:
          buf += ser.readline().decode(errors="ignore")
      return buf
  ```

## 5. JSON 드리븐 테스트 러너 작성

- `tests/test_json_driven.py`
  ```python
  import pytest, json, os
  from .conftest import read_output

  @pytest.mark.parametrize("specfile", ["sensor_id_change.json"])
  def test_flow(ser, specfile):
      path = os.path.join(os.path.dirname(__file__), "specs", specfile)
      spec = json.load(open(path, "r", encoding="utf-8"))

      for step in spec["steps"]:
          ser.write(step["send"].encode())
          time.sleep(0.5)
          out = read_output(ser, timeout=3)
          assert step["expect"] in out, f"{step['expect']} not in\n{out}"
  ```

## 6. VS Code & CI 통합

- `.vscode/tasks.json`에 `pytest` 실행 태스크 추가
- GitHub Actions 예시:
  ```yaml
  - name: Build Firmware
    run: pio run -e uno_r4_wifi

  - name: Run Integration Tests
    run: pytest -q
  ```

---

위 가이드에 따라 설정 후, `pytest`를 실행하면 JSON 스펙 기반으로 시리얼 연동 테스트를 자동으로 수행할 수 있습니다.
