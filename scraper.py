import requests, re
from bs4 import BeautifulSoup
from hotelScraper import extractHotelInformation, HEADING_TAGS

def totalNightsExtractor(soup):
  for tag in soup.find_all(HEADING_TAGS):
    text = tag.get_text(" ", strip = True)
    match = re.search(r"(\d+)[-\s]?(?:night|day)s?", text, re.IGNORECASE)
    if match:
      return match.group(1)
  return None
    


url = "https://alamanahtravel.co.uk/14-days-5-star-non-shifting-hajj-package/"
url2 = "https://www.safamarwahtravel.co.uk/deals/5-star-17-days-non-shifting-hajj-package/"
url3 = "https://www.alhaqtravel.co.uk/book/24-days-shifting-hajj-packages/"

headers = {
    "User-Agent": "Chrome/117.0.0.0",
    # "Referer": "https://alamanahtravel.co.uk/",
}
resp = requests.get(url3, headers=headers)

soup = BeautifulSoup(resp.text, "html.parser")
visible_text = soup.get_text(" ", strip=True)
# print(soup.prettify())
# package_div = soup.find("div", class_="detail_package")
# price = package_div.find("strong").getText()
price = re.search(r"([£$€])\s?(\d+(?:,\d{3})*(?:\.\d{2})?)", visible_text, re.IGNORECASE)
price = price.group(2) if price else None


totalNights = totalNightsExtractor(soup)

nonshifting = bool(re.search(r"\bnon[-\s]?shifting\b", visible_text, re.IGNORECASE))

makkahHotel = re.search(r"(?:Makkah|Mecca|Meccah|Makah)[\s-]*(?:hotels?|Hotel)", visible_text, re.IGNORECASE)
makkahHotel = makkahHotel.groups() if makkahHotel else None
if makkahHotel is None:
  makkahHotel = re.search(r'\b([Hh]otels?\s+in\s+(?:Makkah|Mecca))\b', visible_text, re.IGNORECASE)
  makkahHotel = makkahHotel.groups() if makkahHotel else None

hotelInfo = extractHotelInformation(soup)


makkahHotel = hotelInfo["makkah"]
madinahHotel = hotelInfo["madinah"]
otherHotel = hotelInfo["other"]


print("")
print(price)
print(f"totalNights: {totalNights}")
print(nonshifting)
print(makkahHotel)

print("")
print(f"makkahHotelImages: {makkahHotel['images']}")
print("")
print(f"madinahHotelImages: {madinahHotel['images']}")
print("")
print(f"otherImages: {otherHotel['images']}")
print("")
print(f"makkah hotel info: {makkahHotel}")
print("")
print(f"madinah hotel info: {madinahHotel}")