import publisher.default_health_check
import publisher.handler_call
import publisher.declare

def main():
    # 각 모듈의 메인 함수 또는 실행할 코드를 호출
    publisher.declare.main()
    publisher.default_health_check.main()
    publisher.handler_call.main()

if __name__ == "__main__":
    main()