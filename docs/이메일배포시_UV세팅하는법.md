# 이메일 배포 시 Python UV 세팅 안내

작성일: 2025-08-08

이 저장소를 이메일로 배포받은 사용자가 Windows/VS Code 환경에서 빠르고 오류 없이 실행 환경을 구축할 수 있도록 uv 기반 설치법을 안내합니다.

---

## 1. 저장소 다운로드 및 압축 해제
- 이메일 첨부 또는 링크로 받은 저장소를 원하는 폴더에 압축 해제
- (GitHub에서 직접 clone도 가능)

## 2. VS Code에서 폴더 열기
- VS Code 실행 후, [파일] → [폴더 열기]로 프로젝트 폴더 선택

## 3. Python 환경 및 의존성 설치 (uv 사용)
```powershell
# PowerShell에서 실행
pip install uv
uv venv
uv pip install -r requirements.txt
uv pip install -r dash_requirements.txt
```

## 4. PlatformIO 빌드/업로드/모니터
```powershell
# PlatformIO 명령어 예시
pio run -e uno_r4_wifi
pio run -e uno_r4_wifi --target upload
pio device monitor -b 115200 -p COM4
```

## 5. 대시보드/테스트 스크립트 실행 (필요시)
```powershell
python src_dash/app.py
```

---

자세한 환경 구축법은 `docs/uv_tool_guide.md`와 `README.md`를 참고해 주세요.

문의/지원: 저장소 이슈 탭 또는 이메일 회신
