import pika
import logging
from log.queue_logging import setup_logger # 'control_log.log' 파일에 로그 기록
from receiver.compute_callback import compute_callback  # 컴퓨트 처리 콜백 함수
from receiver.control_callback import control_callback  # 컨트롤 처리 콜백 함수
import configparser

# 로거 설정
logger = setup_logger()

config = configparser.ConfigParser()
config.read('/app/config/auto_heal.conf')

# 여러 Docker API URL 설정
RABBITMQ_HOST = config.get('rabbitmq', 'rabbitmq_addr')
RABBITMQ_USERNAME = config.get('rabbitmq', 'username')
RABBITMQ_PASSWORD = config.get('rabbitmq', 'password')
AUTH = (RABBITMQ_USERNAME, RABBITMQ_PASSWORD)

QUEUE_NAMES = {
    'cloud-auto-heal.compute': compute_callback,
    'cloud-auto-heal.control': control_callback
}

def callback_wrapper(queue_name, ch, method, properties, body):
    # 메시지 수신 및 디코딩
    decoded_body = body.decode('utf-8')
    logger.info(f" [x] Received message from {queue_name} queue - [ payload : {decoded_body} ]")
    # 해당 큐에 맞는 콜백 함수 호출
    QUEUE_NAMES[queue_name](ch, method, properties, body)

def main():
    # RabbitMQ에 연결
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        credentials=pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
    ))
    channel = connection.channel()

    # 각 큐에 대해 소비자 설정
    for queue_name in QUEUE_NAMES:
        # 큐에 대한 소비자 설정
        channel.basic_consume(queue=queue_name, on_message_callback=lambda ch, method, properties, body, qn=queue_name: callback_wrapper(qn, ch, method, properties, body), auto_ack=False)

    logger.info(' [*] Waiting for messages.')
    channel.start_consuming()

if __name__ == "__main__":
    main()