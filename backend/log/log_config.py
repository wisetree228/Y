import logging

logger = logging.getLogger('main_logger')
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('my_log.log')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)