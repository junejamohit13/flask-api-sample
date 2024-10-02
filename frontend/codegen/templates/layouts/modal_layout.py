from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from model_manager import ModelManager, MODEL_SCHEMA

def create_modal(model_name,mode='edit'):
    model_manager = ModelManager()
    data, columns = model_manager.get_data(model_name)
    
    # Convert list values to strings
    formatted_data = []
    for row in data:
        formatted_row = {}
        for key, value in row.items():
            if isinstance(value, list):
                formatted_row[key] = ', '.join(map(str, value))
            else:
                formatted_row[key] = value
        formatted_data.append(formatted_row)
    
    return dbc.Modal(
        [
            dbc.ModalHeader(f"Select {model_name.capitalize()}"),
            dbc.ModalBody(
                dash_table.DataTable(
                    id=f'{model_name}-modal-table-{mode}',
                    columns=[{"name": col.label, "id": col.id} for col in columns],
                    data=formatted_data,  # Use the formatted data here
                    row_selectable='multi',
                    selected_rows=[],
                    page_size=10,
                    style_table={'height': '400px', 'overflowY': 'auto'}
                )
            ),
            dbc.ModalFooter(
                dbc.Button("Save", id=f"save-{model_name}-selection-{mode}", className="ml-auto")
            ),
        ],
        id=f"modal-{model_name}-{mode}",
        size="xl",
        is_open=False,
    )

