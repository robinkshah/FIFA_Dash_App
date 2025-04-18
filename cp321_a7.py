# live server link: https://fifa-dash-app-x23i.onrender.com/ 
# not password protected

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

#clean data
url = "https://en.wikipedia.org/wiki/List_of_FIFA_World_Cup_finals"
tables = pd.read_html(url)
df = tables[3][['Year', 'Winners', 'Runners-up']].copy()
df.columns = ['Year', 'Winner', 'RunnerUp']

# change west germany to germany
df['Winner'] = df['Winner'].replace({'West Germany': 'Germany', 'FR Germany': 'Germany'})
df['RunnerUp'] = df['RunnerUp'].replace({'West Germany': 'Germany', 'FR Germany': 'Germany'})

win_counts = df['Winner'].value_counts().reset_index()
win_counts.columns = ['Country', 'Wins']

#choropleth map
map_fig = px.choropleth(
    win_counts,
    locations='Country',
    locationmode='country names',
    color='Wins',
    title='FIFA World Cup Wins by Country',
    color_continuous_scale='Viridis'
)

# Dash app
app = Dash(__name__)
server = app.server
app.title = "FIFA World Cup Dashboard"

app.layout = html.Div([
    html.H1("FIFA World Cup Finals Dashboard", style={'textAlign': 'center'}),

    # Choropleth map
    dcc.Graph(figure=map_fig),

    html.H2("Select a Country to View Number of Wins"),
    dcc.Dropdown(
        id='country-dropdown',
        options=[{'label': c, 'value': c} for c in sorted(win_counts['Country'].unique())],
        placeholder='Choose a country'
    ),
    html.Div(id='country-output'),

    html.H2("Select a Year to View Final Results"),
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': y, 'value': y} for y in sorted(df['Year'].unique())],
        placeholder='Choose a year'
    ),
    html.Div(id='year-output'),

    html.H2("Full Table of Finals"),
    html.Div([
        dcc.Graph(
            figure=px.bar(
                    df,
                    x="Year",
                    y=[1]*len(df),  # dummy value just to plot bars
                    color="Winner",
                    hover_data=["Winner", "RunnerUp"],
                    labels={"y": "Finals"},
                    title="World Cup Final Winners Over the Years"
                ).update_layout(showlegend=True, yaxis_visible=False)
        )
    ])
], style={'width': '80%', 'margin': 'auto'})

# number of wins
@app.callback(
    Output('country-output', 'children'),
    Input('country-dropdown', 'value')
)
def update_country_wins(country):
    if not country:
        return ""
    wins = win_counts.loc[win_counts['Country'] == country, 'Wins'].values[0]
    return f"{country} has won the FIFA World Cup {wins} time(s)."

#result for selected year
@app.callback(
    Output('year-output', 'children'),
    Input('year-dropdown', 'value')
)
def update_year_result(year):
    if not year:
        return ""
    row = df[df['Year'] == year].iloc[0]
    return f"In {year}, {row['Winner']} defeated {row['RunnerUp']} to win the World Cup."


if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 8050))
    app.run(host='0.0.0.0', port=port, debug=True)
