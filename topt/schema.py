from typing import Any, Dict, List, Optional, Union, Tuple, Type
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


def __to_string(obj: Dict, minify: bool, camel_case: bool) -> str:
  title = obj['title']

  if obj['type'] == 'object':
    properties: str = []
    for key, value in obj['properties'].items():
      required = key in obj.get('required', [])
      if '$ref' in value:
        type_name = value['$ref'].split('/')[-1]
      elif value['type'] == 'array':
        if '$ref' in value['items']:
          type_name = f'{value["items"]["$ref"].split("/")[-1]}[]'
        else:
          type_name = f'{__json_schema_type_to_name[value["items"]["type"]]}[]'
      else:
        type_name = __json_schema_type_to_name[value['type']]
      
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
    
    if minify:
      properties = ' '.join(properties)
      return f'type {title} {{ {properties} }}'
    else:
      properties = '\n '.join(properties)
      return f'type {title} {{\n {properties}\n}}'
  elif 'enum' in obj:
    values = ' | '.join(obj['enum'])
    return f'type {title} = {values}'
  else:
    raise Exception(f'Unknown type: {obj["type"]}')


def schema(model: Type[BaseModel], minify: bool = False, camel_case: bool = False) -> str:
  json_schema = model.schema()

  defs: List[Dict] = []
  for definition in json_schema.get('definitions', {}).values():
    defs.append(definition)
  defs.append(json_schema)
  return '\n'.join([__to_string(d, minify=minify, camel_case=camel_case) for d in defs])
