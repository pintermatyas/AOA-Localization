import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.getLevelName('INFO'))
log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s [%(threadName)s] ")
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)
fh = logging.FileHandler(os.path.dirname(os.path.abspath(__file__)) + '/logs/output.log', mode='w')
fh.setLevel(logging.getLevelName('DEBUG'))
fh.setFormatter(log_formatter)
logger.addHandler(fh)

def get_logger():
    return logger