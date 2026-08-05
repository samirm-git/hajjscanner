from .scrapePage import scrapePage as scrape
from .checkCataloguePage import isCataloguePage
from .uploadS3 import uploadPackageDataToS3
__all__ = ['scrape', 'isCataloguePage', 'uploadPackageDataToS3']