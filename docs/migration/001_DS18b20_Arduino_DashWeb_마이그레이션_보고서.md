# DS18b20_Arduino_DashWeb 마이그레이션 보고서

작성일: 2025-08-08
작성자: 자동화 에이전트

## 개요
이 문서는 기존 저장소 `E:\Project_DS18b20\DS18B20_Arduino_Processing`를 새로운 프로젝트 폴더 `E:\Project_DS18b20\DS18b20_Arduino_DashWeb`로 재구성(이관)한 과정을 정리합니다. `docs/UV_pakage_util`의 가이드(uv 기반 재구축 플로우)를 준수하여, 필수 소스/문서/도구는 그대로 유지하고 빌드/캐시/이전 VCS 이력은 제거하여 "새롭게 시작"할 수 있도록 초기화했습니다.

## 목표
- 새 폴더명: DS18b20_Arduino_DashWeb
- 공개 Git 저장소로 재초기화 및 최초 푸시
- PlatformIO 펌웨어/ Dash 앱/ 문서/ 도구 유지
- 빌드/캐시/로그 및 이전 .git 이력 제거

## 이관 기준
- 포함(keep)
  - PlatformIO 구성과 소스: `platformio.ini`, `src/`, `include/`, `lib/`
  - Dash 앱: `src_dash/`, `dash_requirements.txt`
  - 문서: `docs/`, `docs_arduino/`, `docs_dash/`, 루트 `README*`
  - 도구/스크립트: `tools/`, `scripts/`, `.vscode/`, `.github/`
  - 기타 계획 산출물: `20250807_230338_18b20DashBoard.spec`, `Doxyfile` 등
- 제외(drop)
  - VCS/캐시/빌드/로그: `.git/`, `.pio/`, `.venv/`, `.pytest_cache/`, `build/`, `logs/`

## 수행 내역
1) 폴더 생성 및 복사
- 대상: `E:\Project_DS18b20\DS18b20_Arduino_DashWeb`
- 복사 시 제외: `.git`, `.pio`, `.venv`, `.pytest_cache`, `build`, `logs`

2) Git 재초기화 및 최초 커밋
- 새 로컬 저장소 초기화(초기 커밋)
- 과도하게 엄격했던 `.gitignore`를 완화하여 `include/`, `lib/`, `docs/`, `tools/`, `test/`, `scripts/`, `platformio.ini` 등이 추적되도록 수정

3) GitHub 공개 저장소 개설 및 연동
- 리포지토리: https://github.com/koreatogether/DS18b20_Arduino_DashWeb
- 원격 등록 및 `main` 브랜치 최초 푸시 완료

## 결과 구조(요약)
- 루트: `platformio.ini`, `requirements.txt`, `dash_requirements.txt`, `README*`, `Doxyfile`
- 펌웨어: `src/`, `include/`, `lib/`
- 대시보드: `src_dash/`
- 문서: `docs/`, `docs_arduino/`, `docs_dash/`
- 도구: `tools/`, `scripts/`, `.vscode/`, `.github/`
- 테스트: `test/`
- 로그: `logs/`(비어있는 초기 폴더)

## 재구축/실행 가이드(요지)
`docs/UV_pakage_util/README.md` 가이드에 따라 아래 중 하나를 권장합니다.

- 자동(권장):
  1. `docs/UV_pakage_util/UV_full_setup.ps1` (또는 `.bat`) 실행
  2. 자동으로 uv 설치 → 가상환경 생성 → 의존 설치 → Dash 앱 구동 확인 → PlatformIO 빌드

- 수동:
  1. uv 설치 및 가상환경 생성
  2. 의존 설치: `requirements.txt`, `dash_requirements.txt`
  3. Dash 앱 실행: `src_dash/app.py`
  4. PlatformIO 빌드/업로드: `platformio run [--target upload]`

주의: `platformio.ini`의 `upload_port/monitor_port` 기본값(COM4)을 환경에 맞게 조정하세요.

## 비고 및 다음 단계
- 필요 시 구(旧) 폴더(`DS18B20_Arduino_Processing`) 삭제 여부 확인 후 정리 권장
- CI나 자동화가 필요하면 `.github/workflows` 추가 구성 가능
- 린트/품질 규칙은 `tools/` 스크립트로 확장 가능

## 변경 이력
- 2025-08-08: 최초 작성(마이그레이션 완료 기록)
