#!/usr/bin/env python3
"""检查singbox路由配置"""
import paramiko

SERVER_IP = '54.250.149.157'
SSH_USER = 'root'
SSH_PASS = 'oroVIG38@jh.dxclouds.com'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, 22, SSH_USER, SSH_PASS, timeout=15)

def run_cmd(client, cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    return stdout.channel.recv_exit_status(), stdout.read().decode(), stderr.read().decode()

print('【1. 查看singbox路由规则】')
exit_code, out, err = run_cmd(client, 'cat /root/singbox-eps-node/config.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d.get(\'route\',{}), indent=2, ensure_ascii=False))"')
print(out.strip() if out else '无')

print('\n【2. 查看outbounds配置】')
exit_code, out, err = run_cmd(client, 'cat /root/singbox-eps-node/config.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d.get(\'outbounds\',[]), indent=2, ensure_ascii=False))"')
print(out.strip() if out else '无')

client.close()
