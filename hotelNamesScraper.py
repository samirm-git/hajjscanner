import requests
import sys
import re
import unicodedata
from consts import CITY_PATTERNS

#TODO: REMOVE COMMON_WORDS_RE AND USE CITY_PATTERNS INSTEAD, AND REMOVE 'hotel' SEPARATELY
def build_hotelName_regex(hotel_list):
    escaped = [re.escape(h) for h in hotel_list]
    joined = "|".join(escaped)
    pattern = rf"\b(?:{joined})\b"
    return re.compile(pattern, re.IGNORECASE)


with open('makkah_hotels.txt', 'r') as f:
  makkahHotels = f.read().splitlines()

with open('madinah_hotels.txt', 'r') as f:
  madinahHotels = f.read().splitlines()

HOTEL_NAMES_RE = {
  "makkah": build_hotelName_regex(makkahHotels),
  "madinah": build_hotelName_regex(madinahHotels)
}
  

def clean_text(text):
    def remove_arabic(text):
      return re.sub(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+', '', text)

    def normalize_text(text):
      text = text.lower()
      text = unicodedata.normalize('NFKC', text)

      text = text.encode('ascii', 'ignore').decode('ascii')

      text = re.sub(r"\d+", "", text)         
      text = re.sub(r"[^\w\s]", "", text)
      text = COMMON_WORDS_RE.sub("", text)
      text = re.sub(r"\s+", " ", text).strip()

      return text 

    if not text:
      return ""

    makkah = CITY_PATTERNS["makkah"]
    madinah = CITY_PATTERNS["madinah"]
    COMMON_WORDS_RE = re.compile(
    rf"(?:\bhotel\b|{makkah}|{madinah})",
    re.IGNORECASE
    )

    text = remove_arabic(text)
    text = normalize_text(text)
    return text

def main(city, save=False):
  coords = "(21.1,39.6,21.55,40.15)" if city == "makkah" else "(24.38,39.54,24.58,39.72)"

  url = "https://overpass-api.de/api/interpreter"

  query = f"""
  [out:json];
  (
    node["tourism"~"hotel"]{coords};
    way["tourism"~"hotel"]{coords};
    relation["tourism"~"hotel"]{coords};
    way["building"="hotel"]{coords};
    relation["building"="hotel"]{coords};
  );
  out tags;
  """

  headers = {"User-Agent": "HotelNameScraper"}
  res = requests.post(url, data={"data": query}, headers=headers, timeout=60)

  if res.status_code != 200:
    print(f"request exited with code: {res.status_code}")
    print("not working") 

  else:
      

    data = res.json()


    hotels = set()

    for el in data["elements"]:
        name = el.get("tags", {}).get("name")
        name_en = el.get("tags", {}).get("name:en")
        if name_en:
          clean_name = clean_text(name_en)
          if clean_name:
            hotels.add(clean_name)
        elif name:
          clean_name = clean_text(name)
          if clean_name:
            hotels.add(clean_name)
            

    print(len(hotels))
      
    if save:
      with open(f"{city}_hotels.txt", "w", encoding="utf-8") as f:
        for h in sorted(hotels):
            f.write(h + "\n")

    print("Done")

def temp(city):

  hotels = makkahHotels if city == "makkah" else madinahHotels
  hotelsCleaned = set()
  for hotel in hotels:
    hotelsCleaned.add(clean_text(hotel))
  
  with open(f"{city}_hotels.txt", "w", encoding="utf-8") as f:
    for h in sorted(hotelsCleaned):
      f.write(h + "\n")

if __name__ == "__main__":
  if len(sys.argv) >= 2:
    city = sys.argv[1]

  main(city, save=True)
  # temp(city)
