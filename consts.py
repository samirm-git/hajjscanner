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