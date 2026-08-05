import json
from jsonschema import validate, ValidationError
from utils import getProjectRoot
from HajjUmrahEnum import HajjOrUmrahEnum
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT7

hajjPackageSchema = json.loads((getProjectRoot() / "pageScraper" / "schema" / "hajjPackage.json").read_text())
umrahPackageSchema = json.loads((getProjectRoot() / "pageScraper" / "schema" / "umrahPackage.json").read_text())
hotelSchema = json.loads((getProjectRoot() / "pageScraper" / "schema" / "hotel.json").read_text())

_registry = Registry().with_resources([
    ("hotel.json", Resource.from_contents(hotelSchema, default_specification=DRAFT7))
])

def validateData(scrapedInfo: dict, hajjOrUmrah: HajjOrUmrahEnum):
  try:
    schema = hajjPackageSchema if hajjOrUmrah == HajjOrUmrahEnum.HAJJ else umrahPackageSchema

    validate(instance=scrapedInfo, schema=schema, registry=_registry)
    return None
  except ValidationError as e:
    return e.message
  except Exception as e:
    return str(e)