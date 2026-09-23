import re
from schema.enums import IslamicMonth, DepartureCity

TOTAL_DAYS_REGEX = re.compile(r"\b(\d{1,2})[-\s]?(?:night|day)s?\b",re.IGNORECASE) 
STARS_REGEX = re.compile(r'\b([1-5])\s*(?:-?\s*star|stars?)\b', re.IGNORECASE) 




_ISLAMIC_MONTH_PATTERNS = {
  IslamicMonth.MUHARRAM:        r"\bmuharram\b",
  IslamicMonth.SAFAR:           r"\bsafar\b",
  IslamicMonth.RABI_AL_AWWAL:   r"\brabi(?:'|’)?\s*(?:al[-\s]?)?(?:awwal|i\b|1\b)",
  IslamicMonth.RABI_AL_THANI:   r"\brabi(?:'|’)?\s*(?:al[-\s]?)?(?:thani|ii\b|2\b|akhir)\b",
  IslamicMonth.JUMADA_AL_AWWAL: r"\bjumad[ae]?[-\s]?(?:al[-\s]?)?(?:ula|awwal|i\b|1\b)",
  IslamicMonth.JUMADA_AL_THANI: r"\bjumad[ae]?[-\s]?(?:al[-\s]?)?(?:akhir(?:ah)?|thani|ii\b|2\b)",
  IslamicMonth.RAJAB:           r"\brajab\b",
  IslamicMonth.SHABAN:          r"\bsha(?:'|’)?ban\b",
  IslamicMonth.RAMADAN:         r"\bramad(?:h|z)?an\b",
  IslamicMonth.SHAWWAL:         r"\bshawwal\b",
  IslamicMonth.DHU_AL_QIDAH:    r"\b(?:dhu(?:'l|l|\s+al)?|zul|zil)[-\s]?q(?:a|i)(?:'|’)?dah?\b",
  IslamicMonth.DHU_AL_HIJJAH:   r"\b(?:dhu(?:'l|l|\s+al)?|zul|zil)[-\s]?hijjah?\b",
}

ISLAMIC_MONTH_RE = re.compile("|".join(f"(?P<{month.name}>{pattern})" for month, pattern in _ISLAMIC_MONTH_PATTERNS.items()),
                              re.IGNORECASE)

_DEPARTURE_CITY_PATTERNS = {
  DepartureCity.LONDON:      r"\blondon(?:\s+(?:heathrow|gatwick|luton|stansted|city))?\b",
  DepartureCity.MANCHESTER:  r"\bmanchester\b",
  DepartureCity.BIRMINGHAM:  r"\bbirmingham\b",
  DepartureCity.GLASGOW:     r"\bglasgow\b",
  DepartureCity.EDINBURGH:   r"\bedinburgh\b",
  DepartureCity.LEEDS:       r"\bleeds(?:[-\s]bradford)?\b",
  DepartureCity.NEWCASTLE:   r"\bnewcastle\b",
  DepartureCity.LIVERPOOL:   r"\bliverpool\b",
  DepartureCity.BRISTOL:     r"\bbristol\b",
  DepartureCity.CARDIFF:     r"\bcardiff\b",
  DepartureCity.BELFAST:     r"\bbelfast\b",
}

_DEPARTURE_CITY_CUE = r"\b(?:depart(?:s|ing|ure(?:s)?)?|leaving|flights?|travel(?:l)?ing)(?:\s+from\b)?\b"

DEPARTURE_CITY_RE = re.compile(_DEPARTURE_CITY_CUE + r".{0,15}?" + "|".join(f"(?P<{city.name}>{pattern})" for city, pattern in _DEPARTURE_CITY_PATTERNS.items()),
                                 re.IGNORECASE,)

AZIZIYAH_RE = re.compile(r"\b(?:al[-\s]?)?aziziy{0,2}ah?\b", re.IGNORECASE)


#HOTEL SCRAPER CONSTS
#=======================================

BAD_IMAGE_RE = re.compile(r"(icon|place[-_]?holder)", re.IGNORECASE)

DISTANCE_RE = re.compile(
  r"""
  \b
  (?P<distance>
      \d{1,10}            # integer part (up to 10 digits)
      (?:\.\d{1,6})?      # optional decimal (up to 6 places)
  )
  \s*                     # optional space between number and unit
  (?P<unit>
      # Metric
      km | kilometers? | kilometres?  |
      m  | meters?     | metres?      |

      # Imperial
      mi(?:les?)? |
      ft | feet | foot |
      yd | yards?
  )
  \b
  """,
  re.IGNORECASE | re.VERBOSE,
)


_NUM_WORDS = (
    "one|two|three|four|five|six|seven|eight|nine|ten|"
    "eleven|twelve|thirteen|fourteen|fifteen|sixteen|"
    "seventeen|eighteen|nineteen|twenty"
)

_NUMBER_PATTERN = rf"(?:\d{{1,2}}|{_NUM_WORDS})"
WALK_TIME_RE = re.compile(
    rf"""
    \b
    (?P<time1>{_NUMBER_PATTERN})
    (?:\s*(?:-|–|to)\s*(?P<time2>{_NUMBER_PATTERN}))?
    [\s\-](?:mins?|minutes?)\b
    [^.!?\n]{{0,60}}?
    \bwalk\w*\b
    |
    \bwalk\w*\b
    [^.!?\n]{{0,60}}?
    \b
    (?P<time1b>{_NUMBER_PATTERN})
    (?:\s*(?:-|–|to)\s*(?P<time2b>{_NUMBER_PATTERN}))?
    [\s\-](?:mins?|minutes?)\b
    """,
    re.IGNORECASE | re.VERBOSE
)

# HOTEL_KEYWORDS_RE = re.compile(
#     r'\b(hotel|towers?|suites?|residences?|dar|grand|royale?|plaza|inn|lodge|'
#     r'mövenpick|movenpick|hilton|marriott|pullman|hyatt|novotel|'
#     r'intercontinental|radisson|millennium|'
#     r'swissotel|sheraton|fairmont|voco|conrad|doubletree|ritz|kempinski|'
#     r'jumeirah|rove|ibis|sofitel|raffles|ramada|wyndham|elaf|makarem|'
#     r'emaar|anjum|concorde|meridien|address|rotana)\b',
#     re.IGNORECASE
# )



