from typing import List, Dict, Tuple, Any

ParameterMapping = Dict[str | int, Any]

def __is_id_key(key: str) -> bool:
  return key.endswith('_id') or key.endswith('Id') or key == 'id' or key == 'Id'

def parameterize(prompt: str, items: List[Dict | List]) -> Tuple[str, ParameterMapping]:
  id_count = 0
  parameter_mapping: ParameterMapping = {}

  queue: List[Tuple[str | None, Any]] = [(None, i) for i in items]
  key_value_pairs: List[Tuple[str | None, Any]] = []
  while queue:
    key, item = queue.pop()
    if isinstance(item, dict):
      for key, value in item.items():
        queue.append((key, value))
    elif isinstance(item, list):
      for value in item:
        queue.append((None, value))
    else:
      key_value_pairs.append((key, item))
  
  for key, value in key_value_pairs:
    if __is_id_key(key) and isinstance(value, (str, int)):
      if value not in parameter_mapping:
        id_count += 1
        parameter_mapping[value] = f'$id{id_count}'

  parameterized_prompt = prompt
  # loop parameters sorted by the longest key
  for value, parameter in sorted(parameter_mapping.items(), key=lambda x: len(str(x[0])), reverse=True):
    parameterized_prompt = parameterized_prompt.replace(str(value), parameter)
  
  return parameterized_prompt, parameter_mapping


def deparameterize(prompt: str, parameter_mapping: ParameterMapping) -> str:
  deparameterized_prompt = prompt
  for value, parameter in sorted(parameter_mapping.items(), key=lambda x: len(x[1]), reverse=True):
    deparameterized_prompt = deparameterized_prompt.replace(parameter, str(value))
  return deparameterized_prompt
