from dash import html, dcc
import dash_bootstrap_components as dbc

def layout_clima_AI():
    return html.Div([
        dbc.Row(
            dbc.Col(
                html.Button('AI Summary', id='ai-summary-btn', className='btn btn-secondary mb-3 btn-dark'),  
                width={"size": 6, "offset": 3}  # 使按钮居中显示
            )
        ),
        dbc.Row([  # 创建一行
            dbc.Col(  # 创建一列
                dcc.Input(
                    id='new-tab-input',
                    type='text',
                    placeholder='Asking clima AI...',
                    className='form-control'  # 使用 Bootstrap 类来增加样式
                ),
                width=10  # 指定这列的宽度。Bootstrap 默认一行为 12 单位宽
            ),
            dbc.Col(
                html.Button('Submit', id='new-tab-button', className='btn btn-primary btn-black'),
                width=2
            )
        ]),
        html.Div(id='new-tab-output'),
        html.Div(id='ai-summary-output')  # 用于显示AI总结的输出
    ])