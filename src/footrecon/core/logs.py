import logging


formatter = logging.Formatter('%(levelname)s [%(asctime)s] %(message)s')
logger = logging.getLogger('footrecon')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('footrecon.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
