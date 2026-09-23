import requests
import sys
from utils import normalizeCharacters, removeHotelSignifier
from db import hotelQueries

# def updatedLiteClean(testRun=True):
#   hotels = hotelQueries.getAllHotels()  # (id, fullName, extraCleanedName, liteCleanedName, city)

#   changed = []
#   for hotelId, fullName, extraCleanedName, liteCleanedName, city in hotels:
#     newLiteCleanedName = liteClean(fullName)

#     if newLiteCleanedName != liteCleanedName:
#       changed.append((hotelId, newLiteCleanedName))
#       print(f"Updating hotel {hotelId} ({fullName!r}): liteCleanedName {liteCleanedName!r} -> {newLiteCleanedName!r}")

#   if testRun:
#     print(f"[testRun] Would update {len(changed)}/{len(hotels)} liteCleanedName values")
#   else:
#     if changed:
#       hotelQueries.updateLiteCleanedNames(changed)
#     print(f"Updated {len(changed)}/{len(hotels)} liteCleanedName values")


def updateFullNames(testRun=True):
  import sqlite3
  hotels = hotelQueries.getAllHotels()
  for id, fullName, _, _, _ in hotels:
    newFullName = normalizeCharacters(fullName)
    if fullName != newFullName:
      if testRun:
        print(f"WOULD update fullName {fullName!r} to {newFullName!r}")
      else:
        print(f"Updating {fullName!r} to {newFullName!r}")
        try:
          hotelQueries.updateFullNames(id, newFullName)
        except sqlite3.IntegrityError:
          print(f"deleting duplicate {newFullName!r}")
          hotelQueries.deleteHotels([id])

def removeSubStringDuplicates(cityHotels, testRun=True):
  """
  cityHotels: list of (id, fullName, liteCleanedName) for a single city.

  If one hotel's liteCleanedName is a substring of (or identical to) another
  hotel's, the shorter one is redundant - there's nothing left to fall back
  on, since liteCleanedName already keeps everything but Arabic al-/el-
  prefixes.

  Hotels are processed longest liteCleanedName first (ties broken by id), so
  every longer name is already in keptHotels by the time a shorter,
  possibly-redundant one is checked against it. A genuine substring can never
  be longer than the string containing it, so this order is always safe.
  """
  sortedHotels = sorted(cityHotels, key=lambda hotel: (-len(hotel[2]), hotel[0]))

  keptHotels = []
  hotelsToRemove = []

  for hotelId, fullName, liteCleanedName in sortedHotels:
    if liteCleanedName == "":
      print(f"remove {hotelId}, empty liteCleanedName. fullName: {fullName!r}")
      continue

    # Padding with a boundary space on both sides stops partial-word false
    # hits, e.g. "el" would otherwise match inside "hotel".
    paddedName = " " + liteCleanedName + " "

    foundConflict = False
    for keptId, keptFullName, keptPaddedName in keptHotels:
      if paddedName in keptPaddedName:
        if testRun:
          print(f"WOULD Remove hotel {hotelId}, {fullName!r} liteCleanedName={liteCleanedName!r}): "
              f"substring of/equal to hotel {keptId} ({keptFullName!r})")
        else:
          print(f"Removing hotel {hotelId}, {fullName!r} liteCleanedName={liteCleanedName!r}): "
              f"substring of/equal to hotel {keptId} ({keptFullName!r})")

        hotelsToRemove.append(hotelId)
        foundConflict = True
        break

    if not foundConflict:
      keptHotels.append((hotelId, fullName, paddedName))

  if testRun == False:
    hotelQueries.deleteHotels(hotelsToRemove)


def updateHotelDB(testRun=True):
  pass



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
          full_name = normalizeCharacters(name_en)
          full_name = name_en if full_name == "" else full_name
          clean_name = removeHotelSignifier(name_en)
          clean_name = name_en if clean_name == "" else clean_name
          o = hotelQueries.addHotel(full_name, clean_name, city)
          if o:
            print(f"Adding hotel: {full_name}. Success")

        elif name:
          full_name = normalizeCharacters(name)
          full_name = name if full_name == "" else full_name
          clean_name = removeHotelSignifier(name)
          clean_name = name if clean_name == "" else clean_name
          o = hotelQueries.addHotel(full_name, clean_name, city)
          if o:
            print(f"Adding hotel: {full_name}. Success")

    hotelQueries.deleteNonEnglishHotelNames()     
      

    print("Done")

if __name__ == "__main__":
  if len(sys.argv) >= 2:
    city = sys.argv[1]
  # main(city, save=True)
  # updatedLiteClean(False)
  # updateFullNames(True)
  # makkahHotels = hotelQueries.getCityHotelNames("makkah")
  # madinahHotels = hotelQueries.getCityHotelNames("madinah")
  # removeSubStringDuplicates(makkahHotels, testRun=False)
  # removeSubStringDuplicates(madinahHotels, testRun=False)