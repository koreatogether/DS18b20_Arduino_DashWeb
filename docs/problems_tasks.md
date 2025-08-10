# Problems Panel 정리 체크리스트

> 코드 품질/경고 38개 (사용자 보고). 실제 스캔하며 확정/체크. 필요 시 추가 항목 업데이트.

## 1. 즉시 수정 (런타임/Deprecated)
- [x] pySerial flushInput/flushOutput -> reset_input_buffer/reset_output_buffer (호환 fallback)
- [x] shared_callbacks: sensor_id 캐스팅/타입 경고 정리 (int 리스트 변환 & 반복 int 제거)
- [x] snapshot 함수 반환 구조 타입 힌트 추가
- [x] 예외 처리: broad except 축소 (connect / read loop SerialException 우선)

## 2. 타입/정적 분석 경고
 - [x] UI version 분기 문자열 상수 Enum 화 (UIMode 도입)

- [ ] 로그 출력(🔍/🌙/☀️) 레벨 기반 logging 전환 옵션 초안
## 4. 테스트 & 안정성

### 진행 이력
- 2025-08-10  (오전) : Deprecated 메서드 교체, sensor_id 캐스팅/타입 경고 정리, snapshot 타입 힌트, 예외 축소, DataFrame 컬럼 사전 검증, threshold_map 제거, UI version Enum(UIMode) 적용, select-all/clear-all 구현 완료. 나머지 안정성(screenshot None guard, read loop 백오프), 구조/로그/DRY, 문서 작업은 미완료 상태로 오후 재개 예정.
- 2025-08-10  (오후 1차) : snapshot None guard 및 simulation fallback 강화, read loop exponential backoff 도입.
- [x] 시리얼 미연결 상태 snapshot 안전성 (None guard) 보강
- [x] _read_loop 예외 재시도/백오프 로직 추가
- [x] 단위 테스트: combined-graph 빈 선택 시 빈 Figure 반환 케이스 추가

## 5. 성능/자원
- [x] snapshot 50개 슬라이싱 상수화 (SNAPSHOT_SIZE)
- [x] deque maxlen 상수화 (SENSOR_DATA_MAXLEN 등)
- [ ] deque maxlen 재검토 (센서 폭주 대비 경고 임계치?)

## 6. 문서
- [ ] README: Night v2 주요 변경 요약 섹션
- [ ] 개발자 가이드: 콜백 등록 순서 & 디버그 플래그 설명
- [ ] 시리얼 모듈 주석에 reset_* 사용 이유 추가 (이미 일부 반영, 문서화 필요)

## 7. 선택적 개선
- [x] select-all / clear-all 센서 토글 유틸 버튼 (Night)
- [ ] DRY: status 아이콘 매핑 dict 재사용 (중복 위치 통합)
- [ ] Plotly figure 스타일 프리셋 사전 정의

---
업데이트 방법: 항목 해결 시 체크박스 표기 후 커밋. 새 이슈 발견 시 섹션 추가 또는 분류.
