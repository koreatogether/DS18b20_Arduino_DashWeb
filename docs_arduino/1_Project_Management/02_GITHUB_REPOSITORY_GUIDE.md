# GitHub 저장소 관리 가이드

## 📤 GitHub에 올라가야 하는 필수 파일 목록

### **1. 프로젝트 핵심 파일**
```
✅ src/                              # 소스 코드 디렉토리
├── DS18B20_Embedded_ApplicationV2.ino  # 메인 Arduino 파일
├── application/                     # 애플리케이션 계층
│   ├── MenuController.cpp/.h       # 메뉴 시스템
│   ├── SensorController.cpp/.h     # 센서 관리
│   └── *.cpp/.h                    # 기타 애플리케이션 파일
├── domain/                         # 도메인 계층
└── infrastructure/                 # 인프라 계층

✅ include/                         # 헤더 파일 디렉토리
✅ lib/                            # 프로젝트 전용 라이브러리
✅ test/                           # 테스트 코드
```
**이유**: 프로젝트의 핵심 소스 코드로, 다른 개발자가 프로젝트를 이해하고 빌드하는데 필수

### **2. 빌드 및 설정 파일**
```
✅ platformio.ini                   # PlatformIO 프로젝트 설정
✅ .gitignore                      # Git 무시 파일 목록
✅ .gitattributes                  # Git 속성 설정
```
**이유**: 프로젝트 빌드 환경 재현과 버전 관리에 필수

### **3. 문서 파일**
```
✅ README.md                       # 프로젝트 소개 및 사용법
✅ docs/                          # 프로젝트 문서
├── mustRead/                     # 필수 읽기 문서
├── plan/                         # 개발 계획 및 기록
└── *.md                         # 기타 문서
```
**이유**: 프로젝트 이해, 설치, 사용법 안내에 필수

### **4. 라이선스 및 메타데이터**
```
✅ LICENSE                         # 라이선스 파일
✅ package-lock.json              # 의존성 잠금 파일 (있는 경우)
✅ requirements.txt               # Python 의존성 (있는 경우)
```
**이유**: 법적 보호, 의존성 관리, 프로젝트 메타데이터

### **5. CI/CD 및 자동화**
```
✅ .github/                       # GitHub Actions 워크플로우
├── workflows/                    # 자동화 스크립트
└── ISSUE_TEMPLATE/              # 이슈 템플릿
```
**이유**: 자동 빌드, 테스트, 배포 환경 구성

---

## 🚫 GitHub에 올라가면 안 되는 파일 목록

### **1. 빌드 결과물**
```
❌ .pio/                          # PlatformIO 빌드 캐시
├── build/                        # 컴파일된 바이너리
├── libdeps/                      # 다운로드된 라이브러리
└── .pioenvs/                     # 환경별 빌드 결과
```
**이유**: 용량이 크고, 각 환경에서 다시 생성 가능. 저장소 크기 증가 및 불필요한 충돌 발생

### **2. 개발 환경 설정**
```
❌ .vscode/                       # VS Code 개인 설정
├── settings.json                 # 개인 에디터 설정
├── launch.json                   # 디버그 설정
└── c_cpp_properties.json        # IntelliSense 설정

❌ .idea/                         # IntelliJ/CLion 설정
❌ *.swp, *.swo                   # Vim 임시 파일
❌ .DS_Store                      # macOS 시스템 파일
❌ Thumbs.db                      # Windows 썸네일 캐시
```
**이유**: 개인 개발 환경에 특화된 설정으로, 다른 개발자에게 불필요하거나 충돌 야기

### **3. 임시 및 로그 파일**
```
❌ logs/                          # 실행 로그
├── *.log                         # 로그 파일
├── debug.txt                     # 디버그 출력
└── temp/                         # 임시 파일

❌ *.tmp                          # 임시 파일
❌ *.bak                          # 백업 파일
❌ *~                             # 에디터 백업
```
**이유**: 실행 시 생성되는 임시 데이터로, 저장소에 불필요한 용량 차지

### **4. 컴파일 결과물**
```
❌ *.o, *.obj                     # 오브젝트 파일
❌ *.exe, *.bin                   # 실행 파일
❌ *.hex, *.elf                   # 펌웨어 바이너리
❌ compile_commands.json          # 컴파일 명령 캐시
```
**이유**: 소스코드에서 재생성 가능한 바이너리 파일들

### **5. 민감한 정보**
```
❌ .env                           # 환경 변수 (API 키 등)
❌ secrets.h                      # 비밀 정보
❌ config_private.h               # 개인 설정
❌ *.key, *.pem                   # 인증서/키 파일
```
**이유**: 보안상 민감한 정보 노출 방지

### **6. 대용량 바이너리**
```
❌ *.zip, *.tar.gz                # 압축 파일
❌ *.pdf (대용량)                 # 큰 문서 파일
❌ *.mp4, *.avi                   # 비디오 파일
❌ *.iso, *.img                   # 디스크 이미지
```
**이유**: Git은 텍스트 파일 관리에 최적화, 대용량 바이너리는 저장소 성능 저하

---

## 📋 .gitignore 권장 설정

```gitignore
# PlatformIO
.pio/
.pioenvs/
.piolibdeps/
.vscode/.browse.c_cpp.db*
.vscode/c_cpp_properties.json
.vscode/launch.json
.vscode/ipch/

# Compilation
*.o
*.obj
*.exe
*.bin
*.hex
*.elf
compile_commands.json

# Logs and temporary files
logs/
*.log
*.tmp
*.bak
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# IDE
.idea/
*.swp
*.swo

# Environment variables
.env
secrets.h
config_private.h

# Build artifacts
build/
dist/
```

---

## 🎯 GitHub 저장소 최적화 팁

### **1. README.md 필수 구성요소**
- 프로젝트 설명 및 목적
- 설치 및 빌드 방법
- 사용법 및 예시
- 하드웨어 연결도
- 라이선스 정보

### **2. 릴리스 관리**
- 태그를 활용한 버전 관리
- 릴리스 노트 작성
- 바이너리 파일은 릴리스에만 첨부

### **3. 이슈 및 PR 관리**
- 이슈 템플릿 활용
- 명확한 커밋 메시지
- 브랜치 전략 수립

### **4. 문서화**
- 코드 주석 충실히 작성
- API 문서 자동 생성 (Doxygen)
- 변경 이력 관리 (CHANGELOG.md)

---

**작성일**: 2025-08-03  
**버전**: v1.0  
**적용 대상**: Arduino/PlatformIO 프로젝트