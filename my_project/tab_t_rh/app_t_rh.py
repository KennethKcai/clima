from dash import dcc, html
from dash_extensions.enrich import Output, Input, State
from dash.exceptions import PreventUpdate
import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime

from app import app
from my_project.global_scheme import dropdown_names
from my_project.template_graphs import heatmap, yearly_profile, daily_profile
from my_project.utils import (
    generate_chart_name,
    generate_units,
    generate_units_degree,
    title_with_tooltip,
    summary_table_tmp_rh_tab,
    title_with_link,
    dropdown,
)

var_to_plot = ["Dry bulb temperature", "Relative humidity"]


def layout_t_rh():
    return html.Div(
        className="container-row full-width",
        # style={'position': 'relative'},
        children=[
            # 主内容区域
            html.Div(
                className="container-col",
                style={'width': '70%'},  # 占据剩余的70%宽度
                children=[
                    html.Div(
                        className="container-row full-width align-center justify-center",
                        children=[
                            html.H4(
                                className="text-next-to-input", children=["Select a variable: "]
                            ),
                            dropdown(
                                id="dropdown",
                                className="dropdown-t-rh",
                                options={var: dropdown_names[var] for var in var_to_plot},
                                value=dropdown_names[var_to_plot[0]],
                            ),
                        ],
                    ),
                    html.Div(
                        className="container-col",
                        children=[
                            html.Div(
                                className="container-row align-items-center",  
                                children=[
                                    title_with_link(
                                        text="Yearly chart",
                                        id_button="yearly-chart-label",
                                        doc_link="https://cbe-berkeley.gitbook.io/clima/documentation/tabs-explained/temperature-and-humidity/temperatures-explained",
                                    ),
                                    html.Button(
                                        "AI",
                                        id="ai-button",
                                        n_clicks=0,
                                        className="ml-2 btn btn-dark btn-sm"
                                    ),
                                ]
                            ),
                            dcc.Loading(
                                type="circle",
                                children=html.Div(id="yearly-chart"),
                            ),
                            html.Div(
                                children=title_with_link(
                                    text="Daily chart",
                                    id_button="daily-chart-label",
                                    doc_link="https://cbe-berkeley.gitbook.io/clima/documentation/tabs-explained/temperature-and-humidity/temperatures-explained",
                                ),
                            ),
                            dcc.Loading(
                                type="circle",
                                children=html.Div(id="daily"),
                            ),
                            html.Div(
                                children=title_with_link(
                                    text="Heatmap chart",
                                    id_button="heatmap-chart-label",
                                    doc_link="https://cbe-berkeley.gitbook.io/clima/documentation/tabs-explained/temperature-and-humidity/temperatures-explained",
                                ),
                            ),
                            dcc.Loading(
                                type="circle",
                                children=html.Div(id="heatmap"),
                            ),
                            html.Div(
                                children=title_with_tooltip(
                                    text="Descriptive statistics",
                                    tooltip_text="count, mean, std, min, max, and percentiles",
                                    id_button="table-tmp-rh",
                                ),
                            ),
                            html.Div(
                                id="table-tmp-hum",
                            ),
                        ],
                    ),
                ]
            ),
            # 独立的 textbox 区域
            html.Div(
                className="container-col full-height",
                style={'width': '30%'},  # 占据30%的宽度
                children=[
                    html.Div(
                        className="text-box",
                        style={
                            'position': 'fixed', 
                            'width': '30%', 
                            'height': '100vh',  # 设定高度为视窗高度
                            'overflow': 'auto',  # 自动显示滚动条
                            'background-color': '#000000',  # 黑色背景
                            'color': '#d3d3d3',  # 灰色文字
                            'padding': '20px',  # 内边距
                            'border-radius': '15px',  # 圆角边框
                        },
                        children=[
                            html.P(id='ai-output', children='AI output will appear here after button click.' * 50)  # 增加文本长度来演示滚动效果
                        ]
                    ),
                ]
            )
        ],
    )


@app.callback(
    [
        Output("yearly-chart", "children"),
        Output("store-dbt-yearly-data", "data")
    ],
    [
        Input("df-store", "modified_timestamp"),
        Input("global-local-radio-input", "value"),
        Input("dropdown", "value"),
    ],
    [
        State("df-store", "data"),
        State("meta-store", "data"),
        State("si-ip-unit-store", "data"),
    ],
)
def update_yearly_chart(ts, global_local, dd_value, df, meta, si_ip):
    if dd_value == dropdown_names[var_to_plot[0]]:
        dbt_yearly = yearly_profile(df, "DBT", global_local, si_ip)
        dbt_yearly.update_layout(xaxis=dict(rangeslider=dict(visible=True)))
        units = generate_units_degree(si_ip)
        # print(dbt_yearly.data)
        graph = dcc.Graph(
            config=generate_chart_name("DryBulbTemperature_yearly", meta, units),
            figure=dbt_yearly
        )
        data = dbt_yearly.data  # store data for AI
        return graph, data
    else:
        rh_yearly = yearly_profile(df, "RH", global_local, si_ip)
        rh_yearly.update_layout(xaxis=dict(rangeslider=dict(visible=True)))
        units = generate_units(si_ip)
        graph =  dcc.Graph(
            config=generate_chart_name("RelativeHumidity_yearly", meta, units),
            figure=rh_yearly,
        )
        data = rh_yearly.data  # store data for AI
        return graph, data
    

@app.callback(
    Output('ai-output', 'children'),
    Input('ai-button', 'n_clicks'),
    # State('df-store', 'data')  # store data from API
    State('store-dbt-yearly-data', 'data')  # store data from yearly chart
)
def update_output(n_clicks, df):
    if n_clicks is None or df is None:
        raise PreventUpdate

    # get the y data and base values
    y_values = [item['y'] for item in df if 'y' in item]
    base_values = [item['base'] for item in df if 'base' in item]

    # round the data to 1 decimal place
    rounded_data_y = [[round(num, 1) for num in sublist] for sublist in y_values]
    rounded_data_base = [[round(num, 1) for num in sublist] for sublist in base_values]

    # print(rounded_data_y[0])
    # print(rounded_data_base[0])
    
    # function to generate range list
    def generate_range_list(y_values, base_values):
        lst_range_min = []
        lst_range_max = []

        for i in range(len(base_values)):
            range_min = base_values[i]
            lst_range_min.append(range_min)
            range_max = base_values[i] + y_values[i]
            lst_range_max.append(range_max)
        
        lst_range = []
        for i in range(len(lst_range_min)):
            range_item = [lst_range_min[i], lst_range_max[i]]
            lst_range.append(range_item)
        
        return lst_range

    lst_range_80 = generate_range_list(rounded_data_y[0], rounded_data_base[0])
    lst_range_90 = generate_range_list(rounded_data_y[1], rounded_data_base[1])

    temp_data = rounded_data_y[3]
    tem_range = rounded_data_y[2]

    # restructuring the input json data with 4 sections
    data_with_description = {
        "ASHRAE adaptive comfort (80%) for 80 percentile from the first date to the last date of the year": lst_range_80,
        "ASHRAE adaptive comfort (80%) for 90 percentile from the first date to the last date of the year": lst_range_90,
        "daily temperature average from the first date to the last date of the year": temp_data,
        "daily temperature range from the first date to the last date of the year": tem_range
    }

    json_data = json.dumps(data_with_description, indent=4)

    # API endpoint
    url = "https://api.zerowidth.ai/beta/process/XmZlDB2W1HFIzS7fmawI/fI8ys5r4pBiTnLdlQJdS"
    headers = {
        "Authorization": "Bearer sk0w-e1b943077ab9f86493693118eca0dfeb",
        "Content-Type": "application/json"
    }
    
    print(json_data)
    # Prepare data for API
    data = {
        "data": {
            "variables": {
                "DATA": json_data
            }
        }
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        json_response = response.json()
        content = json_response.get("output_data", {}).get("content", "")
        if content:
            return dcc.Markdown(content)
        else:
            return html.Div('Error: Content is empty')
    else:

        return html.Div('Error: API call failed')



@app.callback(
    Output("daily", "children"),
    [
        Input("df-store", "modified_timestamp"),
        Input("global-local-radio-input", "value"),
        Input("dropdown", "value"),
    ],
    [
        State("df-store", "data"),
        State("meta-store", "data"),
        State("si-ip-unit-store", "data"),
    ],
)
def update_daily(ts, global_local, dd_value, df, meta, si_ip):
    if dd_value == dropdown_names[var_to_plot[0]]:
        units = generate_units_degree(si_ip)
        return dcc.Graph(
            config=generate_chart_name("DryBulbTemperature_daily", meta, units),
            figure=daily_profile(
                df[["DBT", "hour", "UTC_time", "month_names", "day", "month"]],
                "DBT",
                global_local,
                si_ip,
            ),
        )
    else:
        units = generate_units(si_ip)
        return dcc.Graph(
            config=generate_chart_name("RelativeHumidity_daily", meta, units),
            figure=daily_profile(
                df[["RH", "hour", "UTC_time", "month_names", "day", "month"]],
                "RH",
                global_local,
                si_ip,
            ),
        )


@app.callback(
    [Output("heatmap", "children")],
    [
        Input("df-store", "modified_timestamp"),
        Input("global-local-radio-input", "value"),
        Input("dropdown", "value"),
    ],
    [
        State("df-store", "data"),
        State("meta-store", "data"),
        State("si-ip-unit-store", "data"),
    ],
)
def update_heatmap(ts, global_local, dd_value, df, meta, si_ip):
    """Update the contents of tab three. Passing in general info (df, meta)."""
    if dd_value == dropdown_names[var_to_plot[0]]:
        units = generate_units_degree(si_ip)
        return dcc.Graph(
            config=generate_chart_name("DryBulbTemperature_heatmap", meta, units),
            figure=heatmap(
                df[["DBT", "hour", "UTC_time", "month_names", "day"]],
                "DBT",
                global_local,
                si_ip,
            ),
        )
    else:
        units = generate_units(si_ip)
        return dcc.Graph(
            config=generate_chart_name("RelativeHumidity_heatmap", meta, units),
            figure=heatmap(
                df[["RH", "hour", "UTC_time", "month_names", "day"]],
                "RH",
                global_local,
                si_ip,
            ),
        )


@app.callback(
    Output("table-tmp-hum", "children"),
    [
        Input("df-store", "modified_timestamp"),
        Input("dropdown", "value"),
    ],
    [State("df-store", "data"), State("si-ip-unit-store", "data")],
)
def update_table(ts, dd_value, df, si_ip):
    """Update the contents of tab three. Passing in general info (df, meta)."""
    return summary_table_tmp_rh_tab(
        df[["month", "hour", dd_value, "month_names"]], dd_value, si_ip
    )


def default_serializer(obj):
    """JSON serializer for extra types."""
    if isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    elif isinstance(obj, (pd.Timedelta, np.timedelta64)):
        return str(obj)
    elif isinstance(obj, (np.ndarray, pd.Series)):
        return obj.tolist()
    elif isinstance(obj, np.generic):
        return obj.item()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")