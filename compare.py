import enum
import json
import argparse
import tiktoken
from tabulate import tabulate
from typing import List, Dict, Optional, Type, Tuple, Any
from pydantic import BaseModel, Field
import topt



def compare_schema(enc: Any, verbose: bool = False):
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
    snake_case_is_inefficient_because_of_all_the_underscores: str

  data: List[Tuple[str, str]] = [
    ('JSON Schema (indented)', TestModel.schema_json(indent=2)),
    ('JSON Schema', TestModel.schema_json()),
    ('topt', topt.schema(TestModel)),
    ('topt (camel case)', topt.schema(TestModel, camel_case=True)),
    ('topt (minify)', topt.schema(TestModel, minify=True)),
  ]

  if verbose:
    for t, s in data:
      print('-' * 30)
      print(t)
      print('-' * 30)
      print(s)
      print()

  data = [(t, len(s), len(enc.encode(s))) for t, s in data]
  print(tabulate(data, headers=['Type', 'Chars', 'Tokens']))


def compare_dumps(enc: Any, verbose: bool = False):
  objects = {
    'object': """{"title":"My Website","header":{"logo":"logo.png","navigation":[{"text":"Home","link":"index.html"},{"text":"About","link":"about.html"},{"text":"Contact","link":"contact.html"}]},"main":{"sections":[{"title":"Welcome to my website!","content":"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod euismod est, eu fringilla sapien facilisis id. Proin bibendum vestibulum tortor vel aliquam. Integer ultrices justo vitae nisl dapibus sagittis. Sed vitae velit justo."},{"title":"About me","content":"Curabitur vel ullamcorper nibh. In eget nisl vel ante pulvinar aliquet. Suspendisse vel pharetra purus, eu tincidunt libero. Duis ac sagittis dolor. Nulla facilisi. Nam at ex vitae tellus suscipit congue id id libero. Aliquam lobortis lorem non sapien maximus, vitae bibendum ipsum vehicula. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas."},{"title":"Contact me","content":"Curabitur vel ullamcorper nibh. In eget nisl vel ante pulvinar aliquet. Suspendisse vel pharetra purus, eu tincidunt libero. Duis ac sagittis dolor. Nulla facilisi. Nam at ex vitae tellus suscipit congue id id libero. Aliquam lobortis lorem non sapien maximus, vitae bibendum ipsum vehicula. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas."}]},"footer":{"copyright":{"text":"© 2023 My Website","link":"index.html"},"social":[{"icon":"facebook.png","link":"#"},{"icon":"twitter.png","link":"#"},{"icon":"instagram.png","link":"#"}]}}""",

    'array': """[{"name":"John Doe","occupation":"Software Developer","age":30},{"name":"Jane Smith","occupation":"Teacher","age":40},{"name":"Michael Johnson","occupation":"Accountant","age":45},{"name":"Samantha Lee","occupation":"Graphic Designer","age":28},{"name":"Robert Williams","occupation":"Marketing Manager","age":50},{"name":"Emily Davis","occupation":"Journalist","age":35},{"name":"William Brown","occupation":"Engineer","age":42},{"name":"Amanda Wilson","occupation":"Sales Manager","age":37},{"name":"Daniel Martin","occupation":"Doctor","age":55},{"name":"Megan Anderson","occupation":"Web Developer","age":29},{"name":"Christopher Garcia","occupation":"Architect","age":48},{"name":"Stephanie Rodriguez","occupation":"Human Resources Manager","age":39},{"name":"David Hernandez","occupation":"Real Estate Agent","age":44},{"name":"Ashley Perez","occupation":"Graphic Designer","age":27},{"name":"Erica Turner","occupation":"Financial Analyst","age":33},{"name":"James Cooper","occupation":"Project Manager","age":41},{"name":"Michelle Taylor","occupation":"Public Relations Specialist","age":36},{"name":"Steven Parker","occupation":"Lawyer","age":52},{"name":"Lauren Hall","occupation":"Product Manager","age":31},{"name":"Brandon Wright","occupation":"IT Manager","age":47}]""",
  }

  for name, obj in objects.items():
    obj = json.loads(obj)
    data: List[Tuple[str, str]] = [
      ('JSON', topt.dumps(obj, format='json')),
      ('JSON5', topt.dumps(obj, format='json5')),
      ('YAML', topt.dumps(obj, format='yaml')),
      ('shortest', topt.dumps(obj, format='shortest')),
    ]

    print('#' * 30)
    print(name)
    print('#' * 30)

    if verbose:
      for t, s in data:
        print('-' * 30)
        print(t)
        print('-' * 30)
        print(s)
        print()
    
    data = [(t, len(s), len(enc.encode(s))) for t, s in data]
    print(tabulate(data, headers=['Type', 'Chars', 'Tokens']))


def compare_params(enc: Any, verbose: bool = False):
  object = json.loads("""{"products": [{"id": 8281194791208, "title": "Top (Yellow)", "url": "https://shop.com/products/top-yellow", "variants": [{"id": 45154677752104, "title": "S", "available": false}, {"id": 45154677784872, "title": "M", "available": true}, {"id": 45154677817640, "title": "L", "available": true}, {"id": 45154677850408, "title": "XL", "available": true}]}, {"id": 8281196069160, "title": "Top (Red)", "url": "https://shop.com/products/top-red", "variants": [{"id": 45154678112552, "title": "S", "available": true}, {"id": 45154678145320, "title": "M", "available": true}, {"id": 45154678178088, "title": "L", "available": true}, {"id": 45154678210856, "title": "XL", "available": true}]}, {"id": 8281195872552, "title": "Top (Green)", "url": "https://shop.com/products/top-green", "variants": [{"id": 45154677981480, "title": "S", "available": true}, {"id": 45154678014248, "title": "M", "available": true}, {"id": 45154678047016, "title": "L", "available": true}, {"id": 45154678079784, "title": "XL", "available": true}]}]}""")

  prompt = f'Here is an object: {json.dumps(object)}'
  parameterized_prompt, parameter_mapping = topt.parameterize(prompt, [object])

  data: List[Tuple[str, str]] = [
    ('original', prompt),
    ('parameterized', parameterized_prompt),
  ]

  if verbose:
    for t, s in data:
      print('-' * 30)
      print(t)
      print('-' * 30)
      print(s)
      print()
  
  data = [(t, len(s), len(enc.encode(s))) for t, s in data]
  print(tabulate(data, headers=['Type', 'Chars', 'Tokens']))


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--model', default='gpt-4')
  parser.add_argument('--verbose', action='store_true')
  # one or more of 'schema', 'dumps'
  parser.add_argument('--comparisons', nargs='+', choices=['schema', 'dumps', 'params'])

  args = parser.parse_args()

  enc = tiktoken.encoding_for_model(args.model)

  comparisons = {
    'schema': compare_schema,
    'dumps': compare_dumps,
    'params': compare_params,
  }
  for comparison in args.comparisons:
    comparisons[comparison](enc, args.verbose)

