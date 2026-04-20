#!/usr/bin/env python3
"""检查外部订阅访问"""
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

print('【1. 检查域名解析】')
exit_code, out, err = run_cmd(client, 'nslookup jp.290372913.xyz 2>/dev/null || echo "nslookup不可用"')
print(out)

print('【2. 检查Cloudflare代理状态】')
exit_code, out, err = run_cmd(client, 'curl -sI https://jp.290372913.xyz 2>/dev/null | head -5')
print(out if out else '无法访问域名')

print('【3. 检查端口6969外部可达性】')
exit_code, out, err = run_cmd(client, 'curl -sk --connect-timeout 5 https://54.250.149.157:6969/sub -o /dev/null -w "HTTP状态码: %{http_code}\\n" 2>&1')
print(f'  直接IP访问: {out}')

print('【4. 检查域名+端口访问】')
exit_code, out, err = run_cmd(client, 'curl -sk --connect-timeout 5 https://jp.290372913.xyz:6969/sub -o /dev/null -w "HTTP状态码: %{http_code}\\n" 2>&1')
print(f'  域名访问: {out}')

print('【5. 检查当前订阅链接格式】')
print('  正确的订阅链接应该是:')
print(f'  HTTPS: https://54.250.149.157:6969/sub')
print(f'  HTTPS: https://jp.290372913.xyz:6969/sub (如果域名解析正确)')

print('\n【6. 获取完整订阅内容验证】')
exit_code, out, err = run_cmd(client, 'curl -sk https://127.0.0.1:6969/sub 2>/dev/null')
if out:
    import base64
    try:
        decoded = base64.b64decode(out).decode('utf-8')
        print(f'  ✅ 订阅内容(Base64解码后):')
        for line in decoded.strip().split('\n'):
            if '://' in line:
                print(f'    {line[:80]}...' if len(line) > 80 else f'    {line}')
    except:
        print(f'  原始内容: {out[:200]}')

client.close()
