from typing import Dict, Literal
import tiktoken
import json
import json5
import yaml

Format = Literal['json', 'json5', 'yaml', 'shortest']
__format_to_dumps = {
  'json': json.dumps,
  'json5': json5.dumps,
  'yaml': yaml.dump,
}

def dumps(data: Dict, format: Format = 'json5', model: str = 'gpt-4') -> str:
  if format == 'shortest':
    encoder = tiktoken.encoding_for_model(model)
    other_formats = list(__format_to_dumps.keys())
    alternatives = [dumps(data, f) for f in other_formats]
    return min(alternatives, key=lambda s: len(encoder.encode(s)))
  return __format_to_dumps[format](data)
