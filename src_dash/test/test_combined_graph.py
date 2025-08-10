import os
import sys

import pytest

# allow importing core module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import plotly.graph_objects as go
from core.shared_callbacks import register_shared_callbacks
from core.ui_modes import UIMode
from dash import Dash


def snapshot_stub(*args, **kwargs):
    # connection_status, style, current_temps, latest_data, msgs
    return "", {}, {}, [], []


def get_combined_callback(app, *args):
    # Find the combined_graph callback function
    for cb in app.callback_map.values():
        # outputs field may differ; inspect keys instead
        if "combined-graph.figure" in cb["state"][0]["id"] if "state" in cb else False:
            continue
    # Fallback: iterate functions to find matching signature
    for route, cb in app.callback_map.items():
        if "combined-graph.figure" in route:
            return cb["callback"]
    pytest.skip("combined_graph callback not found")


def test_empty_selection_returns_empty_figure():
    app = Dash(__name__, suppress_callback_exceptions=True)
    register_shared_callbacks(app, snapshot_stub, ["#000"], 0.0, 0.0)
    # Retrieve the callback
    # Dash v2 organizes callback_map keys as output+input combo
    cb_func = None
    for cb in app.callback_map.values():
        if cb["callback"].__name__ == "update_combined_graph":
            cb_func = cb["callback"]
            break
    assert cb_func, "update_combined_graph callback not registered"
    # Call original callback function with empty selection (bypass Dash wrapper)
    orig_func = getattr(cb_func, "__wrapped__", cb_func)
    fig = orig_func(0, [], UIMode.NIGHT.value)
    assert isinstance(fig, go.Figure)
    assert not fig.data
    title = fig.layout.title.text if fig.layout.title else fig.layout["title"]
    assert "센서 선택 없음" in title
