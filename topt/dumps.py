from typing import Dict, Literal
from pydantic import BaseModel
import json
import json5
import yaml
from .config import config, Format

Format = Literal['json', 'json5', 'yaml', 'shortest']
__format_to_dumps = {
  'json': json.dumps,
  'json5': json5.dumps,
  'yaml': yaml.dump,
}

def dumps(
  data: Dict | BaseModel,
  format: Format = config.default_dumps_format,
  model: str = config.default_model,
) -> str:
  if isinstance(data, BaseModel):
    data = data.dict()

  if format == 'shortest':
    try:
      import tiktoken
    except ImportError as e:
      raise Exception('Please install tiktoken to use the "shortest" format')

    encoder = tiktoken.encoding_for_model(model)
    other_formats = list(__format_to_dumps.keys())
    alternatives = [dumps(data, f) for f in other_formats]
    return min(alternatives, key=lambda s: len(encoder.encode(s)))
  return __format_to_dumps[format](data)
