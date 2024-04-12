from dash import html, dcc
import dash_bootstrap_components as dbc

def layout_clima_AI():
    return html.Div([
        dbc.Row(
            dbc.Col(
                html.Button('AI Summary', id='ai-summary-btn', className='btn btn-secondary mb-3 btn-dark'),  
                width=2  
            )
        ),
        dbc.Row([  
            dbc.Col( 
                dcc.Input(
                    id='new-tab-input',
                    type='text',
                    placeholder='Asking clima AI...',
                    className='form-control'  
                ),
                width=10  
            ),
            dbc.Col(
                html.Button('Submit', id='new-tab-button', className='btn btn-primary btn-black'),
                width=2
            )
        ]),
        html.Div(id='new-tab-output'),
        html.Div(id='ai-summary-output')  
    ])

