"""DS18B20 Arduino 연계 실시간 Dash 웹 애플리케이션 - 리팩토링 버전"""

import dash

# Core 모듈들
from core import (
    build_validation_layout,
    cleanup_arduino_resources,
    configure_console_encoding,
    create_main_layout,
    create_snapshot_function,
    debug_callback_registration,
    initialize_arduino,
    post_registration_audit,
    print_startup_info,
    register_shared_callbacks,
)
from core.ui_modes import UIMode
from dash import Input, Output, State
from day_sections.day_callbacks import register_day_callbacks

# 레이아웃 모듈들
from day_sections.day_layout import create_layout_v1

# 앱 초기화
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# 콘솔 인코딩 설정
configure_console_encoding()

# Arduino 초기화
arduino_config = initialize_arduino()
arduino = arduino_config["arduino"]
ARDUINO_CONNECTED = arduino_config["connected"]
INITIAL_PORT_OPTIONS = arduino_config["initial_port_options"]
selected_port = arduino_config["selected_port"]
INITIAL_PORT_VALUE = arduino_config["initial_port_value"]

# 상수 정의
COLOR_SEQ = [
    "#2C7BE5",
    "#00A3A3",
    "#E67E22",
    "#6F42C1",
    "#FF6B6B",
    "#20C997",
    "#795548",
    "#FFB400",
]
TH_DEFAULT = 55.0
TL_DEFAULT = -25.0

# 데이터 스냅샷 함수 생성
arduino_connected_ref = {"connected": ARDUINO_CONNECTED}
_snapshot = create_snapshot_function(arduino, arduino_connected_ref)

# 앱 레이아웃 설정
app.layout = create_main_layout(INITIAL_PORT_OPTIONS, selected_port, INITIAL_PORT_VALUE, create_layout_v1)
app.validation_layout = build_validation_layout()

# 간단한 버튼 클릭 테스트 콜백 (비활성화 - 충돌 방지)
# @app.callback(
#     Output('mode-indicator', 'children'),
#     [Input('btn-ver-1', 'n_clicks'), Input('btn-ver-2', 'n_clicks')],
#     prevent_initial_call=True
# )
# def test_button_clicks(n1, n2):
#     """버튼 클릭을 테스트합니다."""
#     print(f"\n🚨 [BUTTON_TEST] 버튼 클릭 테스트 콜백 호출됨!")
#     print(f"� [BUTTOIN_TEST] Day 버튼 클릭 수: {n1}")
#     print(f"� [BUTETON_TEST] Night 버튼 클릭 수: {n2}")
#
#     ctx = dash.callback_context
#     print(f"🚨 [BUTTON_TEST] 콜백 컨텍스트: {ctx.triggered}")
#
#     if not ctx.triggered:
#         print(f"🚨 [BUTTON_TEST] 트리거 없음")
#         return "현재 모드: Day (v1) - 초기 상태"
#
#     trigger_info = ctx.triggered[0]
#     button_id = trigger_info['prop_id'].split('.')[0]
#     trigger_value = trigger_info['value']
#
#     print(f"🚨 [BUTTON_TEST] 트리거된 버튼: {button_id}")
#     print(f"🚨 [BUTTON_TEST] 트리거 값: {trigger_value}")
#
#     if button_id == 'btn-ver-2':
#         print(f"🌙 [BUTTON_TEST] Night 버튼 클릭 감지됨! 클릭 수: {n2}")
#         return f"🌙 Night 모드 클릭됨! (클릭 수: {n2})"
#     elif button_id == 'btn-ver-1':
#         print(f"☀️ [BUTTON_TEST] Day 버튼 클릭 감지됨! 클릭 수: {n1}")
#         return f"☀️ Day 모드 클릭됨! (클릭 수: {n1})"
#     else:
#         print(f"❓ [BUTTON_TEST] 알 수 없는 버튼: {button_id}")
#         return f"❓ 알 수 없는 버튼: {button_id}"


# 메인 레이아웃 전환 콜백 (디버그 강화)
@app.callback(
    [
        Output("main-content", "children"),
        Output("ui-version-store", "data"),
        Output("mode-indicator", "children"),
        Output("mode-feedback", "children"),
    ],
    [Input("btn-ver-1", "n_clicks"), Input("btn-ver-2", "n_clicks")],
    State("ui-version-store", "data"),
    prevent_initial_call=False,
)
def update_main_layout(n1, n2, current_version):
    print(f"\n{'='*50}")  # 유지: 표현식 포함
    print("🔍 [LAYOUT_CALLBACK] 레이아웃 전환 콜백 호출됨")
    print(f"🔍 [LAYOUT_CALLBACK] btn-ver-1 클릭 수: {n1 or 0}")
    print(f"🔍 [LAYOUT_CALLBACK] btn-ver-2 클릭 수: {n2 or 0}")
    print(f"🔍 [LAYOUT_CALLBACK] 현재 버전: {current_version}")

    ctx = dash.callback_context
    print(f"🔍 [LAYOUT_CALLBACK] 콜백 컨텍스트: {ctx.triggered}")

    # 트리거된 버튼 확인
    if not ctx.triggered:
        button_id = "initial"
        print("🔍 [LAYOUT_CALLBACK] 초기 로드 - 기본값 사용")
    else:
        trigger_info = ctx.triggered[0]
        button_id = trigger_info["prop_id"].split(".")[0]
        trigger_value = trigger_info["value"]
        print(f"🔍 [LAYOUT_CALLBACK] 트리거된 버튼: {button_id}, 값: {trigger_value}")

    try:
        # Night 모드 버튼 클릭 처리
        if button_id == "btn-ver-2" and n2 and n2 > 0:
            print("🌙🌙🌙 [NIGHT_MODE] Night mode 버튼 클릭 감지!")
            print(f"🌙 [NIGHT_MODE] 클릭 수: {n2}")
            print("🌙 [NIGHT_MODE] v2 레이아웃 전환 시작...")

            # create_layout_v2 함수 존재 확인
            try:
                print("🔍 [NIGHT_MODE] night_sections.night_layout에서 create_layout_v2 import 시도...")
                from night_sections.night_layout import create_layout_v2

                print("✅ [NIGHT_MODE] create_layout_v2 함수 import 성공!")
            except ImportError as ie1:
                print(f"⚠️ [NIGHT_MODE] 첫 번째 import 실패: {ie1}")
                try:
                    print("🔍 [NIGHT_MODE] night_layout에서 create_layout_v2 import 시도...")
                    from .night_sections.night_layout import create_layout_v2

                    print("✅ [NIGHT_MODE] create_layout_v2 함수 import 성공 (대체 경로)!")
                except ImportError:
                    print("\n" + "=" * 50)
                    print("🔍 [LAYOUT_CALLBACK] 레이아웃 전환 콜백 호출됨")
                    print(f"🔍 [LAYOUT_CALLBACK] btn-ver-1 클릭 수: {n1 if n1 is not None else 0}")
                    print(f"🔍 [LAYOUT_CALLBACK] btn-ver-2 클릭 수: {n2 if n2 is not None else 0}")
                    print(f"🔍 [LAYOUT_CALLBACK] 현재 버전: {current_version}")
                layout_v1 = create_layout_v1(INITIAL_PORT_OPTIONS, selected_port, INITIAL_PORT_VALUE)
                return layout_v1, UIMode.DAY.value

            # 현재 포트 옵션을 실시간으로 가져오기
            print("🔍 [NIGHT_MODE] 포트 옵션 가져오는 중...")
            try:
                from core.arduino_manager import get_current_port_options

                current_port_options, current_default = get_current_port_options()
                print(f"✅ [NIGHT_MODE] 포트 옵션: {len(current_port_options)}개, 기본값: {current_default}")
            except Exception as pe:
                print(f"⚠️ [NIGHT_MODE] 포트 옵션 가져오기 실패: {pe}")
                current_port_options, current_default = (
                    INITIAL_PORT_OPTIONS,
                    selected_port,
                )

            # v2 레이아웃 생성
            print("🔍 [NIGHT_MODE] v2 레이아웃 생성 중...")
            try:
                layout_v2 = create_layout_v2(
                    current_port_options,
                    selected_port or current_default,
                    current_default,
                    app,
                    arduino,
                    ARDUINO_CONNECTED,
                    COLOR_SEQ,
                    TH_DEFAULT,
                    TL_DEFAULT,
                    _snapshot,
                )
                print("✅✅✅ [NIGHT_MODE] v2 레이아웃 생성 완료!")
                print("🌙 [NIGHT_MODE] Night 모드로 전환됩니다!")
                print(f"{'='*50}\n")
                return (
                    layout_v2,
                    UIMode.NIGHT.value,
                    "🌙 Night 모드 활성화",
                    f"🌙 Night 버튼이 클릭되었습니다! (클릭 수: {n2})",
                )
            except Exception as le:
                print(f"❌ [NIGHT_MODE] v2 레이아웃 생성 실패: {le}")
                import traceback

                traceback.print_exc()
                # 레이아웃 생성 실패 시 Day 모드로 fallback
                layout_v1 = create_layout_v1(INITIAL_PORT_OPTIONS, selected_port, INITIAL_PORT_VALUE)
                return (
                    layout_v1,
                    UIMode.DAY.value,
                    "☀️ Day 모드 (오류로 인한 복원)",
                    "❌ Night 모드 오류 발생",
                )

        # Day 모드 버튼 클릭 또는 기본값 처리
        else:
            if button_id == "btn-ver-1" and n1 and n1 > 0:
                print("☀️ [DAY_MODE] Day mode 버튼 클릭 감지!")
                print(f"☀️ [DAY_MODE] 클릭 수: {n1}")
            else:
                print("☀️ [DAY_MODE] 기본 v1 레이아웃 로드")

            print("☀️ [DAY_MODE] v1 레이아웃 생성 중...")
            layout_v1 = create_layout_v1(INITIAL_PORT_OPTIONS, selected_port, INITIAL_PORT_VALUE)
            print("✅ [DAY_MODE] v1 레이아웃 생성 완료!")
            print(f"{'='*50}\n")
            if button_id == "btn-ver-1" and n1 and n1 > 0:
                return (
                    layout_v1,
                    UIMode.DAY.value,
                    "☀️ Day 모드 활성화",
                    f"☀️ Day 버튼이 클릭되었습니다! (클릭 수: {n1})",
                )
            else:
                return (
                    layout_v1,
                    UIMode.DAY.value,
                    "☀️ Day 모드 (기본)",  # plain string
                    "애플리케이션 시작",  # plain string
                )

    except Exception as e:
        print(f"❌ [ERROR] 레이아웃 전환 중 오류: {e}")
        import traceback

        traceback.print_exc()
        print(f"{'='*50}\n")
        # 오류 발생 시 기본 레이아웃 반환
    return (
        create_layout_v1(INITIAL_PORT_OPTIONS, selected_port, INITIAL_PORT_VALUE),
        UIMode.DAY.value,
        "❌ 오류 발생 (Day 모드로 복원)",  # plain string
        "❌ 시스템 오류 발생",  # plain string
    )


# 매우 간단한 버튼 클릭 감지 콜백 (비활성화 - 메인 콜백으로 통합)
# @app.callback(
#     Output('mode-feedback', 'children'),
#     [Input('btn-ver-1', 'n_clicks'), Input('btn-ver-2', 'n_clicks')],
#     prevent_initial_call=True
# )
# def simple_button_test(n1, n2):
#     """가장 간단한 버튼 클릭 테스트"""
#     print(f"\n🚨🚨🚨 [SIMPLE_TEST] 버튼 클릭됨!")
#     print(f"🚨🚨🚨 [SIMPLE_TEST] Day: {n1}, Night: {n2}")
#
#     ctx = dash.callback_context
#     if ctx.triggered:
#         button_id = ctx.triggered[0]['prop_id'].split('.')[0]
#         print(f"🚨🚨🚨 [SIMPLE_TEST] 클릭된 버튼: {button_id}")
#
#         if button_id == 'btn-ver-2':
#             print(f"🌙🌙🌙 [SIMPLE_TEST] NIGHT 버튼 클릭 확인!")
#             return f"🌙 Night 버튼이 클릭되었습니다! (클릭 수: {n2})"
#         else:
#             print(f"☀️☀️☀️ [SIMPLE_TEST] DAY 버튼 클릭 확인!")
#             return f"☀️ Day 버튼이 클릭되었습니다! (클릭 수: {n1})"
#
#     return "버튼을 클릭해보세요"

# 클라이언트 사이드 디버깅은 JavaScript 파일에서 처리

# 콜백 등록
register_shared_callbacks(app, _snapshot, COLOR_SEQ, TH_DEFAULT, TL_DEFAULT)
register_day_callbacks(app, arduino, arduino_connected_ref, COLOR_SEQ, TH_DEFAULT, TL_DEFAULT, _snapshot)

# Night 콜백도 앱 시작 시 미리 등록
try:
    from night_sections.night_callbacks import register_night_callbacks

    register_night_callbacks(
        app,
        arduino,
        arduino_connected_ref,
        COLOR_SEQ,
        TH_DEFAULT,
        TL_DEFAULT,
        _snapshot,
    )
    print("✅ Night 콜백 사전 등록 완료")
except Exception as e:
    print(f"⚠️ Night 콜백 등록 실패: {e}")

# 포트 갱신 콜백은 day_callbacks.py에서 처리

# 디버그 정보 출력
debug_callback_registration(app)
post_registration_audit(app)

if __name__ == "__main__":
    try:
        print_startup_info(ARDUINO_CONNECTED)
        app.run(debug=True, host="127.0.0.1", port=8050, use_reloader=False, threaded=True)
    except KeyboardInterrupt:
        print("\n🛑 사용자가 애플리케이션을 종료했습니다")
    except SystemExit:
        pass
    except Exception as e:
        print(f"\n❌ 애플리케이션 오류: {e}")
    finally:
        cleanup_arduino_resources(arduino)
