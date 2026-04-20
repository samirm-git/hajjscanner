import requests
import sys
from scraper.helpers import cleanText 
from scraper.db import addHotel, getCityHotelNames, deleteNonEnglishHotelNames

HOTELS = {"makkah": getCityHotelNames('makkah'), "madinah": getCityHotelNames("madinah")}
  


def main(city, save=False):
  city = city.lower()
  assert city in ['makkah', 'madinah']
  coords = "(21.1,39.6,21.55,40.15)" if city == "makkah" else "(24.38,39.54,24.58,39.72)"

  url = "https://overpass-api.de/api/interpreter"

  query = f"""
  [out:json];
  (
    node["tourism"="hotel"]{coords};
    way["tourism"="hotel"]{coords};
    relation["tourism"="hotel"]{coords};
    way["building"="hotel"]{coords};
    relation["building"="hotel"]{coords};
  );
  out tags;
  """

  headers = {"User-Agent": "HotelNameScraperv2.1"}
  res = requests.post(url, data={"data": query}, headers=headers, timeout=60)

  if res.status_code != 200:
    print(f"request exited with code: {res.status_code}")
    print("not working") 

  else:
      

    data = res.json()

    for el in data["elements"]:
        name = el.get("tags", {}).get("name")
        name_en = el.get("tags", {}).get("name:en")
        
        if name_en:
          clean_name = cleanText(name_en)
          clean_name = name_en if clean_name == "" else clean_name
          o = addHotel(name_en, clean_name, city)
          if o:
            print(f"Adding hotel: {name_en}. Success")

        elif name:
          clean_name = cleanText(name)
          clean_name = name if clean_name == "" else clean_name
          o = addHotel(name, clean_name, city)
          if o:
            print(f"Adding hotel: {name_en}. Success")

    deleteNonEnglishHotelNames()     
      

    print("Done")

if __name__ == "__main__":
  if len(sys.argv) >= 2:
    city = sys.argv[1]

  main(city, save=True)
  # temp(city)