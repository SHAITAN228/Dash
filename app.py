from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import dash_draggable

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')



df = df.rename(columns={
    'country': 'Страна',
    'continent': 'Континент',
    'year': 'Год', 
    'pop': 'Население',
    'gdpPercap': 'ВВП на душу',
    'lifeExp': 'Продолжительность жизни'
})

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)




app.layout = html.Div([

    html.H3(children='Дашборд по странам', style={'textAlign': 'center'}),


    html.Div([
        html.H4('Выбранный год:'),
        html.Div(id='selected-year-display', style={'fontSize': '20px', 'fontWeight': 'bold'})
    ], style={'textAlign': 'center', 'margin': '0 auto'}),


    dash_draggable.ResponsiveGridLayout(

        id='draggable-dashboard',
        clearSavedLayout=False,
        children=[

            html.Div([
                html.H4('Линейная диаграмма', style={'textAlign': 'center'}),


                dcc.Dropdown(df['Страна'].unique(), ['Canada', 'China'], multi=True, id='line-dropdown-selection'),
                html.Div([

                    html.Label('Показатель:'),
                    dcc.Dropdown(
                        ['Население', 'ВВП на душу', 'Продолжительность жизни'],
                        'Население',
                        id='line-y-axis'
                    ),
                ]),

                dcc.Graph(id='line-graph', style={'height': 300})
            ], style={"height": "100%", "display": "flex", "flex-direction": "column"}),
            



            html.Div([
                html.H4('Пузырьковая диаграмма', style={'textAlign': 'center'}),


                    html.Div([
                    html.Div([
                        html.Label('Ось X:'),

                        dcc.Dropdown(
                            ['Население', 'ВВП на душу', 'Продолжительность жизни'],
                            'ВВП на душу',
                            id='bubble-x-axis'
                        ),
                    ], style={'width': '32%', 'display': 'inline-block'}),

                    html.Div([

                        html.Label('Ось Y:'),

                        dcc.Dropdown(
                            ['Население', 'ВВП на душу', 'Продолжительность жизни'],
                            'Продолжительность жизни',
                            id='bubble-y-axis'
                        ),
                    ], style={'width': '32%', 'display': 'inline-block'}),


                    html.Div([

                        html.Label('Размер пузырьков:'),

                        dcc.Dropdown(
                            ['Население', 'ВВП на душу', 'Продолжительность жизни'],
                            'Продолжительность жизни',
                            id='bubble-size'    

                        ),
                    ], style={'width': '32%', 'display': 'inline-block'}),

                ]),

                dcc.Graph(id='bubble-graph', style={'height': 300})
            ], style={"height": "100%", "display": "flex", "flex-direction": "column"}),
            


            html.Div([
                html.H4('Топ-15 стран по населению'),

                dcc.Graph(id='top15-graph', style={'height': 300})
            ], style={"height": "100%", "display": "flex", "flex-direction": "column"}),
            

            html.Div([

                html.H4('Население по континентам'),

                dcc.Graph(id='pie-graph', style={'height': 300})
            ], style={"height": "100%", "display": "flex", "flex-direction": "column"})
        ]
    )
])

selected_year = df['Год'].max()


@callback(
    Output('line-graph', 'figure'),
    [Input('line-dropdown-selection', 'value'),
     Input('line-y-axis', 'value')]
)
def update_line_graph(selected_countries, y_axis):

    if not selected_countries:
        return px.line(title='Выберите интересующие страны')
    
    dff = df[df['Страна'].isin(selected_countries)]
    fig = px.line(dff, x='Год', y=y_axis, color='Страна')

    fig.update_layout(clickmode='event+select')

    return fig



@callback(
    Output('selected-year-display', 'children'),
    Input('line-graph', 'clickData')
)
def update_selected_year(click_data):
    global selected_year
    
    if click_data and 'points' in click_data:
        selected_year = click_data['points'][0]['x']
    
    return str(selected_year)


@callback(
    Output('bubble-graph', 'figure'),
    [Input('bubble-x-axis', 'value'),
     Input('bubble-y-axis', 'value'),
     Input('bubble-size', 'value'),
     Input('selected-year-display', 'children')]
)
def update_bubble_graph(x_axis, y_axis, size_axis, selected_year_text):

    global selected_year
    dff = df[df['Год'] == selected_year]
    fig = px.scatter(dff, x=x_axis, y=y_axis, size=size_axis, color='Континент', hover_name='Страна', size_max=25)

    return fig

@callback(
    Output('top15-graph', 'figure'),
    Input('selected-year-display', 'children')
)

def update_top15_graph(selected_year_text):

    global selected_year
    dff = df[df['Год'] == selected_year]
    top15 = dff.nlargest(15, 'Население')

    fig = px.bar(top15, x='Население', y='Страна', color='Континент')
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})


    return fig

@callback(
    Output('pie-graph', 'figure'),
    Input('selected-year-display', 'children')
)

def update_pie_graph(selected_year_text):

    global selected_year
    dff = df[df['Год'] == selected_year]
    con_population = dff.groupby('Континент')['Население'].sum().reset_index()
    fig = px.pie(con_population, values='Население', names='Континент')

    return fig

if __name__ == '__main__':
    
    app.run(debug=True)
