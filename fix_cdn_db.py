#!/usr/bin/env python3
"""修复数据库路径不一致和CDN IP为空的问题"""
import paramiko
import time

SERVER_IP = '54.250.149.157'
SSH_USER = 'root'
SSH_PASS = 'oroVIG38@jh.dxclouds.com'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, 22, SSH_USER, SSH_PASS, timeout=15)

def run_cmd(client, cmd, timeout=10):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    return stdout.channel.recv_exit_status(), stdout.read().decode(), stderr.read().decode()

print('【1. 检查CDN服务日志】')
exit_code, out, err = run_cmd(client, 'journalctl -u singbox-cdn --no-pager -n 20 2>&1 | tail -20')
print(out)

print('【2. 手动运行CDN监控脚本获取IP】')
exit_code, out, err = run_cmd(client, 'cd /root/singbox-eps-node && python3 scripts/cdn_monitor.py 2>&1', timeout=30)
print(f'  {out}')

print('【3. 检查数据库中的CDN IP数据】')
exit_code, out, err = run_cmd(client, 'python3 -c "import sqlite3; conn=sqlite3.connect(\'/root/singbox-eps-node/data/singbox.db\'); cursor=conn.cursor(); cursor.execute(\'SELECT * FROM cdn_settings\'); print(cursor.fetchall()); conn.close()" 2>/dev/null || echo "无法读取数据库"')
print(f'  {out}')

print('【4. 检查订阅服务是否能读取CDN IP】')
exit_code, out, err = run_cmd(client, 'curl -sk https://127.0.0.1:6969/sub 2>/dev/null | head -c 200')
print(f'  {out if out else "无响应"}')

print('【5. 重启CDN服务】')
run_cmd(client, 'systemctl restart singbox-cdn')
time.sleep(5)

print('【6. 检查CDN服务状态】')
exit_code, out, err = run_cmd(client, 'systemctl is-active singbox-cdn')
print(f'  singbox-cdn: {out.strip()}')

client.close()
print('\n✅ 修复完成！')
