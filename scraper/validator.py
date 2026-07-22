import json
from jsonschema import validate, ValidationError
from scraper.helpers import getProjectRoot
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT7

# Built once at import time — hotel.json's content is fixed for the life of
# the process, so there's no reason to re-read the file or rebuild the
# registry on every call.

hajjPackageSchema = json.loads((getProjectRoot() / "schema" / "hajjPackage.json").read_text())
umrahPackageSchema = json.loads((getProjectRoot() / "schema" / "umrahPackage.json").read_text())
hotelSchema = json.loads((getProjectRoot() / "schema" / "hotel.json").read_text())

_registry = Registry().with_resources([
    ("hotel.json", Resource.from_contents(hotelSchema, default_specification=DRAFT7))
])

def validateData(scrapedInfo: dict, hajjOrUmrah: str):
  try:
    if hajjOrUmrah == 'hajj':
      schema = hajjPackageSchema
    elif hajjOrUmrah == 'umrah':
      schema = umrahPackageSchema
    else:
      raise ValueError(f"expected 'hajj' or 'umrah' got {hajjOrUmrah}")

    validate(instance=scrapedInfo, schema=schema, registry=_registry)
    return None
  except ValidationError as e:
    return e.message
  except Exception as e:
    return str(e)