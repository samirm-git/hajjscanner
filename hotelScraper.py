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
    "madinah": re.compile(r"\b(madinah|medina|medinah|madina)\b", re.IGNORECASE),
}
BAD_IMAGE = re.compile(r"(icon|place[-_]?holder)", re.IGNORECASE)
  

def jsonUperCaseTypes(obj):
  unsupported = ["$schema", "$id", "title", "uniqueItems", "minLength", "maxLength"]
  if isinstance(obj, dict):
    result = {}
    for key, value in obj.items():
      if key in unsupported:
        continue
      elif key == "type":
        if isinstance(value, str):
          result[key] = value.upper()
        elif isinstance(value, list):
          assert len(value) == 2, "must only be max 2 types. The second type should be null"
          assert value[1] == "null", "must only be max 2 types. The second type should be null"
          result[key] = value[0].upper()
          result['nullable'] = True
        
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

def remove_property(schema: dict, propName: str) -> None:
  schema.get("properties", {}).pop(propName, None)
  if "required" in schema:
      while propName in schema["required"]:
          schema["required"].remove(propName)

def LLMPrompter(client, containerText, hotelSchema):
  response = client.models.generate_content(
  model="gemini-2.5-flash",
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

    

def scrapeHotelImages(container_soup):
  hotelImgs = set()
  imgs = container_soup.find_all("img") #I think you can add a regex expression as a another parameter to make sure the image src does not include 'placeholder'
  if not len(imgs) > 3:
    return []
  for img in imgs:
    src = (img.get("data-src") or img.get("data-original") or img.get("data-lazy") or img.get("src"))
    if not src:
      continue
    elif bool(BAD_IMAGE.search(src)):
        continue
    else:
       hotelImgs.add(src)
  
  return hotelImgs


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
def scrapeHotelInformation(soup, city):
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
