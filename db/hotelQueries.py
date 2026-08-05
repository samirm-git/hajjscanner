import sqlite3
from pathlib import Path
DB_PATH = Path(__file__).parent / 'scraper.db'

def getCityHotelNames(city) -> dict:
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT id, fullName, extraCleanedName FROM hotels WHERE city = ? ORDER BY id",
            (city,)
        ).fetchall()

    return rows

def getAllHotels() -> list:
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT id, fullName, extraCleanedName, liteCleanedName, city FROM hotels ORDER BY id"
        ).fetchall()
    return rows

def updateLiteCleanedNames(rows):
    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany(
            "UPDATE hotels SET liteCleanedName = ? WHERE id = ?",
            ((liteCleanedName, hotelId) for hotelId, liteCleanedName in rows)
        )

def updateFullNames(id, newFullName):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE hotels SET fullName = ? WHERE id = ?",
            (newFullName, id)
        )


def deleteHotels(ids):
    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany("DELETE FROM hotels WHERE id = ?", ((hotelId,) for hotelId in ids))

def addHotel(fullName, extraCleanedName, liteCleanedName, city):
    with sqlite3.connect(DB_PATH) as conn:
      cursor = conn.execute(
        "INSERT OR IGNORE INTO hotels (fullName, extraCleanedName, liteCleanedName, city) VALUES (?, ?, ?, ?)",
        (fullName, extraCleanedName, liteCleanedName, city))
    return cursor.rowcount > 0

def deleteNonEnglishHotelNames():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""DELETE FROM hotels WHERE fullName GLOB '*[ء-ي]*' AND fullName NOT GLOB '*[A-Za-z]*';""")
    return cursor.rowcount > 0
