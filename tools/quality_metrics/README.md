# 코드 품질 메트릭 모니터링 시스템

DS18B20 Embedded Application의 코드 품질을 자동으로 모니터링하고 분석하는 도구입니다.

## 📊 주요 기능

### 1. 코드 품질 메트릭 수집
- **코드 메트릭**: 라인 수, 함수/클래스 개수, 복잡도
- **아키텍처 메트릭**: Clean Architecture 준수도, 의존성 역전 원칙
- **테스트 메트릭**: 테스트 커버리지, 성공률, 실행 시간
- **빌드 메트릭**: 컴파일 성공 여부, 메모리 사용률, 경고/오류 개수

### 2. 트렌드 분석
- 품질 점수 변화 추적
- 메트릭별 상세 변화 분석
- 자동 권장사항 생성

### 3. 자동화된 모니터링
- GitHub Actions CI/CD 통합
- PowerShell/Bash 스크립트 지원
- 정기적 품질 체크

## 🚀 사용법

### 기본 품질 메트릭 실행
```bash
# Python 스크립트 직접 실행
python tools/quality_metrics/code_metrics.py

# 결과 파일 위치:
# - logs/quality/metrics_YYYYMMDD_HHMMSS.json
# - logs/quality/quality_report_YYYYMMDD_HHMMSS.md
```

### 트렌드 분석 실행
```bash
# 과거 데이터와 비교하여 트렌드 분석
python tools/quality_metrics/trend_analyzer.py


### 자동화된 전체 품질 모니터링

# 분석만 실행 (빌드/테스트 건너뛰기)
powershell -ExecutionPolicy Bypass -File tools/quality_metrics/monitor_quality.ps1 -SkipBuild -SkipTest

# 상세 출력 포함
## DS18B20_Embedded_ApplicationV2 Quality Metrics
```

#### Linux/macOS (Bash)
# 전체 프로세스 실행

# Git Bash에서도 사용 가능
```
## 📈 품질 점수 기준

### 전체 품질 점수 (0-100)
- **90-100**: 🎉 탁월한 품질
- **80-89**: ✅ 좋은 품질
- **아키텍처 메트릭**: 30% (계층 분리, 의존성 역전, 인터페이스 사용)
- **테스트 메트릭**: 25% (테스트 성공률, 커버리지)
- **빌드 메트릭**: 20% (컴파일 성공, 메모리 사용률)
## 📋 생성되는 리포트
### 1. 품질 메트릭 리포트 예시
```markdown
# DS18B20 Embedded Application - Code Quality Report
Generated: 2025-07-30T05:28:53.190715

## 📊 Overall Quality Score: 90.9/100

### 📈 Code Metrics
- Source Files: 5 (.cpp)
- Header Files: 11 (.h)
- Test Files: 2
- Total Lines: 1,222
- Functions: 72
- Classes: 10
- Average Complexity: 0.6

### 🏗️ Architecture Metrics (Score: 85.0/100)
- Layer Separation: 90.0/100
- Dependency Inversion: 80.0/100
- Interface Usage: 90.0/100

### 🧪 Test Metrics
- Test Cases: 16
- Success Rate: 100.0%
- Execution Time: 0.860s
- Coverage Estimate: 40.0%

### 🔨 Build Metrics
- Compilation: ✅ Success
- RAM Usage: 22.6%
- Flash Usage: 70.1%
```

### 2. 트렌드 분석 리포트 예시
```markdown
# DS18B20 Quality Metrics Trend Analysis
Generated: 2025-07-30T05:31:03.123456

## 📈 Overall Quality Score Trend
- Latest Score: 90.9/100
- Previous Score: 60.5/100
- Change: +30.4 points

## 💡 Recommendations
- ✅ Quality score improved significantly!
```

## 🔧 CI/CD 통합

GitHub Actions에서 자동으로 품질 메트릭이 실행됩니다:

```yaml
- name: Run code quality metrics analysis
  run: python tools/quality_metrics/code_metrics.py

- name: Upload quality metrics
  uses: actions/upload-artifact@v4
  with:
    name: quality-metrics
    path: |
      logs/quality/*.json
      logs/quality/*.md
```

## 📁 파일 구조

```
tools/quality_metrics/
├── code_metrics.py          # 기본 품질 메트릭 수집
├── trend_analyzer.py        # 트렌드 분석
├── monitor_quality.ps1      # Windows 자동화 스크립트
├── monitor_quality.sh       # Linux/macOS 자동화 스크립트
└── README.md               # 이 파일

logs/quality/
├── metrics_*.json          # JSON 메트릭 데이터
├── quality_report_*.md     # 마크다운 리포트
├── trend_analysis_*.json   # 트렌드 분석 데이터
└── trend_report_*.md       # 트렌드 리포트
```

## 🎯 권장 사항

### 개발 워크플로우
1. **코드 변경 후**: `python tools/quality_metrics/code_metrics.py`
2. **주기적 체크**: `monitor_quality.ps1` 실행
3. **릴리스 전**: 품질 점수 85점 이상 확인

### 모니터링 주기
- **일일**: 자동화 스크립트 실행
- **주간**: 트렌드 분석 검토
- **릴리스**: 모든 메트릭 검증

이 품질 모니터링 시스템을 통해 DS18B20 Embedded Application의 코드 품질을 지속적으로 관리하고 개선할 수 있습니다.
