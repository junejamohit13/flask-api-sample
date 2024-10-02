from dataclasses import dataclass
from dash import html
import dash_bootstrap_components as dbc
import dash_table
from model_manager import Column, ModelManager

def get_select_table_layout(select_table_id: str, columns: list[Column], data, row_selectable='single', page_size=10, filter_action='native', selected_rows=[]):
    # Convert list fields to comma-separated strings for display in the DataTable
    formatted_data = []
    for row in data:
        formatted_row = {}
        for key, value in row.items():
            if isinstance(value, list):
                formatted_row[key] = ', '.join(map(str, value))
            else:
                formatted_row[key] = value
        formatted_data.append(formatted_row)

    columns = [{'name': col.label, 'id': col.id, 'type': col.type, 'editable': False} for col in columns]

    return dash_table.DataTable(
        id=select_table_id,
        data=formatted_data,
        columns=columns,
        filter_action=filter_action,
        row_selectable=row_selectable,
        selected_rows=selected_rows,
        page_size=page_size,
    )

def get_edit_save_alert_id(edit_save_alert_id: str):
    return dbc.Alert(
        id=edit_save_alert_id,
        dismissable=True,
        is_open=False,  # Initially hidden
    )

def get_edit_form_id(model_class: str):
    print(f"{model_class}_edit_form")
    return f"{model_class}_edit_form"




def get_entry_form(columns: list[Column], selected_row: dict, table_id: str, suffix: str = '-edit'):
    form_items = []
    relation_fields = ModelManager.get_relation_fields(table_id)
    for col in columns:
        if not col.is_relation:
            form_items.append(dbc.Col([
                dbc.Label(col.label),
                dbc.Input(type=col.type, id=f"{table_id}-{col.id}{suffix}", value=selected_row.get(col.id, ''), disabled=not col.editable),
            ], width=6))
        elif col.id in relation_fields:
            value = ', '.join(selected_row.get(col.id, [])) if isinstance(selected_row.get(col.id), list) else selected_row.get(col.id, '')
            form_items.append(dbc.Row([
                dbc.Col([
                    dbc.Label(col.label),
                    dbc.InputGroup([
                        dbc.Input(type="text", id=f"{table_id}-{col.id}{suffix}", value=value, disabled=True),
                        dbc.Button("Select", id=f"select-{table_id}-{col.id}{suffix}", n_clicks=0),
                    ]),
                ], width=6),
            ], className="mb-3"))

    form_items.append(dbc.Button("Save", id=f"save-{table_id}{suffix}", color="primary"))
    
    return dbc.Form(form_items)