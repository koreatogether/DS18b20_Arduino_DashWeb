## DS18B20 Arduino DashWeb (UNO R4 WiFi)

Arduino Uno R4 WiFi 보드와 DS18B20 디지털 온도 센서를 이용해 신뢰성 있는 온도 수집과 직렬(JSON) 통신을 제공하는 펌웨어입니다. 코드 구조는 OOP/SOLID/DIP 원칙을 따르며, 센서 관리·명령 처리·상태 관리·통신을 역할별 컴포넌트로 분리했습니다.

### 주요 기능
- DS18B20 온도 센서 읽기 및 다중 센서 지원
- 직렬 JSON 통신(요청/응답, 상태/경고/센서 데이터)
- 하트비트/헬스체크 및 간단한 테스트 메시지 주기 전송
- 소프트웨어 리셋(Control: reset) 등 기본 제어 명령
- UNO R4 WiFi(48MHz, 32KB RAM, 256KB Flash)에 최적화된 빌드 세팅

### 하드웨어 요구사항
- Arduino Uno R4 WiFi
- DS18B20 센서 1개 이상(풀업 저항 포함 일반 배선)
- USB 케이블, PC (Windows 권장), VS Code + PlatformIO

---

## 프로젝트 구조(요약)

트래킹되는 핵심 디렉토리만 표기합니다. 일부 로컬 도구/개발 보조 폴더는 .gitignore로 제외됩니다.

```
docs/                # 일반 문서
docs_arduino/        # Arduino 관련 가이드/보고서
docs_dash/           # 대시보드 관련 문서
include/             # 공용 헤더
lib/                 # 외부/로컬 라이브러리(필요 시)
src/                 # Arduino 소스 (메인: DS18B20_Arduino.ino)
src_dash/            # (옵션) Python 대시보드/테스트 유틸 스크립트
platformio.ini       # PlatformIO 환경 설정 (UNO R4 WiFi)
README.md            # 현재 문서
```

주요 소스 구성(발췌):
- `src/DS18B20_Arduino.ino`: 진입점, 시스템 초기화/루프, JSON 모드 토글 지원
- `src/SerialCommunication.*`: 기본(텍스트/CSV) 직렬 통신 헬퍼
- `src/JsonCommunication.*`: JSON 메시지 송수신, 파싱/포맷팅
- `src/SensorManager.*`: DS18B20 초기화/읽기/헬스체크, 다중 센서 지원
- `src/CommandProcessor.*`: 수신 명령 처리(JSON/기본)
- `src/SystemState.*`: 주기 타이머, 카운터 등 상태 관리

의존 라이브러리(PlatformIO lib_deps):
- DallasTemperature
- OneWire
- ArduinoJson

---

## 빠른 시작 (Windows / VS Code + PlatformIO)

1) VS Code에 PlatformIO IDE 확장 설치
2) 본 저장소를 열기
3) 보드/포트 확인 및 `platformio.ini` 포트 조정
	- 기본값: `upload_port = COM4`, `monitor_port = COM4`
4) 빌드/업로드/모니터

명령줄에서 실행하려면:

```bat
:: 빌드
pio run -e uno_r4_wifi

:: 업로드 (보드 연결 필요)
pio run -e uno_r4_wifi --target upload

:: 시리얼 모니터 (기본 115200bps)
pio device monitor -b 115200 -p COM4
```

메모리 사용 예(최근 빌드): RAM ~12%, Flash ~27% (참고용)

---

## 직렬(JSON) 통신 요약

펌웨어는 기본적으로 JSON 모드가 활성화되어 있습니다(`useJsonMode = true`).

요청 예시(호스트 → 보드):
- 설정 토글: `{ "type": "config", "content": "toggle_json_mode" }`
- 상태 조회: `{ "type": "request", "content": "get_stats" }`
- 센서 목록: `{ "type": "request", "content": "get_sensors" }`
- 온도 요청: `{ "type": "request", "content": "get_temperature" }`
- 제어(리셋): `{ "type": "control", "content": "reset" }`

응답/이벤트 예시(보드 → 호스트):
- 시스템 메시지: `{ "level": "info", "message": "Arduino started..." }`
- 센서 데이터: `{ "sensorId": 1, "temperature": 25.5, "status": "ok" }`
- 경고: `{ "sensorId": 1, "type": "HIGH_TEMP", "value": 31.2, "level": "warning" }`

CSV/텍스트 모드도 지원하나, 가급적 JSON 사용을 권장합니다.

---

## 설정(PlatformIO)

`platformio.ini` 주요 항목:
- `board = uno_r4_wifi`
- `upload_port`, `monitor_port`: 환경에 맞게 COM 포트 지정
- `monitor_speed = 115200`
- 필요한 경우 빌드 플래그/라이브러리 의존을 추가 조정

---

## 문제 해결(Troubleshooting)
- 업로드/모니터 실패: 장치 관리자에서 COM 포트 확인 후 `platformio.ini` 포트 수정
- 센서 미검출: 배선/풀업 저항 확인, 데이터핀 번호(`ONE_WIRE_BUS`) 확인
- JSON 파싱 오류: 호스트에서 전송한 JSON 형식/인코딩 검토

---

## 개발 / 코드 품질(workflow)
Python 기반 보조 스크립트(`src_dash/`, `tools/`)는 다음 품질 도구 체인을 사용합니다.

| 도구        | 목적                          | 비고                                            |
| ----------- | ----------------------------- | ----------------------------------------------- |
| `ruff`      | Lint (E,F,W) + 빠른 규칙 검사 | flake8 대체, `line-length=110` (pyproject.toml) |
| `black`     | 포맷터                        | 서식 일관성, 라인 길이 110                      |
| `isort`     | 임포트 정렬                   | CI 유지 (추후 ruff I 규칙으로 통합 가능)        |
| `autoflake` | 미사용 import/변수 제거       | 파괴적 변경은 pre-commit/수동 사용 권장         |
| `pyright`   | 정적 타입 검사                | VS Code(Pylance) 연동                           |

### 변경 사항 요약
* `.flake8` 설정 파일 제거 → `pyproject.toml` 중심 구성
* CI / Pre-commit 모두 flake8 → ruff 로 전환
* 최대 라인 길이 110 으로 통일(ruff / black / 편집기)
* 레거시 스크립트(`tools/legacy/auto_fix_flake8.py`, `tools/legacy/fix_flake8_errors.py`)로 이동 (참고 전용)
* 과거 flake8 결과 로그는 `logs/quality/legacy_flake8/` 로 보관 (필요 시 이력 비교 용도)

### 로컬 품질 체크 (선택)
```bash
ruff check src_dash src
black --check src_dash src
isort --check-only src_dash src
```

자동 수정 파이프라인은 `tools/auto_lint_and_format.py` 에서 실행 순서:
1. autoflake (옵션) → 2. isort → 3. ruff --fix → 4. black → 5. ruff 재검사 → 6. pyright

### CI 반영
`.github/workflows/ci-lint.yml` 에서 flake8 단계가 제거되고 `Ruff lint` 단계가 추가되었습니다.

---

## 라이선스 / 기여
- 라이선스: TBD (프로젝트 요구에 맞게 지정 예정)
- 이슈/PR 환영: 재현 가능한 정보와 로그를 포함해 주세요.

---

문의/지원: 저장소 이슈 탭을 이용해 주세요.