
def jsonUperCaseTypes(obj):
  unsupported = ["$schema", "$id", "title", "uniqueItems", "minLength", "maxLength"]
  if isinstance(obj, dict):
    result = {}
    for key, value in obj.items():
      if key in unsupported:
        continue
      elif key == "type":
        if isinstance(value, str):
          result[key] = value.upper()
        elif isinstance(value, list):
          assert len(value) == 2, "must only be max 2 types. The second type should be null"
          assert value[1] == "null", "must only be max 2 types. The second type should be null"
          result[key] = value[0].upper()
          result['nullable'] = True
        
      elif key in ["$schema", "$id", "title"]:
        # Skip JSON Schema metadata
        continue
      else:
        result[key] = jsonUperCaseTypes(value)
    return result
    
  elif isinstance(obj, list):
    return [jsonUperCaseTypes(item) for item in obj]
  else:
    return obj

def remove_property(schema: dict, propName: str) -> None:
  schema.get("properties", {}).pop(propName, None)
  if "required" in schema:
      while propName in schema["required"]:
          schema["required"].remove(propName)