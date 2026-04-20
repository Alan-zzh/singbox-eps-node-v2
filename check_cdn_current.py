#!/usr/bin/env python3
"""查看服务器上的CDN监控脚本当前内容"""
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

print('【查看CDN监控脚本当前内容】')
exit_code, out, err = run_cmd(client, 'cat /root/singbox-eps-node/scripts/cdn_monitor.py')
print(out.strip() if out else '无')

client.close()
