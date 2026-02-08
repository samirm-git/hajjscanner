import requests
from bs4 import BeautifulSoup

def makeRequest(url):
  headers = {
    "User-Agent": "Chrome/117.0.0.0",
    # "Referer": "https://alamanahtravel.co.uk/",
  }
  resp = requests.get(url, headers=headers)
  return resp

def getSoup(respText, parser="html.parser"):
  soup = BeautifulSoup(respText, parser)
  return soup