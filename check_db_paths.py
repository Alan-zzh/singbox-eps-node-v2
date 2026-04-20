#!/usr/bin/env python3
"""检查数据库路径和SUB_TOKEN配置"""
import paramiko

SERVER_IP = '54.250.149.157'
SSH_USER = 'root'
SSH_PASS = 'oroVIG38@jh.dxclouds.com'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, 22, SSH_USER, SSH_PASS, timeout=15)

def run_cmd(client, cmd, timeout=10):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    return stdout.channel.recv_exit_status(), stdout.read().decode(), stderr.read().decode()

print('【1. 检查.env文件中的SUB_TOKEN】')
exit_code, out, err = run_cmd(client, 'grep SUB_TOKEN /root/singbox-eps-node/.env 2>/dev/null || echo "未找到SUB_TOKEN"')
print(f'  {out.strip()}')

print('\n【2. 检查config.py中的数据库路径】')
exit_code, out, err = run_cmd(client, 'grep -n "DB_FILE\|DB_PATH\|DATA_DIR\|BASE_DIR" /root/singbox-eps-node/scripts/config.py')
print(f'  {out}')

print('\n【3. 检查cdn_monitor.py中的数据库路径】')
exit_code, out, err = run_cmd(client, 'grep -n "DB_FILE\|DB_PATH\|DATA_DIR\|singbox.db" /root/singbox-eps-node/scripts/cdn_monitor.py | head -10')
print(f'  {out}')

print('\n【4. 检查subscription_service.py中的数据库路径】')
exit_code, out, err = run_cmd(client, 'grep -n "DB_FILE\|DB_PATH\|DATA_DIR\|singbox.db" /root/singbox-eps-node/scripts/subscription_service.py | head -10')
print(f'  {out}')

print('\n【5. 检查数据库文件是否存在】')
exit_code, out, err = run_cmd(client, 'find /root -name "singbox.db" 2>/dev/null || echo "未找到singbox.db"')
print(f'  {out}')

print('\n【6. 检查数据库中的CDN IP数据】')
exit_code, out, err = run_cmd(client, 'python3 -c "import sqlite3; conn=sqlite3.connect(\'/root/singbox-eps-node/data/singbox.db\'); cursor=conn.cursor(); cursor.execute(\'SELECT * FROM cdn_settings\'); print(cursor.fetchall()); conn.close()" 2>/dev/null || echo "无法读取数据库"')
print(f'  {out}')

print('\n【7. 检查systemd服务文件中的路径】')
exit_code, out, err = run_cmd(client, 'cat /etc/systemd/system/singbox-sub.service 2>/dev/null || echo "未找到服务文件"')
print(f'  {out}')

print('\n【8. 检查CDN服务文件中的路径】')
exit_code, out, err = run_cmd(client, 'cat /etc/systemd/system/singbox-cdn.service 2>/dev/null || echo "未找到服务文件"')
print(f'  {out}')

client.close()
