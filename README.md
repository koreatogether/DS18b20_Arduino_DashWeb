## DS18B20 Arduino DashWeb (UNO R4 WiFi)

Arduino Uno R4 WiFi 보드와 DS18B20 디지털 온도 센서를 이용해 안정적이고 검증 가능한(Validation & Health Monitoring) 온도 수집 + JSON/CSV 직렬 통신 + 선택형 Python Dash 웹 대시보드를 제공하는 프로젝트입니다. 코드 구조는 OOP/SOLID/DIP 원칙을 따르며, 센서 관리·명령 처리·상태 관리·통신·프론트엔드 표시를 역할별 컴포넌트로 분리했습니다.

### 주요 기능 (Firmware)
- 다중 DS18B20 센서 스캔 / 동적 개수 제한 (MAX_SENSORS)
- 센서별 검증 로직: 범위 체크(-55~125℃), 급격 변화 감지(MAX_TEMP_CHANGE), 연결상태 자동 복구
- Scratchpad TH(Byte2)를 활용한 사용자 Sensor ID 저장/변경(EEPROM 영속화) & 검증 (`changeSensorId` + `verifySensorIdChange`)
- 센서 개별 측정 주기 커스터마이징 (기본 1s conversion → per-sensor interval 관리)
- 통합 에러/상태 이벤트: READ_ERROR / TEMP_OUT_OF_RANGE / SUDDEN_CHANGE / DISCONNECTED / RECONNECTED
- JSON 기반 직렬 메시지 (sensor / system / heartbeat / status / alert / error) + CSV 하위호환 모드
- 하트비트(업타임, 메모리, health) 및 주기적 Health Check (연결/미연결 센서 카운트 보고)
- UNO R4 WiFi(48MHz, 32KB RAM, 256KB Flash)에 최적화 (12-bit 변환 750ms 고려한 batch request + interval loop)

### 주요 기능 (Dashboard / Host Python)
- PySerial 기반 실시간 수집 스레드 (비차단 read loop, in_waiting burst 처리)
- JSON/CSV 자동 구분 파싱 + 센서 주소(System 메시지에서 추출) 연계 표시
- 최근 센서 데이터(디폴트 50개) 요약 그래프 + 센서별 상세 그래프
- Night / Day UI 모드 (plotly_white / plotly_dark 동적 템플릿)
- 센서 주소(ROM Code) 16진 포매팅 및 UI 표현(4-4-4-4 그룹)
- 연결 상태/건강도(최근 데이터 수신 시각, 연결 시간) 기본 통계
- 임계값 TH/TL 전역선 오버레이 지원

### 하드웨어 요구사항
- Arduino Uno R4 WiFi
- DS18B20 센서 1개 이상 (4.7kΩ Pull-up 권장)
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
- `src/DS18B20_Arduino.ino`: 진입점, 시스템 초기화/루프, JSON 모드 토글
- `src/SerialCommunication.*`: CSV/텍스트 출력 호환 모드
- `src/JsonCommunication.*`: JSON 직렬 메시지 레이어 (sensor/system/heartbeat/alert/error)
- `src/SensorManager.*`: 센서 스캔, 온도 검증, 에러 누적/복구, 사용자 ID EEPROM 저장/검증
- `src/CommandProcessor.*`: 명령 파싱 및 실행 (reset 등)
- `src/SystemState.*`: 주기 타이머, 상태 카운터
- `src_dash/core/serial_json_communication.py`: 실시간 수집 + JSON/CSV 파싱 + 주소 추출 + 상태 통계
- `src_dash/core/shared_callbacks.py`: Dash 콜백 (집계 그래프, 상세 그래프, 센서 패널, Night/Day 모드)

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

## 직렬(JSON/CSV) 통신 요약

기본값은 JSON 모드(`jsonMode = true`). CSV 모드는 호환 용도로 유지됩니다.

예시 (Firmware → Host):
```jsonc
{"type":"sensor","timestamp":123456,"id":1,"temp":23.75,"status":"ok"}
{"type":"system","timestamp":123500,"msg":"SENSOR_1_ADDRESS_28:FF:64:1E:80:16:04:3C","level":"info"}
{"type":"heartbeat","timestamp":125000,"uptime":125,"memory":12345,"health":"ok"}
{"type":"error","timestamp":130000,"error":"SENSOR_1_READ_ERROR_3"}
```

CSV (Fallback) 예시:
```
SENSOR_DATA,1,23.75,125000
SYSTEM,SENSOR_1_ADDRESS_28:FF:64:1E:80:16:04:3C
HEARTBEAT,125,12345,ok
ERROR,SENSOR_1_READ_ERROR_3
```

Host 수집 모듈(`ArduinoSerial`)은 JSON/CSV를 자동 식별하고 센서 주소를 System 메시지에서 추출해 UI에 4-4-4-4 그룹 형태로 표시합니다.

센서 ID 변경 명령(향후 명령 프로토콜 확장 예정)은 EEPROM TH 바이트 활용으로 재부팅 후에도 지속됩니다.

---

## 설정(PlatformIO)

`platformio.ini` 주요 항목:
- `board = uno_r4_wifi`
- `upload_port`, `monitor_port`: 환경에 맞게 COM 포트 지정
- `monitor_speed = 115200`
- 필요한 경우 빌드 플래그/라이브러리 의존을 추가 조정

---

## 문제 해결 (Troubleshooting)
- 업로드/모니터 실패: 장치 관리자에서 COM 포트 확인 후 `platformio.ini` 포트 수정
- 센서 미검출: 배선/풀업 저항, 해상도(12bit 변환 750ms 딜레이) 확인, 데이터핀 번호(`ONE_WIRE_BUS`) 검증
- 급격 변화 반복 에러: 주변 온도 급변 상황이 아니라면 배선 접촉/노이즈 확인 (Shielded 케이블 검토)
- TEMP_OUT_OF_RANGE: -55~125℃ 범위 벗어난 값은 폐기 → 전원/접촉 불안정 여부 확인
- READ_ERROR 누적 후 DISCONNECTED: 센서 물리 연결/전압/풀업 저항 점검, 재접속 시 RECONNECTED 메시지 발생
- JSON 파싱 오류: Host 측 비표준 문자/인코딩 또는 펌웨어 출력 혼선 여부 확인

---

## 개발 / 코드 품질 (Workflow)
Python 기반 보조 스크립트(`src_dash/`, `tools/`)는 다음 품질 도구 체인을 사용합니다.

| 도구        | 목적                          | 비고                                            |
| ----------- | ----------------------------- | ----------------------------------------------- |
| `ruff`      | Lint (E,F,W) + 빠른 규칙 검사 | flake8 대체, `line-length=110` (pyproject.toml) |
| `black`     | 포맷터                        | 서식 일관성, 라인 길이 110                      |
| `isort`     | 임포트 정렬                   | CI 유지 (추후 ruff I 규칙으로 통합 가능)        |
| `autoflake` | 미사용 import/변수 제거       | 파괴적 변경은 pre-commit/수동 사용 권장         |
| `pyright`   | 정적 타입 검사                | VS Code(Pylance) 연동                           |

### 최근 품질/구조 변경 요약
* flake8 → ruff 전환 (단일 Lint 표준) / 최대 라인 길이 110 통일
* 타입 안정성: pyright (Pylance) 오류 0 유지 목표 / Optional 접근 None 가드 패턴 확립
* 자동 포맷 파이프라인 (`tools/auto_lint_and_format.py`): autoflake → isort → ruff --fix → black → ruff 재검사 → pyright
* Dash 그래프 안정화: None/단일 포인트 데이터에서도 라인/마커 표시 (가시성 문제 근본 원인 분리)
* 직렬 수집 루프 재작성: in_waiting burst 읽기 + 안전 디코딩 + 5초 상태 로그
* 센서 주소 추출 & UI 표시(조회/디버그 가속)
* Sensor ID EEPROM 저장/검증 기능 도입 (시스템 재기동 후 지속)

### 로컬 품질 체크 (선택)
```bash
ruff check src_dash src
black --check src_dash src
isort --check-only src_dash src
```

자동 수정 파이프라인은 `tools/auto_lint_and_format.py` 에서 실행 순서:
1. autoflake (옵션) → 2. isort → 3. ruff --fix → 4. black → 5. ruff 재검사 → 6. pyright

### CI
GitHub Actions 워크플로우에서 ruff / black / pyright / pytest (coverage 선택 구성) 실행. 향후 하드웨어 연계 테스트는 시뮬레이션 레이어로 분리 예정.

### 대시보드 실행 (선택 사용)
```bash
pip install -r requirements.txt
python -m src_dash.app  # 또는 VS Code debug config 사용
```

### 펌웨어 빌드 & 업로드 (요약)
```bat
pio run -e uno_r4_wifi
pio run -e uno_r4_wifi --target upload
pio device monitor -b 115200 -p COMx
```

### 데이터 수집 모듈 단독 테스트
```bash
python src_dash/core/serial_json_communication.py
```

### 향후 예정(ROADMAP)
- [ ] 센서 ID 변경 명령 호스트 UI 통합
- [ ] 센서별 개별 임계값(TH/TL) 적용 및 알람 이벤트 표준화
- [ ] 최근 에러 버퍼 / 통계 UI 표시 강화
- [ ] 펌웨어 → 호스트 측 명령 Ack 구조 정비
- [ ] 고온/이상 변화 Alert JSON 통합 처리

---

## 라이선스 / 기여
- 라이선스: TBD (조율 중)
- 이슈/PR 환영: 재현 가능한 정보(로그/환경/센서 수) 포함

---

문의/지원: 저장소 이슈 탭을 이용해 주세요. (센서 수 / 보드 정보 / 최근 시스템 메시지 포함 권장)