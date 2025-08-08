import dash
from dash import html, dcc

app = dash.Dash(__name__)

# Generate static layout for 8 sensor sections
def sensor_section(section_num):
    return html.Div(
        [
            # Left: Temperature info
            html.Div(
                [
                    html.Div(f"Section {section_num:02}", style={"font-weight": "bold", "color": "white"}),
                    html.Div("01", style={"color": "white"}),
                    html.Div("25.6°C", style={"color": "white", "font-size": "20px"}),
                ],
                style={"width": "15%", "display": "inline-block", "vertical-align": "top"},
            ),
            # Middle-left: Buttons
            html.Div(
                [
                    html.Button("ID 변경", style={"margin": "2px"}),
                    html.Button("상/하한 임계값 변경", style={"margin": "2px"}),
                    html.Button("측정 주기 변경", style={"margin": "2px"}),
                ],
                style={"width": "25%", "display": "inline-block", "vertical-align": "top"},
            ),
            # Middle-right: Placeholder Graph
            html.Div(
                [
                    html.Div(f"Line {section_num}", style={"color": "white"}),
                    dcc.Graph(
                        id=f"graph-{section_num}",
                        figure={
                            "data": [],
                            "layout": {
                                "xaxis": {"visible": False},
                                "yaxis": {"visible": False},
                                "paper_bgcolor": "black",
                                "plot_bgcolor": "black",
                                "margin": dict(l=0, r=0, t=0, b=0),
                            },
                        },
                        style={"height": "80px"},
                    ),
                ],
                style={"width": "50%", "display": "inline-block", "vertical-align": "top"},
            ),
            # Right: Tool icon
            html.Div("🛠", style={"width": "5%", "display": "inline-block", "text-align": "center", "color": "white"}),
        ],
        style={"margin-bottom": "10px"},
    )

app.layout = html.Div(
    [
        html.H4("온도창", style={"color": "white", "font-weight": "bold", "margin-bottom": "10px"}),
        html.Hr(style={"border-color": "#555"}),
        html.Div([sensor_section(i) for i in range(1, 9)], style={"margin-bottom": "20px"}),
        html.H4("제어 패널", style={"color": "white", "margin-top": "30px", "margin-bottom": "10px", "font-weight": "bold"}),
        html.Div(
            [
                html.Button("보드 연결", style={"margin": "4px", "background-color": "#444", "color": "white", "border": "none", "padding": "5px 10px", "border-radius": "4px"}),
                html.Button("포트 선택", style={"margin": "4px", "background-color": "#555", "color": "white", "border": "none", "padding": "5px 10px", "border-radius": "4px"}),
                html.Button("COM1", style={"margin": "4px", "background-color": "#666", "color": "white", "border": "none", "padding": "5px 10px", "border-radius": "4px"}),
                html.Button("연결", style={"margin": "4px", "background-color": "#28a745", "color": "white", "border": "none", "padding": "5px 10px", "border-radius": "4px"}),
            ],
            style={"margin-bottom": "10px"},
        ),
        html.Div(style={"height": "80px", "background-color": "#222", "border-radius": "5px"}),
        html.H4("시스템 로그", style={"color": "white", "margin-top": "30px", "margin-bottom": "10px", "font-weight": "bold"}),
        html.Div(style={"height": "100px", "background-color": "#222", "border-radius": "5px"}),
    ],
    style={"background-color": "black", "padding": "20px", "font-family": "Arial, sans-serif"},
)

if __name__ == "__main__":
    app.run(debug=True)