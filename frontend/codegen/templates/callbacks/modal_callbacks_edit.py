from dash.dependencies import Input, Output, State
from dash import no_update
from model_manager import MODEL_SCHEMA, RELATION_FIELDS, RELATION_KEY_TABLE
import dash
def create_toggle_modal(model, field):
                def toggle_modal(n1, n2, is_open):
                    
                    ctx = dash.callback_context
                    if ctx.triggered:
                        
                        button_id = ctx.triggered[0].get('prop_id').split('.')[0]
                        if button_id.startswith('save') and (button_id.endswith('-selection-edit') or button_id.endswith('-selection-add')) and n2>0:
                            return False
                        if button_id.startswith('select') and (button_id.endswith('-edit') or button_id.endswith('-add')) and n1>0:
                            return True
                    return is_open
                return toggle_modal

def create_update_selected_values_edit(model, field):
                print("create_update_selected_values called")
                def update_selected_values(n_clicks, selected_rows, data, table_data, table_selected_rows):
                    ctx = dash.callback_context
                    if ctx.triggered:
                        button_id = ctx.triggered[0].get('prop_id').split('.')[0]
                        if button_id.startswith('save') and button_id.endswith('-selection-edit') and n_clicks>0:
                            if n_clicks is not None and n_clicks>0:
                                id_field = field[:-1]  # Remove the 's' from the end
                                selected_ids = [data[i][id_field] for i in (selected_rows or [])]
                                selected_ids_str = ', '.join(selected_ids)
                            
                                # Update the main table data
                                if table_selected_rows and table_data:
                                    row_index = table_selected_rows[0]
                                    table_data[row_index][field] = selected_ids_str
                                    return selected_ids_str, table_data
                                
                        
                    return no_update, no_update
                return update_selected_values

def create_update_selected_values_add(model, field):
                print("create_update_selected_values called")
                def update_selected_values(n_clicks, selected_rows, data, table_data, table_selected_rows):
                    ctx = dash.callback_context
                    if ctx.triggered:
                        button_id = ctx.triggered[0].get('prop_id').split('.')[0]
                        if button_id.startswith('save') and button_id.endswith('-selection-edit') and n_clicks>0:
                            if n_clicks is not None and n_clicks>0:
                                id_field = field[:-1]  # Remove the 's' from the end
                                selected_ids = [data[i][id_field] for i in (selected_rows or [])]
                                selected_ids_str = ', '.join(selected_ids)
                            
                                # Update the main table data
                                if table_selected_rows and table_data:
                                    row_index = table_selected_rows[0]
                                    table_data[row_index][field] = selected_ids_str
                                    return selected_ids_str, table_data
                                
                        
                    return no_update, no_update
                return update_selected_values


def create_pre_select_rows(model, field):
                def pre_select_rows(n_clicks_select,n_clicks_save, current_value, data):
                    ctx = dash.callback_context
                    if ctx.triggered:
                        button_id = ctx.triggered[0].get('prop_id').split('.')[0]
                        if button_id.startswith('select') and button_id.endswith('-edit') and n_clicks_select>0:
                            if current_value and data:
                                current_ids = [id.strip() for id in current_value.split(',') if id.strip()]
                                id_field = field[:-1]  # Remove the 's' from the end
                                return [i for i, row in enumerate(data) if row.get(id_field) in current_ids]
                        if button_id.startswith('save') and button_id.endswith('-selection-edit') and n_clicks_save>0:
                            return []
                    return []
                return pre_select_rows
def register_modal_callbacks_edit(app, model_manager):
    for model_name, relation_fields in RELATION_FIELDS.items():
        for relation_field in relation_fields:
            related_model = RELATION_KEY_TABLE[relation_field]
            

            app.callback(
                Output(f'modal-{related_model}-edit', 'is_open'),
                [Input(f'select-{model_name}-{relation_field}-edit', 'n_clicks'),
                 Input(f'save-{related_model}-selection-edit', 'n_clicks')],
                [State(f'modal-{related_model}-edit', 'is_open')]
            )(create_toggle_modal(model_name, relation_field))

            app.callback(
                Output(f'modal-{related_model}-add', 'is_open'),
                [Input(f'select-{model_name}-{relation_field}-add', 'n_clicks'),
                 Input(f'save-{related_model}-selection-add', 'n_clicks')],
                [State(f'modal-{related_model}-edit', 'is_open')]
            )(create_toggle_modal(model_name, relation_field))

            app.callback(
                Output(f'{model_name}-{relation_field}-edit', 'value'),
                Output(f'{model_name}-edit-table', 'data'),
                [Input(f'save-{related_model}-selection-edit', 'n_clicks')],
                [State(f'{related_model}-modal-table-edit', 'selected_rows'),
                 State(f'{related_model}-modal-table-edit', 'data'),
                 State(f'{model_name}-edit-table', 'data'),
                 State(f'{model_name}-edit-table', 'selected_rows')]
            )(create_update_selected_values_edit(model_name, relation_field))


            app.callback(
                Output(f'{model_name}-{relation_field}-add', 'value'),
                [Input(f'save-{related_model}-selection-add', 'n_clicks')],
                [State(f'{related_model}-modal-table-add', 'selected_rows'),
                 State(f'{related_model}-modal-table-add', 'data'),
                ]
            )(create_update_selected_values_add(model_name, relation_field))

            app.callback(
                Output(f'{related_model}-modal-table-edit', 'selected_rows'),
                [Input(f'select-{model_name}-{relation_field}-edit', 'n_clicks'),
                 Input(f'save-{related_model}-selection-edit', 'n_clicks')],
                [State(f'{model_name}-{relation_field}-edit', 'value'),
                 State(f'{related_model}-modal-table-edit', 'data')]
            )(create_pre_select_rows(model_name, relation_field))

    print("Registered modal callbacks:")
    for callback in app.callback_map:
        print(f"  {callback}")


# for model_name in MODEL_SCHEMA.keys():
#     @app.callback(
#         Output(f'modal-{model_name}', 'is_open'),
#         [Input(f'select-{model_name}-dept_ids-edit', 'n_clicks'),
#          Input(f'save-{model_name}-selection', 'n_clicks')],
#         [State(f'modal-{model_name}', 'is_open')]
#     )
#     def toggle_modal(n1, n2, is_open):
#         if n1 or n2:
#             return not is_open
#         return is_open

#     @app.callback(
#         Output(f'{model_name}-dept_ids-edit', 'value'),
#         [Input(f'save-{model_name}-selection', 'n_clicks')],
#         [State(f'{model_name}-modal-table', 'selected_rows'),
#          State(f'{model_name}-modal-table', 'data')]
#     )
#     def update_selected_values(n_clicks, selected_rows, data):
#         if n_clicks and selected_rows:
#             selected_ids = [data[i]['dept_id'] for i in selected_rows]
#             return ', '.join(selected_ids)
#         return no_update

#     @app.callback(
#         Output(f'{model_name}-modal-table', 'selected_rows'),
#         [Input(f'select-{model_name}-dept_ids-edit', 'n_clicks')],
#         [State(f'{model_name}-dept_ids-edit', 'value'),
#          State(f'{model_name}-modal-table', 'data')]
#     )
#     def pre_select_rows(n_clicks, current_value, data):
#         if n_clicks and current_value:
#             current_ids = [id.strip() for id in current_value.split(',')]
#             return [i for i, row in enumerate(data) if row['dept_id'] in current_ids]
#         return []

