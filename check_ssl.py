#!/usr/bin/env python3
"""检查HTTPS证书配置"""
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

# 检查证书文件
print('=== 证书文件 ===')
exit_code, out, err = run_cmd('ls -la /root/singbox-eps-node/cert/')
print(out.strip() if out else '无')

# 检查证书详情
print('\n=== 证书详情 ===')
exit_code, out, err = run_cmd('openssl x509 -in /root/singbox-eps-node/cert/fullchain.pem -text -noout 2>&1 | head -20')
print(out.strip() if out else '无')

# 检查订阅服务代码中的SSL配置
print('\n=== 订阅服务SSL配置 ===')
exit_code, out, err = run_cmd('grep -A5 "ssl_context" /root/singbox-eps-node/scripts/subscription_service.py')
print(out.strip() if out else '无')

# 检查服务启动方式
print('\n=== 服务启动方式 ===')
exit_code, out, err = run_cmd('cat /etc/systemd/system/singbox-sub.service')
print(out.strip() if out else '无')

client.close()
