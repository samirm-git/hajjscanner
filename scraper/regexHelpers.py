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


def hasKeywordPattern(keywordPattern, text):
  if isKeywordExcludedRegex(keywordPattern).search(text):
    return False
  elif re.search(keywordPattern, text, re.IGNORECASE):
    return True
  else:
    return False 