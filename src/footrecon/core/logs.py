import logging


formatter = logging.Formatter('%(levelname)s [%(asctime)s] %(message)s')
logger = logging.getLogger('footrecon')
logger.setLevel(logging.INFO)
handler = logging.FileHandler('footrecon.log')
handler.setFormatter(formatter)
logger.addHandler(handler)
