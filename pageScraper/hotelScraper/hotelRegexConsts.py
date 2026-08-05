import re

CITY_PATTERNS = {
    "makkah": r"\b(makkah|mecca|meccah|makah)\b",
    "madinah": r"\b(madinah|medina|medinah|madina)\b",
}

HOTEL_SIGNIFIER = re.compile(rf"(?:\bhotel\b|\bal[-\s]?|\bel[-\s]?|{CITY_PATTERNS['makkah']}|{CITY_PATTERNS['madinah']})", re.IGNORECASE)

HOTEL_SIGNIFIER_LITE = re.compile(rf"(?:\bal[-\s]?|\bel[-\s]?|{CITY_PATTERNS['makkah']}|{CITY_PATTERNS['madinah']})", re.IGNORECASE)


BAD_IMAGE_RE = re.compile(r"(icon|place[-_]?holder)", re.IGNORECASE)

HOTEL_KEYWORDS_RE = re.compile(
    r'\b(hotel|towers?|suites?|residences?|dar|grand|royale?|plaza|inn|lodge|'
    r'mövenpick|movenpick|hilton|marriott|pullman|hyatt|novotel|'
    r'intercontinental|radisson|millennium|'
    r'swissotel|sheraton|fairmont|voco|conrad|doubletree|ritz|kempinski|'
    r'jumeirah|rove|ibis|sofitel|raffles|ramada|wyndham|elaf|makarem|'
    r'emaar|anjum|concorde|meridien|address|rotana)\b',
    re.IGNORECASE
)

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

NUMBER_PATTERN = rf"(?:\d{{1,2}}|{_NUM_WORDS})"
WALK_TIME_RE = re.compile(
    rf"""
    \b
    (?P<time1>{NUMBER_PATTERN})
    (?:\s*(?:-|–|to)\s*(?P<time2>{NUMBER_PATTERN}))?
    [\s\-](?:mins?|minutes?)\b
    [^.!?\n]{{0,60}}?
    \bwalk\w*\b
    |
    \bwalk\w*\b
    [^.!?\n]{{0,60}}?
    \b
    (?P<time1b>{NUMBER_PATTERN})
    (?:\s*(?:-|–|to)\s*(?P<time2b>{NUMBER_PATTERN}))?
    [\s\-](?:mins?|minutes?)\b
    """,
    re.IGNORECASE | re.VERBOSE
)


