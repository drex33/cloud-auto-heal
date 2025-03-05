import requests
import json
import logging
import configparser

config = configparser.ConfigParser()
config.read('/app/config/auto_heal.conf')

# 여러 Docker API URL 설정
CONTROL_HOSTS = config.get('hosts', 'control_hosts').split(',')

########################################
# 컨테이너 헬스체크 (auto_heal_default) #
########################################
 
# 체크할 컨테이너
CONTAINERS = [
    'nova_api',
    'cinder_api',
    'placement_api',
    'cinder_volume',
    'nova_conductor',
    'nova_scheduler'
]

# 컨테이너 재시작 횟수를 저장할 딕셔너리
restart_count = {}

def handle_container_auto_heal(logger):
    for container_name in CONTAINERS:
        for docker_host in CONTROL_HOSTS:
            docker_host = docker_host.strip()
            response = requests.get(f'http://{docker_host}:2375/containers/{container_name}/json')
            
            if response.status_code == 200:
                container_info = response.json()
                container_status = container_info['State']['Status']
                container_health = container_info['State']['Health']['Status']

                if container_status == 'running' and container_health == 'healthy':
                    logger.info(f"[ {docker_host} - {container_name} ] is healthy\n")
                    restart_count[docker_host] = 0
                else:
                    if docker_host not in restart_count:
                        restart_count[docker_host] = 0

                    restart_count[docker_host] += 1

                    if restart_count[docker_host] > 3:
                        logger.error(f"[ {docker_host} - {container_name} ] has been restarted 3 times but still has issue. Check System manually\n")
                    else:
                        logger.warning(f"[ {docker_host} - {container_name} ] Something wrong! Restarting container (Attempt {restart_count[docker_host]})\n")
                        restart_response = requests.post(f'http://{docker_host}:2375/containers/{container_name}/restart')
                        if restart_response.status_code == 204:
                            logger.info(f"[ {docker_host} - {container_name} ] restarted successfully\n")
                        else:
                            logger.error(f"[ {docker_host} - {container_name} ] Failed to restart container\n")
            else:
                logger.error(f"[ {docker_host} - {container_name} ] Failed to retrieve container. Check your API request\n")

