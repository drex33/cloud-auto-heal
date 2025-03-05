import requests
import json
import time
import configparser
from requests.auth import HTTPBasicAuth
from log.deploy_queue import setup_logger

logger = setup_logger()

config = configparser.ConfigParser()
config.read('/app/config/auto_heal.conf')

# 여러 Docker API URL 설정
RABBITMQ_URL = config.get('rabbitmq', 'rabbitmq_addr')

# RabbitMQ 서버 정보 및 인증 정보
RABBITMQ_USERNAME = config.get('rabbitmq', 'username')
RABBITMQ_PASSWORD = config.get('rabbitmq', 'password')
AUTH = HTTPBasicAuth(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)

# 메시지 전송 데이터 설정
compute_messages = [
    {"exchange": "cloud-auto-heal.compute", "routing_key": "cloud.auto.heal.compute", "payload": "container_auto_heal"}
]

control_messages = [
    {"exchange": "cloud-auto-heal.control", "routing_key": "cloud.auto.heal.control", "payload": "container_auto_heal"}
]

def send_message(message):
    url = f"http://{RABBITMQ_URL}/api/exchanges/%2f/{message['exchange']}/publish"
    data = {
        "properties": {},
        "routing_key": message['routing_key'],
        "payload": message['payload'],
        "payload_encoding": "string"
    }
    response = requests.post(url, auth=AUTH, headers={"content-type": "application/json"}, data=json.dumps(data))
    if response.status_code == 200:
        logger.info(f"Message sent to exchange '{message['exchange']}' with routing key '{message['routing_key']}' and payload '{message['payload']}'")
    else:
        logger.error(f"Failed to send message to exchange '{message['exchange']}' with routing key '{message['routing_key']}' and payload '{message['payload']}', status code: {response.status_code}")

def main():
    while True:
        for message in compute_messages + control_messages:
            send_message(message)
        time.sleep(60)  # 1분 대기

if __name__ == "__main__":
    main()
