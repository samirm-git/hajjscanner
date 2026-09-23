from enum import Enum
import re

MAKKAH_REGEX = re.compile(r"\b(makkah|mecca|meccah|makah)\b", re.IGNORECASE)
MADINAH_REGEX = re.compile(r"\b(madinah|medina|medinah|madina)\b", re.IGNORECASE)

class City(Enum):
  MAKKAH = "makkah"
  MADINAH = "madinah"

  @property
  def regex(self) -> str:
    if self is City.MAKKAH:
      return MAKKAH_REGEX
    else:
      return MADINAH_REGEX

  @property
  def label(self) -> str:
    return self.value.capitalize()