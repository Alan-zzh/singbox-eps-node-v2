#!/usr/bin/env python3
"""修复订阅服务HTTPS并验证"""
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

# 1. 上传修复后的config.py
print('【上传修复后的config.py】')
with open('scripts/config.py', 'r', encoding='utf-8') as f:
    config_content = f.read()
run_cmd(client, f"cat > /root/singbox-eps-node/scripts/config.py << 'CONFIGEOF'\n{config_content}\nCONFIGEOF")
print('  ✅ config.py已上传')

# 2. 重启订阅服务
print('\n【重启订阅服务】')
run_cmd(client, 'systemctl restart singbox-sub')
time.sleep(3)

# 3. 检查服务状态
print('\n【检查服务状态】')
exit_code, out, err = run_cmd(client, 'systemctl is-active singbox-sub')
print(f'  singbox-sub: {out.strip()}')

# 4. 查看启动日志
print('\n【查看启动日志】')
exit_code, out, err = run_cmd(client, 'journalctl -u singbox-sub --no-pager -n 5 2>&1 | tail -5')
print(out)

# 5. 测试HTTPS
print('\n【测试HTTPS订阅链接】')
exit_code, out, err = run_cmd(client, 'curl -sk -o /dev/null -w "HTTP状态码: %{http_code}\\n响应大小: %{size_download}字节\\n" https://127.0.0.1:6969/sub 2>&1')
print(f'  {out}')

# 6. 获取订阅内容并解码
print('\n【获取订阅内容】')
exit_code, out, err = run_cmd(client, 'curl -sk https://127.0.0.1:6969/sub 2>/dev/null')
if out:
    import base64
    try:
        decoded = base64.b64decode(out).decode('utf-8')
        lines = decoded.strip().split('\n')
        print(f'  ✅ 订阅内容有效，共{len(lines)}个节点:')
        for line in lines[:6]:
            if '://' in line:
                protocol = line.split('://')[0]
                name = line.split('#')[-1] if '#' in line else '未命名'
                print(f'    - {protocol}: {name}')
    except:
        print(f'  ⚠️ 内容格式: {out[:100]}...')
else:
    print('  ❌ 无法获取订阅内容')

client.close()
print('\n' + '=' * 60)
print('✅ 修复完成！')
print('=' * 60)
