import re, json, sys
from dotenv import load_dotenv
from helpers import makeRequest, getSoup, removeFooterHeaderNav, loadHajjPackageSchema
from hotelScraper import scrapeHotelInformation, HEADING_TAGS 
from validator import validateData
from upload import uploadPackageDataToS3

load_dotenv()
def scrapeTotalDays(soup):
  for tag in soup.find_all(HEADING_TAGS):
    text = tag.get_text(strip = True)
    match = re.search(r"(\d+)[-\s]?(?:night|day)s?", text, re.IGNORECASE)
    if match:
      return int(match.group(1))
  return None

def scrapeCompanyFromUrl(url):
  match = re.search(r'(?:www\.)?([^.]+)\.', url.split('//')[-1])
  return match.group(1) if match else ''

def scrapePPP(soup): 
  priceRegex = re.compile(r"([£$€])\s?(\d+(?:,\d{3})*(?:\.\d{2})?)", re.IGNORECASE)
  #can do re.search(r"...", soup.get_text(strip=True)) for faster searching (not sure how much faster)
  #but then we would not know which container the matching text comes from which may be useful e.g. finding the parent container for more context (although not doing this currently).
  #moreover, with soup.find(...) we can filter the containers we are searching through e.g heading [h1, h2, ..., h6] containers.
  priceContainer = soup.find(string=priceRegex)
  if priceContainer:
    match = priceRegex.match(priceContainer.get_text(strip=True))
    currency = match.group(1)
    #TODO: CONVERT CURRENCY TO STANDARD CURRENCY PRICE TO STANDARD CURRENCY E.G £
    price = match.group(2)
    price = price.replace(",", '').strip()
    return int(price)
  else:
    return None

def scrapeTier(soup):
  tierRegex = re.compile(r"luxury|premium|economy", re.IGNORECASE)
  tierContainer = soup.find(string=tierRegex)
  if tierContainer:
    return tierRegex.search(tierContainer.get_text(strip=True)).group(1)
  else: 
    return None

def scrapeStars(soup):
  starsRegex = re.compile(r'\b([1-5])\s*(?:-?\s*star|stars?)\b', re.IGNORECASE)
  starContainer = soup.find(string=starsRegex)
  if starContainer:
    return int(starsRegex.search(starContainer.get_text(strip=True)).group(1))
  return None

def scrapeIsShifting(soup):
  nonshifting = bool(re.search(r"\bnon[-\s]?shifting\b", soup.get_text(strip=True), re.IGNORECASE))  
  if nonshifting:
    return False
  else:
    return True

def scrapeIsVisaIncluded(soup):
  isVisaIncludedRegex = re.compile(r'\b(?:visa|visas?)\s+(?:is\s+)?(?:included|covered|provided|arranged|taken\s+care\s+of)\b|\b(?:includes?|with|including)\s+(?:visa|visas?)\b', re.IGNORECASE)
  isVisaIncluded = bool(isVisaIncludedRegex.search(soup.get_text(strip=True)))
  if isVisaIncluded:
    return True
  else:
    visaRegex = re.compile('visa', re.IGNORECASE)
    visaContainer = soup.find(string=visaRegex)
    if not visaContainer:
      return False
    else:
      #REQUIRES FURTHER ANALYSIS. MAYBE PASS THE PARENT DIV TO LLM
      return None
  

def scrapePackageInfo(url):
  packageInfoResolvers = {
    'ppp': scrapePPP,
    'total_days': scrapeTotalDays,
    # 'tier': scrapeTier,
    'stars': scrapeStars,
    'isShifting': scrapeIsShifting,
    'makkahHotel': scrapeHotelInformation,
    'madinahHotel': scrapeHotelInformation,
    'isVisaIncluded': scrapeIsVisaIncluded
  }
  packageInfo = {'url':url}


  resp = makeRequest(url)
  soup = getSoup(resp.text, parser="lxml")
  soup = removeFooterHeaderNav(soup)
  if soup.find("main"):
    soup = soup.find("main")

  nLinks = len(soup.find_all("a", href=True))
  if nLinks > 10:
    #IF MORE THAN 10 LINKS IT IS LIKELY TO BE A CATALOGUE PAGE NOT A PACKAGE DETAILS PAGE
    #TODO: HANDLE CATALOGUE PAGE TO FIND PACKAGE DETAILS PAGES
    return 

  packageInfo['company'] = scrapeCompanyFromUrl(url)
  for key in packageInfoResolvers.keys():
    if packageInfo.get(key, False):
      continue

    if key == 'makkahHotel':
      packageInfo[key] = packageInfoResolvers[key](soup, 'makkah')
    elif key == 'madinahHotel':
      packageInfo[key] = packageInfoResolvers[key](soup, 'madinah')
    else:
      packageInfo[key] = packageInfoResolvers[key](soup)
    

  # fname = url[8:-1].replace("/","").replace("\\","")
  # with open(f'scraperOutputs/{fname}.txt','a') as f:
  #   f.write("=====================================")
  #   json.dump(packageInfo, f, indent=4)
  #   f.write('\n')

  validateData(packageInfo)
  return packageInfo

if __name__ == "__main__":
  url = "https://alamanahtravel.co.uk/14-days-5-star-non-shifting-hajj-package/"
  url2 = "https://www.safamarwahtravel.co.uk/deals/5-star-17-days-non-shifting-hajj-package/"
  url3 = "https://www.alhaqtravel.co.uk/book/24-days-shifting-hajj-packages/"
  url4 = "https://duatravels.co.uk/package/shifting-luxury-hajj-package/"

  urls = [url, url2, url3, url4]
  if len(sys.argv) >= 2:
    userChosenUrl = int(sys.argv[1])
  else:
    userChosenUrl = 2

  temp = {
    "ppp": 7360,
    "total_days": 24,
    "stars": 3,
    "isshifting": True,
    "makkahhotel": {
        "nights": None,
        "name": "emaar grand hotel",
        "stars": 3,
        "hasfreewifi": True,
        "hasac": True,
        "otheramenities": "flat-screen tvs, private bathrooms, city views, 24-hour front desk, concierge service, daily housekeeping, room service, on-site restaurant serving international and local cuisines.",
        "distancetoharam": 700,
        "walktoharam": None,
        "numberofbeds": None,
        "images": [
            "https://www.alhaqtravel.co.uk/media/hotels/573185498.jpg",
            "https://www.alhaqtravel.co.uk/media/hotels/573185759.jpg",
            "https://www.alhaqtravel.co.uk/media/hotels/520998869.jpg",
            "https://www.alhaqtravel.co.uk/media/hotels/520998888.jpg",
            "https://www.alhaqtravel.co.uk/media/hotels/573185529.jpg",
            "https://www.alhaqtravel.co.uk/media/hotels/573185497.jpg",
            "https://www.alhaqtravel.co.uk/media/hotels/573186443.jpg",
            "https://www.alhaqtravel.co.uk/media/hotels/573185445.jpg",
            "https://www.alhaqtravel.co.uk/media/hotels/573186350.jpg",
            "https://www.alhaqtravel.co.uk/media/hotels/520999850.jpg",
            "https://www.alhaqtravel.co.uk/media/hotels/573185502.jpg",
            "https://www.alhaqtravel.co.uk/media/hotels/573185400.jpg",
            "https://www.alhaqtravel.co.uk/media/hotels/573186596.jpg",
            "https://www.alhaqtravel.co.uk/media/hotels/573185526.jpg"
        ]
    },
    "madinahhotel": {
        "nights": None,
        "name": "al rawda al aqeeq hotel",
        "stars": None,
        "hasfreewifi": True,
        "hasac": None,
        "otheramenities": "laundry service, room service, dry cleaning, luggage storage, safety deposit boxes, designated smoking area, daily housekeeping",
        "distancetoharam": 600,
        "walktoharam": 8,
        "numberofbeds": None,
        "images": [
            "https://www.alhaqtravel.co.uk/media/hotels/al_rawda_al_aqeeq_hotel_dining_area.jpg",
            "https://www.alhaqtravel.co.uk/media/hotels/al_rawda_al_aqeeq_hotel_dining_table.jpg",
            "https://www.alhaqtravel.co.uk/media/hotels/al_rawda_al_aqeeq_hotel_room.jpg",
            "https://www.alhaqtravel.co.uk/media/hotels/al_rawda_al_aqeeq_hotel.jpg",
            "https://www.alhaqtravel.co.uk/media/hotels/al_rawda_al_aqeeq_hotel_kitchen.jpg",
            "https://www.alhaqtravel.co.uk/media/hotels/al_rawda_al_aqeeq_hotel_counter.jpg",
            "https://www.alhaqtravel.co.uk/media/hotels/al_rawda_al_aqeeq_hotel_bedroom.jpg",
            "https://www.alhaqtravel.co.uk/media/hotels/al_rawda_al_aqeeq_hotel_hall.jpg",
            "https://www.alhaqtravel.co.uk/media/hotels/al_rawda_al_aqeeq_hotel_bathroom.jpg",
            "https://www.alhaqtravel.co.uk/media/hotels/al_rawda_al_aqeeq_hotel_food.jpg"
        ]
    },
    "isvisaincluded": None
} 
  
  # temp2 = json.dumps(temp, indent=4)
  # uploadPackageDataToS3(temp2, 'alhaqtravel') 
  packageInfo = scrapePackageInfo(urls[userChosenUrl]) 
  uploadPackageDataToS3(packageInfo, packageInfo["company"])




  #==========================================
  # tempScraper(visible_text)
  #==========================================


  # print(soup.prettify())
  # package_div = soup.find("div", class_="detail_package")
  # price = package_div.find("strong").getText()
