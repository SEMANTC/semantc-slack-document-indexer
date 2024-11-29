# app/utils/logger.py

import logging
import sys
from typing import Optional

def setup_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """SETUP LOGGER WITH STANDARD FORMAT"""
    logger = logging.getLogger(name)
    
    if level:
        logger.setLevel(level)
    else:
        logger.setLevel(logging.INFO)

    # create handler if none exists
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
        logger.addHandler(handler)
    
    return logger