# Logging infrastructure
from loguru import logger

logger.add('data/raw_logs/system.log', rotation='500 MB')
