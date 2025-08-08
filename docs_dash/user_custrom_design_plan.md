# DS18B20 웹 대시보드 사용자 커스텀 디자인 계획서 (Checklist)

목표: 현대적 디자인, 가시성, 기능성, UX/UI, 눈 피로 최소 색상 조합, 40대 중반 노안 고려(너무 크지 않게)까지 아우르는 “사용자 커스텀 가능한 디자인 시스템”을 별도 파일로 제공. 기능 로직 변경 없이 레이아웃/스타일/그래프 테마/폰트/색/크기/라운드/버튼 배치 등 거의 전부를 사용자가 조절하게 함. app.py는 최소 변경(후킹만)으로 유지.

가이드 원칙
- 분리: 디자인/레이아웃=custom_design.py(필요 시 custom_design_ui.py 추가), 기능=기존 app.py 콜백 그대로
- OOP·SOLID·DIP: 인터페이스/토큰/템플릿 중심 아키텍처. 구현 교체/확장 쉬움
- 상태 기반: 사용자 설정은 Store(localStorage) + JSON 파일로 보존/불러오기
- 저피로 색상/타이포: 고대비-저채도 라이트/다크 테마 제공, 적정 폰트 크기(기본 15~16px), 충분한 라인하이트(1.3~1.45)
- Dash 분리 원칙 준수: app.py 길이 증가 방지, 디자인 전용 파일 1~2개만 추가

---

## 1. 산출물(파일) 설계
1) src_dash/custom_design.py (필수, ≤250줄)
- 역할: 디자인 토큰, Plotly 템플릿, 컴포넌트별 스타일 레지스트리, 초기 레이아웃 스펙 제공
- 공개 API(계약):
  - get_theme(mode): "light"|"dark" 테마 토큰(dict)
  - get_plotly_template(mode): Plotly template dict
  - get_component_style(component_id, role): 스타일 dict 반환(예: sensor-card, button-primary)
  - get_layout_grid(): CSS Grid/Flex 단위의 위치 크기 사양(dict)
  - get_defaults(): 기본 사용자 설정 전체 스냅샷(dict)

2) src_dash/custom_design_ui.py (선택, ≤250줄)
- 역할: “디자인 모드” UI(설정 패널) + 불러오기/저장/리셋/프리셋
- 공개 API(계약):
  - build_customizer_panel(): Dash 컴포넌트 트리(사이드 패널) 반환
  - register_customizer_callbacks(app): 값 변경→Store/JSON 저장, 프리셋 전환, 미리보기 반영

3) src_dash/assets/custom_design.css (선택)
- 역할: CSS 변수(:root) 기반 토큰 정의, 접근성/반응형/포커스 스타일, 미세 트윅

4) src_dash/custom_design_config.json (런타임 생성/저장)
- 역할: 사용자가 저장한 커스텀 설정(모드, 색, 폰트, 컴포넌트 배치/크기 등)

---

## 2. 최소 침습 통합 포인트(app.py 수정 안내)
- from custom_design import get_theme, get_plotly_template, get_component_style, get_layout_grid, get_defaults
- dcc.Store(id='design-store', storage_type='local', data=get_defaults()) 추가
- 레이아웃 구성 시 style=… 부분을 get_component_style("컴포넌트ID", "role")로 교체
- 그래프 생성 시 figure.update_layout(template=get_plotly_template(mode)) 적용
- 옵션: 오른쪽 사이드에 build_customizer_panel() 추가(토글 버튼으로 숨김)

주의: 기능 콜백/로직은 손대지 않음. 스타일/레이아웃 바인딩만 교체.

---

## 3. 사용자 커스텀 범위(요구사항 맵핑)
- 위치/크기 배정: 센서 카드 그리드, 우측 제어 패널(폭·정렬), 그래프 영역, 시스템 로그 높이/폭
- 폰트: 기본 크기(15~16px), 헤더/카드/버튼/로그 폰트 크기·두께·패밀리
- 색상: 배경, 카드 배경, 버튼 배경/텍스트, 테두리, 그래프 배경/격자/선/점·강조 색
- 라운드/그림자: 버튼/카드 radius, box-shadow 강도(시각적 피로 저감)
- 그래프: Plotly template(colorway, paper_bg, plot_bg, gridcolor, line width, marker size)
- 간격/여백: 카드 간격, 내부 패딩, 섹션 마진(밀집/여유 프리셋)
- 다크/라이트 모드: 저채도·저휘도 라이트, 저대비 영역 최소화한 다크
- 버튼 확장: 사용자 신규 버튼 추가(라벨, 색, radius, 액션 바인딩은 추후 콜백 연결)

---

## 4. 데이터 구조(계약)
- design-store.data(JSON)
  - mode: "light" | "dark"
  - tokens: colors, typography, spacing, radii, shadows
  - layout: 영역 정의(grid/flex 파라미터)
  - components: { component_id: { style: {...}, visible: true/false } }
  - plotly: { template_name, colorway, line_width, marker_size, gridcolor, paper_bg, plot_bg }

검증: 허용 키 화이트리스트(SAFE_KEYS)만 적용, 나머지 무시

---

## 5. Plotly 그래프 테마(피로 최소화 기준)
- 라이트: paper_bg=#F8FAFB, plot_bg=#FFFFFF, grid=#E6E9EE, colorway=[#2C7BE5, #00A3A3, #6C757D, #E67E22, #6F42C1]
- 다크: paper_bg=#0F1216, plot_bg=#151A21, grid=#2A2F39, colorway=[#5CA8FF, #2AD4D4, #A0A7B1, #FF9E57, #B58CFF]
- 선 굵기 2.25px, 마커 5px, 투명 그리드, Y-축 자동 범위+패딩 2~3

---

## 6. 레이아웃 시스템
- 기본: responsive Flex/Grid(모바일 1열, 태블릿 2열, 데스크탑 2~3영역)
- 우측 패널 폭 기본 280px(사용자 조절 240~360px)
- 센서 카드: n개 자동 래핑, 카드 폭 150~180px, 간격 8~12px
- 시스템 로그: 높이 200~400px 가변, 모노스페이스 폰트 13~14px
- 디자인 모드: 드래그/리사이즈(옵션, dash-grid-layout 연동 고려)

---

## 7. 버튼 사용자 추가(그래픽적 배치 포함)
- custom_design_ui.py에서 “디자인 모드” 진입 시:
  - 신규 버튼 추가(+), 라벨 입력, 색상 선택, radius 슬라이더, 크기/위치 지정(그리드 슬롯)
  - 프리뷰 즉시 반영 → 저장 시 components에 등록
  - 액션(기능 콜백)은 별도 매핑 키로 보관(action_key). 추후 callbacks.py에서 action_key ↔ 콜백 연결 매핑만 추가

안전장치: 버튼 수 제한(예: 20개), 라벨 길이 제한, 색상 대비 경고(AA 권고)

---

## 8. 접근성/가시성 가이드
- 기본 폰트 15.5px, H1 22~24px, H3 17~18px, 버튼 14.5~15px
- 라인하이트 1.35~1.45, 여백 간격 6~12px
- 대비비 AA 이상(텍스트 대비 ≥ 4.5:1)
- 호버/포커스 가시성: outline/음영/밝기 변조
- 애니메이션 최소화(그래프 업데이트만)

---

## 9. 저장/로드/프리셋
- localStorage(dcc.Store) 자동 저장, "저장" 클릭 시 custom_design_config.json에도 동기화
- 프리셋: Light-Comfort, Light-Compact, Dark-Calm, Dark-HighContrast
- 가져오기/내보내기: JSON 업/다운로드

---

## 10. 체크리스트(구현 단계)
A. 스캐폴딩
- [ ] custom_design.py 생성: 토큰/템플릿/스타일/레이아웃/디폴트
- [ ] design-store(로컬) 추가 및 app.py 스타일 바인딩 지점 식별 목록 작성
- [ ] Plotly 템플릿 연동 코드 후킹 포인트 정의

B. 테마/토큰
- [ ] light/dark 토큰 정의(colors, spacing, radii, typography)
- [ ] Plotly template 2종 구성 + colorway
- [ ] 그래프 기본 선/마커/그리드 설정 통일

C. 컴포넌트 스타일 맵
- [ ] 헤더/H1/H3, 센서 카드, 우측 패널, 버튼(기본/강조), 로그 박스
- [ ] 공통 spacing/radius/shadow 옵션 적용
- [ ] 가시성(visible) 토글 반영

D. 레이아웃
- [ ] Grid/Flex 스펙: 센서 카드 영역, 우측 패널, 그래프, 로그
- [ ] 반응형 브레이크포인트 정의
- [ ] 우측 패널 폭 조절 옵션(240~360)

E. 사용자 설정
- [ ] design-store 스키마/화이트리스트 적용
- [ ] 저장/로드(로컬→JSON) 루틴
- [ ] 프리셋 4종

F. 버튼 추가 UI(선택: custom_design_ui.py)
- [ ] 디자인 모드 패널/컨트롤(색상, 라벨, radius, 위치)
- [ ] 신규 버튼 생성/미리보기/등록 흐름
- [ ] action_key 매핑 스펙 문서화

G. 접근성
- [ ] 대비/폰트/라인하이트/포커스 상태 점검
- [ ] 색상 조합 경고 로직(선택)

H. 통합
- [ ] app.py에 최소 후킹 적용(임포트, Store, style/템플릿 연결)
- [ ] 기존 콜백 영향 0 확인(동일 컴포넌트 ID 유지)

I. 테스트/품질
- [ ] 스냅 스토어 로드/세이브 유닛테스트
- [ ] 기본/프리셋 렌더 스모크 테스트
- [ ] 성능: 레이아웃/스타일 변경이 업데이트 주기(1초)와 충돌 없는지 확인

---

## 11. 리스크/대안
- 드래그 배치 라이브러리 의존: dash-grid-layout 미사용 시 대안으로 슬럿 기반 grid-area 입력 제공
- 과도한 옵션 노출로 복잡성 증가: 프리셋+전문가 모드로 단계화
- 성능 저하: style dict 최소화, memoization, template 공유

---

## 12. 성공 기준
- app.py 기능 콜백 무변경 상태로 전 영역 스타일/레이아웃이 외부에서 제어됨
- 사용자 설정이 재시작 간 지속(localStorage+JSON)
- 라이트/다크 전환과 폰트/간격 조정이 즉시 반영
- 버튼 추가/수정이 디자인 모드에서 가능하며 안전 가드 적용

---

## 13. 다음 단계(실행 제안)
- 1일차: custom_design.py 구현 + app.py 후킹 포인트 1차 적용(그래프 템플릿, 상단/패널/카드/로그 스타일)
- 2일차: 프리셋/저장·로드 + 레이아웃 조절 옵션
- 3일차: 디자인 모드(UI) + 버튼 추가(그래픽 배치 간소 버전)

필요 시 이 계획에 따라 코드 파일 생성까지 진행하겠습니다(최대 2파일).
