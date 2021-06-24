import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate
from my_project.utils import generate_chart_name

from my_project.global_scheme import (
    fig_config,
    dropdown_names,
    container_row_center_full,
    container_col_center_one_of_three,
)
from dash.dependencies import Input, Output, State

from my_project.tab_data_explorer.charts_data_explorer import (
    custom_heatmap,
    two_var_graph,
    three_var_graph,
)
from my_project.template_graphs import heatmap, yearly_profile, daily_profile, barchart
import pandas as pd

from app import app, cache, TIMEOUT


def section_one_inputs():
    """Return the inputs from section one."""
    return html.Div(
        className="container-row full-width row-center",
        children=[
            html.H6(className="text-next-to-input", children=["Variable:"]),
            dcc.Dropdown(
                id="sec1-var-dropdown",
                options=[
                    {"label": i, "value": dropdown_names[i]} for i in dropdown_names
                ],
                value="DBT",
            ),
        ],
    )


def section_one():
    """Return the graphs for section one"""
    return html.Div(
        className="container-col full-width",
        children=[
            section_one_inputs(),
            dcc.Loading(
                type="circle",
                children=html.Div(id="yearly-explore", className="full-width"),
            ),
            dcc.Loading(
                type="circle",
                children=[
                    dcc.Graph(
                        className="full-width", id="query-daily", config=fig_config
                    ),
                ],
            ),
            dcc.Loading(
                type="circle",
                children=[
                    dcc.Graph(
                        className="full-width", id="query-heatmap", config=fig_config
                    ),
                ],
            ),
        ],
    )


def section_two_inputs():
    """Return all the input forms from section two."""
    return html.Div(
        className="container-row full-width three-inputs-container",
        children=[
            html.Div(
                className=container_col_center_one_of_three,
                children=[
                    html.Div(
                        className=container_row_center_full,
                        children=[
                            html.H6(
                                className="text-next-to-input", children=["Variable:"]
                            ),
                            dcc.Dropdown(
                                id="sec2-var-dropdown",
                                options=[
                                    {"label": i, "value": dropdown_names[i]}
                                    for i in dropdown_names
                                ],
                                value="RH",
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                className=container_col_center_one_of_three,
                children=[
                    dbc.Checklist(
                        options=[
                            {"label": "Apply Time Filters", "value": "time"},
                        ],
                        value=[],
                        id="sec2-time-filter-input",
                    ),
                    html.Div(
                        className="container-row full-width justify-center",
                        children=[
                            html.H6("Month Range"),
                            dcc.RangeSlider(
                                id="sec2-month-slider",
                                className="month-hour-slider",
                                min=1,
                                max=12,
                                step=1,
                                value=[1, 12],
                                marks={1: "1", 12: "12"},
                                tooltip={"always_visible": False, "placement": "top"},
                                allowCross=True,
                            ),
                        ],
                    ),
                    html.Div(
                        className="container-row full-width justify-center",
                        children=[
                            html.H6("Hour Range"),
                            dcc.RangeSlider(
                                className="month-hour-slider",
                                id="sec2-hour-slider",
                                min=1,
                                max=24,
                                step=1,
                                value=[1, 24],
                                marks={1: "1", 24: "24"},
                                tooltip={
                                    "always_visible": False,
                                    "placement": "topLeft",
                                },
                                allowCross=True,
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                className=container_col_center_one_of_three,
                children=[
                    dbc.Checklist(
                        options=[
                            {"label": "Apply Data Filters", "value": "data"},
                        ],
                        value=[],
                        id="sec2-data-filter-input",
                    ),
                    html.Div(
                        className=container_row_center_full,
                        children=[
                            html.H6(
                                className="text-next-to-input",
                                children=["Filter Variable:"],
                            ),
                            dcc.Dropdown(
                                id="sec2-data-filter-var",
                                options=[
                                    {"label": i, "value": dropdown_names[i]}
                                    for i in dropdown_names
                                ],
                                value="RH",
                            ),
                        ],
                    ),
                    html.Div(
                        className=container_row_center_full,
                        children=[
                            html.H6(
                                className="text-next-to-input", children=["Min Value:"]
                            ),
                            dbc.Input(
                                className="num-input",
                                id="sec2-min-val",
                                placeholder="Enter a number for the min val",
                                type="number",
                                min=0,
                                step=1,
                            ),
                        ],
                    ),
                    html.Div(
                        className=container_row_center_full,
                        children=[
                            html.H6(
                                className="text-next-to-input", children=["Max Value:"]
                            ),
                            dbc.Input(
                                className="num-input",
                                id="sec2-max-val",
                                placeholder="Enter a number for the max val",
                                type="number",
                                min=0,
                                step=1,
                            ),
                        ],
                    ),
                    # dbc.Button(
                    #     "Apply", color = "primary", className = "mr-1", id = "tab6-sec2-data-button"
                    # )
                ],
            ),
        ],
    )


def section_two():
    """Return the two graphs in section two."""
    return html.Div(
        id="tab6-sec2-container",
        className="container-col justify-center full-width",
        children=[
            section_two_inputs(),
            dcc.Loading(
                type="circle",
                children=[
                    dcc.Graph(
                        className="full-width", id="custom-heatmap", config=fig_config
                    ),
                ],
            ),
            dbc.Checklist(
                options=[
                    {"label": "Normalize", "value": "normal"},
                ],
                value=[],
                id="normalize",
            ),
            dcc.Loading(
                type="circle",
                children=[
                    dcc.Graph(
                        className="full-width", id="custom-summary", config=fig_config
                    ),
                ],
            ),
        ],
    )


def section_three_inputs():
    """"""
    return html.Div(
        className="container-row full-width three-inputs-container",
        children=[
            html.Div(
                className=container_col_center_one_of_three,
                children=[
                    html.Div(
                        className=container_row_center_full,
                        children=[
                            html.H6(
                                className="text-next-to-input", children=["X Variable:"]
                            ),
                            dcc.Dropdown(
                                className="tab6-sec3-dropdown",
                                id="tab6-sec3-var-x-dropdown",
                                options=[
                                    {"label": i, "value": dropdown_names[i]}
                                    for i in dropdown_names
                                ],
                                value="DBT",
                            ),
                        ],
                    ),
                    html.Div(
                        className=container_row_center_full,
                        children=[
                            html.H6(
                                className="text-next-to-input", children=["Y Variable:"]
                            ),
                            dcc.Dropdown(
                                className="tab6-sec3-dropdown",
                                id="tab6-sec3-var-y-dropdown",
                                options=[
                                    {"label": i, "value": dropdown_names[i]}
                                    for i in dropdown_names
                                ],
                                value="RH",
                            ),
                        ],
                    ),
                    html.Div(
                        className=container_row_center_full,
                        children=[
                            html.H6(
                                className="text-next-to-input", children=["Color By:"]
                            ),
                            dcc.Dropdown(
                                className="tab6-sec3-dropdown",
                                id="tab6-sec3-colorby-dropdown",
                                options=[
                                    {"label": i, "value": dropdown_names[i]}
                                    for i in dropdown_names
                                ],
                                value="GHrad",
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                className=container_col_center_one_of_three,
                children=[
                    dbc.Checklist(
                        options=[
                            {"label": "Apply Time Filters", "value": "time"},
                        ],
                        value=[],
                        id="tab6-sec3-time-filter-input",
                    ),
                    html.Div(
                        className="container-row full-width justify-center",
                        children=[
                            html.H6("Month Range"),
                            dcc.RangeSlider(
                                id="tab6-sec3-query-month-slider",
                                min=1,
                                max=12,
                                step=1,
                                value=[1, 12],
                                marks={1: "1", 12: "12"},
                                tooltip={"always_visible": False, "placement": "top"},
                                allowCross=True,
                            ),
                        ],
                    ),
                    html.Div(
                        className="container-row full-width justify-center",
                        children=[
                            html.H6("Hour Range"),
                            dcc.RangeSlider(
                                id="tab6-sec3-query-hour-slider",
                                min=1,
                                max=24,
                                step=1,
                                value=[1, 24],
                                marks={1: "1", 24: "24"},
                                tooltip={"always_visible": False, "placement": "top"},
                                allowCross=True,
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                className=container_col_center_one_of_three,
                children=[
                    dbc.Checklist(
                        options=[
                            {"label": "Apply Data Filters", "value": "data"},
                        ],
                        value=[],
                        id="tab6-sec3-data-filter-input",
                    ),
                    html.Div(
                        className=container_row_center_full,
                        children=[
                            html.H6(
                                className="text-next-to-input",
                                children=["Filter Variable:"],
                            ),
                            dcc.Dropdown(
                                className="tab6-sec3-dropdown",
                                id="tab6-sec3-filter-var-dropdown",
                                options=[
                                    {"label": i, "value": dropdown_names[i]}
                                    for i in dropdown_names
                                ],
                                value="RH",
                            ),
                        ],
                    ),
                    html.Div(
                        className=container_row_center_full,
                        children=[
                            html.H6(
                                className="text-next-to-input", children=["Min Value:"]
                            ),
                            dbc.Input(
                                className="num-input",
                                id="tab6-sec3-min-val",
                                placeholder="Enter a number for the min val",
                                type="number",
                                min=0,
                                step=1,
                            ),
                        ],
                    ),
                    html.Div(
                        className=container_row_center_full,
                        children=[
                            html.H6(
                                className="text-next-to-input", children=["Max Value:"]
                            ),
                            dbc.Input(
                                className="num-input",
                                id="tab6-sec3-max-val",
                                placeholder="Enter a number for the max val",
                                type="number",
                                min=0,
                                step=1,
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def section_three():
    """Return the two graphs in section three."""
    return html.Div(
        className="container-col full-width",
        children=[
            section_three_inputs(),
            dcc.Loading(
                type="circle",
                children=[
                    dcc.Graph(id="three-var", config=fig_config),
                ],
            ),
            dcc.Loading(
                type="circle",
                children=[
                    dcc.Graph(id="two-var", config=fig_config),
                ],
            ),
        ],
    )


def layout_data_explorer():
    """Return the contents of tab six." """
    return html.Div(
        className="continer-col justify-center",
        children=[section_one(), section_two(), section_three()],
    )


@app.callback(
    Output("yearly-explore", "children"),
    # Section One
    [Input("sec1-var-dropdown", "value")],
    # General
    [Input("global-local-radio-input", "value")],
    [State("df-store", "data")],
    [State("meta-store", "data")],
)
@cache.memoize(timeout=TIMEOUT)
def update_tab_yearly(var, global_local, df, meta):
    """Update the contents of tab size. Passing in the info from the dropdown and the general info."""
    df = pd.read_json(df, orient="split")
    if df[var].mean() == 99990.0:
        return dbc.Alert(
            """The selected variable is not available,
            the Clima tool could not generate the yearly plot""",
            color="warning",
            className="m-4",
        )
    else:
        return dcc.Graph(
            config=generate_chart_name("data_explorer", meta),
            figure=yearly_profile(df, var, global_local),
        )


@app.callback(
    Output("query-daily", "figure"),
    # Section One
    [Input("sec1-var-dropdown", "value")],
    # General
    [Input("global-local-radio-input", "value")],
    [State("df-store", "data")],
)
@cache.memoize(timeout=TIMEOUT)
def update_tab_daily(var, global_local, df):
    """Update the contents of tab size. Passing in the info from the dropdown and the general info."""
    df = pd.read_json(df, orient="split")
    return daily_profile(df, var, global_local)


@app.callback(
    Output("query-heatmap", "figure"),
    # Section One
    [Input("sec1-var-dropdown", "value")],
    # General
    [Input("global-local-radio-input", "value")],
    [State("df-store", "data")],
)
@cache.memoize(timeout=TIMEOUT)
def update_tab_heatmap(var, global_local, df):
    """Update the contents of tab size. Passing in the info from the dropdown and the general info."""
    df = pd.read_json(df, orient="split")
    return heatmap(df, var, global_local)


### Section Two ###
@app.callback(
    Output("custom-heatmap", "figure"),
    Output("custom-summary", "style"),
    Output("custom-summary", "figure"),
    Output("normalize", "style"),
    # Section Two
    [Input("sec2-var-dropdown", "value")],
    [Input("sec2-time-filter-input", "value")],
    [Input("sec2-month-slider", "value")],
    [Input("sec2-hour-slider", "value")],
    [Input("sec2-data-filter-input", "value")],
    [Input("sec2-data-filter-var", "value")],
    [Input("sec2-min-val", "value")],
    [Input("sec2-max-val", "value")],
    [Input("normalize", "value")],
    # General
    [Input("global-local-radio-input", "value")],
    [State("df-store", "data")],
)
@cache.memoize(timeout=TIMEOUT)
def update_tab_six_two(
    var,
    time_filter,
    month,
    hour,
    data_filter,
    filter_var,
    min_val,
    max_val,
    normalize,
    global_local,
    df,
):
    """Update the contents of tab size. Passing in the info from the dropdown and the general info."""
    df = pd.read_json(df, orient="split")
    time_filter_info = [time_filter, month, hour]
    data_filter_info = [data_filter, filter_var, min_val, max_val]

    heatmap = custom_heatmap(df, global_local, var, time_filter_info, data_filter_info)
    no_display = {"display": "none"}

    if data_filter:
        return (
            heatmap,
            {},
            barchart(df, var, time_filter_info, data_filter_info, normalize),
            {},
        )
    return heatmap, no_display, {"data": [], "layout": {}, "frames": []}, no_display


### Section Three ###
@app.callback(
    Output("three-var", "figure"),
    Output("two-var", "figure"),
    # Section Three
    [Input("tab6-sec3-var-x-dropdown", "value")],
    [Input("tab6-sec3-var-y-dropdown", "value")],
    [Input("tab6-sec3-colorby-dropdown", "value")],
    [Input("tab6-sec3-time-filter-input", "value")],
    [Input("tab6-sec3-query-month-slider", "value")],
    [Input("tab6-sec3-query-hour-slider", "value")],
    [Input("tab6-sec3-data-filter-input", "value")],
    [Input("tab6-sec3-filter-var-dropdown", "value")],
    [Input("tab6-sec3-min-val", "value")],
    [Input("tab6-sec3-max-val", "value")],
    # General
    [Input("global-local-radio-input", "value")],
    [State("df-store", "data")],
)
@cache.memoize(timeout=TIMEOUT)
def update_tab_six_three(
    var_x,
    var_y,
    colorby,
    time_filter,
    month,
    hour,
    data_filter,
    data_filter_var,
    min_val,
    max_val,
    global_local,
    df,
):
    """Update the contents of tab size. Passing in the info from the dropdown and the general info."""
    # todo: dont allow to input if apply filter not checked
    # if (min_val3 is None or max_val3 is None) and data_filter3:
    #     raise PreventUpdate
    df = pd.read_json(df, orient="split")
    time_filter_info = [time_filter, month, hour]
    data_filter_info = [data_filter, data_filter_var, min_val, max_val]
    if data_filter and (min_val is None or max_val is None):
        raise PreventUpdate
    else:
        two = two_var_graph(
            df, global_local, var_x, var_y, colorby, time_filter_info, data_filter_info
        )
        three = three_var_graph(
            df, global_local, var_x, var_y, colorby, time_filter_info, data_filter_info
        )
        return three, two