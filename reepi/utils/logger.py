"""
Logging utilities for the REEpy package.
"""

import logging
import sys
from typing import Optional

def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Name of the logger, typically __name__
        level: Logging level (default: INFO)
        
    Returns:
        Configured logger instance
    """
    if level is None:
        level = logging.INFO
        
    logger = logging.getLogger(name)
    
    # Only configure the logger if it hasn't been configured already
    if not logger.handlers:
        logger.setLevel(level)
        
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        
        # Create formatter and add it to the handler
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
        
    return logger
