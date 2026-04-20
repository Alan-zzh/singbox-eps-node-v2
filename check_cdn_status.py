#!/usr/bin/env python3
"""查看CDN状态"""
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

print('【数据库中的优选IP】')
exit_code, out, err = run_cmd(client, 'sqlite3 /root/singbox-eps-node/data/singbox.db "SELECT * FROM cdn_settings;"')
print(out.strip() if out else '无数据')

print('\n【CDN监控最新日志】')
exit_code, out, err = run_cmd(client, 'tail -20 /root/singbox-eps-node/logs/cdn_monitor.log 2>/dev/null || journalctl -u singbox-cdn --no-pager -n 10')
print(out.strip()[-1000:] if out else '无日志')

client.close()
