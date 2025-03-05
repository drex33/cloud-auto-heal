import pika
import configparser
from log.deploy_queue import setup_logger

logger = setup_logger()

def main():
    config = configparser.ConfigParser()
    config.read('/app/config/auto_heal.conf')

    # RabbitMQ 서버 정보 읽기
    RABBITMQ_HOST = config.get('rabbitmq', 'rabbitmq_addr')
    RABBITMQ_USERNAME = config.get('rabbitmq', 'username')
    RABBITMQ_PASSWORD = config.get('rabbitmq', 'password')

    # RabbitMQ 연결 설정
    connection_params = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        credentials=pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
    )

    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    # Exchange, Queue 및 라우팅 키 매핑
    EXCHANGE_NAMES = {
        'cloud-auto-heal.compute': 'cloud.auto.heal.compute',
        'cloud-auto-heal.control': 'cloud.auto.heal.control'
    }

    QUEUE_NAMES = {
        'cloud-auto-heal.compute': 'cloud.auto.heal.compute',
        'cloud-auto-heal.control': 'cloud.auto.heal.control'
    }

    # Exchange 생성
    for exchange_name in EXCHANGE_NAMES:
        exchange_type = 'direct'
        channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=exchange_type,
            durable=True  # 서버 재시작 시에도 Exchange 유지
        )

    # 큐 생성 및 바인딩
    for queue_name, routing_key in QUEUE_NAMES.items():
        exchange_name = queue_name
        channel.queue_declare(
            queue=queue_name,
            durable=True
        )
        channel.queue_bind(
            exchange=exchange_name,
            queue=queue_name,
            routing_key=routing_key
        )
        logger.info(f"Queue '{queue_name}' is bound to Exchange '{exchange_name}' with routing key '{routing_key}'.")

    # 연결 종료
    connection.close()

if __name__ == "__main__":
    main()
