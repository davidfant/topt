from typing import Dict, List, Type, Tuple, Any
from pydantic import BaseModel
import subprocess
import tempfile
import json
import logging

logger = logging.getLogger(__name__)


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
  elif obj.get('type') == 'array':
    type_name, type_defs = __to_string(obj['items'], minify=minify, camel_case=camel_case)
    return f'{type_name}[]', type_defs

  title = obj['title'].replace(' ', '') if 'title' in obj else None
  if 'enum' in obj:
    values = ' | '.join([f"'{v}'" for v in obj['enum']])
    if title:
      return title, [f'type {title} = {values}']
    else:
      return values, []
  elif 'allOf' in obj:
    types = [__to_string(v, minify=minify, camel_case=camel_case) for v in obj['allOf']]
    if len(types) == 1:
      return types[0]
    type_names, type_defs = zip(*types)
    inline_type_def = " | ".join(type_names)
    if title:
      return title, [*__flatten(type_defs), f'type {title} = {inline_type_def}']
    else:
      return inline_type_def, [*__flatten(type_defs)]
  elif 'anyOf' in obj:
    types = [__to_string(v, minify=minify, camel_case=camel_case) for v in obj['anyOf']]
    if len(types) == 1:
      return types[0]
    type_names, type_defs = zip(*types)
    inline_type_def = " | ".join(type_names)
    if title:
      return title, [*__flatten(type_defs), f'type {title} = {inline_type_def}']
    else:
      return inline_type_def, [*__flatten(type_defs)]
  elif 'oneOf' in obj:
    types = [__to_string(v, minify=minify, camel_case=camel_case) for v in obj['oneOf']]
    if len(types) == 1:
      return types[0]
    type_names, type_defs = zip(*types)
    inline_type_def = " | ".join(type_names)
    if title:
      return title, [*__flatten(type_defs), f'type {title} = {inline_type_def}']
    else:
      return inline_type_def, [*__flatten(type_defs)]
  elif not 'type' in obj:
    return 'any', []
  elif obj.get('type') == 'object':
    if not 'properties' in obj:
      additional_props = obj.get('additionalProperties', [])
      if not additional_props:
        return 'Record<string, unknown>', []
      
      if isinstance(additional_props, dict):
        additional_props = [additional_props]

      types = [__to_string(v, minify=minify, camel_case=camel_case) for v in additional_props]
      type_names, type_defs = zip(*types)
      return f'Record<string, {" | ".join(type_names)}>', [*__flatten(type_defs)]

    properties: str = []
    all_type_defs: List[str] = []
    for key, value in obj['properties'].items():
      required = key in obj.get('required', [])
      type_name, type_defs = __to_string(value, minify=minify, camel_case=camel_case)
      
      prop_name = snake_to_camel_case(key) if camel_case else key
      prop = f'{prop_name}: {type_name};' if required else f'{prop_name}?: {type_name};'
      if 'description' in value or 'default' in value or 'format' in value:
        prop += ' /*'
        if 'description' in value:
          prop += f' {value["description"]}'
        if 'format' in value:
          prop += f' format = {value["format"]}'
        if 'default' in value:
          prop += f' default = {value["default"]}'
        prop += ' */'
      properties.append(prop)
      all_type_defs.extend(type_defs)
    
    inline_type_def = f'{{ {" ".join(properties)} }}' if minify else '{\n ' + '\n '.join(properties) + '\n}'
    if title:
      all_type_defs.append(f'type {title} = {inline_type_def}')
      return title, all_type_defs
    else:
      return inline_type_def, all_type_defs
  
  if not 'type' in obj:
    logger.warning(f'Unknown type: {obj}')
    return 'unknown', []

  type_name = __json_schema_type_to_name[obj['type']]
  return type_name, []


def schema(model: Type[BaseModel] | Dict, minify: bool = False, camel_case: bool = False) -> str:
  if isinstance(model, dict):
    json_schema = model
  else:
    json_schema = model.schema()

  type_defs: List[Dict] = []
  for definition in json_schema.get('definitions', {}).values():
    type_defs.append(definition)
  type_defs.append(json_schema)

  types = [__to_string(d, minify=minify, camel_case=camel_case) for d in type_defs]
  type_names, type_defs = zip(*types)
  return '\n'.join(__flatten(type_defs))

  # 1. dump json schema in temporary file
  # 2. run json2ts
  # json2ts /private/var/folders/j2/stdvm9c50l109dgfdqv45x400000gn/T/n8n/schema.json --bannerComment ""
  # 3. for each line starting with "export ", remove "export "
  # 4. return all lines
  # with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
  #   json.dump(json_schema, f)
  #   f.close()
  #   output = subprocess.check_output(['json2ts', f.name, '--bannerComment', ''])
  #   lines = output.decode('utf-8').split('\n')
  #   lines = [line[7:] if line.startswith('export ') else line for line in lines]
  #   return '\n'.join(lines)




