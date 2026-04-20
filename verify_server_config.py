#!/usr/bin/env python3
"""验证服务器上的实际配置"""
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

print('【1. 检查服务器上的config.py路径配置】')
exit_code, out, err = run_cmd(client, 'grep -n "BASE_DIR\|DB_FILE\|DB_PATH\|DATA_DIR" /root/singbox-eps-node/scripts/config.py')
print(out)

print('【2. 检查是否有S-UI路径引用】')
exit_code, out, err = run_cmd(client, 'grep -r "s-ui\|singbox-manager" /root/singbox-eps-node/scripts/ 2>/dev/null || echo "无S-UI路径引用"')
print(f'  {out}')

print('【3. 检查fix_脚本数量】')
exit_code, out, err = run_cmd(client, 'ls /root/singbox-eps-node/fix_*.py 2>/dev/null | wc -l')
print(f'  fix_脚本数量: {out.strip()}')

print('【4. 检查数据库表结构】')
exit_code, out, err = run_cmd(client, 'python3 -c "import sqlite3; conn=sqlite3.connect(\'/root/singbox-eps-node/data/singbox.db\'); cursor=conn.cursor(); cursor.execute(\'SELECT name FROM sqlite_master WHERE type=\\\"table\\\"\'); print(cursor.fetchall()); conn.close()"')
print(f'  数据库表: {out}')

print('【5. 检查CDN IP数据】')
exit_code, out, err = run_cmd(client, 'python3 -c "import sqlite3; conn=sqlite3.connect(\'/root/singbox-eps-node/data/singbox.db\'); cursor=conn.cursor(); cursor.execute(\'SELECT * FROM cdn_settings\'); [print(f\"  {r[0]}: {r[1]}\") for r in cursor.fetchall()]; conn.close()"')
print(out if out else '  无CDN数据')

print('【6. 检查订阅服务日志】')
exit_code, out, err = run_cmd(client, 'journalctl -u singbox-sub --no-pager -n 10 2>&1 | tail -10')
print(out)

client.close()
