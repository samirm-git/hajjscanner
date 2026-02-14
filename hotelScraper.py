import re, json 
from dotenv import load_dotenv
import os
from google import genai
from google.genai.types import GenerateContentConfig
from helpers import loadHotelSchema

load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
CONTAINER_TAGS = ["div", "section", "article", "td", "tr"]
HEADING_TAGS = ["h1", "h2", "h3", "h4", "h5", "h6", "small", "strong"]
CITY_PATTERNS = {
    "makkah": re.compile(r"\b(makkah|mecca|meccah|makah)\b", re.IGNORECASE),
    "madinah": re.compile(r"\b(madinah|medina)\b", re.IGNORECASE),
}
BAD_IMAGE = re.compile(r"(icon|place[-_]?holder)", re.IGNORECASE)
  

def jsonUperCaseTypes(obj):
  unsupported = ["$schema", "$id", "title", "uniqueItems", "minLength", "maxLength"]
  if isinstance(obj, dict):
    result = {}
    for key, value in obj.items():
      if key in unsupported:
        continue
      elif key == "type" and isinstance(value, str):
        result[key] = value.upper()
      elif key in ["$schema", "$id", "title"]:
        # Skip JSON Schema metadata
        continue
      else:
        result[key] = jsonUperCaseTypes(value)
    return result
    
  elif isinstance(obj, list):
    return [jsonUperCaseTypes(item) for item in obj]
  else:
    return obj

def LLMPrompter(containerText, hotelSchema):
  print("MADE IT TO LLM PROMPTER")
  with genai.Client(api_key=GEMINI_KEY) as client:
    response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"""You are extracting hotel information from the following website text.
Text:
  {containerText}
""",
    config=GenerateContentConfig(response_mime_type="application/json", response_schema=hotelSchema)
      )

  with open('gemini_output.txt','a') as f:
    f.write('\n')
    f.writelines(response.text)


  return response.text
    

def scrapeHotelImages(container_soup):
  hotelImgs = set()
  imgs = container_soup.find_all("img") #I think you can add a regex expression as a another parameter to make sure the image src does not include 'placeholder'
  if not len(imgs) > 3:
    return set() 
  for img in imgs:
    src = (img.get("data-src") or img.get("data-original") or img.get("data-lazy") or img.get("src"))
    if not src:
      continue
    elif bool(BAD_IMAGE.search(src)):
        continue
    else:
       hotelImgs.add(src)
  
  return hotelImgs


def checkCityInHotelText(text, desiredCity):
  otherCity = 'madinah' if desiredCity == 'makkah' else 'makkah'
  if CITY_PATTERNS[desiredCity].search(text):
    if CITY_PATTERNS[otherCity].search(text):
      return False
    else:
      return True
  else:
    return False


def scrapeHotelInformation(soup, city):
  hotelSchema = jsonUperCaseTypes(loadHotelSchema())

  cityInfo = {'images':set()}
  seen = set()

  for container in soup.find_all(CONTAINER_TAGS):
    if id(container) in seen:
      continue
    
    headingText = " ".join(h.get_text(strip=True) for h in container.find_all(HEADING_TAGS))            
    if not checkCityInHotelText(headingText, desiredCity=city.lower()):
      continue
    
    for descendant in container.find_all(CONTAINER_TAGS):
        seen.add(id(descendant))

    fullText = container.get_text(strip=True) # Use fullText as a fall back e.g. call AI model with fullText
    llmOutText = LLMPrompter(fullText, hotelSchema)
    
    if llmOutText:
      cityInfo.update(json.loads(llmOutText))
      
    cityInfo['images'].update(scrapeHotelImages(container))

  return cityInfo
