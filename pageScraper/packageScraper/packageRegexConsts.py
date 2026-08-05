import re

ISLAMIC_MONTH_PATTERNS = {
  "Muharram":        r"muharram",
  "Safar":           r"safar",
  "Rabi' al-Awwal":  r"rabi(?:'|’)?\s*(?:al[-\s]?)?(?:awwal|i|1)",
  "Rabi' al-Thani":  r"rabi(?:'|’)?\s*(?:al[-\s]?)?(?:thani|ii|2|akhir)",
  "Jumada al-Ula":   r"jumad[ae]?[-\s]?(?:al[-\s]?)?(?:ula|awwal|i|1)",
  "Jumada al-Akhirah": r"jumad[ae]?[-\s]?(?:al[-\s]?)?(?:akhir(?:ah)?|thani|ii|2)",
  "Rajab":           r"rajab",
  "Sha'ban":         r"sha(?:'|’)?ban",
  "Ramadan":         r"ramad(?:h|z)?an",
  "Shawwal":         r"shawwal",
  "Dhu al-Qa'dah":   r"dhu(?:l|\s+al)?[-\s]?q(?:a|i)(?:'|’)?dah?",
  "Dhu al-Hijjah":   r"(?:dhu|zul|zil)(?:l|\s+al)?[-\s]?hijjah?",
}

ISLAMIC_MONTH_RE = re.compile(
  r"\b(" + "|".join(ISLAMIC_MONTH_PATTERNS.values()) + r")\b",
  re.IGNORECASE
)

_DEPARTURE_CITY_PATTERNS = {
  "London": r"london(?:\s+(?:heathrow|gatwick|luton|stansted|city))?",
  "Manchester": r"manchester",
  "Birmingham": r"birmingham",
  "Glasgow": r"glasgow",
  "Edinburgh": r"edinburgh",
  "Leeds": r"leeds(?:[-\s]bradford)?",
  "Newcastle": r"newcastle",
  "Liverpool": r"liverpool",
  "Bristol": r"bristol",
  "Cardiff": r"cardiff",
  "Belfast": r"belfast"
}

_DEPARTURE_CITY_CUE = r"\b(?:depart(?:s|ing|ure(?:s)?)?|leaving|flights?|travel(?:l)?ing)(?:\s+from\b)?\b"

DEPARTURE_CITY_RE = re.compile(_DEPARTURE_CITY_CUE + "|".join( 
      f"(?P<{city}>{pattern})" for city, pattern in _DEPARTURE_CITY_PATTERNS.items()), re.IGNORECASE) 

AZIZIYAH_RE = re.compile(r"\b(?:al[-\s]?)?aziziy{0,2}ah?\b", re.IGNORECASE)
