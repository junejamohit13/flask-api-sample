import dash
from dash import Input, Output, State, ctx, dcc, html, dash_table
import pandas as pd
import sqlite3
import dash_bootstrap_components as dbc

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# Set up SQLite database

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: "Source Sans Pro", sans-serif;
                color: #262730;
                background-color: #f0f2f6;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
            }
            h1 {
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 2rem;
            }
            h2 {
                font-size: 1.8rem;
                font-weight: 600;
                margin-top: 2rem;
                margin-bottom: 1rem;
            }
            .btn-streamlit {
                background-color: #ffffff;
                color: #262730;
                border: 1px solid #d2d6dd;
                border-radius: 0.25rem;
                padding: 0.5rem 1rem;
                font-size: 1rem;
                font-weight: 400;
                transition: all 0.2s;
            }
            .btn-streamlit:hover {
                background-color: #f0f2f6;
                border-color: #a3a8b8;
            }
            .dash-table-container {
                margin-bottom: 1rem;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''




# Read initial data from database
def fetch_data():
    with sqlite3.connect(db_url) as conn:
        df = pd.read_sql_query('SELECT * FROM sample_data', conn)
    return df

# Fetch initial data
data = fetch_data()
columns = data.columns.tolist()

# Create main filters
def create_main_filters(df, key_columns, primary_key_column):
    filter_columns = [col for col in df.columns if col not in key_columns + [primary_key_column]]
    dropdowns = [
        dcc.Dropdown(
            id=f'dropdown-{col}',
            options=[{'label': value, 'value': value} for value in df[col].unique()],
            multi=True,
            placeholder=f'Select {col}...'
        ) for col in filter_columns
    ]
    # Create rows with 3 dropdowns each
    dropdown_rows = []
    for i in range(0, len(dropdowns), 3):
        row = dbc.Row([
            dbc.Col(dropdown, width=4) for dropdown in dropdowns[i:i+3]
        ], className="mb-3")
        dropdown_rows.append(row)
    return dropdown_rows, filter_columns

# Set up Dash layout
filter_rows, filter_columns = create_main_filters(data, key_columns=[], primary_key_column='id')

app.layout = dbc.Container([
    html.H2(f"Data Entry POC"),
    html.Div(filter_rows),
    dash_table.DataTable(
        id='editable-table',
        columns=[
            {'name': col, 'id': col, 'editable': col != 'id'} for col in columns
        ],
        data=data.to_dict('records'),
        editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        style_table={'overflowX': 'auto'},
        style_cell={
            'minWidth': '100px', 'width': '150px', 'maxWidth': '180px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'textAlign': 'left'
        },
    ),
    html.Button("Save Changes", id="save-button", n_clicks=0, className="btn-streamlit mt-3"),
    html.Div(id="save-status")
], className="mb-4")

# Callback to filter the main table
@app.callback(
    Output('editable-table', 'data'),
    [Input(f'dropdown-{col}', 'value') for col in filter_columns]
)
def filter_main_table(*values):
    filtered_data = data.copy()
    if any(value is not None for value in values):
        for col, value in zip(filter_columns, values):
            if value:
                filtered_data = filtered_data[filtered_data[col].isin(value)]
    return filtered_data.to_dict('records')

# Callback to save updated data to the database
@app.callback(
    Output("save-status", "children"),
    Input("save-button", "n_clicks"),
    State("editable-table", "data"),
    prevent_initial_call=True
)
def save_changes(n_clicks, updated_data):
    if n_clicks > 0:
        with sqlite3.connect(db_url) as conn:
            cursor = conn.cursor()
            # Loop through updated data and update the database
            for row in updated_data:
                columns_to_update = [col for col in row.keys() if col != 'id']
                set_clause = ', '.join([f"{col} = ?" for col in columns_to_update])
                values = [row[col] for col in columns_to_update] + [row['id']]
                cursor.execute(f'''
                    UPDATE sample_data
                    SET {set_clause}
                    WHERE id = ?
                ''', values)
            conn.commit()
        return "Changes saved successfully!"
    return ""
columns_to_update = [col for col in row.keys() if col != 'id' and not (pd.isna(row[col]) and pd.isna(data.loc[data['id'] == row['id'], col].values[0])) and row[col] != data.loc[data['id'] == row['id'], col].values[0]]

# Run Dash app
if __name__ == "__main__":
    app.run_server(debug=True,port=8060)
