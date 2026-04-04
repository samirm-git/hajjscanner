import json
from pathlib import Path
from jsonschema import validate, ValidationError
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT7
from scraper.helpers import getProjectRoot


def validateData(dict):
  try:
    # Load schemas
    path = getProjectRoot() / "schema" 
    with open(path / "hajjPackage.json") as f:
        hajjPackageSchema = json.load(f)

    with open(path / "hotel.json") as f:
        hotelSchema = json.load(f)

    # Create registry for handling $ref
    registry = Registry().with_resources([
        ("hotel.json", Resource.from_contents(hotelSchema, default_specification=DRAFT7))
    ])

    instance = json.loads(json.dumps(dict))

    validate(instance=instance, schema=hajjPackageSchema, registry=registry)
    return None
  
  except ValidationError as e:
    return e.message  # invalid + reason

  except Exception as e:
    # Catch unexpected errors (optional but useful)
    return str(e)