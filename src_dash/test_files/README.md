# 🧪 Arduino DS18B20 테스트 도구들

이 폴더에는 Arduino DS18B20 시스템을 테스트하기 위한 다양한 도구들이 있습니다.

## 📋 테스트 파일 목록

### ✅ **단독 실행 가능한 테스트들**

1. **test_quick.py** - 빠른 연결 테스트 (5초)
   ```bash
   python src_dash/test_files/test_quick.py
   ```
   - **의존성**: `serial` (표준 라이브러리)
   - **용도**: Arduino 연결 및 기본 데이터 수신 확인

2. **test_arduino_serial_output.py** - 기본 시리얼 출력 테스트
   ```bash
   python src_dash/test_files/test_arduino_serial_output.py
   ```
   - **의존성**: `serial` (표준 라이브러리)
   - **용도**: Arduino 시리얼 출력 및 명령 응답 테스트

3. **test_safe_debug.py** - 안전한 디버그 (Ctrl+C 지원)
   ```bash
   python src_dash/test_files/test_safe_debug.py
   ```
   - **의존성**: `core.serial_json_communication`
   - **용도**: 안전한 종료 기능이 있는 장시간 디버그

4. **test_debug_data.py** - 데이터 수신 상태 디버그
   ```bash
   python src_dash/test_files/test_debug_data.py
   ```
   - **의존성**: `core.serial_json_communication`
   - **용도**: Arduino 데이터 수신 및 저장 상태 확인

5. **test_detailed.py** - 상세 명령 응답 테스트
   ```bash
   python src_dash/test_files/test_detailed.py
   ```
   - **의존성**: `core.port_manager`
   - **용도**: 각 명령별 응답 확인 및 JSON 통신 테스트

6. **test_comprehensive.py** - 포괄적인 시스템 테스트
   ```bash
   python src_dash/test_files/test_comprehensive.py
   ```
   - **의존성**: `core.port_manager`
   - **용도**: 자동 포트 탐지, 시리얼 통신, 센서 데이터 수신 종합 테스트

## 🔧 의존성 정보

### 표준 라이브러리만 사용
- `test_quick.py`
- `test_arduino_serial_output.py`

### core 모듈 의존
- `test_safe_debug.py` → `core.serial_json_communication`
- `test_debug_data.py` → `core.serial_json_communication`
- `test_detailed.py` → `core.port_manager`
- `test_comprehensive.py` → `core.port_manager`

## 💡 사용 권장 순서

1. **test_quick.py** - 기본 연결 확인
2. **test_arduino_serial_output.py** - 시리얼 출력 확인
3. **test_debug_data.py** - 데이터 수신 상태 확인
4. **test_comprehensive.py** - 종합 시스템 테스트

## ⚠️ 주의사항

- 모든 테스트는 Arduino가 COM4에 연결되어 있다고 가정합니다
- 일부 테스트는 core 모듈을 import하므로 경로 설정이 포함되어 있습니다
- 테스트 실행 전 Arduino에 DS18B20 펌웨어가 업로드되어 있어야 합니다