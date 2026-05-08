import sqlite3
import json
from scraper.helpers import getProjectRoot

DB_PATH = getProjectRoot() / 'scraper' / 'scraper.db' 

#provider TABLE
#=======================================
def addProvider(name: str, homepage_url: str, metadata: dict = {}):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO providers (name, homepage_url, metadata) VALUES (?, ?, ?)",
            (name, homepage_url, json.dumps(metadata))
        )

def updateProviderMetadata(provider: str, metadata: dict):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE providers SET metadata = ? WHERE name = ?",
            (json.dumps(metadata), provider)
        )

def getProviderMetadata(provider: str) -> dict:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT metadata FROM providers WHERE name = ?", (provider,)
        ).fetchone()
    return json.loads(row[0]) if row else {}

def getAllProviders():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT name, homepage_url FROM providers ORDER BY name").fetchall()
    return {row[0]: row[1] for row in rows}


#package_urls TABLE
#=====================================================
def saveUrls(provider: str, urls: set[str], type: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO package_urls (provider, url, type) VALUES (?, ?, ?)",
            [(provider, url, type) for url in urls]
        )

def removeUrl(url: str):
  with sqlite3.connect(DB_PATH) as conn:
      cursor = conn.execute(
          "DELETE FROM package_urls WHERE url = ?", (url,)
      )
      if cursor.rowcount <= 0:
        print(f"Failed to remove url from package_urls: {url}")

def flagUrlIsCatalogue(url:str):
  with sqlite3.connect(DB_PATH) as conn:
      cursor = conn.execute(
          "UPDATE package_urls SET isCatalogue = 1 WHERE url = ?", (url,)
      )
      if cursor.rowcount <= 0:
         print(f"failed to flag url as catalogue page: {url} ")

def setScrapped(url:str):
   with sqlite3.connect(DB_PATH) as conn:
      cursor = conn.execute(
         "UPDATE package_urls SET scraped = 1 WHERE url = ?", (url,)
      )
      if cursor.rowcount <0:
         print(f"failed to set url to scrapped: {url}") 

def getAllUrls(type: str, scrapeNewOnly=False) -> dict[str, list[str]]:
  scrapeNewOnlyString = "AND scraped = 0" if scrapeNewOnly else ""
  with sqlite3.connect(DB_PATH) as conn:
      rows = conn.execute(
          f"""SELECT provider, url FROM package_urls
              WHERE type = ? AND isCatalogue = 0 {scrapeNewOnlyString}
              ORDER BY provider""",
          (type,)
      ).fetchall()

  result = {}
  for provider, url in rows:
      result.setdefault(provider, []).append(url)

  return result

#hotels TABLE
#===================================================
def addHotel(fullName, shortName, city):
    with sqlite3.connect(DB_PATH) as conn:
      cursor = conn.execute(
        "INSERT OR IGNORE INTO hotels (fullName, shortName, city) VALUES (?, ?, ?)",
        (fullName, shortName, city))
    return cursor.rowcount > 0

def deleteNonEnglishHotelNames():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""DELETE FROM hotels WHERE fullName GLOB '*[ء-ي]*' AND fullName NOT GLOB '*[A-Za-z]*';""")
    return cursor.rowcount > 0

def getCityHotelNames(city) -> list:
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT shortName, fullName FROM hotels WHERE city = ?",(city,)).fetchall()
        cityHotels = {short: full for short, full in rows}
        
    return cityHotels
  

def UpdateHotelShortName():
  from scraper.helpers import cleanText
  with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT id, fullName FROM hotels")
    rows = cursor.fetchall()
    cursor.executemany(
    "UPDATE hotels SET shortName = ? WHERE id = ?",
    [(cleanText(fullname), row_id) for row_id, fullname in rows]
    ) 
    
