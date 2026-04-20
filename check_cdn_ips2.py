#!/usr/bin/env python3
"""检查当前CDN优选IP和DNS解析情况"""
import paramiko

SERVER_IP = '54.250.149.157'
SSH_USER = 'root'
SSH_PASS = 'oroVIG38@jh.dxclouds.com'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, 22, SSH_USER, SSH_PASS, timeout=15)

def run_cmd(client, cmd, timeout=15):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    return stdout.channel.recv_exit_status(), stdout.read().decode(), stderr.read().decode()

print('【1. 当前数据库中的优选IP】')
exit_code, out, err = run_cmd(client, 'sqlite3 /root/singbox-eps-node/data/singbox.db "SELECT * FROM cdn_settings;"')
print(out.strip() if out else '无数据')

print('\n【2. 当前CDN监控日志】')
exit_code, out, err = run_cmd(client, 'journalctl -u singbox-cdn --no-pager -n 15')
print(out.strip()[-1000:] if out else '无日志')

print('\n【3. 测试之前优选IP的延迟】')
ips = ['172.64.33.166', '162.159.45.15', '108.162.198.145']
for ip in ips:
    exit_code, out, err = run_cmd(client, f'ping -c 1 -W 2 {ip} 2>&1 | grep "time="')
    print(f'{ip}: {out.strip() if out else "超时"}')

print('\n【4. 测试当前优选IP的延迟】')
current_ips = ['104.21.35.190', '172.67.178.214']
for ip in current_ips:
    exit_code, out, err = run_cmd(client, f'ping -c 1 -W 2 {ip} 2>&1 | grep "time="')
    print(f'{ip}: {out.strip() if out else "超时"}')

print('\n【5. 测试DNS解析】')
exit_code, out, err = run_cmd(client, 'dig +short jp.290372913.xyz @222.246.129.80 +time=3')
print(f'湖南电信DNS: {out.strip() if out else "无响应"}')

client.close()
