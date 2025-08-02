import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

# Read the CSV file - update this path to your CSV file location
df = pd.read_csv('merged1_energy_data.csv')  # Replace with your actual CSV file path

# Convert date column to datetime (adjust column name as needed)
if 'Month' in df.columns:
    df['Month'] = pd.to_datetime(df['Month'])
elif 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.rename(columns={'Date': 'Month'})

# Convert numeric columns to proper data types
numeric_cols = df.select_dtypes(include=['object']).columns
for col in numeric_cols:
    if col != 'Month':
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Create the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Energy Sector BI Dashboard", className="text-center mb-4"), width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Key Metrics"),
                dbc.CardBody([
                    html.Div(id="metrics-container")
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dcc.Tabs(id="tabs", value='overview', children=[
                dcc.Tab(label='Overview', value='overview'),
                dcc.Tab(label='Generation Analysis', value='generation'),
                dcc.Tab(label='Customer Analysis', value='customer'),
                dcc.Tab(label='Infrastructure', value='infrastructure'),
                dcc.Tab(label='Renewable Focus', value='renewable'),
            ]),
            html.Div(id="tab-content")
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dcc.DatePickerRange(
                id='date-range',
                start_date=df['Month'].min(),
                end_date=df['Month'].max(),
                display_format='YYYY-MM-DD'
            )
        ], width=12)
    ], className="mt-4")
], fluid=True)

# Helper function to get column names safely
def get_column_safe(df, possible_names):
    for name in possible_names:
        if name in df.columns:
            return name
    return None

# Callback for updating key metrics
@app.callback(
    Output("metrics-container", "children"),
    [Input("date-range", "start_date"),
     Input("date-range", "end_date")]
)
def update_metrics(start_date, end_date):
    filtered_df = df[(df['Month'] >= start_date) & (df['Month'] <= end_date)]
    
    if len(filtered_df) == 0:
        return html.Div("No data available for selected date range")
    
    latest = filtered_df.iloc[-1]
    
    # Get key metrics with safe column access
    consumption_col = get_column_safe(df, ['electricity_consumption_GWh', 'Total_Consumption', 'Consumption'])
    renewable_col = get_column_safe(df, ['Renewable_Share_%', 'Renewable_Share', 'Renewable_Percentage'])
    customers_col = get_column_safe(df, ['Cummulative_Connections', 'Total_Customers', 'Customers'])
    transmission_col = get_column_safe(df, ['Total HV and MV', 'Total_Transmission', 'Transmission_Total'])
    
    metrics = []
    
    if consumption_col:
        metrics.append(
            dbc.Col([
                html.H6("Total Consumption (GWh)"),
                html.H4(f"{latest[consumption_col]:.1f}")
            ], width=3)
        )
    
    if renewable_col:
        metrics.append(
            dbc.Col([
                html.H6("Renewable Share (%)"),
                html.H4(f"{latest[renewable_col]:.1f}%")
            ], width=3)
        )
    
    if customers_col:
        metrics.append(
            dbc.Col([
                html.H6("Total Customers"),
                html.H4(f"{latest[customers_col]:,.0f}")
            ], width=3)
        )
    
    if transmission_col:
        metrics.append(
            dbc.Col([
                html.H6("Total Transmission (km)"),
                html.H4(f"{latest[transmission_col]:,.0f}")
            ], width=3)
        )
    
    return dbc.Row(metrics) if metrics else html.Div("Metrics not available")

# Callback for updating tab content
@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "value"),
     Input("date-range", "start_date"),
     Input("date-range", "end_date")]
)
def update_tab_content(tab, start_date, end_date):
    filtered_df = df[(df['Month'] >= start_date) & (df['Month'] <= end_date)]
    
    if tab == 'overview':
        return overview_tab(filtered_df)
    elif tab == 'generation':
        return generation_tab(filtered_df)
    elif tab == 'customer':
        return customer_tab(filtered_df)
    elif tab == 'infrastructure':
        return infrastructure_tab(filtered_df)
    elif tab == 'renewable':
        return renewable_tab(filtered_df)

# Overview Tab
def overview_tab(filtered_df):
    figures = []
    
    # Consumption trend
    consumption_col = get_column_safe(filtered_df, ['electricity_consumption_GWh', 'Total_Consumption', 'Consumption'])
    if consumption_col:
        fig_consumption = px.line(
            filtered_df, 
            x='Month', 
            y=consumption_col,
            title='Electricity Consumption Trend',
            labels={consumption_col: 'Consumption (GWh)', 'Month': 'Date'}
        )
        figures.append(dbc.Col(dcc.Graph(figure=fig_consumption), width=6))
    
    # Renewable share
    renewable_col = get_column_safe(filtered_df, ['Renewable_Share_%', 'Renewable_Share', 'Renewable_Percentage'])
    if renewable_col:
        fig_renewable = px.line(
            filtered_df, 
            x='Month', 
            y=renewable_col,
            title='Renewable Energy Share',
            labels={renewable_col: 'Renewable Share (%)', 'Month': 'Date'}
        )
        figures.append(dbc.Col(dcc.Graph(figure=fig_renewable), width=6))
    
    # Generation sources (if available)
    generation_cols = [col for col in filtered_df.columns if col.upper() in ['HYDRO', 'THERMAL', 'WIND', 'GEOTHERMAL', 'SOLAR', 'IMPORTS', 'BAGASSE_BIOGAS']]
    if generation_cols:
        fig_generation = px.area(
            filtered_df, 
            x='Month', 
            y=generation_cols,
            title='Energy Generation by Source',
            labels={'value': 'Generation (GWh)', 'Month': 'Date', 'variable': 'Source'}
        )
        figures.append(dbc.Col(dcc.Graph(figure=fig_generation), width=12))
    
    # Customer connections
    customers_col = get_column_safe(filtered_df, ['Cummulative_Connections', 'Total_Customers', 'Customers'])
    if customers_col:
        fig_customers = px.line(
            filtered_df, 
            x='Month', 
            y=customers_col,
            title='Cumulative Customer Connections',
            labels={customers_col: 'Customers', 'Month': 'Date'}
        )
        figures.append(dbc.Col(dcc.Graph(figure=fig_customers), width=12))
    
    return dbc.Row(figures) if figures else html.Div("No data available for overview")

# Generation Analysis Tab
def generation_tab(filtered_df):
    figures = []
    
    # Find generation columns
    generation_cols = [col for col in filtered_df.columns if col.upper() in ['HYDRO', 'THERMAL', 'WIND', 'GEOTHERMAL', 'SOLAR', 'IMPORTS', 'BAGASSE_BIOGAS']]
    
    if generation_cols:
        fig_monthly = px.bar(
            filtered_df, 
            x='Month', 
            y=generation_cols,
            title='Monthly Generation by Source',
            labels={'value': 'Generation (GWh)', 'Month': 'Date', 'variable': 'Source'},
            barmode='stack'
        )
        figures.append(dbc.Col(dcc.Graph(figure=fig_monthly), width=12))
        
        # Renewable vs non-renewable if thermal and imports exist
        thermal_col = get_column_safe(filtered_df, ['Thermal', 'THERMAL'])
        imports_col = get_column_safe(filtered_df, ['IMPORTS', 'Imports'])
        
        if thermal_col and imports_col:
            renewable_cols = [col for col in generation_cols if col.upper() not in ['THERMAL', 'IMPORTS']]
            if renewable_cols:
                temp_df = filtered_df.copy()
                temp_df['NonRenewable'] = temp_df[thermal_col] + temp_df[imports_col]
                temp_df['Renewable'] = temp_df[renewable_cols].sum(axis=1)
                
                fig_renewable_vs = px.area(
                    temp_df, 
                    x='Month', 
                    y=['Renewable', 'NonRenewable'],
                    title='Renewable vs Non-Renewable Generation',
                    labels={'value': 'Generation (GWh)', 'Month': 'Date', 'variable': 'Type'}
                )
                figures.append(dbc.Col(dcc.Graph(figure=fig_renewable_vs), width=6))
        
        # Import dependency
        if imports_col:
            total_col = get_column_safe(filtered_df, ['Total', 'total_generation'])
            if total_col:
                temp_df = filtered_df.copy()
                temp_df['Import_Percentage'] = (temp_df[imports_col] / temp_df[total_col]) * 100
                
                fig_imports = px.line(
                    temp_df, 
                    x='Month', 
                    y='Import_Percentage',
                    title='Import Dependency',
                    labels={'Import_Percentage': 'Import Percentage (%)', 'Month': 'Date'}
                )
                figures.append(dbc.Col(dcc.Graph(figure=fig_imports), width=6))
    
    return dbc.Row(figures) if figures else html.Div("No generation data available")

# Customer Analysis Tab
def customer_tab(filtered_df):
    figures = []
    
    # New customers
    new_customers_col = get_column_safe(filtered_df, ['Number_of_new_customers', 'New_Customers', 'Monthly_New_Customers'])
    if new_customers_col:
        fig_new_customers = px.bar(
            filtered_df, 
            x='Month', 
            y=new_customers_col,
            title='New Customers per Month',
            labels={new_customers_col: 'New Customers', 'Month': 'Date'}
        )
        figures.append(dbc.Col(dcc.Graph(figure=fig_new_customers), width=6))
    
    # Cumulative customers
    customers_col = get_column_safe(filtered_df, ['Cummulative_Connections', 'Total_Customers', 'Customers'])
    if customers_col:
        fig_cumulative = px.line(
            filtered_df, 
            x='Month', 
            y=customers_col,
            title='Cumulative Customer Growth',
            labels={customers_col: 'Customers', 'Month': 'Date'}
        )
        figures.append(dbc.Col(dcc.Graph(figure=fig_cumulative), width=6))
    
    # Tariff analysis (if tariff columns exist)
    tariff_cols = [col for col in filtered_df.columns if 'tariff' in col.lower() or 'per_kWh' in col or 'rate' in col.lower()]
    if tariff_cols:
        tariff_df = filtered_df.melt(
            id_vars=['Month'],
            value_vars=tariff_cols,
            var_name='Customer Category',
            value_name='Tariff'
        )
        
        fig_tariff = px.line(
            tariff_df, 
            x='Month', 
            y='Tariff',
            color='Customer Category',
            title='Average Tariff by Customer Category',
            labels={'Tariff': 'Tariff (per kWh)', 'Month': 'Date'}
        )
        figures.append(dbc.Col(dcc.Graph(figure=fig_tariff), width=12))
    
    return dbc.Row(figures) if figures else html.Div("No customer data available")

# Infrastructure Tab
def infrastructure_tab(filtered_df):
    figures = []
    
    # Find transmission/infrastructure columns
    transmission_cols = [col for col in filtered_df.columns if any(voltage in col for voltage in ['kV', 'KV', 'voltage', 'transmission', 'line'])]
    
    if transmission_cols:
        fig_transmission = px.area(
            filtered_df, 
            x='Month', 
            y=transmission_cols,
            title='Transmission Infrastructure by Type',
            labels={'value': 'Length (km)', 'Month': 'Date', 'variable': 'Infrastructure Type'}
        )
        figures.append(dbc.Col(dcc.Graph(figure=fig_transmission), width=12))
    
    # Total transmission
    total_transmission_col = get_column_safe(filtered_df, ['Total HV and MV', 'Total_Transmission', 'Total_Infrastructure'])
    if total_transmission_col:
        fig_total_transmission = px.line(
            filtered_df, 
            x='Month', 
            y=total_transmission_col,
            title='Total Transmission Infrastructure',
            labels={total_transmission_col: 'Length (km)', 'Month': 'Date'}
        )
        figures.append(dbc.Col(dcc.Graph(figure=fig_total_transmission), width=6))
    
    return dbc.Row(figures) if figures else html.Div("No infrastructure data available")

# Renewable Focus Tab
def renewable_tab(filtered_df):
    figures = []
    
    # Renewable generation
    renewable_gen_col = get_column_safe(filtered_df, ['Renewable_Generation', 'Total_Renewable', 'Renewable_Total'])
    if renewable_gen_col:
        fig_renewable_generation = px.line(
            filtered_df, 
            x='Month', 
            y=renewable_gen_col,
            title='Total Renewable Generation',
            labels={renewable_gen_col: 'Generation (GWh)', 'Month': 'Date'}
        )
        figures.append(dbc.Col(dcc.Graph(figure=fig_renewable_generation), width=6))
    
    # Renewable share
    renewable_share_col = get_column_safe(filtered_df, ['Renewable_Share_%', 'Renewable_Share', 'Renewable_Percentage'])
    if renewable_share_col:
        fig_renewable_share = px.line(
            filtered_df, 
            x='Month', 
            y=renewable_share_col,
            title='Renewable Energy Share',
            labels={renewable_share_col: 'Renewable Share (%)', 'Month': 'Date'}
        )
        figures.append(dbc.Col(dcc.Graph(figure=fig_renewable_share), width=6))
    
    # Renewable sources breakdown
    renewable_cols = [col for col in filtered_df.columns if col.upper() in ['HYDRO', 'WIND', 'GEOTHERMAL', 'SOLAR', 'BAGASSE_BIOGAS']]
    if renewable_cols:
        fig_renewable_sources = px.area(
            filtered_df, 
            x='Month', 
            y=renewable_cols,
            title='Renewable Generation by Source',
            labels={'value': 'Generation (GWh)', 'Month': 'Date', 'variable': 'Source'}
        )
        figures.append(dbc.Col(dcc.Graph(figure=fig_renewable_sources), width=12))
    
    return dbc.Row(figures) if figures else html.Div("No renewable data available")

# Expose server for deployment
server = app.server

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=False)