import logging

console_level = logging.DEBUG
file_level = logging.DEBUG

logger = logging.getLogger(__name__)
logger.setLevel(file_level)
console_handler = logging.StreamHandler()
console_handler.setLevel(console_level)
console_handler.setFormatter(logging.Formatter("%(message)s"))
logger.handlers.clear()
logger.addHandler(console_handler)
