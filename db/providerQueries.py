import sqlite3
import json
from pathlib import Path
DB_PATH = Path(__file__).parent / 'scraper.db'


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
