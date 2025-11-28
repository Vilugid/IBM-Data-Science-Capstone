# spacex-dash-app.py
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# NOTE: use the exact column names used in your CSV
# Check columns (uncomment to debug)
# print(spacex_df.columns)

# min and max payload for slider (use exact CSV column name)
payload_col = 'Payload Mass (kg)'
min_payload = spacex_df[payload_col].min()
max_payload = spacex_df[payload_col].max()

# Create a Dash application
app = dash.Dash(__name__)

# Build dropdown options using unique launch sites
launch_sites = spacex_df['Launch Site'].unique().tolist()
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': site, 'value': site} for site in launch_sites
]

# App layout
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
    ),

    # TASK 1: Dropdown for Launch Site selection
    html.Div([
        dcc.Dropdown(
            id='site-dropdown',
            options=dropdown_options,
            value='ALL',
            placeholder="Select a Launch Site",
            searchable=True,
            style={'width': '80%', 'padding': '3px', 'font-size': '16px'}
        )
    ], style={'display': 'flex', 'justifyContent': 'center'}),

    html.Br(),

    # TASK 2: Pie chart for success counts
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    # TASK 3: Payload slider
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=int(min_payload),
        max=int(max_payload),
        step=100,
        marks={int(i): str(int(i)) for i in range(int(min_payload), int(max_payload)+1, int((max_payload-min_payload)//5 or 1))},
        value=[int(min_payload), int(max_payload)]
    ),
    html.Br(),

    # TASK 4: Scatter chart for payload vs success
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# TASK 2 callback: update pie chart based on selected site
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    # CSV column names: 'Launch Site' and 'class' (0/1)
    if selected_site == 'ALL':
        # Aggregate total successful launches per site
        success_counts = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size().reset_index(name='success_count')
        fig = px.pie(success_counts, values='success_count', names='Launch Site', 
                     title='Total Successful Launches by Site')
    else:
        # Filter dataframe for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        # Count success vs failure
        outcome_counts = filtered_df['class'].value_counts().reset_index()
        outcome_counts.columns = ['class', 'count']
        outcome_counts['class'] = outcome_counts['class'].replace({1: 'Success', 0: 'Failure'})
        fig = px.pie(outcome_counts, values='count', names='class', title=f'Success vs Failure for {selected_site}')
    return fig

# TASK 4 callback: update scatter chart based on site and payload range
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    # filter by payload range (use exact column)
    mask = (spacex_df[payload_col] >= low) & (spacex_df[payload_col] <= high)
    filtered_df = spacex_df[mask]

    if selected_site == 'ALL':
        fig = px.scatter(
            filtered_df, 
            x=payload_col,
            y='class',
            color='Booster Version' if 'Booster Version' in filtered_df.columns else 'Booster Version',
            hover_data=['Launch Site', 'Payload Mass (kg)'],
            title='Correlation between Payload and Success for All Launch Sites',
            labels={'class': 'Landing Success (1=Success,0=Fail)'}
        )
    else:
        site_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(
            site_df,
            x=payload_col,
            y='class',
            color='Booster Version' if 'Booster Version' in site_df.columns else 'Booster Version',
            hover_data=['Launch Site', 'Payload Mass (kg)'],
            title=f'Correlation between Payload and Success for site {selected_site}',
            labels={'class': 'Landing Success (1=Success,0=Fail)'}
        )
    fig.update_yaxes(tickvals=[0,1], ticktext=['Failure','Success'])
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8051)

