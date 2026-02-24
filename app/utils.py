"""
Utility functions for FinGuard API
"""

import base64
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Setup and configure logger for the application"""
    logger = logging.getLogger(name)
    
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    
    return logger


def encode_file_to_base64(file_bytes: bytes) -> str:
    """Convert file bytes to base64 encoded string"""
    return base64.b64encode(file_bytes).decode('utf-8')


def parse_metadata(metadata_str: Optional[str]) -> Dict[str, Any]:
    """Parse metadata JSON string to dictionary"""
    try:
        return json.loads(metadata_str) if metadata_str else {}
    except json.JSONDecodeError:
        return {}


def get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()


def prepare_media_metadata(filename: str, extra_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Prepare metadata dictionary for media files"""
    meta = {"filename": filename}
    if extra_metadata:
        meta.update(extra_metadata)
    return meta
