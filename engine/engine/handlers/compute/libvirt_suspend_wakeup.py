import requests
import json
import logging
import configparser

config = configparser.ConfigParser()
config.read('/app/config/auto_heal.conf')

# 여러 Docker API URL 설정
COMPUTE_HOSTS = config.get('hosts', 'compute_hosts').split(',')


exec_virsh_list = {
    "AttachStdin": True,
    "AttachStdout": True,
    "AttachStderr": True,
    "Tty": True,
    "Cmd": ["bash", "-c", "virsh list --all | grep pmsuspend"]
    }

exec_virsh_wakeup = {
        "AttachStdin": True,
    "AttachStdout": True,
    "AttachStderr": True,
    "Tty": True,
    "Cmd": ["bash", "-c", "virsh list --all | grep 'shut off' | awk '{print $2}' | xargs -I{} virsh dompmwakeup {}"]
    }

exec_stdout = {
    "Detach": False,
    "Tty": True
    }

def handle_suspend_wakeup(logger):
    try:
        for docker_host in COMPUTE_HOSTS:
            docker_host = docker_host.strip()
            virsh_list_response = requests.post(f'http://{docker_host}:2375/containers/nova_libvirt/exec', json=exec_virsh_list)
        if virsh_list_response.status_code == 201:
            nova_libvirt_virsh_list_data = virsh_list_response.json()
            nova_libvirt_virsh_list_cmd_id = nova_libvirt_virsh_list_data['Id']
            nova_libvirt_virsh_list_response = requests.post(f'http://{docker_host}:2375/{nova_libvirt_virsh_list_cmd_id}/start', json=exec_stdout)
            if "pmsuspend" in nova_libvirt_virsh_list_response.text:
                logger.warning(f"[ {docker_host} ] - Found Suspended instance\n")
                wakeup_response = requests.post(f'http://{docker_host}:2375/containers/nova_libvirt/exec', json=exec_virsh_wakeup)
                nova_libvirt_virsh_wakeup = wakeup_response.json()
                nova_libvirt_virsh_wakeup_cmd_id = nova_libvirt_virsh_wakeup['Id']
                virsh_wakeup_response = requests.post(f'http://{docker_host}:2375/{nova_libvirt_virsh_wakeup_cmd_id}/start', json=exec_stdout)
                nova_compute_restart_response = requests.post(f'http://{docker_host}:2375/containers/nova_compute/restart')
                if virsh_wakeup_response ==200 and nova_compute_restart_response == 204:
                    logger.info("Wake up Suspended instance Process completed successfully\n")
                else:
                    logger.error("Something Wrong with qemu domain! Check logs.\n")
            else:
                logger.info("There is no Suspended instance.\n")
        else:
            logger.error("Fail to call libvirt exec command. Check your API request\n")
    except Exception as e:
        logger.error(f"Wake up process failed: {str(e)}\n")