import enum
import tiktoken
from tabulate import tabulate
from typing import List, Dict, Optional, Type, Tuple
from pydantic import BaseModel, Field
import topt

class TestModel(BaseModel):
  class NestedModel(BaseModel):
    id: str
  
  class Enum(str, enum.Enum):
    a = 'a'
    b = 'b'

  nested: NestedModel
  list: List[NestedModel]
  enum: Enum
  float: float
  int: int
  boolean: bool
  string: str = Field(description='string description')
  optional: Optional[str] = None
  dictionary: Dict
  defaulted: int = 0
  snake_case: str


if __name__ == '__main__':
  enc = tiktoken.encoding_for_model('gpt-4')

  data: List[Tuple[str, str]] = [
    ('JSON Schema (indented)', TestModel.schema_json(indent=2)),
    ('JSON Schema', TestModel.schema_json()),
    ('topt', topt.schema(TestModel, minify=False)),
    ('topt (minify)', topt.schema(TestModel, minify=True)),
  ]

  for t, s in data:
    print('-' * 50)
    print(t)
    print('-' * 50)
    print(s)
    print()

  data = [(t, len(s), len(enc.encode(s))) for t, s in data]
  print(tabulate(data, headers=['Type', 'Chars', 'Tokens']))
