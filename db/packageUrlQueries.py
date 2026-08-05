import sqlite3
from pathlib import Path
DB_PATH = Path(__file__).parent / 'scraper.db'

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

def getAllUrls(hajjOrUmrahString: str, scrapeNewOnly=False) -> dict[str, list[str]]:
  scrapeNewOnlyString = "AND scraped = 0" if scrapeNewOnly else ""
  with sqlite3.connect(DB_PATH) as conn:
      rows = conn.execute(
          f"""SELECT provider, url FROM package_urls
              WHERE type = ? AND isCatalogue = 0 {scrapeNewOnlyString}
              ORDER BY provider""",
          (hajjOrUmrahString,)
      ).fetchall()

  result = {}
  for provider, url in rows:
      result.setdefault(provider, []).append(url)

  return result