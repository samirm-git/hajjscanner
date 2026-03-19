import re

CONTAINER_TAGS = ["div", "section", "article", "td", "tr"]
HEADING_TAGS = ["h1", "h2", "h3", "h4", "h5", "h6", "small", "strong"]
CITY_PATTERNS = {
    "makkah": re.compile(r"\b(makkah|mecca|meccah|makah)\b", re.IGNORECASE),
    "madinah": re.compile(r"\b(madinah|medina|medinah|madina)\b", re.IGNORECASE),
}

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

TO_METRES = {
    "km": 1000, "kilometer": 1000, "kilometre": 1000,
    "kilometers": 1000, "kilometres": 1000,
    "m": 1, "meters": 1, "metres": 1,
    "mi": 1609.344, "mile": 1609.344, "miles": 1609.344,
    "ft": 0.3048, "foot": 0.3048, "feet": 0.3048,
    "yd": 0.9144, "yard": 0.9144, "yards": 0.9144,
}

NUM_WORDS = (
    "one|two|three|four|five|six|seven|eight|nine|ten|"
    "eleven|twelve|thirteen|fourteen|fifteen|sixteen|"
    "seventeen|eighteen|nineteen|twenty"
)

NUMBER_PATTERN = rf"(?:\d{{1,2}}|{NUM_WORDS})"

WORD_TO_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20,
}

WALK_TIME_RE = re.compile(
  rf"""
  \b
  (?P<time1>{NUMBER_PATTERN})
  (?:\s*(?:-|–|to)\s*(?P<time2>{NUMBER_PATTERN}))?   # optional range

  \s*(?:mins?|minutes?)\b
  """,
  re.IGNORECASE | re.VERBOSE
)