import dash
from dash import dcc, html, Input, Output, callback
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

PROVINCE_FILES = {
    'Newfoundland and Labrador': 'Newfoundland and Labrador.csv',
    'Alberta': 'Alberta.csv',
    'British Columbia': 'British Columbia.csv',
    'Manitoba': 'Manitoba.csv',
    'New Brunswick': 'New Brunswick.csv',
    'Northwest Territories': 'Northwest Territories.csv',
    'Nova Scotia': 'Nova Scotia.csv',
    'Nunavut': 'Nunavut.csv',
    'Ontario': 'Ontario.csv',
    'Prince Edward Island': 'Prince Edward Island.csv',
    'Quebec': 'Quebec.csv',
    'Saskatchewan': 'Saskatchewan.csv',
    'Yukon': 'Yukon.csv'
}

ABBREV_TO_NAME = {
    'NL': 'Newfoundland and Labrador',
    'PE': 'Prince Edward Island',
    'NS': 'Nova Scotia',
    'NB': 'New Brunswick',
    'QC': 'Quebec',
    'ON': 'Ontario',
    'MB': 'Manitoba',
    'SK': 'Saskatchewan',
    'AB': 'Alberta',
    'BC': 'British Columbia',
    'YT': 'Yukon Territory',
    'NT': 'Northwest Territories',
    'NU': 'Nunavut'
}

PROVINCE_ABBREV = {
    'Alberta': 'AB',
    'British Columbia': 'BC',
    'Manitoba': 'MB',
    'New Brunswick': 'NB',
    'Newfoundland and Labrador': 'NL',
    'Nova Scotia': 'NS',
    'Northwest Territories': 'NT',
    'Nunavut': 'NU',
    'Ontario': 'ON',
    'Prince Edward Island': 'PE',
    'Quebec': 'QC',
    'Saskatchewan': 'SK',
    'Yukon': 'YT'
}

ESSENTIAL_OCCUPATIONS = {
    'Nurses': ['31301', '31302'],
    'Police': ['42100'],
    'Firefighters': ['42101']
}

NOC_CATEGORIES = {
    0: '0 Legislative/Management',
    1: '1 Business/Finance',
    2: '2 Natural/Applied Sciences',
    3: '3 Health',
    4: '4 Education/Law',
    5: '5 Art/Culture',
    6: '6 Sales/Service',
    7: '7 Trades/Transport',
    8: '8 Natural Resources',
    9: '9 Manufacturing'
}

ENGINEER_OCCUPATIONS = {
    'Computer Engineers': '21311',
    'Mechanical Engineers': '21301',
    'Electrical Engineers': '21310'
}

PROVINCE_COORDS = {
    'AB': {'lat': 53.9333, 'lon': -116.5765},
    'BC': {'lat': 53.7267, 'lon': -127.6476},
    'MB': {'lat': 53.7609, 'lon': -98.8139},
    'NB': {'lat': 46.5653, 'lon': -66.4619},
    'NL': {'lat': 48.6560, 'lon': -55.7519},
    'NS': {'lat': 44.6816, 'lon': -63.7443},
    'NT': {'lat': 64.8255, 'lon': -124.8457},
    'NU': {'lat': 70.2998, 'lon': -83.1076},
    'ON': {'lat': 51.2538, 'lon': -85.3232},
    'PE': {'lat': 46.5107, 'lon': -63.4168},
    'QC': {'lat': 52.9399, 'lon': -73.5491},
    'SK': {'lat': 52.9399, 'lon': -106.4509},
    'YT': {'lat': 64.2823, 'lon': -135.0000}
}

PROVINCE_ORDER = [
    'NL', 'PE', 'NS', 'NB', 'QC', 'ON', 'MB', 
    'SK', 'AB', 'BC', 'YT', 'NT', 'NU'
]

canada_geojson = requests.get("https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/canada.geojson").json()


''' ---------------------------
    Data Processing
   ---------------------------'''

def load_and_process_data():
    
    # task 1 data
    task1_data = []

    for province, file in PROVINCE_FILES.items():
        df = pd.read_csv(file)
        num_cols = ['Total - Gender', 'Men+ 10', 'Women+ 11']
        
        for col in num_cols:
            df[col] = df[col].str.replace(',', '').astype(float)
        
        population = df.iloc[0]['Total - Gender']
        services = {}
        
        for service, codes in ESSENTIAL_OCCUPATIONS.items():
            mask = df['Occupation - Unit group - National Occupational Classification (NOC) 2021 (821A) 9'].str.contains('|'.join(codes))
            services[service] = df[mask]['Total - Gender'].sum() / population
        task1_data.append({'Province': province, **services})
    
    task1_df = pd.DataFrame(task1_data)
    task1_df['Abbrev'] = task1_df['Province'].map(PROVINCE_ABBREV)

    # task 2 data
    task2_data = []

    for province, file in PROVINCE_FILES.items():
        df = pd.read_csv(file)
        for col in ['Men+ 10', 'Women+ 11']:
            df[col] = df[col].str.replace(',', '').astype(float)
        
        province_data = []
        for noc_code, category in NOC_CATEGORIES.items():
            mask = df['Occupation - Unit group - National Occupational Classification (NOC) 2021 (821A) 9'].str.startswith(f"{noc_code} ")
            cat_df = df[mask]
            
            if not cat_df.empty:
                total_men = cat_df['Men+ 10'].sum()
                total_women = cat_df['Women+ 11'].sum()
                province_data.append({'Province': province,'Category': category,'NOC_Code': noc_code, 'Men': total_men,'Women': total_women,'Total': total_men + total_women})
        task2_data.extend(province_data)
    
    task2_df = pd.DataFrame(task2_data)
    return task1_df, task2_df

task1_df, task2_df = load_and_process_data()

# task 2 data processing
def process_task2_data():
    task2_data = []
    
    for province, file in PROVINCE_FILES.items():
        df = pd.read_csv(file)
        
        for col in ['Men+ 10', 'Women+ 11']:
            df[col] = df[col].str.replace(',', '').astype(float)
        
        for noc_code, category in NOC_CATEGORIES.items():
            mask = df['Occupation - Unit group - National Occupational Classification (NOC) 2021 (821A) 9'].str.startswith(f"{noc_code} ")
            cat_df = df[mask]
            
            if not cat_df.empty:
                total_men = cat_df['Men+ 10'].sum()
                total_women = cat_df['Women+ 11'].sum()
                total = total_men + total_women
                
                task2_data.append({'Province': province,'Abbrev': PROVINCE_ABBREV[province],'Category': category,'NOC_Code': noc_code,'Men%': total_men / total if total > 0 else 0,'Women%': total_women / total if total > 0 else 0,'Total': total})
    
    return pd.DataFrame(task2_data)

task2_df = process_task2_data()

def process_engineer_data():
    # task 3 data
    engineer_data = []

    for province, file in PROVINCE_FILES.items():
        df = pd.read_csv(file)
        abbrev = PROVINCE_ABBREV[province]
        
        df['Total - Gender'] = df['Total - Gender'].str.replace(',', '').astype(float)
        population = df.iloc[0]['Total - Gender']
        
        totals = {}
        for eng_type, noc_code in ENGINEER_OCCUPATIONS.items():
            mask = df['Occupation - Unit group - National Occupational Classification (NOC) 2021 (821A) 9'].str.contains(noc_code)
            totals[eng_type] = df[mask]['Total - Gender'].sum()
        
        total_engineers = sum(totals.values())
        engineer_data.append({'Province': province,'Abbrev': abbrev,'ProvinceName': ABBREV_TO_NAME[abbrev],'Total Engineers': total_engineers,'Per Capita': total_engineers / population if population > 0 else 0,**totals,
            'lat': PROVINCE_COORDS[abbrev]['lat'],'lon': PROVINCE_COORDS[abbrev]['lon']})
    
    return pd.DataFrame(engineer_data)

engineer_df = process_engineer_data()

def empty_message(message="Please Select at least one engineer type to see the data", height=500):
    return {
        'data': [],
        'layout': {
            'xaxis': {'visible': False},
            'yaxis': {'visible': False},
            'annotations': [{'text': message,'xref': 'paper','yref': 'paper','x': 0.5,'y': 0.5,'showarrow': False,'font': {'size': 20},'align': 'center'}],
            'height': height,
            'margin': {'t': 40, 'b': 0, 'l': 0, 'r': 0}
        }
    }

def process_occupation_data():
    # task 4 data
    occupation_data = []

    for province, file in PROVINCE_FILES.items():
        df = pd.read_csv(file)
        abbrev = PROVINCE_ABBREV[province]
        
        # clean and categorize data
        df['Total'] = df['Total - Gender'].str.replace(',', '').astype(float)
        df['NOC1'] = df['Occupation - Unit group - National Occupational Classification (NOC) 2021 (821A) 9'].str[0]
        
        for noc_code, cat_name in NOC_CATEGORIES.items():
            if noc_code == 0: continue
            
            total = df[df['NOC1'] == str(noc_code)]['Total'].sum()
            province_total = df['Total'].sum()
            occupation_pct = (total / province_total) * 100 if province_total > 0 else 0
            
            occupation_data.append({'Province': abbrev,'Occupation': cat_name.split(' ', 1)[1], 'Percentage': round(occupation_pct, 1)})
    
    return pd.DataFrame(occupation_data)

occupation_df = process_occupation_data()


''' ---------------------------
     Dash App
    ---------------------------'''

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Occupation Distribution in Canada", style={'textAlign': 'center', 'padding': '20px', 'marginBottom': '20px'}),
    
    # Task 1 layout
    html.Div([
        html.Div([
            html.H2("Essential Services Distribution", style={'marginBottom': '15px'}),
            dcc.RadioItems(id='task1-service-select',
                options=[{'label': ' All Services', 'value': 'All'}, {'label': ' Nurses', 'value': 'Nurses'}, {'label': ' Police', 'value': 'Police'}, {'label': ' Firefighters', 'value': 'Firefighters'}],
                value='All', inline=True, labelStyle={'margin': '5px', 'padding': '5px 15px'}, style={'width': '90%', 'margin': '0 auto 20px'})
        ], style={'textAlign': 'center'}),
        
        dcc.Graph(id='task1-graph', style={'height': '60vh', 'margin': '20px 0'})

    ], style={'border': '2px solid #f0f0f0', 'borderRadius': '10px', 'padding': '20px', 'margin': '20px 0'}),
    
    # Task 2 layout
    html.Div([
        html.Div([
            html.H2("Gender Distribution by Occupation", style={'marginBottom': '15px'}),
            dcc.Dropdown(id='task2-category-select', options=[{'label': n, 'value': i} for i, n in NOC_CATEGORIES.items()], value=0, style={'width': '80%', 'margin': '0 auto 20px'}, clearable=False)
        ], style={'textAlign': 'center'}),
        
        dcc.Graph(id='task2-graph', style={'height': '65vh', 'margin': '20px 0'})
    ], style={'border': '2px solid #f0f0f0', 'padding': '20px', 'margin': '20px 0'}),


    # Task 3 layout
    html.Div([
        html.Div([
            html.H2("Engineering Workforce Overview", style={'marginBottom': '15px'}),
            html.Div([
                dcc.Checklist(id='engineer-type-select',
                    options=[
                        {'label': ' Computer Engineers', 'value': 'Computer Engineers'},
                        {'label': ' Mechanical Engineers', 'value': 'Mechanical Engineers'},
                        {'label': ' Electrical Engineers', 'value': 'Electrical Engineers'}
                    ],
                    value=['Computer Engineers', 'Mechanical Engineers', 'Electrical Engineers'], inline=True,labelStyle={'margin': '10px', 'paddingRight': '20px'})
            ], style={'width': '90%', 'margin': '0 auto 20px'}),
            
            html.Div([
                dcc.Graph(id='engineer-map', style={'width': '55%', 'display': 'inline-block'}),
                dcc.Graph(id='engineer-barchart', style={'width': '43%', 'display': 'inline-block', 'marginLeft': '2%'})
            ])
        ], style={'textAlign': 'center'})
    ], style={'border': '2px solid #f0f0f0', 'padding': '25px', 'margin': '20px 0'}),

    # Task 4 layout
    html.Div([
        html.Div([
            html.H2("Occupation Distribution By Province", style={'marginBottom': '15px'}),
            dcc.Slider(id='province-slider', min=0, max=12, step=1, value=5, marks={i: {'label': abbrev, 'style': {'fontSize': 12}} for i, abbrev in enumerate(PROVINCE_ORDER)}, tooltip={'placement': 'bottom', 'always_visible': True}),
            dcc.Graph(id='occupation-chart', style={'height': '70vh', 'margin': '0 auto', 'maxWidth': '800px'})
        ], style={'textAlign': 'center'})
    ], style={'border': '2px solid #f0f0f0', 'padding': '25px', 'margin': '20px 0'})
])


''' ---------------------------
     Callbacks
    ---------------------------'''

# Task 1 callback
@app.callback(
    Output('task1-graph', 'figure'),
    [Input('task1-service-select', 'value')]
)

def update_task1(selected_service):
    df = task1_df.copy()
    
    if selected_service == 'All':
        df['Total'] = df[list(ESSENTIAL_OCCUPATIONS.keys())].sum(axis=1)
        df['Breakdown'] = df.apply(lambda x: "<br>".join([f"{k}: {x[k]:.2%}" for k in ESSENTIAL_OCCUPATIONS.keys()]), axis=1)
        df_sorted = df.sort_values('Total', ascending=False)
        fig = px.bar(df_sorted, x='Abbrev', y='Total', text=df_sorted['Total'].apply(lambda x: f"{x:.2%}"), 
                     title="Essential Services Distribution per Capita", hover_data=['Province', 'Breakdown'])
        fig.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>Total: %{y:.2%}<br>%{customdata[1]}", marker_color='#8F48DB', textfont_size=14)
    else:
        df_sorted = df.sort_values(selected_service, ascending=False)
        fig = px.bar(df_sorted, x='Abbrev', y=selected_service, text=df_sorted[selected_service].apply(lambda x: f"{x:.2%}"), 
                     title=f"{selected_service} Distribution per Capita", hover_data=['Province'])
        fig.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>%{y:.2%}", marker_color='#4D85DE', textfont_size=14)
    
    fig.update_layout(yaxis_tickformat=',.2%', xaxis_title="Province/Territory", yaxis_title="Percentage of Population", uniformtext_minsize=12,
        hoverlabel=dict(bgcolor="white", font_size=14), margin=dict(l=50, r=50, t=80, b=50), height=400)
    
    return fig

# Task 2 callback
@app.callback(
    Output('task2-graph', 'figure'),
    [Input('task2-category-select', 'value')]
)

def update_task2(selected_category):
    filtered_df = task2_df[task2_df['NOC_Code'] == selected_category]
    category_name = NOC_CATEGORIES[selected_category]
    
    plot_df = filtered_df.melt(id_vars=['Abbrev', 'Province'],value_vars=['Men%', 'Women%'],var_name='Gender',value_name='Percentage')
    
    fig = px.bar(plot_df,x='Abbrev',y='Percentage',color='Gender',barmode='group',title=f"{category_name} Gender Distribution by Province",
        labels={'Percentage': 'Proportion of Workforce', 'Abbrev': 'Province/Territory'}, color_discrete_map={'Men%': '#636efa', 'Women%': '#EF3C3F'},
        text=plot_df['Percentage'].apply(lambda x: f"{x:.1%}"),hover_data={'Province': True, 'Abbrev': False, 'Gender': False})
    
    fig.update_layout(
        xaxis={'categoryorder': 'total descending'}, yaxis_tickformat=',.0%', yaxis = dict(showgrid=True,gridcolor='lightgrey'), uniformtext_minsize=10,
        hovermode='x unified', legend_title='Gender', plot_bgcolor='white', margin=dict(t=60), height=450)
    
    fig.update_traces(textposition='outside',textfont_size=12,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "%{y:.1%} of workforce"))
    
    return fig

# Task 3 callback
@app.callback(
    [Output('engineer-map', 'figure'),
     Output('engineer-barchart', 'figure')],
    [Input('engineer-type-select', 'value')]
)

def update_task3(selected_types):
    if not selected_types:
        return empty_message(), empty_message(" ")
    
    filtered_df = engineer_df.copy()
    filtered_df['Total'] = filtered_df[selected_types].sum(axis=1)
    filtered_df = filtered_df.sort_values('Total', ascending=False)

    # choropleth
    map_fig = px.choropleth(filtered_df, geojson=canada_geojson, locations='ProvinceName', featureidkey="properties.name", color='Total', color_continuous_scale='Teal',
        scope='north america', hover_name='ProvinceName', hover_data=['Computer Engineers', 'Mechanical Engineers', 'Electrical Engineers', 'Total'],
        labels={'Total': 'Total Engineers'}, title='Engineering Workforce Map')

    # horizontal bar chart
    bar_fig = px.bar(filtered_df, x='Total', y='Abbrev', orientation='h', text_auto=',.0f', title='Engineer Count by Province', labels={'Total': 'Count'},
        color_discrete_sequence=['#6BADBA'], hover_data=['Computer Engineers', 'Mechanical Engineers', 'Electrical Engineers', 'Total']
    )

    map_fig.update_traces(
        hovertemplate=(
            "<b>%{location}</b><br>"
            "Computer: %{customdata[0]:,}<br>"
            "Mechanical: %{customdata[1]:,}<br>"
            "Electrical: %{customdata[2]:,}<br>"
            "Total: %{customdata[3]:,}<extra></extra>"))

    bar_fig.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Computer: %{customdata[0]:,}<br>"
            "Mechanical: %{customdata[1]:,}<br>"
            "Electrical: %{customdata[2]:,}<br>"))

    map_fig.add_scattergeo(lon=filtered_df['lon'], lat=filtered_df['lat'], text=filtered_df['Abbrev'], mode='text', 
                           textfont=dict(size=12, color='black', family='Arial', weight='bold'), hoverinfo='none', showlegend=False)
    map_fig.update_layout(coloraxis_colorbar=dict(title="Engineers"), margin=dict(l=0, r=0, t=40, b=0))
    map_fig.update_geos(visible=False, center={"lat": 62, "lon": -90}, projection_scale=1.2, lataxis_range=[41.7, 83.1], lonaxis_range=[-141.0, -52.6], bgcolor='rgba(240,240,240,0.5)')

    bar_fig.update_layout(yaxis={'categoryorder': 'total ascending'}, xaxis_title="Number of Engineers", yaxis_title="Province/Territory",
        margin=dict(l=120, r=0, t=40, b=0), showlegend=False)

    return map_fig, bar_fig

# Task 4 callback
@app.callback(
    Output('occupation-chart', 'figure'),
    [Input('province-slider', 'value')]
)

def update_occupation_chart(province_idx):
    province_abbrev = PROVINCE_ORDER[province_idx]
    full_name = ABBREV_TO_NAME.get(province_abbrev, province_abbrev)
    filtered_df = occupation_df[occupation_df['Province'] == province_abbrev]
    
    colors = px.colors.qualitative.Plotly * 2
    filtered_df = filtered_df.reset_index(drop=True)
    
    fig = go.Figure()
    
    for idx, row in filtered_df.iterrows():
        fig.add_trace(go.Barpolar(r=[row['Percentage']], theta=[idx * (360/len(filtered_df))], name=row['Occupation'], text=[f"{row['Percentage']}%"],
            hoverinfo='name+text', marker_color=colors[idx % len(colors)], width=15, marker_line_color='black', marker_line_width=0.5))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 20], tickfont_size=12, tickvals=[0, 5, 10, 15, 20], ticktext=['0%', '5%', '10%', '15%', '20%'], gridcolor='lightgray'),
            angularaxis=dict(rotation=90, direction='clockwise', tickmode='array', tickvals=list(range(0, 360, int(360/len(filtered_df)))),
                ticktext=filtered_df['Occupation'], tickfont=dict(size=12, color='black'), gridcolor='lightgray'), bgcolor='rgba(245,245,245,0.5)'
        ),
        title=f"Occupation Distribution in {full_name}", showlegend=False, height=650, margin=dict(l=100, r=100)
    )
    
    return fig


if __name__ == '__main__':
    app.run(debug=True, port=8050)