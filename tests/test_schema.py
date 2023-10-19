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
 dictionary: object;
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

if __name__ == '__main__':
  unittest.main()
