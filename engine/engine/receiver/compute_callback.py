from log.compute_logging import setup_logger # 'compute_.log' 파일에 로그 기록
from handlers.compute.container_auto_heal import handle_container_auto_heal
from handlers.compute.libvirt_suspend_wakeup import handle_suspend_wakeup

# 로거 설정
logger = setup_logger()

# 페이로드에 따른 핸들러 맵핑
payload_handlers = {
    "container_auto_heal": handle_container_auto_heal,
    "libvirt_suspend_wakeup": handle_suspend_wakeup,
    # 추가적인 페이로드 핸들러들을 여기에 추가
}

def compute_callback(ch, method, properties, body):
    message = body.decode()

    for payload, handler in payload_handlers.items():
        if payload in message:
            logger.info(f"{payload} payload received, invoking handler.")
            handler(logger)  # 핸들러에 로거 전달
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

    logger.info(f"No specific handler found for message: {message}")
    ch.basic_ack(delivery_tag=method.delivery_tag)