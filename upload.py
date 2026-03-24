import boto3
import re
import json
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()
s3 = boto3.client('s3')

def urlToKey(url: str) -> str:
    """
    Converts a URL into a readable S3 key using the domain as the prefix.
    e.g. "https://example.com/hajj/gold-package?year=2025"
         → "example.com/hajj_gold-package_year-2025.json"
    """
    parsed = urlparse(url)

    companyName = re.search(r'(?:www\.)?([^.]+)\.', url.split('//')[-1]).group(1)
    
    # prefix = parsed.netloc  # e.g. "example.com"

    # Build slug from path + query only
    full = parsed.path
    if parsed.query:
        full += "_" + parsed.query

    slug = re.sub(r"[^a-zA-Z0-9\-]", "_", full).strip("_")
    slug = re.sub(r"_+", "_", slug)

    # Truncate safely to avoid S3's 1024-char key limit
    max_slug_len = 1024 - len(companyName) - len(".json") - 1
    slug = slug[:max_slug_len]

    return f"{companyName}/{slug}.json"


def uploadPackageDataToS3(packageInfo, url):
  
  packageInfo = json.dumps(packageInfo, indent=4)
  try:
    response = s3.put_object(Bucket='hajjpackagedata', Key=f'raw/{urlToKey(url)}', Body=packageInfo, ContentType='application/json')
  except ClientError as e:
    print(e)

