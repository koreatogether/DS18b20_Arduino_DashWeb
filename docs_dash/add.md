# 추가 제안 (Night 모드 미니 그래프 및 향후 개선)

## 1. 즉시 적용된 개선
- Night(v2) 모드: 8개 센서별 미니 그래프 실시간 라인 업데이트.
- 동적 Y축: 센서별 최소/최대에 패딩 적용해 변동이 작아도 확대된 가독성 제공.
- 성능: latest 50개 샘플만 유지하여 렌더 부하 경감.

## 2. 향후 소규모 개선 아이디어
1. 미니 그래프 온도 라벨 오버레이: 최신 값 텍스트로 상단 우측 표시 (hover 없이 읽기 가능).
2. 최근 N 선택 기능: 50/100/300 포인트 토글 → 세밀/장기 추세 전환.
3. 센서 비활성 상태 페이드 처리: 최근 X초 미수신 센서 라인 색을 회색톤으로 자동 하향.
4. 임계값(TL/TH) 편집 UI: 모달 또는 인라인 입력 → 즉시 반영 + 저장.
5. 세션 유지: 센서 표시/선택 목록(senso-line-toggle) localStorage 동기화(dcc.Store(storage_type='local')).
6. 네트워크/시리얼 헬스 뷰: Heartbeat 주기 기반 지연(ms) 계산 및 막대/게이지 표시.
7. 알람 히스토리 탭: ALERT 수신 건을 별도 DataTable로 누적 + CSV 내보내기.
8. 그래프 스냅샷 저장: 현재 Plotly 그림 PNG export 버튼 외에 '📌 Snapshot' 누르면 특정 시점 freeze.
9. 성능 최적화: pandas 변환 구간 최소화(센서별 deque 캐시) 후 고정 길이 numpy array로 직접 Figure 업데이트.
10. 테스트 자동화: Dash callback 단위 pytest + playwright 시각 스냅샷.

## 3. 중장기 아이디어
- WebSocket 전환(시리얼->서버->WS)으로 latency 감소 및 다중 클라이언트 지원.
- Prometheus exporter + Grafana 연동으로 장기 보존/알람.
- Alert Rule 엔진 (조건식 DSL: temp > TH 3회 연속 등) 구성.
- 다국어(i18n) 토글: 한/영 UI 동적 변환 리소스 JSON.

## 4. 기술적 메모
- 현 mini 그래프는 interval 1s 공용 트리거 → 센서별 측정 주기를 도입하면 개별 최근 데이터 슬라이스 길이가 다를 수 있으므로 X축 정렬(실시간 timestamp) 기준으로 OK.
- 임계선(TH/TL) 추가 시 y-range 계산 시 포함 필요.
- 콜백 수 증가 대비: pattern-matching(ALL/MATCH) 도입 시 확장성 개선 가능.

(이 문서는 자동 생성되었습니다. 유지보수 시 변경 이력 상단에 날짜 추가 권장.)
