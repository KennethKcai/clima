import dash
from dash import dcc, html
from dash_extensions.enrich import Output, Input, State
from dash import callback_context
from dash.exceptions import PreventUpdate
from dash.dependencies import ALL
import requests
import json
import pandas as pd
import numpy as np
import re
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
design_strategy_button = html.Div([
    html.Button("Design Strategy", id='strategy-button', n_clicks=0),
    html.Div(id='strategy-click-output', style={'padding': '5px'})
], style={'marginBottom': '20px'})



def layout_t_rh():
    return html.Div(
        className="container-row full-width",
        # style={'position': 'relative'},
        children=[
            # 主内容区域

            html.Div(
                id='main-content',
                className="container-col",
                style={'width': '100%'},  # 占据剩余的70%宽度
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
                id='text-box-container',
                className="container-col full-height",
                style={'width': '30%', 'display': 'none'},  # 初始隐藏
                children=[
                    dcc.Loading(
                        id="loading-ai-output",
                        children=[
                            html.Div(
                                id='ai-output',
                                className="text-box",
                                style={
                                    'height': '100vh', 
                                    'overflow': 'auto', 
                                    # 'position': 'fixed',
                                    'background-color': '#ededed',  # 修改背景颜色为灰色
                                    'color': '#4a4a49',  # 修改文本颜色为黑色
                                    'padding': '20px', 
                                    'border-radius': '15px',
                                },
                            
                                children=[
                                    html.P(
                                        "AI output will appear here after button click." * 50,
                                        style={
                                            'fontSize': '10px'  # 减小字体大小
                                        }
                                    )
                                ]
                            )
                        ],
                        type="circle",  # 指定加载指示器的样式
                    ),
                ]
            )

        ],
    )


@app.callback(
    [
        Output("yearly-chart", "children"),
        Output("store-dbt-yearly-data", "data"),
        Output("store-rh-yearly-data", "data")

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
        # print(data)
        return graph, data, None
    else:
        rh_yearly = yearly_profile(df, "RH", global_local, si_ip)
        rh_yearly.update_layout(xaxis=dict(rangeslider=dict(visible=True)))
        units = generate_units(si_ip)
        graph =  dcc.Graph(
            config=generate_chart_name("RelativeHumidity_yearly", meta, units),
            figure=rh_yearly,
        )
        data = rh_yearly.data  # store data for AI
        # print(data)
        return graph, None, data
    
@app.callback(
    [Output('text-box-container', 'style'),
     Output('main-content', 'style')],
    [Input('ai-button', 'n_clicks')]
)
def toggle_textbox_visibility(n_clicks):
    if n_clicks is None:
        raise PreventUpdate

    if n_clicks % 2 == 0:
        return {'display': 'none'}, {'width': '100%'}
    else:
        return {'width': '30%', 'display': 'block'}, {'width': '70%'}

@app.callback(
    Output('ai-output', 'children'),
    [Input('text-box-container', 'style')],
    [
        State('store-dbt-yearly-data', 'data'),
        State('store-rh-yearly-data', 'data')
    ],
)
def update_output(textbox_style, df_dbt, df_rh):
    if df_dbt:
        # DBT data
        if textbox_style['display'] == 'none' or df_dbt is None:
            return PreventUpdate

        try:
            y_values = [item['y'] for item in df_dbt if 'y' in item]
            base_values = [item['base'] for item in df_dbt if 'base' in item]
            rounded_data_y = [[round(num, 1) for num in sublist] for sublist in y_values]
            rounded_data_base = [[round(num, 1) for num in sublist] for sublist in base_values]

            lst_range_80 = [[base + y, base] for base, y in zip(rounded_data_base[0], rounded_data_y[0])]
            lst_range_90 = [[base + y, base] for base, y in zip(rounded_data_base[1], rounded_data_y[1])]

            data_with_description = {
                "ASHRAE adaptive comfort (80%)": lst_range_80,
                "ASHRAE adaptive comfort (90%)": lst_range_90,
                "Daily temperature average": rounded_data_y[3],
                "Daily temperature range": rounded_data_y[2]
            }
            json_data = json.dumps(data_with_description, indent=4)

            url = "https://api.zerowidth.ai/beta/process/XmZlDB2W1HFIzS7fmawI/fI8ys5r4pBiTnLdlQJdS"
            headers = {
                "Authorization": "Bearer sk0w-e1b943077ab9f86493693118eca0dfeb",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json={'data': {'variables': {'DATA': json_data}}}, headers=headers)
            if response.status_code == 200:
                content = response.json().get("output_data", {}).get("content", "")
                if content:
                # 将自定义文本与API返回的Markdown内容合并
                    months = re.findall(r'\b(JAN|FEB|MAR|APR|MAY|JUN|JULY|JUL|AUG|SEP|OCT|NOV|DEC)\b', content)
                    buttons = [html.Div([
                        html.Button(f"Continue Analyzing {month}", id={'type': 'month-button', 'index': month}, n_clicks=0),
                        dcc.Loading(
                            type="circle",  # 加载动画的类型
                            children=html.Div(id={'type': 'click-output', 'index': month}, style={'padding': '5px'})
                        )
                    ], style={'marginBottom': '20px'}) for month in set(months)]

                    # buttons.append(design_strategy_button)

                    full_content = f"### Tempreature AI analysis:\n\n {content}\n\n---\n\n"
                    return [dcc.Markdown(full_content)] + buttons
                else:
                    return "Content is empty"
            else:
                return f"API Error: {response.status_code}"
        except Exception as e:
            return f"Error processing data: {str(e)}"

    # RH data 
    elif df_rh:
        if textbox_style['display'] == 'none' or df_rh is None:
            return PreventUpdate

        # print(df_rh)
        try:
            y_values = [item['y'] for item in df_rh if 'y' in item]
            base_values = [item['base'] for item in df_rh if 'base' in item]
            ave_values = [item['customdata'] for item in df_rh if 'customdata' in item]


            rounded_data_y = [[round(num, 1) for num in sublist] for sublist in y_values]
            rounded_data_base = [[round(num, 1) for num in sublist] for sublist in base_values]
            rounded_data_ave = [[[round(num[0], 1)] + num[1:] for num in sublist] for sublist in ave_values]


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

            rh_range = generate_range_list(rounded_data_y[1], rounded_data_base[1])
            rh_band = generate_range_list(rounded_data_y[0], rounded_data_base[0])

            rh_ave = rounded_data_ave[0]

            data_with_description = {
                "humidity comfort band(%) from the first date to the last date of the year": rh_band,
                "Relative humidity Range(%) from the first date to the last date of the year": rh_range,
                "Average Relative humidity from the first date to the last date of the year": rh_ave
            }

            json_data = json.dumps(data_with_description, indent=4)

            url = "https://api.zerowidth.ai/beta/process/XmZlDB2W1HFIzS7fmawI/cVpYPLjRmxtZoHbHp24H"
            headers = {
                "Authorization": "Bearer sk0w-e1b943077ab9f86493693118eca0dfeb", 
                "Content-Type": "application/json"
            }

            data = {
                "data": {
                    "variables": {
                        "DATA": json_data,
                    }
                }
            }

            response = requests.post(url, json=data, headers=headers)

            if response.status_code == 200:
                content = response.json().get("output_data", {}).get("content", "")
                if content:
                # 将自定义文本与API返回的Markdown内容合并
                    months = re.findall(r'\b(JAN|FEB|MAR|APR|MAY|JUN|JULY|JUL|AUG|SEP|OCT|NOV|DEC)\b', content)
                    buttons = [html.Div([
                        html.Button(f"Continue Analyzing {month}", id={'type': 'month-button', 'index': month}, n_clicks=0),
                        dcc.Loading(
                            type="circle",  # 加载动画的类型
                            children=html.Div(id={'type': 'click-output', 'index': month}, style={'padding': '5px'})
                        )
                    ], style={'marginBottom': '20px'}) for month in set(months)]

                    # buttons.append(design_strategy_button)

                    full_content = f"### Humidity AI analysis:\n\n {content}\n\n---\n\n"
                    return [dcc.Markdown(full_content)] + buttons
                else:
                    return "Content is empty"
            else:
                return f"API Error: {response.status_code}"
        except Exception as e:
            return f"Error processing data: {str(e)}"

# Update the special month click output
@app.callback(
    Output({'type': 'click-output', 'index': dash.dependencies.MATCH}, 'children'),
    Input({'type': 'month-button', 'index': dash.dependencies.MATCH}, 'n_clicks'),
    State({'type': 'month-button', 'index': dash.dependencies.MATCH}, 'id'),
    State('store-dbt-yearly-data', 'data'),  # 假设这里存储的是原始数据
    prevent_initial_call=True
)
def on_button_click(n_clicks, button_id, df):
    if n_clicks is None or df is None:
        raise PreventUpdate
    
    month = button_id['index']

    try:
        y_values = [item['y'] for item in df if 'y' in item]
        base_values = [item['base'] for item in df if 'base' in item]
        rounded_data_y = [[round(num, 1) for num in sublist] for sublist in y_values]
        rounded_data_base = [[round(num, 1) for num in sublist] for sublist in base_values]

        lst_range_80 = [[base + y, base] for base, y in zip(rounded_data_base[0], rounded_data_y[0])]
        lst_range_90 = [[base + y, base] for base, y in zip(rounded_data_base[1], rounded_data_y[1])]

        data_with_description = {
            "ASHRAE adaptive comfort (80%)": lst_range_80,
            "ASHRAE adaptive comfort (90%)": lst_range_90,
            "Daily temperature average": rounded_data_y[3],
            "Daily temperature range": rounded_data_y[2]
        }
        json_data = json.dumps(data_with_description, indent=4)

        url = "https://api.zerowidth.ai/beta/process/dUakZrqR6iPgiJXslVOE/keL4947TSV17cRgaA1KM"
        headers = {
            "Authorization": "Bearer sk0w-d4b90953c5f969ae83fd15bbe10b3b53",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json={'data': {'variables': {'DATA': json_data, 'MONTH': month}}}, headers=headers)
        if response.status_code == 200:
            content = response.json().get("output_data", {}).get("content", "")
            if content:
                full_content = f"### Special month AI analysis:\n\n {content}\n\n---\n\n"
                return [dcc.Markdown(full_content)]
            else:
                return "Content is empty"
        else:
            return f"API Error: {response.status_code}"
    except Exception as e:
        return f"Error processing data: {str(e)}"


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


