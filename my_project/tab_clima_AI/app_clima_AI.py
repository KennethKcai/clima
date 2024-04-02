from dash import Dash, dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
import openai
load_dotenv()  # 读取 .env 文件中的环境变量

import os
openai.api_key = os.getenv('OPENAI_API_KEY')


def layout_clima_AI():
    return html.Div([
        dbc.Row(
            dbc.Col(
                html.Button('AI Summary', id='ai-summary-btn', className='btn btn-secondary mb-3 btn-dark'),  
                width=2  # 使按钮居中显示
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

@app.callback(
    Output('ai-summary-output', 'children'),
    [Input('ai-summary-btn', 'n_clicks')],
    [State('df-store', 'data')]
)
def get_ai_summary(n_clicks, df_json):
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    if n_clicks is None or df_json is None or triggered_id != 'ai-summary-btn':
        raise PreventUpdate

    
    # 创建摘要请求
    prompt = "Summarize the following data: \n\n" + df_json.head(10).to_string(index=False) + "\n\nSummary:"

    response = openai.Completion.create(
        engine="text-davinci-003",  # 根据你的API版本选择合适的engine
        prompt=prompt,
        max_tokens=150  # 设置最大的token数量
    )

    summary = response.choices[0].text.strip() if response else "Failed to get summary."
    return html.Div(summary)

if __name__ == '__main__':
    app.run_server(debug=True)