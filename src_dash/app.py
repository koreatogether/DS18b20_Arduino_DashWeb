"""DS18B20 Arduino 연계 실시간 Dash 웹 애플리케이션 - 리팩토링 버전"""
import dash
from dash import Input, Output, State

# Core 모듈들
from core import (
    initialize_arduino, cleanup_arduino_resources,
    create_snapshot_function, register_shared_callbacks,
    create_main_layout, build_validation_layout,
    configure_console_encoding, debug_callback_registration, 
    post_registration_audit, print_startup_info
)

# 레이아웃 모듈들
from night_sections.night_layout import create_layout_v2
from day_sections.day_layout import create_layout_v1
from day_sections.day_callbacks import register_day_callbacks

# 앱 초기화
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# 콘솔 인코딩 설정
configure_console_encoding()

# Arduino 초기화
arduino_config = initialize_arduino()
arduino = arduino_config['arduino']
ARDUINO_CONNECTED = arduino_config['connected']
INITIAL_PORT_OPTIONS = arduino_config['initial_port_options']
selected_port = arduino_config['selected_port']
INITIAL_PORT_VALUE = arduino_config['initial_port_value']

# 상수 정의
COLOR_SEQ = ["#2C7BE5", "#00A3A3", "#E67E22", "#6F42C1", "#FF6B6B", "#20C997", "#795548", "#FFB400"]
TH_DEFAULT = 55.0
TL_DEFAULT = -25.0

# 데이터 스냅샷 함수 생성
arduino_connected_ref = {'connected': ARDUINO_CONNECTED}
_snapshot = create_snapshot_function(arduino, arduino_connected_ref)

# 앱 레이아웃 설정
app.layout = create_main_layout(INITIAL_PORT_OPTIONS, selected_port, INITIAL_PORT_VALUE, create_layout_v1)
app.validation_layout = build_validation_layout()

# 메인 레이아웃 전환 콜백
@app.callback(
    Output('main-content', 'children'),
    Output('ui-version-store', 'data'),
    Input('btn-ver-1', 'n_clicks'),
    Input('btn-ver-2', 'n_clicks'),
    State('ui-version-store', 'data')
)
def update_main_layout(n1, n2, current_version):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'btn-ver-1'  # Default to v1
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'btn-ver-2':
        print("🌙 Night mode 버튼 클릭 - v2 레이아웃 전환")
        return create_layout_v2(INITIAL_PORT_OPTIONS, selected_port, INITIAL_PORT_VALUE, 
                               app, arduino, ARDUINO_CONNECTED, COLOR_SEQ, TH_DEFAULT, TL_DEFAULT, _snapshot), 'v2'
    else:  # btn-ver-1 or default
        if button_id == 'btn-ver-1':
            print("☀️ Day mode 버튼 클릭 - v1 레이아웃 전환")
        return create_layout_v1(INITIAL_PORT_OPTIONS, selected_port, INITIAL_PORT_VALUE), 'v1'

# 콜백 등록
register_shared_callbacks(app, _snapshot, COLOR_SEQ, TH_DEFAULT, TL_DEFAULT)
register_day_callbacks(app, arduino, arduino_connected_ref, COLOR_SEQ, TH_DEFAULT, TL_DEFAULT, _snapshot)

# Night 콜백도 앱 시작 시 미리 등록
try:
    from night_sections.night_callbacks import register_night_callbacks
    register_night_callbacks(app, arduino, arduino_connected_ref, COLOR_SEQ, TH_DEFAULT, TL_DEFAULT, _snapshot)
    print("✅ Night 콜백 사전 등록 완료")
except Exception as e:
    print(f"⚠️ Night 콜백 등록 실패: {e}")

# 디버그 정보 출력
debug_callback_registration(app)
post_registration_audit(app)

if __name__ == '__main__':
    try:
        print_startup_info(ARDUINO_CONNECTED)
        app.run(debug=False, host='127.0.0.1', port=8050, 
                use_reloader=False, threaded=True)
    except KeyboardInterrupt:
        print("\n🛑 사용자가 애플리케이션을 종료했습니다")
    except SystemExit:
        pass
    except Exception as e:
        print(f"\n❌ 애플리케이션 오류: {e}")
    finally:
        cleanup_arduino_resources(arduino)