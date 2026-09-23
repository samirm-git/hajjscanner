import re

def _isKeywordExcludedRegex(keywordPattern: str):
    #kewywordPattern must be a regex string
    pattern = rf"""
\b
(
    (?:no|non|not|without|excluding|excludes?)      # negation words
    [^.!?\n]*?                                 # small gap
    {keywordPattern}
  |
    {keywordPattern}
    [^.!?\n]*?
    (?:not\s+included|not\s+provided|unavailable|excluded)
  |
    {keywordPattern}\s*[❌✗✘]                          # symbol-based negation
)
\b
"""
    return re.compile(pattern, re.IGNORECASE | re.VERBOSE)


def hasKeywordPattern(keywordPattern: str, textList: list[str]):
  excludedRegex = _isKeywordExcludedRegex(keywordPattern)
  includedRegex = re.compile(keywordPattern, re.IGNORECASE)
  match = regexSearch(excludedRegex, textList)                     #DO NOT NEED TO ITERATE AS WE ONLY CARE IF THE VALUE WAS FOUND OR NOT.
  if match:
    return False
  
  match = regexSearch(includedRegex, textList)
  if match:
    return True
  else:
    return None

def regexSearch(regex, textList):
  for text in textList:
    match = regex.search(text)
    if match:
      return match

  return None

def iterMatches(regex, textList):
    for text in textList:
        for match in regex.finditer(text):
            yield match

#FUTURE: POSSIBLE IMPROVEMENT WILL TEST LATER
# def regexSearch(regex, soup):
#     blob = "\n".join(soup.stripped_strings)
#     return regex.search(blob)

# def getCompanyNameFromUrl(baseUrl):
#   return re.search(r'(?:www\.)?([^.]+)\.', baseUrl.split('//')[-1]).group(1)