#!/usr/bin/env python3
"""检查订阅服务SSL配置"""
import paramiko

SERVER_IP = '54.250.149.157'
SSH_USER = 'root'
SSH_PASS = 'oroVIG38@jh.dxclouds.com'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, 22, SSH_USER, SSH_PASS, timeout=15)

def run_cmd(cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    return stdout.channel.recv_exit_status(), stdout.read().decode(), stderr.read().decode()

# 检查订阅服务代码末尾
print('=== 订阅服务启动代码 ===')
exit_code, out, err = run_cmd('tail -30 /root/singbox-eps-node/scripts/subscription_service.py')
print(out.strip() if out else '无')

# 检查是否有SSL配置
print('\n=== SSL相关代码 ===')
exit_code, out, err = run_cmd('grep -n "ssl\\|SSL\\|cert\\|key\\|https" /root/singbox-eps-node/scripts/subscription_service.py')
print(out.strip() if out else '无')

client.close()
