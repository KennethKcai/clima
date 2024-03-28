# 在对应的 Tab 文件夹中创建一个新文件，例如 new_tab/app_new_tab.py
from dash import html, dcc

def layout_clima_AI():
    return html.Div([
        dcc.Input(id='new-tab-input', type='text', placeholder='Enter something...'),
        html.Button('Submit', id='new-tab-button'),
        html.Div(id='new-tab-output')  # 这个 Div 用来显示按钮点击后的输出
    ])
