#!/usr/bin/env python3
"""检查服务器配置"""
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

print('=== .env内容 ===')
exit_code, out, err = run_cmd('cat /root/singbox-eps-node/.env')
print(out.strip() if out else '无')

print('\n=== 数据库CDN IP ===')
exit_code, out, err = run_cmd('python3 /root/singbox-eps-node/scripts/check_db.py 2>/dev/null || echo 无脚本')
print(out.strip() if out else '无')

print('\n=== 订阅服务日志 ===')
exit_code, out, err = run_cmd('journalctl -u singbox-sub --no-pager -n 50 2>/dev/null | tail -30')
print(out.strip() if out else '无')

client.close()
