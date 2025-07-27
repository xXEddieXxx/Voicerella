import logging
import sys

PRODUCTION = False

def setup_logger():
    logger = logging.getLogger("VoicerellaBot")
    if PRODUCTION:
        logger.setLevel(logging.WARNING)
    else:
        logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    if not logger.hasHandlers():
        logger.addHandler(handler)
    return logger

logger = setup_logger()
