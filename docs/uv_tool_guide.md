# Python `uv` Tool 안내

작성일: 2025-08-08

## 개요
`uv`는 Python 프로젝트에서 패키지 설치, 가상환경 생성, 의존성 관리(잠금/복원)를 빠르고 신뢰성 있게 처리하는 최신 툴입니다. 기존 `pip`/`venv`/`pip-tools` 대비 속도와 재현성, Windows 호환성이 뛰어납니다.

## 주요 기능 및 사용 목적
- **초고속 패키지 설치**: 기존 pip 대비 수~수십 배 빠른 설치 속도
- **가상환경 자동 생성**: 별도 venv 명령 없이 프로젝트별 격리 환경 생성
- **잠금(lock) 파일 지원**: `requirements.lock`으로 의존성 버전 고정, 재현성 보장
- **cross-platform 지원**: Windows, macOS, Linux 모두 안정적으로 동작
- **pip/requirements.txt 호환**: 기존 방식과 병행 가능

## 언제, 왜 사용하는가?
- **새 프로젝트 환경 구축**: 의존성 설치/가상환경 생성이 한 번에 처리됨
- **CI/CD, 자동화 스크립트**: 빠른 설치와 재현성으로 빌드/테스트 속도 향상
- **팀 협업/배포**: lock 파일로 환경 차이 최소화, "설치 실패" 문제 감소
- **Windows 환경**: 경로/권한 문제 없이 안정적으로 동작

## 내 프로젝트에서의 유용함
- `docs/UV_pakage_util/UV_full_setup.ps1` 등 자동화 스크립트에서 uv를 사용해 Python 대시보드/테스트 환경을 신속하게 구축
- `requirements.txt`, `dash_requirements.txt` 기반으로 필요한 패키지 설치 및 lock 파일 생성
- 가상환경 자동 생성으로 로컬 환경 오염 방지
- Windows에서도 빠르고 오류 없이 설치 가능
- CI/CD, 배포, 재현 테스트에 적합

## 기본 사용법 예시

### 1. 패키지 설치 및 가상환경 생성
```powershell
uv venv
uv pip install -r requirements.txt
uv pip install -r dash_requirements.txt
```

### 2. lock 파일 생성/사용
```powershell
uv pip freeze > requirements.lock
uv pip install -r requirements.lock
```

### 3. 자동화 스크립트에서 활용
- `docs/UV_pakage_util/UV_full_setup.ps1` 실행 시 uv가 자동으로 설치/환경 생성/의존성 설치를 처리

## 참고 링크
- 공식 문서: https://github.com/astral-sh/uv
- 주요 명령어: `uv venv`, `uv pip install`, `uv pip freeze`, `uv pip sync`

## 결론
`uv`는 Python 환경 구축과 패키지 관리의 속도·재현성·호환성을 크게 개선해줍니다. 본 프로젝트에서는 대시보드/테스트 자동화, Windows 환경 신뢰성 확보, 협업/배포 편의성에 특히 유용합니다.
