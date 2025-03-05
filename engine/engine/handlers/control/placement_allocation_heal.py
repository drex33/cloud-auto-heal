import requests
import json
import logging
import configparser

config = configparser.ConfigParser()
config.read('/app/config/auto_heal.conf')

# 여러 Docker API URL 설정
VIP = config.get('hosts', 'VIP')

# Placement allocation 에러 추출 데이터
exec_placement_audit = {
    "AttachStdin": True,
    "AttachStdout": True,
    "AttachStderr": True,
    "Tty": True,
    "Cmd": ["bash", "-c", "nova-manage placement audit --verbose"]
    }

        # exec 출력 데이터
exec_stdout = {
    "Detach": False,
    "Tty": True
    }

allocation_heal_data = {
    "AttachStdin": True,
    "AttachStdout": True,
    "AttachStderr": True,
    "Tty": True,
    "Cmd": ["bash", "-c", "nova-manage placement heal_allocations"]
    }

def handle_allocation_heal(logger):
    try:
        audit_response = requests.post(f'http://{VIP}:2375/containers/nova_api/exec', json=exec_placement_audit)

        if audit_response.status_code == 201:
            nova_manage_placement_audit_data = audit_response.json()
            nova_manage_placement_audit_cmd_id = nova_manage_placement_audit_data['Id']
            nova_manage_placement_audit_response = requests.post(f'http://{VIP}:2375/{nova_manage_placement_audit_cmd_id}/start', json=exec_stdout)
            if "has allocations against this compute host but is not found in the database." in nova_manage_placement_audit_response.text:
                logger.warning("Allocation issue detected: allocations exist but the entry is not found in the database.\n")
                heal_response = requests.post(f'http://{VIP}:2375/containers/nova_api/exec', json=allocation_heal_data)
                nova_manage_allocation_heal = heal_response.json()
                nova_manage_allocation_heal_cmd_id = nova_manage_allocation_heal['Id']
                allocation_heal_response = requests.post(f'http://{VIP}:2375/{nova_manage_allocation_heal_cmd_id}/start', json=exec_stdout)
                if allocation_heal_response == 200:
                    logger.info("Placement Resource Tracker Allocation heal process completed successfully\n")
                else:
                    logger.error("Something Wrong with resource tracker! Check logs.\n")
            else:
                logger.info("There is no misplaced allocations data\n")
        else:
            logger.error("Fail to call Placement exec command. Check your API request\n")

    except Exception as e:
        logger.error(f"Allocation heal failed: {str(e)}\n")