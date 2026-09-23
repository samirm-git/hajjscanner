from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Annotated, ClassVar
from .enums import DepartureCity, IslamicMonth, Month, Season, Tier
from datetime import date
from hijridate import Gregorian

class SchemaModel(BaseModel):
  # extra="forbid" turns a typo'd field name into a loud error, in scraper output
  # AND in the tests/data/*/expected.json fixtures.
  model_config = ConfigDict(extra="forbid")


class BasePackageCore(SchemaModel):
  YEAR_MIN: ClassVar[int] = 2020
  STARS_BOUNDS: ClassVar[tuple[int, int]] = (1, 5)  # (min, max)


  ppp: int | None = Field(description="Overridden per package type with its own bounds")
  year: Annotated[int, Field(ge=YEAR_MIN, le=date.today().year+1)] | None
  total_days: int | None = Field(description="Overridden per package type with its own bounds")
  tier: Tier | None = None  # optional key in both schemas
  stars: Annotated[int, Field(ge=STARS_BOUNDS[0], le=STARS_BOUNDS[1])] | None
  departure_city: DepartureCity | None
  is_visa_included: bool | None

class HajjPackageCore(BasePackageCore):
  PPP_BOUNDS: ClassVar[tuple[int, int]] = (2_000, 25_000)
  TOTAL_DAYS_BOUNDS: ClassVar[tuple[int, int]] = (10, 30)

  ppp: Annotated[int, Field(ge=PPP_BOUNDS[0], le=PPP_BOUNDS[1])] | None
  total_days: Annotated[int, Field(ge=TOTAL_DAYS_BOUNDS[0], le=TOTAL_DAYS_BOUNDS[1])] | None
  is_shifting: bool | None

class UmrahPackageCore(BasePackageCore):
  PPP_BOUNDS: ClassVar[tuple[int, int]] = (100, 10_000)  # (min, max)
  TOTAL_DAYS_BOUNDS: ClassVar[tuple[int, int]] = (5, 30)  # (min, max)

  ppp: Annotated[int, Field(ge=PPP_BOUNDS[0], le=PPP_BOUNDS[1])] | None
  total_days: Annotated[int, Field(ge=TOTAL_DAYS_BOUNDS[0], le=TOTAL_DAYS_BOUNDS[1])] | None
  season: Season | None
  month: Month | None
  islamic_month: IslamicMonth | None
  is_ziyarat_included: bool | None

  @model_validator(mode="after")
  def fillMissingDateFields(self):
    # month -> islamicMonth deduction needs a year to anchor the conversion,
    # since the same islamicMonth/month pairing shifts every Gregorian year.
    CONST_DAY = 5
    MONTH_TO_SEASON: dict[Month, Season] = {
      Month.DECEMBER: Season.WINTER,
      Month.JANUARY: Season.WINTER,
      Month.FEBRUARY: Season.WINTER,
      Month.MARCH: Season.SPRING,
      Month.APRIL: Season.SPRING,
      Month.MAY: Season.SPRING,
      Month.JUNE: Season.SUMMER,
      Month.JULY: Season.SUMMER,
      Month.AUGUST: Season.SUMMER,
      Month.SEPTEMBER: Season.AUTUMN,
      Month.OCTOBER: Season.AUTUMN,
      Month.NOVEMBER: Season.AUTUMN,
  } 
    if self.year is not None:
      if self.month is not None and self.islamic_month is None:
        islamicMonthIndex = Gregorian(self.year, self.month.index, CONST_DAY).to_hijri().month
        self.islamic_month = IslamicMonth.from_index(islamicMonthIndex)
  
      elif self.islamic_month is not None and self.month is None:
        #TODO: COMPLETE THIS
        pass
  
    # season <-> month is a fixed, certain mapping, no year needed
    if self.month is not None and self.season is None:
      self.season = MONTH_TO_SEASON.get(self.month)
  
    return self


class Hotel(SchemaModel):
  NAME_LENGTH_BOUNDS: ClassVar[tuple[int, int]] = (2, 100)  
  TOTAL_DAYS_BOUNDS: ClassVar[tuple[int, int]] = (1, 20)  
  IMAGES_MIN_COUNT: ClassVar[int] = 1  
  STARS_BOUNDS: ClassVar[tuple[int, int]] = (1, 5)  
  DISTANCE_TO_HARAM_BOUNDS: ClassVar[tuple[int, int]] = (500, 4000)  
  WALK_TO_HARAM_BOUNDS: ClassVar[tuple[int, int]] = (2, 40)  
  NUMBER_OF_BEDS_BOUNDS: ClassVar[tuple[int, int]] = (1, 6)  

  name: Annotated[str, Field(min_length=NAME_LENGTH_BOUNDS[0], max_length=NAME_LENGTH_BOUNDS[1])] | None
  images: Annotated[list[str], Field(min_length=IMAGES_MIN_COUNT)] | None
  total_days: Annotated[int, Field(ge=TOTAL_DAYS_BOUNDS[0], le=TOTAL_DAYS_BOUNDS[1])] | None
  stars: Annotated[int, Field(ge=STARS_BOUNDS[0], le=STARS_BOUNDS[1])] | None
  has_wifi: bool | None
  has_ac: bool | None
  distance_to_haram: Annotated[int, Field(ge=DISTANCE_TO_HARAM_BOUNDS[0], le=DISTANCE_TO_HARAM_BOUNDS[1])] | None
  walk_to_haram: Annotated[int, Field(ge=WALK_TO_HARAM_BOUNDS[0], le=WALK_TO_HARAM_BOUNDS[1])] | None
  number_of_beds: Annotated[int, Field(ge=NUMBER_OF_BEDS_BOUNDS[0], le=NUMBER_OF_BEDS_BOUNDS[1])] | None
  other_amenities: str | None = None  # optional key

class BasePackage(SchemaModel):
  url: str
  company: str
  package_core: BasePackageCore
  makkah_hotel: Hotel | None
  madinah_hotel: Hotel | None

class HajjPackage(BasePackage):
  package_core: HajjPackageCore
 
class UmrahPackage(BasePackage):
  package_core: UmrahPackageCore