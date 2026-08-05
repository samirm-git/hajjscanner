import re
import unicodedata
from .hotelRegexConsts import HOTEL_SIGNIFIER, HOTEL_SIGNIFIER_LITE

def normalizeCharacters(text):
    # Removes Arabic script and transliterates accented/irregular characters
    # down to their closest plain-ASCII equivalent (e.g. "\u00F4" -> "o") instead
    # of silently dropping them. NFKD decomposes an accented character into
    # its base letter plus a separate combining accent mark, so ascii-encode
    # with errors="ignore" only strips the accent mark and keeps the letter.
    if not text:
        return ""

    text = re.sub(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+', '', text)
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r"\d+", "", text)

    # Clean up artifacts left behind by the removals above: empty
    # parens/brackets (e.g. "Tower (2)" -> "Tower ()"), dangling
    # separators (e.g. "Hotel - " or "- Tower"), and any resulting
    # double whitespace.
    text = re.sub(r"\(\s*\)|\[\s*\]", "", text)
    text = re.sub(r"\s+-\s*$|^\s*-\s+", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text

def _clean(text, signifier):
    if not text:
      return ""

    text = normalizeCharacters(text)
    text = text.lower()
    # signifier must run before punctuation is stripped: \bal[-\s]?
    # consumes the separator in e.g. "al-madinah", which is what exposes
    # "madinah" as a fresh word-boundary for the city alternative to also
    # match in the same pass. Stripping punctuation first would glue them
    # into "almadinah", leaving "madinah" stuck after "al" is removed.
    text = signifier.sub("", text)
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text

def cleanText(text):
    return _clean(text, HOTEL_SIGNIFIER)

def liteClean(text):
  #POSSIBLY ADD CITY_PATTERNS['makkah'] AND CITY_PATTERNS['madinah'] TO SIGNIFIER
    return _clean(text, HOTEL_SIGNIFIER_LITE)
