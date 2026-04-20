#!/usr/bin/env python3
"""检查订阅服务生成的链接"""
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

# 检查数据库CDN IP
print('=== 数据库CDN IP ===')
exit_code, out, err = run_cmd('python3 -c "import sqlite3; conn=sqlite3.connect(\'/root/singbox-eps-node/data/singbox.db\'); c=conn.cursor(); c.execute(\'SELECT * FROM cdn_settings\'); rows=c.fetchall(); [print(f\'{r[0]}: {r[1]}\') for r in rows]; conn.close()"')
print(out.strip() if out else '空')

# 检查订阅服务生成的链接
print('\n=== 订阅服务生成的链接 ===')
exit_code, out, err = run_cmd('cd /root/singbox-eps-node && python3 -c "from scripts.subscription_service import generate_all_links; links=generate_all_links(); [print(l) for l in links]"')
print(out.strip() if out else '空')
if err:
    print(f'错误: {err[:500]}')

# 检查curl订阅
print('\n=== curl订阅测试 ===')
exit_code, out, err = run_cmd('curl -sk https://localhost:9443/sub/JP')
print(f'响应长度: {len(out)}')
print(f'响应内容: {out[:200]}')

client.close()
