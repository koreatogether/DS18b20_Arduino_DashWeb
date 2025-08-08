# SuperClaude + MCP 고효율 예시 프롬프트 모음 (DS18b20 프로젝트 전용)

본 문서는 docs/command(하위 폴더 제외) 내 지침들을 바탕으로, 실제 작업 생산성을 크게 높이는 “아이디어/행동/결과 중심”의 예시 프롬프트를 압축 정리했습니다. 기본 제공(또는 사용 중)일 가능성이 높은 MCP를 조합해 시너지를 내는 패턴 위주로 작성했습니다. 필요 시 적합한 명령(/sc:analyze, /sc:build, /sc:implement, /sc:test, /sc:troubleshoot, /sc:workflow, /sc:document, /sc:git, /sc:cleanup, /sc:design, /sc:estimate, /sc:improve, /sc:task, /sc:spawn, /sc:load 등)을 상황에 맞게 바꿔 사용하세요.

가정: 다음 MCP가 연결되어 있거나 쉽게 추가 가능하다고 가정합니다(없으면 해당 부분만 생략/대체).
- GitHub MCP: 이슈/PR/알림/리뷰/Actions(워크플로) 연동
- Notifications MCP: 알림 기반 작업 착수/회고
- Code Search/Index MCP: 대규모 코드/문서 탐색, RAG 인덱스
- Web/Docs Fetch MCP: 외부 문서/데이터 참고
- Python/Pylance MCP: 타입/임포트/품질 점검(파이썬 측)

형식: [의도] / [사용할 때] / [프롬프트] / [기대 산출물] / [추천 MCP 조합]

---

## 1) 펌웨어-대시 보드 프로토콜 스키마 동기화 자동 점검
- 의도: src(펌웨어) ↔ src_dash(파이썬/Dash) 간 직렬 JSON 스키마 드리프트 자동 탐지/수정 제안
- 사용할 때: 직렬 통신 오류/필드 누락/이름 변경으로 연동 깨질 때
- 프롬프트:
  - "/sc:analyze 프로젝트 컨텍스트 로드 후 'Serial JSON 프로토콜' 관점으로 src/, include/, src_dash/ 를 비교해 드리프트를 탐지해줘. 바뀐 필드/타입/범위를 표로 정리하고, 하위 호환 방식을 제안해. 이어서 /sc:design 으로 JSON 스키마 계약(API) 초안을 제시하고, /sc:implement 로 펌웨어와 파이썬 양쪽 수정 패치를 분리해줘. 마지막으로 /sc:test 로 src_dash/test_* 스크립트를 실행 가능한 형태의 테스트 플랜을 만들어줘."
- 기대 산출물: 드리프트 표, 합의된 스키마, 최소 변경 패치, 테스트 플랜/체크리스트
- 추천 MCP 조합: Code Search/Index, GitHub(브랜치/PR), Notifications(결과 알림)

## 2) Windows 직렬 포트 플레이크(간헐 타임아웃) 자동 트러블슈팅
- 의도: COM 포트 목록/접속/타임아웃/버퍼 누수 문제 재현-분석-수정 루프
- 사용할 때: COM4/COM5 등 포트 점유/타임아웃 빈발 시
- 프롬프트:
  - "/sc:troubleshoot 'Windows cmd.exe 환경 기준'으로 직렬 연결 타임아웃을 재현하고, src/SerialCommunication.* 의 읽기/쓰기/타임아웃/재시도/백오프 로직을 점검해줘. 최소 변경으로 안정화 패치를 제안하고, /sc:test 로 src_dash/quick_test.py 와 test_* 조합해 '자동 재시도 + 포트 클린업' 플로우를 검증해줘. 실패 시 로그를 요약하고 원인별 대응표를 만들어줘."
- 기대 산출물: 원인 가설/증거, 최소 패치, 재현/회귀 테스트 시나리오, 대응표
- 추천 MCP 조합: Code Search, GitHub(핫픽스 PR), Notifications

## 3) DS18B20 임계치(TH/TL) 설정 기능 안전추가 + 회귀방지
- 의도: addFunction_TH_TL.md 요구 반영해 설정 가능 임계치 구현 및 회귀 테스트
- 사용할 때: 임계치 로직/알람/보고 체인의 신뢰성 강화 필요 시
- 프롬프트:
  - "/sc:design addFunction_TH_TL.md 과 SensorManager.* / SystemState.* 를 기반으로 TH/TL 설정/검증/알림 흐름을 설계해줘. /sc:implement 로 플래그 기반(기본 off) 점진 도입 코드를 제안하고, /sc:test 로 정상/경계/오탐 케이스 회귀 테스트를 추가해줘. /sc:document 로 README 및 docs_arduino/ 가이드를 갱신하는 초안도 만들어줘."
- 기대 산출물: 설계 다이어그램/순서, 안전가드 포함 패치, 회귀 테스트, 문서 초안
- 추천 MCP 조합: Code Search, GitHub, Actions(테스트), Notifications

## 4) 품질 게이트 일원화(Arduino + Python) 파이프라인 구축
- 의도: cppcheck, PlatformIO, Python 테스트/린트/커버리지 단일 워크플로로 통합
- 사용할 때: 각 스택 결과가 따로 놀아 품질 추적이 어려울 때
- 프롬프트:
  - "/sc:workflow ‘품질 게이트 단일화’ 목표로 tools/*.bat|ps1, platformio.ini, Python tests 를 통합하는 CI 설계를 제안해줘. /sc:build 로 cppcheck/format/PlatformIO build/Python pytest 를 한 번에 도는 잡 구성을 설계하고, /sc:git 로 브랜치/PR/체크런 규칙을 도입해. /sc:document 로 배지/README 갱신 초안도 제공해줘."
- 기대 산출물: 단일 CI 설계, 워크플로/배지 초안, 브랜치 보호 제안
- 추천 MCP 조합: GitHub(Actions/PR/Checks), Code Search, Notifications

## 5) 비밀/민감정보 사전 차단 + 유출 대응 플레이북
- 의도: trufflehog 등으로 정기 스캔, 히트 시 자동 이슈/PR/회수 가이드 생성
- 사용할 때: 릴리즈 직전, 외부 협업 증가, 이메일/키 배포 시
- 프롬프트:
  - "/sc:analyze tools/trufflehog_gitscan.py 와 .gitignore, docs 의 현재 정책을 점검하고, /sc:test 로 git history 및 최신 변경을 스캔 플랜으로 검증해줘. 유출 의심 항목 발견 시 /sc:task 로 회수/키로테이션/히스토리 정리 단계를 체크리스트화하고, /sc:git 로 보호 브랜치/PR 템플릿에 보안 체크 항목을 추가해줘."
- 기대 산출물: 스캔 결과/오탐 구분, 회수 플레이북, 템플릿/정책 강화안
- 추천 MCP 조합: GitHub(Issues/PR/Checks), Code Search, Notifications

## 6) Doxygen 문서 자동화 + README/가이드 싱크
- 의도: Doxyfile 기반 HTML 문서와 상위 README, 가이드 문서 자동 싱크
- 사용할 때: 코드 변경 대비 문서 최신화 필요 시
- 프롬프트:
  - "/sc:document Doxyfile 을 이용해 public API 기준 자동 문서화를 설계하고, /sc:analyze 로 README_english.md, docs_arduino/*, docs_dash/* 를 스냅샷해 변경 영향도를 매핑해줘. /sc:workflow 로 ‘코드 변경 → 문서 빌드 → 링크 갱신 → PR’ 자동화를 제안해줘."
- 기대 산출물: 문서 링크 지형도, 자동화 설계, 갱신 체크리스트/PR 템플릿
- 추천 MCP 조합: GitHub(Actions/Pages), Code Search, Web Fetch(배지/호스팅 가이드)

## 7) 단계적 마이그레이션(웨이브) 오케스트레이션
- 의도: 위험 분산을 위한 웨이브 기반(스몰 배치) 변경 도입
- 사용할 때: 큰 리팩터링/구조 변경/통신 프로토콜 갱신 시
- 프롬프트:
  - "/sc:workflow ‘웨이브 모드’로 대규모 변경을 2~3단계로 나눠 계획해줘. 각 웨이브의 범위/가드레일/롤백 계획과 /sc:spawn 로 하위 작업을 위임하고, /sc:test 로 단계별 품질 게이트를 강제해줘. /sc:git 으로 브랜치 전략/릴리즈 태깅 정책도 제안해줘."
- 기대 산출물: 웨이브별 목표/가드/롤백, 하위 작업 위임, 태깅/릴리즈 전략
- 추천 MCP 조합: GitHub(Projects/PR/Actions), Notifications

## 8) CI 실패 알림 → 자동 원인 요약 → 수정 PR 생성 루프
- 의도: 알림에서 바로 실패 원인 요약/재현/수정까지 일관 루프
- 사용할 때: CI 빨간불 지속 발생 시
- 프롬프트:
  - "/sc:analyze 최근 CI 실패 알림을 수집해 공통 원인별(컴파일/린트/테스트/환경) 버킷을 만들고, 대표 케이스를 /sc:troubleshoot 으로 재현-분석해줘. /sc:implement 로 최소 변경 패치를 제안하고, /sc:test 로 해당 실패가 반드시 초록불로 바뀌는 회귀 케이스를 추가해줘. 필요 시 /sc:git 로 핫픽스 PR 까지 만들어줘."
- 기대 산출물: 실패 원인 버킷, 재현 스크립트, 핫픽스 PR 초안, 회귀 테스트
- 추천 MCP 조합: Notifications, GitHub(Actions/PR), Code Search

## 9) 릴리즈 준비: 버전, 체인지로그, 릴리즈 노트, 아티팩트
- 의도: 릴리즈 반복작업 자동화 + 품질 게이트 연결
- 사용할 때: 릴리즈/태깅 직전
- 프롬프트:
  - "/sc:estimate 최근 변경과 이슈/PR 기록을 요약해 semver 기준 다음 버전을 제안하고, /sc:document 로 체인지로그/릴리즈 노트 초안을 생성해줘. /sc:workflow 로 빌드/테스트/아티팩트 업로드/릴리즈 게시까지의 단계를 설계하고, /sc:git 로 태그/릴리즈 생성 PR 을 준비해줘."
- 기대 산출물: 버전 제안, 체인지로그/릴리즈 노트, 릴리즈 파이프라인 초안
- 추천 MCP 조합: GitHub(Release/Actions), Code Search, Notifications

## 10) 성능/지연 회귀 감시: 로그 기반 비교 보고서
- 의도: tools/run_acceleration_test.bat 등 실행 로그 비교 → 회귀 감지
- 사용할 때: 최적화/리팩터링 후 성능 보증 필요 시
- 프롬프트:
  - "/sc:test 최근 성능 관련 로그를 집계해 baseline 대비 변화(평균/95p/최악)를 계산하고, /sc:analyze 로 회귀 의심 구간을 코드 레벨로 추적해줘. /sc:improve 로 마이크로 최적화 후보를 제안하고, /sc:document 로 ‘성능 예산’과 경보 임계치를 정의해줘."
- 기대 산출물: 회귀 보고서, 핫스팟 코드 후보, 개선안, 성능 예산 문서
- 추천 MCP 조합: Code Search/Index, GitHub(Actions artifacts), Notifications

## 11) HIL(실장 하드웨어) 테스트 매트릭스 자동 확장
- 의도: 실제 센서/보드/포트 조합별 테스트 전략 수립/실행
- 사용할 때: 환경별 차이로 현장 버그가 재현 어려울 때
- 프롬프트:
  - "/sc:design HIL 테스트 매트릭스를 정의하고, /sc:test 로 각 조합(센서 수/케이블 길이/온도 범위/포트 상태)별 체크리스트를 생성해줘. /sc:workflow 로 야간 배치 테스트(가능 시) 또는 수동 절차를 문서화하고, /sc:document 로 결과 기록/사진/로그 취합 포맷을 정해줘."
- 기대 산출물: 테스트 매트릭스/체크리스트, 절차 문서, 결과 수집 양식
- 추천 MCP 조합: Code Search, GitHub(Projects/Issues), Notifications

## 12) 직렬 통신 회복력: 핸드셰이크/백오프/워치독
- 의도: 장기 실행 중 연결 불안정에 대한 복원력 강화
- 사용할 때: 장시간 운용에서 간헐 오류/메모리 누수 의심 시
- 프롬프트:
  - "/sc:analyze SerialCommunication.* 와 SystemHealthMonitor.h 를 검토해 핸드셰이크/지수 백오프/워치독/버퍼 가드 전략을 제안해줘. /sc:implement 로 옵션 플래그 기반 최소 변경 패치를 제시하고, /sc:test 로 장시간 시뮬레이션/에러 주입 시나리오를 추가해줘."
- 기대 산출물: 회복력 설계, 최소 패치, 장시간 테스트 시나리오
- 추천 MCP 조합: Code Search, Notifications, GitHub(PR)

## 13) Dash 오프라인/페일세이프 모드(가짜 데이터 주입)
- 의도: 보드 미연결/포트 점유 시 UX 유지
- 사용할 때: 데모/현장 점검에서 장치 부재로 Dash가 비정상 종료될 때
- 프롬프트:
  - "/sc:design src_dash 내 fake data 주입 플래그/환경변수 설계를 제안해줘. /sc:implement 로 안전한 기본값(오프라인 시 자동 fallback) 코드를 추가하고, /sc:test 로 실제 장치/미장치 시나리오 모두에서 UX를 확인하는 체크리스트를 만들어줘."
- 기대 산출물: 설계/플래그, 구현 패치, 시나리오 테스트
- 추천 MCP 조합: Code Search, GitHub, Notifications

## 14) 문서-코드 불일치 감시 봇(주기 점검)
- 의도: README/가이드와 실제 코드/설정 간 차이 자동 감지/이슈화
- 사용할 때: 문서 최신성 유지가 어려울 때
- 프롬프트:
  - "/sc:analyze README*.md, docs_arduino/*, docs_dash/* 와 실제 코드(설정/플래그/경로/스크립트)를 매칭해 불일치 목록을 만들어줘. /sc:task 로 해결 체크리스트를 만들고, /sc:document 로 문서 자동 갱신 규칙과 책임자를 제안해줘."
- 기대 산출물: 불일치 목록, 수정 체크리스트, 유지 규칙
- 추천 MCP 조합: Code Search/Index, GitHub(Issues), Notifications

## 15) uv 기반 파이썬 환경 보증 + 이메일 배포 시 셋업 자동검증
- 의도: docs/UV_pakage_util/ 가이드와 실제 환경 일치 보장
- 사용할 때: 외부/내부 배포, 교육/온보딩 시 환경 꼬임 방지
- 프롬프트:
  - "/sc:workflow ‘이메일 배포 시 UV 세팅’ 가이드에 따라 requirements/uv spec 을 검증하고, /sc:test 로 설치/실행/테스트 스모크를 자동 검증하는 체크 시퀀스를 설계해줘. 실패 시 /sc:troubleshoot 로 흔한 오류 테이블/자가진단을 추가해줘."
- 기대 산출물: 설치 검증 시퀀스, 실패 대응표, 온보딩 체크리스트
- 추천 MCP 조합: Python/Pylance, GitHub(Actions), Notifications

---

## 공통 사용 팁
- 항상 /sc:load 로 최소 컨텍스트를 먼저 로드(글롭/크기 제한/요약) → /sc:analyze 로 가설 설정 → /sc:design·/sc:build·/sc:implement → /sc:test → /sc:document → /sc:git 순으로 파이프라이닝하면 실패율이 급감합니다.
- ‘증거 기반’ 출력 습관화: 로그 요약, 변경 diff, 테스트 결과 스냅샷, 체크리스트 등 객관 자료를 반드시 산출물에 포함시켜 재현성과 신뢰도를 확보하세요.
- MCP는 적게, 강하게: 1~2개의 핵심 MCP를 먼저 깊게 활용(예: GitHub+Code Search), 필요할 때만 추가하세요.
- 실패를 자동 이슈화: 실패/경고가 누적되면 자동으로 /sc:task 생성 → 담당/기한/완료 기준 할당 흐름을 붙이세요.

## 빠른 시작용 미니 프롬프트
- "/sc:workflow 이 레포의 ‘직렬 JSON 계약 재검토 → 최소 패치 → 회귀 테스트’까지를 한 번에 수행해줘. /sc:load 로 src/, include/, src_dash/ 만 요약 로드하고, 드리프트를 표로 내고, 호환성 유지 조건 하 패치를 제안하고, 실패 재현/회귀 테스트 플랜을 산출물로 남겨줘. GitHub MCP가 가능하면 브랜치/PR 초안까지 만들어줘."

이 파일은 예시/아이디어 모음입니다. 환경/정책에 맞게 프롬프트를 조정해 사용하세요.
