from enum import StrEnum, auto

class Tier(StrEnum):
  LUXURY = auto() 
  PREMIUM = auto()
  ECONOMY = auto()


class Season(StrEnum):
  WINTER = auto()
  SPRING = auto()
  SUMMER = auto()
  AUTUMN = auto()


class Month(StrEnum):
  JANUARY = auto()
  FEBRUARY = auto()
  MARCH = auto()
  APRIL = auto()
  MAY = auto()
  JUNE = auto()
  JULY = auto()
  AUGUST = auto()
  SEPTEMBER = auto()
  OCTOBER = auto()
  NOVEMBER = auto()
  DECEMBER = auto()

  @property
  def index(self) -> int:
    """1-12, matching hijridate library convention"""
    return list(type(self)).index(self) + 1

  @classmethod
  def from_index(cls, index: int):
    return list(cls)[index - 1]

class IslamicMonth(StrEnum):
  MUHARRAM         = "Muharram"
  SAFAR            = "Safar"
  RABI_AL_AWWAL    = "Rabi' al-Awwal"
  RABI_AL_THANI    = "Rabi' al-Thani"
  JUMADA_AL_AWWAL  = "Jumada al-Awwal"
  JUMADA_AL_THANI  = "Jumada al-Thani"
  RAJAB            = "Rajab"
  SHABAN           = "Sha'ban"
  RAMADAN          = "Ramadan"
  SHAWWAL          = "Shawwal"
  DHU_AL_QIDAH     = "Dhu al-Qi'dah"
  DHU_AL_HIJJAH    = "Dhu al-Hijjah"

  @property
  def index(self) -> int:
    """1-12, matching hijridate library convention"""
    return list(type(self)).index(self) + 1

  @classmethod
  def from_index(cls, index: int):
    return list(cls)[index - 1]


class DepartureCity(StrEnum):
  LONDON = auto()
  MANCHESTER = auto()
  BIRMINGHAM = auto()
  GLASGOW = auto()
  EDINBURGH = auto()
  LEEDS = auto()
  NEWCASTLE = auto()
  LIVERPOOL = auto()
  BRISTOL = auto()
  CARDIFF = auto()
  BELFAST = auto()
