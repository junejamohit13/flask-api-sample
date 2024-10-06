import dash
from dash import Input, Output, State, ctx, dcc, html, dash_table
import pandas as pd
import sqlite3
import dash_bootstrap_components as dbc
from config import *
# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])


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



# Fetch initial data
data = []

# Set up Dash layout
app.layout = dbc.Container([
    html.H2(f"Data Entry POC"),
    dash_table.DataTable(
        id='editable-table',
        columns=[
            {'name': 'ID', 'id': 'id', 'editable': False},
            {'name': 'Name', 'id': 'name', 'editable': True},
            {'name': 'Age', 'id': 'age', 'editable': True},
            {'name': 'City', 'id': 'city', 'editable': True}
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
    html.Button("Save Changes", id="save-button", n_clicks=0,className="btn-streamlit mt-3"),
    html.Div(id="save-status")
], className="mb-4")

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
                cursor.execute('''
                    UPDATE sample_data
                    SET name = ?, age = ?, city = ?
                    WHERE id = ?
                ''', (row['name'], row['age'], row['city'], row['id']))
            conn.commit()
            print("Changes saved successfully!")
        return "Changes saved successfully!"
    return ""

# Run Dash app
if __name__ == "__main__":
    app.run_server(debug=True,port=8058)
