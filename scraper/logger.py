import logging
from logging.handlers import TimedRotatingFileHandler
from tqdm import tqdm
from scraper.helpers import getProjectRoot


class TqdmLoggingHandler(logging.Handler):
    """Routes log records through tqdm.write so they don't break progress bars."""
    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.write(msg)
        except Exception:
            self.handleError(record)

_FORMATTER = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
_CONSOLE_HANDLER = TqdmLoggingHandler()
_CONSOLE_HANDLER.setLevel(logging.WARNING)
_CONSOLE_HANDLER.setFormatter(_FORMATTER)


def getCategoryLogger(category):
  """
  Returns a logger dedicated to one failure category, writing to logs/{category}.log. Rotated daily.
  """
  logger = logging.getLogger(f"scraper.{category}")
  if logger.handlers:
      return logger

  logger.setLevel(logging.DEBUG)  # let the logger pass everything; handler decides what's written
  logger.propagate = False  # don't bubble up to root logger / duplicate output

  log_dir = getProjectRoot() / "logs"
  log_dir.mkdir(parents=True, exist_ok=True)

  file_handler = TimedRotatingFileHandler(
      log_dir / f"{category}.log", when="midnight", backupCount=14
  )
  file_handler.setLevel(logging.WARNING)
  file_handler.setFormatter(_FORMATTER)
  logger.addHandler(file_handler)

  logger.addHandler(_CONSOLE_HANDLER)  # shared console handler for live feedback

  return logger