import re

def isKeywordExcludedRegex(keywordPattern):
    #kewywordPattern must be a regex string
    pattern = rf"""
\b
(
    (?:no|not|without|excluding|excludes?)      # negation words
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


def hasKeywordPattern(keywordPattern, soup):
  excludedRegex = isKeywordExcludedRegex(keywordPattern)
  includedRegex = re.compile(keywordPattern, re.IGNORECASE)
  match = regexSearch(excludedRegex, soup)
  if match:
    return False
  
  match = regexSearch(includedRegex, soup)
  if match:
    return True
  else:
    return False 

def regexSearch(regex, soup):
  for text in soup.stripped_strings:
    match = regex.search(text)
    if match:
      return match

  return None

#FUTURE: POSSIBLE IMPROVEMENT WILL TEST LATER
# def regexSearch(regex, soup):
#     blob = "\n".join(soup.stripped_strings)
#     return regex.search(blob)

def getCompanyNameFromUrl(baseUrl):
  return re.search(r'(?:www\.)?([^.]+)\.', baseUrl.split('//')[-1]).group(1)