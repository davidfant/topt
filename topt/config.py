from pydantic import BaseModel
from typing import Literal, Optional

Format = Literal['json', 'json5', 'yaml', 'shortest']

class Config(BaseModel):
  default_dumps_format: Optional[Format] = 'json5'
  default_model: str = 'gpt-4'

config = Config()

def configure(_config: Config):
  global config
  config = _config
