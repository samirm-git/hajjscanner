import re
import unicodedata
from cityEnum import MAKKAH_REGEX, MADINAH_REGEX

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

def removeHotelSignifier(text):
    HOTEL_SIGNIFIER = re.compile(rf"(?:\bhotel\b|\bal[-\s]?|\bel[-\s]?|{MAKKAH_REGEX}|{MADINAH_REGEX})", re.IGNORECASE)
    # HOTEL_SIGNIFIER_LITE = re.compile(rf"(?:\bal[-\s]?|\bel[-\s]?|{MAKKAH_REGEX}|{MADINAH_REGEX})", re.IGNORECASE)

    if not text:
      return ""

    text = normalizeCharacters(text)
    text = text.lower()

    text = HOTEL_SIGNIFIER.sub("", text)

    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text