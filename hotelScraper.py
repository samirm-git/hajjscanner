import json 
from dotenv import load_dotenv
import os
from google import genai
from google.genai.types import GenerateContentConfig
from helpers import loadHotelSchema, isKeywordIncludedRegex
from gemini_helpers import *
from consts import BAD_IMAGE_RE, CITY_PATTERNS, DISTANCE_RE, TO_METRES

load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
CONTAINER_TAGS = ["div", "section", "article", "td", "tr"]
HEADING_TAGS = ["h1", "h2", "h3", "h4", "h5", "h6", "small", "strong"]


def LLMPrompter(client, containerText, hotelSchema):
  response = client.models.generate_content(
  model="gemini-2.5-flash-lite",
  contents=f"""Extract hotel information from the text below. Infer where reasonable (e.g. 'Quad'=4 beds, 'days'='nights', drive time is not walk time). Do any necessary metric conversions e.g. miles to metres. Use null if genuinely unavailable.

Text:
{containerText}
""",
  config=GenerateContentConfig(response_mime_type="application/json", response_schema=hotelSchema)
    )

  with open('gemini_output.txt','a') as f:
    f.write('\n')
    f.writelines(response.text)

  try:
    output = json.loads(response.text)
    return output
  except json.JSONDecodeError as e:
    print(f"llmOutput not valid json: {response.text}")
    print(e)
    return None

    

def scrapeHotelImages(soup):
  hotelImgs = set()
  imgs = soup.find_all("img") #I think you can add a regex expression as a another parameter to make sure the image src does not include 'placeholder'
  if not len(imgs) > 3:
    return []
  for img in imgs:
    src = (img.get("data-src") or img.get("data-original") or img.get("data-lazy") or img.get("src"))
    if not src:
      continue
    elif bool(BAD_IMAGE_RE.search(src)):
        continue
    else:
       hotelImgs.add(src)
  
  return hotelImgs

def scrapeHasWifi(soup):
  wifiRegex = isKeywordIncludedRegex("wifi")
  return soup.find(string=wifiRegex) is not None 

def scrapeHasAC(soup):
  acRegex = isKeywordIncludedRegex("ac")
  return soup.find(string=acRegex) is not None

def scrapeDistanceToHaram(soup):
  match = DISTANCE_RE.find(soup.get_text(strip=True))
  if match:
    distance = float(match.group("distance"))
    unit = match.group("unit").lower()
    if TO_METRES.get(unit, False) == False:
      print(f"ERROR: unknown unit {unit}. Acceptable units: {TO_METRES.keys()}")
    
    return distance * TO_METRES[unit]
  

def scrapeWalkToHaram(soup):
  pass

def checkCityinText(text, city):
  if CITY_PATTERNS[city].search(text):
    return True
  else:
    return False


def getChildContainerIDs(container):
  out = set()
  for descendant in container.find_all(CONTAINER_TAGS):
    out.add(id(descendant))
  
  return out


  #TODO: ADD MANUAL SCRAPPING FOR ALL OTHER FIELDS. ONLY CALL LLM IF FIELDS ARE MISSING OR TO COMPARE ANSWERS
  # print(hotelSchema)
def scrapeHotelInfo(soup, city):
  city = city.lower()
  otherCity = 'madinah' if city == 'makkah' else 'makkah'
  hotelSchema = jsonUperCaseTypes(loadHotelSchema())
  remove_property(hotelSchema, 'images')


  hotelInfo = {}
  seen = set()

  with genai.Client(api_key=GEMINI_KEY) as client:
    for container in soup.find_all(CONTAINER_TAGS):
      if id(container) in seen:
        continue

      headingText = " ".join(h.get_text(strip=True) for h in container.find_all(HEADING_TAGS))            
      if not headingText:
        seen.update(getChildContainerIDs(container))

      elif not checkCityinText(headingText, city):
        # print(f"Did not find desired city: {city}")
        seen.update(getChildContainerIDs(container))
      
      elif checkCityinText(headingText, otherCity):
        pass
        # print(f"Found other city: {otherCity}")
        
      else:
        # print(f"found container with desired city: {city}, and no other city: {otherCity} in heading text")
        seen.update(getChildContainerIDs(container)) 

        fullText = container.get_text("\n", strip=True) # Use fullText as a fall back e.g. call AI model with fullText
        
        llmOutput = LLMPrompter(client, fullText, hotelSchema)
        hotelImages = scrapeHotelImages(container)
        if llmOutput:
          hotelInfo.update(llmOutput)

        if hotelImages:   
          if hotelInfo.get('images', False):
            hotelInfo['images'].update(hotelImages)
          else:
            hotelInfo["images"] = hotelImages
    

  if hotelInfo == {}:
    return None
  if hotelInfo.get("images", False):
      hotelInfo["images"] = list(hotelInfo["images"])
  else:
      hotelInfo["images"] = None
  return hotelInfo
