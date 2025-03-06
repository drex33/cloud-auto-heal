# Cloud Auto Healing

VD-i 인프라 장애상황에 대응하기 위해 개발함

24/08/27 도커 컨테이너 테스트완료\
24/08/28 main branch deploy

---
ver 0.1 
```
VD에 영향있는 컨테이너 헬스체크 및 자동 재기동 스크립트 개발
```


---
ver 1.0
```
컴퓨트 서버 및 컨트롤서버 콜백함수 등록위해 (큐 분리)
rabbitMQ 수신부 모듈 분리
```


---
ver 1.1
```
Placement allocation, Libvirt suspended 케이스 모듈 개발
로깅 모듈 분리
```

---
ver 1.2 (최신)
```
헬스체크 및 각 케이스에 따라 분리되는 핸들러 모듈, 컨픽값 분리
도커 컨테이너 빌드
```

## Flow Chart

![image](https://github.com/user-attachments/assets/9746d6e7-a8b0-4b8c-90ac-85e833d04b17)


### 각 컨테이너 서비스 동작서버
container-auto-heal-monitor - 배포서버 (Deploy)\
container-auto-heal-engine - 컨트롤러 (Control)


## 작동 방식


##### 1. Msg Publish
배포서버에서 동작하는 모니터에서 미리 정의해둔 Queue,Routing Key를 들고 Exchange 에 특정 페이로드를 포함한 메시지를 발행한다.

컨테이너 헬스체크 및 모니터링을 위해 주기적으로 메시지를 발행하게 설정되있다. 
<br/><br/>
##### 2. Queue Receive & Delivery
RabbitMQ 에서 큐를 수신하고, 엔진은 큐이름을 보고 Callback 함수로 큐를 전달한다.
<br/><br/>
##### 3. Queue Decoding & Dedicate Handler
전달받은 큐를 디코딩하여 페이로드를 확인하고 페이로드별로 지정된 핸들러가 동작하게된다.
<br/><br/>
예를 들어, cloud-auto-heal.control 큐의 페이로드가 container_auto_heal 이면 컨테이너 헬스체크 및 Revive 핸들러가 작동하게된다.
<br/><br/>
##### 4. Execute Handler
핸들러는 등록된 메인함수를 동작하는데, Docker API 를 통해 실행된다. (Port : 2375)
<br/><br/>
## 3. 배포 및 실행 방법


### 1. docker build ~ 수동 설치
```
# monitor 서비스 컨테이너 빌드
cd container-auto-healing/monitor
docker build -f Dockerfile.monitor -t cloud-auto-heal-monitor --network=host .

# engine 서비스 컨테이너 빌드
cd container-auto-healing/engine
docker build -f Dockerfile.engine -t cloud-auto-heal-engine --network=host .

# Docker API CALL Setting - Control, Compute 서버에 적용
# dir = /lib/systemd/system/docker.service
-H unix:///var/run/docker.sock -H 0.0.0.0:2375 - ExecStart 에 추가
systemctl daemon-reload
systemctl restart docker

# Rabbitmq Mangement Plugin enable - Contorl 서버 적용
docker exec rabbitmq rabbitmq-plugins enable rabbitmq_management

# conf 파일 발급위하여 일회성 실행
docker run --rm -d --net=host cloud-auto-heal-engine
docker run --rm -d --net=host cloud-auto-heal-monitor

# 로컬에 생성된 conf 파일 수정 및 docker-compose
# /etc/auto_heal.conf
docker-compose up -d
```

### 2. 도커이미지 등록 후 배포
```
# mercy-monitor.tar - 모니터
# mercy-engine.tar - 엔진

docker load -i mercy-monitor.tar
docker load -i mercy-engine.tar

# conf 파일 발급위하여 일회성 실행
docker run --rm -d --net=host cloud-auto-heal-engine
docker run --rm -d --net=host cloud-auto-heal-monitor

# Docker API CALL Setting - Control, Compute 서버에 적용
# dir = /lib/systemd/system/docker.service
-H unix:///var/run/docker.sock -H 0.0.0.0:2375 - ExecStart 에 추가
systemctl daemon-reload
systemctl restart docker

# Rabbitmq Mangement Plugin enable - Contorl 서버 적용
docker exec rabbitmq rabbitmq-plugins enable rabbitmq_management

# 로컬에 생성된 conf 파일 수정 및 docker-compose
# /etc/auto_heal.conf
docker-compose up -d
```

### 3. 앤서블 이용한 자동 배포
```
추후 개발예정
```
