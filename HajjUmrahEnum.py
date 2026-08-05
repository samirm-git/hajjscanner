from enum import Enum
import re

HAJJREGEX = re.compile(
    r"(?:hajj[-_]*(?:[\w]*[-_])*package|package[-_]*(?:[\w]*[-_])*hajj)",
    re.IGNORECASE
)

UMRAHREGEX = re.compile(
    r"(?:umrah?[-_]*(?:[\w]*[-_])*package|package[-_]*(?:[\w]*[-_])*umrah?)",
    re.IGNORECASE
)

class HajjOrUmrahEnum(Enum):
  HAJJ = "hajj"
  UMRAH = "umrah"

  @property
  def regex(self) -> str:
    if self is HajjOrUmrahEnum.HAJJ:
      return HAJJREGEX
    else:
      return UMRAHREGEX

  @property
  def label(self) -> str:
    return self.value.capitalize()