"""버튼 클릭 테스트용 간단한 앱"""

import dash
from dash import Input, Output, callback_context, html

# 간단한 앱 생성
app = dash.Dash(__name__)

# 레이아웃
app.layout = html.Div(
    [
        html.H1("버튼 클릭 테스트"),
        html.Div(
            [
                html.Button(
                    "☀️ Day 버튼",
                    id="btn-day",
                    n_clicks=0,
                    style={
                        "marginRight": "10px",
                        "padding": "15px 25px",
                        "fontSize": "18px",
                        "backgroundColor": "#007bff",
                        "color": "white",
                        "border": "none",
                        "borderRadius": "5px",
                        "cursor": "pointer",
                    },
                ),
                html.Button(
                    "🌙 Night 버튼",
                    id="btn-night",
                    n_clicks=0,
                    style={
                        "padding": "15px 25px",
                        "fontSize": "18px",
                        "backgroundColor": "#6c757d",
                        "color": "white",
                        "border": "none",
                        "borderRadius": "5px",
                        "cursor": "pointer",
                    },
                ),
            ],
            style={"textAlign": "center", "margin": "20px"},
        ),
        html.Div(
            id="result",
            style={
                "textAlign": "center",
                "fontSize": "20px",
                "margin": "20px",
                "padding": "20px",
                "border": "2px solid #007bff",
                "borderRadius": "10px",
            },
        ),
    ]
)


# 콜백
@app.callback(
    Output("result", "children"),
    [Input("btn-day", "n_clicks"), Input("btn-night", "n_clicks")],
    prevent_initial_call=False,
)
def update_result(day_clicks, night_clicks):
    print("\n🚨🚨🚨 [TEST] 콜백 호출됨!")
    print(f"🚨 [TEST] Day 클릭: {day_clicks}")
    print(f"🚨 [TEST] Night 클릭: {night_clicks}")

    ctx = callback_context
    print(f"🚨 [TEST] 컨텍스트: {ctx.triggered}")

    if not ctx.triggered:
        print("🚨 [TEST] 초기 로드")
        return "버튼을 클릭해보세요!"

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    print(f"🚨🚨🚨 [TEST] 클릭된 버튼: {button_id}")

    if button_id == "btn-night":
        print("🌙🌙🌙 [TEST] Night 버튼 클릭됨!")
        return f"🌙 Night 버튼이 클릭되었습니다! (총 {night_clicks}번)"
    if button_id == "btn-day":
        print("☀️☀️☀️ [TEST] Day 버튼 클릭됨!")
        return f"☀️ Day 버튼이 클릭되었습니다! (총 {day_clicks}번)"

    return f"Day: {day_clicks}, Night: {night_clicks}"


if __name__ == "__main__":
    print("Button test app starting...")
    app.run(debug=True, host="127.0.0.1", port=8051)
