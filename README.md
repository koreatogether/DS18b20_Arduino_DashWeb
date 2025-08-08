## DS18B20 Embedded Temperature Monitoring System
## 주요 기능
## 프로젝트 구조

### src_processing 폴더 주요 코드 구조 (2025-08-04 기준)

- **메인 UI/로직(main.pde)**: 센서 박스, 버튼, 그래프 등 전체 UI를 draw()에서 관리. 센서별 배열 구조(`SensorBox[]`, `SensorButton[][]`, `TemperatureGraph[]`). draw()에서 `drawScenarioTest()` 호출로 테스트 UI 오버레이.
- **자동화 테스트 UI(scenarioTest.pde)**: 테스트 시작 버튼(오른쪽 하단, `testBtnX`, `testBtnY`). `drawScenarioTest()`에서 테스트 버튼 및 자동화 시나리오 실행. `mousePressedScenarioTest()`에서 버튼 클릭 감지 후 자동 테스트 시작. `setupScenarioTest()`에서 버튼 위치 초기화(main.pde의 setup에서 호출).
- **센서 버튼 이벤트(MouseEvents.pde)**: `mousePressedSensorButtons()`, `mouseReleased()`로 센서 버튼 클릭/해제 이벤트 처리. main.pde의 mousePressed()에서 함께 호출.
- **UI 컴포넌트 클래스**: `SensorBox.pde`(센서 박스), `SensorButton.pde`(센서 버튼), `temperatureGraph.pde`(온도 그래프) 등 각 UI별 display()/상태 관리 메서드 구현.
- **기타**: 모든 .pde 파일에서 함수 중복(특히 draw, setup, mousePressed) 없이 연결됨. 테스트 버튼 클릭 시 자동화 시나리오 정상 동작. UI/테스트/센서 이벤트가 모두 독립적으로 관리됨.
## 빠른 시작
## 시스템 사양
## 개발 환경
## 사용 예시
## 주요 기능
## 라이선스
## 기여하기
## 지원