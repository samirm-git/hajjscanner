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

def removeUrl(url: str) -> bool:
  with sqlite3.connect(DB_PATH) as conn:
      cursor = conn.execute(
          "DELETE FROM package_urls WHERE url = ?", (url,)
      )
  return cursor.rowcount > 0


def getAllUrls(type: str) -> dict[str, list[str]]:
  with sqlite3.connect(DB_PATH) as conn:
      rows = conn.execute(
          """SELECT provider, url FROM package_urls
              WHERE type = ?
              ORDER BY provider""",
          (type,)
      ).fetchall()

  result = {}
  for provider, url in rows:
      result.setdefault(provider, []).append(url)

  return result