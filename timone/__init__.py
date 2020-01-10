# timone : Python package
import logging
"""Top-level package for timone."""

__author__ = """Giovanni Stracquadanio"""
__email__ = 'dr.stracquadanio@gmail.com'
__version__ = '0.3.1'

# default values
DEFAULT_ENDPOINT_URL="http://127.0.0.1:8000"
DEFAULT_STORAGE="DumbStorageDriver"
DEFAULT_OBJECT_EXPIRESIN=3600
DEFAULT_LOG_LEVEL=logging.INFO
DEFAULT_BLOCK_SIZE=1024 * 1024
DEFAULT_MAX_FILE = 1000
