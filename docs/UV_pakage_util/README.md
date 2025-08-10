# DS18B20 프로젝트 UV(uv) 기반 재구축 가이드

본 문서는 UV(ufmt/uv/ruff 계열의 초고속 파이썬 패키지/가상환경 관리자)를 사용해, 본 저장소를 신규 PC에 신속히 재구축하고 바로 실행 가능한 상태로 만드는 체크리스트입니다.

이 가이드는 다음 핵심 영역을 한 번에 준비합니다.
- 루트/문서(docs*, docs_arduino, docs_dash)
- 펌웨어(PlatformIO: src, include, lib, platformio.ini)
- 데스크톱/웹앱(Dash: src_dash)
- 공용 도구와 CI 보조 스크립트(tools, logs)

## 전제
- OS: Windows 10/11
- Shell: cmd.exe
- UV 설치됨 (없다면 아래 준비 단계에서 자동 설치 경로 제공)
- Arduino Uno R4 WiFi 연결 가능(옵션)

---

## 0. 빠른 개요(한 번에 끝내기)
- Python 가상환경 생성 및 종속 설치(uv)
- Dash 앱 실행 확인
- PlatformIO 펌웨어 빌드/업로드 확인
- 로그/문서 경로 점검

필요한 명령은 아래 섹션별 체크리스트에 준비되어 있습니다. 가급적 자동화 스크립트를 먼저 실행하면 대부분 일괄 처리됩니다.

---

## 1. 준비 단계(Checklist)
- [ ] Microsoft C++ 빌드 도구(Visual Studio Build Tools) 설치 여부 확인(선택)
- [ ] Git 설치 여부 확인(선택)
- [ ] Python 3.10+ 설치 여부 확인
- [ ] uv 설치 여부 확인 (없으면 스크립트가 자동 설치)
- [ ] PlatformIO Core 설치 여부 확인(없으면 자동 설치)

선택적 설치는 자동 스크립트가 가급적 처리합니다. 설치 권한이 필요한 항목은 관리자 권한이 요구될 수 있습니다.

---

## 2. 폴더 구조 안내(핵심만)
- [ ] 루트: platformio.ini, requirements.txt, dash_requirements.txt, README.md 등 공용 설정/문서
- [ ] src, include, lib: Arduino 펌웨어 소스 및 헤더, 라이브러리
- [ ] src_dash: Dash/Flask 기반 데스크톱 웹앱 소스
- [ ] tools: 빌드/테스트/품질 검사 스크립트 모음
- [ ] logs, docs_dash/logs: 실행/품질 로그 저장 위치
- [ ] docs_arduino, docs_dash, docs: 각종 가이드/진행 문서

---

## 3. 자동 재구축(권장) – 일괄 스크립트
다음 배치 파일은 uv를 이용해 파이썬 환경을 준비하고, 앱 실행과 펌웨어 빌드까지 순차 수행합니다.

- [ ] tools\project_build_and_run.py을 우선 실행해 작동 여부를 확인
- [ ] 또는 아래 제공되는 배치 스크립트(UV_full_setup.bat) 사용

UV_full_setup.bat는 아래를 수행합니다:
1) uv 설치(미설치 시)
2) Python 가상환경(.venv) 생성 및 활성화
3) pip 대신 uv로 종속 패키지 설치(requirements.txt + dash_requirements.txt)
4) 코드 품질(옵션): ruff/pylint 실행 및 로그 저장 (flake8 사용 중단)
5) Dash 앱 구동 테스트(src_dash/app.py)
6) PlatformIO 펌웨어 빌드 및(옵션) 업로드
7) 로그/산출물 경로 안내

---

## 4. 수동 단계(세부 절차) – 필요 시
- [ ] uv 설치: https://github.com/astral-sh/uv 참고 또는 스크립트 자동 설치
- [ ] 가상환경 생성: uv venv .venv
- [ ] 종속 설치: uv pip install -r requirements.txt && uv pip install -r dash_requirements.txt
- [ ] Dash 앱 실행: .venv\Scripts\python.exe -u src_dash\app.py
- [ ] PlatformIO 빌드: "%USERPROFILE%\.platformio\penv\Scripts\platformio.exe" run
- [ ] 업로드(옵션): "%USERPROFILE%\.platformio\penv\Scripts\platformio.exe" run --target upload --environment uno_r4_wifi

주의: platformio.ini의 upload_port/monitor_port는 COM4 기본값입니다. PC 환경에 맞게 변경하세요.

---

## 5. 환경 확인 체크(런타임)
- [ ] src_dash 앱이 http://127.0.0.1:8050 에서 실행되는지 확인
- [ ] 포트 드롭다운에 장치가 표시되는지, 선택/연결이 되는지 확인
- [ ] 센서 데이터 스트림(CSV/JSON) 수신 로그가 표시되는지 확인
- [ ] PlatformIO 빌드 성공 및 업로드(옵션) 성공 확인

---

## 6. 문제 해결 가이드(요지)
- [ ] 포트 권한/지연: 펌웨어에서 while(!Serial) 대기 3초 제한 패치 적용됨
- [ ] Windows cp949 이모지 문제: UTF-8 강제 설정으로 해결(app.py 내 _configure_console_encoding)
- [ ] Dash 콜백 오류(KeyError): 초기 옵션 선반영 + prevent_initial_callbacks로 해결됨
- [ ] Plotly ValueError: 타입 강제변환 및 go.Figure 폴백 추가
- [ ] 시리얼 타임아웃: 짧은 타임아웃과 바이트 버퍼링 처리

---

## 7. 산출물/로그 위치
- [ ] docs_dash/logs: 앱/검사 로그 모음
- [ ] build/uno_r4_wifi: PlatformIO 빌드 산출물
- [ ] logs/: 프로젝트 공용 로그 저장소

---

## 8. 다음 단계(선택)
- [ ] 린트 정리(불필요 import/공백/라인길이): ruff/pylint 기준 또는 코드 손질 (flake8 → ruff 전환)
- [ ] runner 정책/키워드 구성 외부화(tools 폴더): 운영환경 맞춤
- [ ] Windows 서비스/스케줄러 등록: 자동 실행

---

본 가이드를 기반으로 UV_full_setup.bat/UV_full_setup.ps1을 함께 사용하면 신규 PC에서도 본 프로젝트를 최소 클릭으로 재구축할 수 있습니다.
