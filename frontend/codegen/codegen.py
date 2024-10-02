import pandas as pd
from jinja2 import Environment, FileSystemLoader
import jinja2
import os 
import shutil
code_dir = "frontend"
os.makedirs(code_dir,exist_ok=True)
os.makedirs(os.path.join(code_dir,"layouts"),exist_ok=True)
os.makedirs(os.path.join(code_dir,"callbacks"),exist_ok=True)
def read_excel_schema(file_path):
    tables_df = pd.read_excel(file_path, sheet_name='tables')
    relationships_df = pd.read_excel(file_path, sheet_name='relationships')
    return tables_df, relationships_df

def process_tables(tables_df):
    model_schema = {}
    for _, row in tables_df.iterrows():
        table_name = row['tablename']
        if table_name not in model_schema:
            model_schema[table_name] = []
        
        model_schema[table_name].append({
            'id': row['columnname'],
            'label': row['columnname'].replace('_', ' ').title(),
            'type': row['columntype'],
            'editable': not row['pk'],  # Set editable to False if it's a primary key
            'is_relation': False,
            'pk': row['pk'],
            'related_table': None,  # Initialize related_table
            'related_column': None  # Initialize related_column
        })
    return model_schema

def process_relationships(relationships_df, model_schema):
    relation_fields = {table: [] for table in model_schema}
    relation_key_table = {}

    for _, row in relationships_df.iterrows():
        table1, table2 = row['table1'], row['table2']
        pk1, pk2 = row['table1_pk'], row['table2_pk']

        # Update is_relation and add relationship info for table1
        for column in model_schema[table1]:
            if column['id'] == pk2:
                column['is_relation'] = True
                column['related_table'] = table2
                column['related_column'] = pk1
                relation_fields[table1].append(pk2)
                relation_key_table[pk2] = table2

        # Update is_relation and add relationship info for table2
        for column in model_schema[table2]:
            if column['id'] == pk1:
                column['is_relation'] = True
                column['related_table'] = table1
                column['related_column'] = pk2
                relation_fields[table2].append(pk1)
                relation_key_table[pk1] = table1

        # Add reverse relationship field (e.g., post_ids for user table)
        reverse_field_name = f"{table2.lower()}_ids"
        model_schema[table1].append({
            'id': reverse_field_name,
            'label': reverse_field_name.replace('_', ' ').title(),
            'type': 'list',
            'editable': False,
            'is_relation': True,
            'pk': False,
            'related_table': table2,
            'related_column': pk2
        })
        relation_fields[table1].append(reverse_field_name)

    return relation_fields, relation_key_table, model_schema

def generate_model_manager(model_schema, relation_fields, relation_key_table):
    template_loader = jinja2.FileSystemLoader(searchpath="./templates")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("model_manager_template.py.j2")

     # Assuming the schema is for the 'user' table

    rendered = template.render(
        model_schema=model_schema,
        relation_fields=relation_fields,
        relation_key_table=relation_key_table
    )

    with open(os.path.join(code_dir,'model_manager.py'), 'w') as f:
        f.write(rendered)

def generate_layouts(model_schema):
    template_loader = jinja2.FileSystemLoader(searchpath="./templates/layouts")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("table_layout.py.j2")
    for table,columns in model_schema.items():
        rendered = template.render(table_name = table)
        with open(os.path.join(code_dir,'layouts',f"{table}_layout.py"),"w") as f:
            f.write(rendered)

def generate_callbacks(model_schema):
    template_loader = jinja2.FileSystemLoader(searchpath="./templates/callbacks")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("table_callback.py.j2")
    for table,columns in model_schema.items():
        rendered = template.render(table_name = table)
        with open(os.path.join(code_dir,"callbacks",f"{table}_callbacks.py"),"w") as f:
            f.write(rendered)


def copy_layout_util(source_path,destination_path):
    #source_path = os.path.join('templates', 'layouts', 'layout_util.py')
    #destination_path = os.path.join('layouts', 'layout_util.py')
    
    try:
        shutil.copy2(source_path, destination_path)
        print(f"Successfully copied layout_util.py to {destination_path}")
    except FileNotFoundError:
        print(f"Error: {source_path} not found.")
    except PermissionError:
        print(f"Error: Permission denied when copying to {destination_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
def generate_app(model_schema):
    template_loader = jinja2.FileSystemLoader(searchpath="./templates")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("app.py.j2")
    rendered = template.render(model_schema=model_schema,default_table='user')
    with open(os.path.join(code_dir,"app.py"),"w") as f:
        f.write(rendered)

def main():
    excel_file = 'schema.xlsx'
    tables_df, relationships_df = read_excel_schema(excel_file)

    model_schema = process_tables(tables_df)
    relation_fields, relation_key_table, model_schema = process_relationships(relationships_df, model_schema)
    print("model_schema",model_schema['user'])
    generate_model_manager(model_schema, relation_fields, relation_key_table)
    generate_layouts(model_schema=model_schema)
    copy_layout_util(os.path.join('templates', 'layouts', 'layout_util.py'),os.path.join(code_dir, 'layouts', 'layout_util.py'))  # Add this line to copy layout_util.py
    copy_layout_util(os.path.join('templates', 'callbacks', 'modal_callbacks_edit.py'),os.path.join(code_dir, 'callbacks', 'modal_callbacks_edit.py'))  # Add this line to copy layout_util.py
    copy_layout_util(os.path.join('templates', 'layouts', 'modal_layout.py'),os.path.join(code_dir, 'layouts', 'modal_layout.py'))  # Add this line to copy layout_util.py
    copy_layout_util(os.path.join('templates', 'layouts', '__init__.py'),os.path.join(code_dir, 'layouts', '__init__.py'))  # Add this line to copy layout_util.py

    generate_callbacks(model_schema=model_schema)
    generate_app(model_schema=model_schema)
if __name__ == "__main__":
    main()
