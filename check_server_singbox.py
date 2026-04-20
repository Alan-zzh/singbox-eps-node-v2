#!/usr/bin/env python3
"""检查服务器singbox配置"""
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

# 检查singbox配置中的Trojan-WS入站
print('=== singbox配置（Trojan相关） ===')
exit_code, out, err = run_cmd('cat /root/singbox-eps-node/config.json | python3 -m json.tool | grep -A20 -i trojan')
print(out.strip() if out else '无')

# 检查端口监听
print('\n=== 端口监听状态 ===')
exit_code, out, err = run_cmd('netstat -tlnp | grep -E "2083|8443|443|2053"')
print(out.strip() if out else '无')

# 检查singbox服务状态
print('\n=== singbox服务状态 ===')
exit_code, out, err = run_cmd('systemctl status singbox 2>&1 | head -15')
print(out.strip() if out else '无')

# 测试CDN IP连通性
print('\n=== CDN IP连通性测试 ===')
exit_code, out, err = run_cmd('ping -c 3 104.16.124.96')
print(out.strip() if out else '无')

# 测试端口连通性
print('\n=== 端口2083连通性测试 ===')
exit_code, out, err = run_cmd('timeout 5 bash -c "echo > /dev/tcp/104.16.124.96/2083" && echo "端口开放" || echo "端口不通"')
print(out.strip() if out else '无')

client.close()
