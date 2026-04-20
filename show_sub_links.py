#!/usr/bin/env python3
"""生成正确的订阅链接"""
import paramiko
import base64

SERVER_IP = '54.250.149.157'
SSH_USER = 'root'
SSH_PASS = 'oroVIG38@jh.dxclouds.com'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, 22, SSH_USER, SSH_PASS, timeout=15)

def run_cmd(client, cmd, timeout=10):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    return stdout.channel.recv_exit_status(), stdout.read().decode(), stderr.read().decode()

print('=' * 60)
print('✅ 订阅服务已修复！以下是正确的订阅链接')
print('=' * 60)

print('\n【推荐订阅链接】(HTTPS + 服务器IP直连)')
print(f'https://{SERVER_IP}:6969/sub')
print(f'https://{SERVER_IP}:6969/sub/JP')
print(f'https://{SERVER_IP}:6969/sub/SUB_TOKEN')

print('\n【备用订阅链接】(HTTP + 服务器IP直连)')
print(f'http://{SERVER_IP}:6969/sub')

print('\n【域名订阅链接】(需关闭Cloudflare代理)')
print(f'https://jp.290372913.xyz:6969/sub')
print('注意：需要在Cloudflare DNS设置中将代理状态改为"仅限DNS"')

print('\n' + '=' * 60)
print('【当前订阅内容验证】')
print('=' * 60)

exit_code, out, err = run_cmd(client, 'curl -sk https://127.0.0.1:6969/sub 2>/dev/null')
if out:
    try:
        decoded = base64.b64decode(out).decode('utf-8')
        lines = decoded.strip().split('\n')
        print(f'✅ 共{len(lines)}个节点:\n')
        for i, line in enumerate(lines, 1):
            if '://' in line:
                protocol = line.split('://')[0].upper()
                name = line.split('#')[-1] if '#' in line else '未命名'
                print(f'  {i}. {protocol}: {name}')
    except:
        print(f'原始内容: {out[:200]}')
else:
    print('❌ 无法获取订阅内容')

print('\n' + '=' * 60)
print('【使用说明】')
print('=' * 60)
print('1. 复制上面的订阅链接到你的代理软件')
print('2. 推荐使用 HTTPS + IP直连 方式')
print('3. 如果使用域名，需在Cloudflare关闭代理(橙色云朵→灰色云朵)')
print('4. 订阅更新时选择"跳过证书验证"或"允许不安全连接"')

client.close()
