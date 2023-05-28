from typing import Dict, List, Type, Tuple, Any
from pydantic import BaseModel


__json_schema_type_to_name = {
  'string': 'string',
  'number': 'float',
  'integer': 'int',
  'boolean': 'bool',
  'object': 'object',
}

def snake_to_camel_case(string: str) -> str:
  return ''.join(word if i == 0 else word.capitalize() for i, word in enumerate(string.split('_')))


def __flatten(list: List[List[Any]]) -> List[Any]:
  return [item for sublist in list for item in sublist]


def __to_string(
  obj: Dict,
  minify: bool,
  camel_case: bool,
) -> Tuple[str, List[str]]:

  if '$ref' in obj:
    title = obj['$ref'].split('/')[-1]
    return title, []
  elif obj['type'] == 'array':
    type_name, type_defs = __to_string(obj['items'], minify=minify, camel_case=camel_case)
    return f'{type_name}[]', type_defs

  title = obj['title'].replace(' ', '')
  if 'enum' in obj:
    values = ' | '.join(obj['enum'])
    return title, [f'type {title} = {values}']
  elif 'allOf' in obj:
    types = [__to_string(v, minify=minify, camel_case=camel_case) for v in obj['allOf']]
    if len(types) == 1:
      return types[0]
    type_names, type_defs = zip(*types)
    return title, [*__flatten(type_defs), f'type {title} = {" | ".join(type_names)}']
  elif 'anyOf' in obj:
    types = [__to_string(v, minify=minify, camel_case=camel_case) for v in obj['allOf']]
    if len(types) == 1:
      return types[0]
    type_names, type_defs = zip(*types)
    return title, [*__flatten(type_defs), f'type {title} = {" | ".join(type_names)}']
  elif obj['type'] == 'object':
    if not 'properties' in obj:
      return 'object', []

    properties: str = []
    all_type_defs: List[str] = []
    for key, value in obj['properties'].items():
      required = key in obj.get('required', [])
      type_name, type_defs = __to_string(value, minify=minify, camel_case=camel_case)
      
      prop_name = snake_to_camel_case(key) if camel_case else key
      prop = f'{prop_name}: {type_name};' if required else f'{prop_name}?: {type_name};'
      if 'description' in value or 'default' in value:
        prop += ' /*'
        if 'description' in value:
          prop += f' {value["description"]}'
        if 'default' in value:
          prop += f' default = {value["default"]}'
        prop += ' */'
      properties.append(prop)
      all_type_defs.extend(type_defs)
    
    if minify:
      properties = ' '.join(properties)
      all_type_defs.append(f'type {title} {{ {properties} }}')
    else:
      properties = '\n '.join(properties)
      all_type_defs.append(f'type {title} {{\n {properties}\n}}')
    return title, all_type_defs
  else:
    type_name = __json_schema_type_to_name[obj['type']]
    return type_name, []


def schema(model: Type[BaseModel] | Dict, minify: bool = False, camel_case: bool = False) -> str:
  if isinstance(model, dict):
    json_schema = model
  else:
    json_schema = model.schema()
  
  import json
  print(json.dumps(json_schema, indent=2))

  type_defs: List[Dict] = []
  for definition in json_schema.get('definitions', {}).values():
    type_defs.append(definition)
  type_defs.append(json_schema)

  types = [__to_string(d, minify=minify, camel_case=camel_case) for d in type_defs]
  type_names, type_defs = zip(*types)
  return '\n'.join(__flatten(type_defs))
