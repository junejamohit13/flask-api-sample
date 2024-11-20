from typing import Dict, Union, List, Type
from .bfs import find_path_between_models, get_relationships
from .models import QueryConfig
from .templates.base import TemplateManager
import os

class QueryGenerator:
    def __init__(self, template_manager: TemplateManager = None):
        self.template_manager = template_manager or TemplateManager()
    
    def generate_sqlalchemy_code(
        self,
        session,
        start_model: Type,
        end_model: Union[Type, List[Type]],
        end_filter: Union[str, Dict[Type, List[Dict[str, str]]], None] = None,
        other_entities: List[Type] = None
    ) -> str:
        """Generate SQLAlchemy query code"""
        # Convert single end_model to list for consistent handling
        end_models = [end_model] if not isinstance(end_model, list) else end_model
        
        # Find paths to all end models and other entities
        all_paths = {}
        all_entities = end_models + (other_entities or [])
        
        # Get unique paths for all entities (both for filtering and loading)
        for target_model in all_entities:
            if target_model not in all_paths:  # Avoid finding same path twice
                path = find_path_between_models(start_model, target_model)
                if not path:
                    raise ValueError(f"No path found between {start_model.__name__} and {target_model.__name__}")
                all_paths[target_model] = path
        
        # Build the join conditions and joinedload options
        joins = []
        options = []
        seen_paths = set()  # Track all relationship paths
        
        # Process paths for joins (needed for filtering)
        for target_model in end_models:
            path = all_paths[target_model]
            current_model = start_model
            for _, relationship_key, next_model in path:
                join_str = f"{current_model.__name__}.{relationship_key}"
                if join_str not in seen_paths:
                    joins.append(f".join({join_str})")
                    seen_paths.add(join_str)
                current_model = next_model
        
        # Process paths for joinedload (needed for eager loading)
        if other_entities:
            for entity in other_entities:
                path = all_paths[entity]
                # Build the complete joinedload path
                joined_load_path = []
                current_model = start_model
                
                for _, rel_key, next_model in path:
                    if not joined_load_path:
                        # First relationship starts from start_model
                        joined_load_path.append(f"{current_model.__name__}.{rel_key}")
                    else:
                        # Subsequent relationships need to be chained
                        joined_load_path.append(rel_key)
                    current_model = next_model
                
                # Create the joinedload with the full path
                if joined_load_path:
                    path_str = '.'.join(joined_load_path)
                    if path_str not in seen_paths:
                        options.append(f"joinedload({path_str})")
                        seen_paths.add(path_str)
        
        # Build the query string
        query_parts = [
            f"return (session.query({start_model.__name__})"
        ]
        
        # Add joins
        query_parts.extend(joins)
        
        # Handle filters
        if end_filter:
            if isinstance(end_filter, str):
                query_parts.append(f".filter({end_filter})")
            else:
                filter_conditions = []
                for model, conditions in end_filter.items():
                    model_conditions = []
                    for cond in conditions:
                        condition = cond['condition']
                        operator = cond.get('operator', 'and').lower()
                        
                        if operator == 'or':
                            if not model_conditions:
                                model_conditions.append(f"({condition})")
                            else:
                                model_conditions.append(f" | ({condition})")
                        else:
                            if not model_conditions:
                                model_conditions.append(f"({condition})")
                            else:
                                model_conditions.append(f" & ({condition})")
                    
                    if model_conditions:
                        model_filter = " ".join(model_conditions)
                        if "|" in model_filter:
                            model_filter = f"({model_filter})"
                        filter_conditions.append(model_filter)
                
                if filter_conditions:
                    combined_filters = " & ".join(filter_conditions)
                    query_parts.append(f".filter({combined_filters})")
        
        # Add options if any
        if options:
            options_str = ', '.join(options)
            query_parts.append(f".options({options_str})")
        
        # Complete the query
        query_str = '\n    '.join(query_parts)
        query_str += ")"
         
        return query_str
        
    
    def generate_graphql_query_file(
        self,
        filename: str,
        query_configs: Dict[str, dict],
    ) -> str:
        """Generate a Python file with GraphQL-ready query functions"""
        print(f"Template directory: {os.path.join(os.path.dirname(__file__), 'templates/query_templates')}")
        
        # Convert raw configs to QueryConfig objects and ensure defaults
        processed_configs = {}
        for name, config in query_configs.items():
            if 'other_entities' not in config:
                config['other_entities'] = []
            if 'column_mappings' not in config:
                config['column_mappings'] = {}
            processed_configs[name] = QueryConfig.from_dict(config)
        
        # First generate the mapper file
        print("Generating mapper file...")
        mapper_code = self.template_manager.render_template(
            "graphql/mapper",
            {}
        )
        mapper_file = f"{filename}_mapper.py"
        print(f"Writing mapper to: {mapper_file}")
        print(f"Mapper code length: {len(mapper_code)}")
        with open(mapper_file, 'w') as f:
            f.write(mapper_code)
        
        # Then generate the query file
        print("Generating query file...")
        rendered_code = self.template_manager.render_template(
            "graphql/query",
            {
                'query_configs': processed_configs,
                'generate_sqlalchemy_code': self.generate_sqlalchemy_code
            }
        )
        print(f"Query code length: {len(rendered_code)}")
        
        query_file = f"{filename}.py"
        print(f"Writing query to: {query_file}")
        with open(query_file, 'w') as f:
            f.write(rendered_code)
        
        return query_file
