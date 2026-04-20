#!/usr/bin/env python3
"""检查修复后的订阅链接"""
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

# 检查生成的Trojan链接
print('=== 生成的Trojan链接 ===')
exit_code, out, err = run_cmd('cd /root/singbox-eps-node && python3 -c "from scripts.subscription_service import generate_all_links; links=generate_all_links(); [print(l) for l in links if \'trojan\' in l.lower()]"')
print(out.strip() if out else '无')

# 对比用户提供的可用链接
print('\n=== 用户可用链接 ===')
print('trojan://uG3hixuWQUJTq6_-Qiakow@104.16.124.96:2083?security=tls&sni=jp.290372913.xyz&insecure=1&allowInsecure=1&type=ws&host=jp.290372913.xyz&path=%2Ftrojan-ws#JP-Trojan-WS-CDN')

# 检查CDN IP连通性
print('\n=== CDN IP连通性 ===')
exit_code, out, err = run_cmd('curl -sk --connect-timeout 5 https://104.16.124.96:2083/trojan-ws -H "Host: jp.290372913.xyz" -o /dev/null -w "HTTP状态: %{http_code}\\n连接时间: %{time_connect}s\\n总时间: %{time_total}s" 2>&1')
print(out.strip() if out else '无')

# 检查端口监听
print('\n=== 端口2083监听 ===')
exit_code, out, err = run_cmd('netstat -tlnp | grep 2083')
print(out.strip() if out else '无')

client.close()
