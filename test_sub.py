#!/usr/bin/env python3
"""测试sing-box JSON路由规则"""
import paramiko
import json

SERVER_IP = '54.250.149.157'
SSH_USER = 'root'
SSH_PASS = 'oroVIG38@jh.dxclouds.com'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, 22, SSH_USER, SSH_PASS, timeout=15)

def run_cmd(client, cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    return stdout.channel.recv_exit_status(), stdout.read().decode(), stderr.read().decode()

print('【检查订阅服务日志】')
exit_code, out, err = run_cmd(client, 'journalctl -u singbox-sub --no-pager -n 20')
print(out.strip()[-1000:] if out else '无')

print('\n【直接访问订阅页面】')
exit_code, out, err = run_cmd(client, 'curl -sk https://localhost:9443/ 2>&1 | head -20')
print(out.strip() if out else '无')

print('\n【检查端口9443监听】')
exit_code, out, err = run_cmd(client, 'netstat -tlnp | grep 9443')
print(out.strip() if out else '无')

client.close()
