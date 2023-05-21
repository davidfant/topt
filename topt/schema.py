from typing import Any, Dict, List, Optional, Union, Tuple, Type
from pydantic import BaseModel


__json_schema_type_to_name = {
  'string': 'string',
  'number': 'float',
  'integer': 'int',
  'boolean': 'bool',
  'object': 'object',
}


def __to_string(obj: Dict, minify: bool) -> str:
  title = obj['title']

  if obj['type'] == 'object':
    properties: str = []
    for key, value in obj['properties'].items():
      required = key in obj['required']
      if '$ref' in value:
        type_name = value['$ref'].split('/')[-1]
      elif value['type'] == 'array':
        if '$ref' in value['items']:
          type_name = f'{value["items"]["$ref"].split("/")[-1]}[]'
        else:
          type_name = f'{__json_schema_type_to_name[value["items"]["type"]]}[]'
      else:
        type_name = __json_schema_type_to_name[value['type']]
      
      prop = f'{key}: {type_name};' if required else f'{key}?: {type_name};'
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


def schema(model: Type[BaseModel], minify: bool = False) -> str:
  json_schema = model.schema()

  defs: List[Dict] = []
  for definition in json_schema.get('definitions', {}).values():
    defs.append(definition)
  defs.append(json_schema)
  return '\n'.join([__to_string(d, minify=minify) for d in defs])
