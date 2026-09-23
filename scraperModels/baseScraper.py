from pydantic import BaseModel, TypeAdapter, ValidationError
from typing import Callable, ClassVar
from bs4 import BeautifulSoup

def scrapes(field: str):
  """Tags a scrape method as the producer of one MODEL field.
  Usage:
      @scrapes("ppp")
      def scrapePPP(self): ...
  """
  def decorator(func):
    func.field = field
    return func
  return decorator


class BaseScraper:
  MODEL: ClassVar[type[BaseModel] | None] = None
  _scrapers: ClassVar[dict[str, Callable]] = {}
  _adapaters: ClassVar[dict[str, TypeAdapter]] = {}

  def __init__(self, soup: BeautifulSoup):
    self.soup = soup

    headingsTags = ["h1", "h2", "h3", "h4", "h5", "h6", "small", "strong"]
    self.headingsList = [s for tagName in headingsTags for tag in soup.findAll(tagName) for s in tag.stripped_strings ]

    self.textList = list(soup.stripped_strings) #CHANGE THIS TO BODY TEXT NOT CONTAINING HEADING TEXT

    pass

  def __init_subclass__(cls, **kwargs): 
    super().__init_subclass__(**kwargs)
    cls._buildAndValidateRegistry()

  @classmethod
  def _buildAdapter(cls, field: str) -> TypeAdapter:
    annotation = cls.MODEL.model_fields[field].annotation
    return TypeAdapter(annotation)

  @classmethod
  def _buildAndValidateRegistry(cls):
    scrapers = {}
    for name in dir(cls):
      method = getattr(cls, name)
      field = getattr(method, "field", None)
      if field is not None:
        scrapers[field] = method
    cls._scrapers = scrapers

    if cls.MODEL is None:
      return  # no MODEL yet - nothing to check

    registered, declared = set(scrapers), set(cls.MODEL.model_fields)
    if registered != declared:
      raise TypeError(
        f"{cls.__name__}: scrapers don't match {cls.MODEL.__name__} fields "
        f"(missing={declared - registered}, unexpected={registered - declared})")

    cls._adapters = {
        field: cls._buildAdapter(field) for field in declared
    }

  @classmethod
  def isFieldValid(cls, field:str, value) -> bool:
    try:
      cls._adapters[field].validate_python(value)
      return True
    except ValidationError:
      return False


  def run(self):
    result = {field: fn(self) for field, fn in self._scrapers.items()}
    return self.MODEL(**result)
    