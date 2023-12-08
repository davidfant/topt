import unittest
import enum
from typing import List, Dict, Optional
from topt.schema import schema
from pydantic import BaseModel, Field

class TestSchema(unittest.TestCase):

  def test_pydantic(self):
    self.maxDiff = None

    class TestModel(BaseModel):
      class NestedModel(BaseModel):
        id: str
      
      class Enum(str, enum.Enum):
        a = 'a'
        b = 'b'

      nested: NestedModel
      nested_with_description: NestedModel = Field(description='description')
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

    stringified = schema(TestModel, minify=False)
    self.assertEqual(stringified, """
type NestedModel = {
 id: string;
}
type Enum = 'a' | 'b'
type TestModel = {
 nested: NestedModel;
 nested_with_description: NestedModel; /* description */
 list: NestedModel[];
 enum: Enum;
 float: float;
 int: int;
 boolean: bool;
 string: string; /* string description */
 optional?: string;
 dictionary: Record<string, unknown>;
 defaulted?: int; /* default = 0 */
 snake_case: string;
}
""".strip())
  
  def test_pydantic_minify(self):
    class TestModel(BaseModel):
      class NestedModel(BaseModel):
        id: str
      nested: NestedModel
    
    stringified = schema(TestModel, minify=True)
    self.assertEqual(stringified, """
type NestedModel = { id: string; }
type TestModel = { nested: NestedModel; }
""".strip())

  def test_formats_dict_key_and_value_types(self):
    class TestModel(BaseModel):
      int_key: Dict[str, int]
      combined_key: Dict[str, str | bool]
    
    stringified = schema(TestModel, minify=False)
    self.assertEqual(stringified, """
type TestModel = {
 int_key: Record<string, int>;
 combined_key: Record<string, string | bool>;
}
""".strip())
    
  def test_escapes_dict_keys(self):
    stringified = schema({
      'type': 'object',
      'title': 'TestModel',
      'properties': {
        'normal': { 'type': 'string' },
        'key with space': { 'type': 'string' },
        'key.with.dot': { 'type': 'string' },
      },
    }, minify=False)
    self.assertEqual(stringified, """
type TestModel = {
 normal?: string;
 "key with space"?: string;
 "key.with.dot"?: string;
}
""".strip())


if __name__ == '__main__':
  unittest.main()
