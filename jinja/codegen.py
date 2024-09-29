# codegen.py

import os
import pandas as pd
from jinja2 import Environment, FileSystemLoader

# Define paths
TEMPLATES_DIR = 'templates'
EXCEL_FILE = 'schema.xlsx'
OUTPUT_DIR = 'generated_flask_app'

# Initialize Jinja2 environment
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), trim_blocks=True, lstrip_blocks=True)

# Helper function to convert snake_case to CamelCase
def snake_to_camel(snake_str):
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)

def main():
    # Read Excel sheets
    tables_df = pd.read_excel(EXCEL_FILE, sheet_name='tables')
    relationships_df = pd.read_excel(EXCEL_FILE, sheet_name='relationships')

    # Process tables
    tables = {}
    for _, row in tables_df.iterrows():
        table = row['tablename']
        column = {
            'columnname': row['columnname'],
            'columntype': row['columntype'],
            'pk': row['pk']
        }
        if table not in tables:
            tables[table] = {
                'class_name': snake_to_camel(table),
                'columns': [],
                'relationships': []
            }
        tables[table]['columns'].append(column)

    # Process relationships
    relationships = []
    for _, row in relationships_df.iterrows():
        relationship = {
            'relationship_table': row['relationship_table'],
            'table1': row['table1'],
            'table2': row['table2'],
            'table1_pk':row['table1_pk'],
            'table2_pk':row['table2_pk']
        }
        relationships.append(relationship)
        # Update tables with relationships
        tables[row['table1']]['relationships'].append({
            'related_table': row['table2'],
            'related_class': snake_to_camel(row['table2']),
            'relationship_table': row['relationship_table'],
            'back_populates': row['table1'] + 's'
        })
        tables[row['table2']]['relationships'].append({
            'related_table': row['table1'],
            'related_class': snake_to_camel(row['table1']),
            'relationship_table': row['relationship_table'],
            'back_populates': row['table2'] + 's'
        })
    
    # Create output directories
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, 'models'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, 'blueprints'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, 'repository'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, 'cache'), exist_ok=True)

    # Create __init__.py files
    for folder in ['models', 'blueprints', 'repository', 'cache']:
        init_file = os.path.join(OUTPUT_DIR, folder, '__init__.py')
        with open(init_file, 'w') as f:
            f.write(env.get_template('init_py.j2').render())

    
    
    # Create models
    model_template = env.get_template('model.py.j2')
    for table_name, details in tables.items():
        model_content = model_template.render(
            class_name=details['class_name'],
            table_name=table_name,
            columns=details['columns'],
            relationships=details['relationships']
        )
        model_file = os.path.join(OUTPUT_DIR, 'models', f'{table_name}.py')
        with open(model_file, 'w') as f:
            f.write(model_content)

    #Create association_tables
    association_tables_template = env.get_template("associated_tables.py.j2")
    association_content = association_tables_template.render(relationships=relationships) 
    model_file = os.path.join(OUTPUT_DIR, 'models', f'associations.py')
    with open(model_file, 'w') as f:
            f.write(association_content)
    # Create blueprints
    blueprint_template = env.get_template('blueprint.py.j2')
    for table_name, details in tables.items():
        blueprint_content = blueprint_template.render(
            table_name=table_name,
            class_name=details['class_name'],
            columns=details['columns'],
            relationships=details['relationships']
        )
        blueprint_file = os.path.join(OUTPUT_DIR, 'blueprints', f'{table_name}_bp.py')
        with open(blueprint_file, 'w') as f:
            f.write(blueprint_content)

    # Create repository
    repository_template = env.get_template('repository.py.j2')
    repository_content = repository_template.render(
        tables=tables
    )
    repository_file = os.path.join(OUTPUT_DIR, 'repository', 'repository.py')
    with open(repository_file, 'w') as f:
        f.write(repository_content)

    # Create cache_layer.py
    cache_template = env.get_template('cache_layer.py.j2')
    cache_content = cache_template.render(
        tables=tables
    )
    cache_file = os.path.join(OUTPUT_DIR, 'cache', 'cache_layer.py')
    with open(cache_file, 'w') as f:
        f.write(cache_content)

    # Create app.py
    app_template = env.get_template('app.py.j2')
    blueprint_imports = ""
    blueprint_registers = ""
    model_imports = ""
    for table_name in tables.keys():
        snake_table = snake_to_camel(table_name)
        model_imports += f"from models.{table_name} import {snake_table}\n"
        blueprint_imports += f"from blueprints.{table_name}_bp import {table_name}_bp\n"
        blueprint_registers += f"app.register_blueprint({table_name}_bp)\n"
    app_content = app_template.render(
        model_imports=model_imports,
        blueprint_imports=blueprint_imports,
        blueprint_registers=blueprint_registers
    )
    app_file = os.path.join(OUTPUT_DIR, 'app.py')
    with open(app_file, 'w') as f:
        f.write(app_content)

    # Create config.py
    config_file = os.path.join(OUTPUT_DIR, 'config.py')
    with open(config_file, 'w') as f:
        f.write("# Configuration settings can be added here.\n")

    # Create __init__.py in root
    root_init = os.path.join(OUTPUT_DIR, '__init__.py')
    with open(root_init, 'w') as f:
        f.write("# Generated Flask Application\n")

    # Create requirements.txt
    requirements = [
        "Flask",
        "Flask-SQLAlchemy",
    ]
    requirements_file = os.path.join(OUTPUT_DIR, 'requirements.txt')
    with open(requirements_file, 'w') as f:
        f.write('\n'.join(requirements))

    print(f"Code generation complete. Check the '{OUTPUT_DIR}' directory.")

if __name__ == "__main__":
    main()
