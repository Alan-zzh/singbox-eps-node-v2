#!/usr/bin/env python3
"""检查订阅服务响应"""
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

# 检查curl订阅（带详细输出）
print('=== curl订阅测试（详细） ===')
exit_code, out, err = run_cmd('curl -vsk https://localhost:9443/sub/JP 2>&1')
print(out[-1000:] if len(out) > 1000 else out)

# 检查HTTP订阅
print('\n=== HTTP订阅测试 ===')
exit_code, out, err = run_cmd('curl -s http://localhost:9443/sub/JP')
print(f'HTTP响应长度: {len(out)}')
print(f'HTTP响应内容: {out[:500]}')

# 检查sing-box JSON
print('\n=== sing-box JSON测试 ===')
exit_code, out, err = run_cmd('curl -sk https://localhost:9443/singbox/JP | head -20')
print(out.strip() if out else '空')

client.close()
