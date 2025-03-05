import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(log_file='/var/log/deploy_queue.log'):
    # 디렉토리가 존재하지 않으면 생성
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    logger = logging.getLogger('deploy_logger')
    logger.setLevel(logging.INFO)

    if not logger.hasHandlers():
        handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=5*1024*1024,  # 최대 파일 크기 5MB
            backupCount=5  # 백업할 파일 개수
        )

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger