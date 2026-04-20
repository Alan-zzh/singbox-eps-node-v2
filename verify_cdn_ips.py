#!/usr/bin/env python3
"""验证订阅内容中的CDN节点是否使用优选IP"""
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

print('【1. 获取订阅内容并解码】')
exit_code, out, err = run_cmd(client, 'curl -sk https://127.0.0.1:6969/sub 2>/dev/null')
if out:
    try:
        decoded = base64.b64decode(out).decode('utf-8')
        lines = decoded.strip().split('\n')
        print(f'✅ 共{len(lines)}个节点:\n')
        for i, line in enumerate(lines, 1):
            if '://' in line:
                # 提取协议、IP和名称
                parts = line.split('#')
                name = parts[1] if len(parts) > 1 else '未命名'
                url_part = parts[0]
                
                # 提取IP地址
                if '@' in url_part:
                    ip_port = url_part.split('@')[1].split('?')[0]
                    ip = ip_port.split(':')[0]
                else:
                    ip = '未知'
                
                print(f'  {i}. {name}')
                print(f'     IP: {ip}')
                print(f'     完整: {line[:80]}...' if len(line) > 80 else f'     完整: {line}')
                print()
    except Exception as e:
        print(f'❌ 解码失败: {e}')
        print(f'原始内容: {out[:200]}')
else:
    print('❌ 无法获取订阅内容')

print('【2. 检查数据库中的CDN IP】')
exit_code, out, err = run_cmd(client, 'python3 -c "import sqlite3; conn=sqlite3.connect(\'/root/singbox-eps-node/data/singbox.db\'); cursor=conn.cursor(); cursor.execute(\'SELECT * FROM cdn_settings\'); [print(f\"  {row[0]}: {row[1]}\") for row in cursor.fetchall()]; conn.close()" 2>/dev/null || echo "无法读取数据库"')
print(out)

print('【3. 验证CDN节点是否使用优选IP】')
# 检查订阅中的CDN节点IP是否与数据库中的IP匹配
exit_code, out, err = run_cmd(client, '''
python3 << 'PYEOF'
import sqlite3
import base64
import urllib.parse

# 读取数据库中的CDN IP
conn = sqlite3.connect('/root/singbox-eps-node/data/singbox.db')
cursor = conn.cursor()
cursor.execute('SELECT key, value FROM cdn_settings WHERE key LIKE "%cdn_ip%"')
cdn_ips = {row[0]: row[1] for row in cursor.fetchall()}
conn.close()

print("数据库中的CDN IP:")
for key, ip in cdn_ips.items():
    print(f"  {key}: {ip}")

# 获取订阅内容
import subprocess
result = subprocess.run(['curl', '-sk', 'https://127.0.0.1:6969/sub'], capture_output=True, text=True)
if result.stdout:
    try:
        decoded = base64.b64decode(result.stdout).decode('utf-8')
        lines = decoded.strip().split('\n')
        print("\n订阅中的CDN节点:")
        for line in lines:
            if '-CDN' in line and '://' in line:
                # 提取IP
                if '@' in line:
                    ip_port = line.split('@')[1].split('?')[0]
                    ip = ip_port.split(':')[0]
                    name = line.split('#')[1] if '#' in line else '未命名'
                    print(f"  {name}: {ip}")
    except:
        print("无法解析订阅内容")
PYEOF
''')
print(out if out else '无法验证')

client.close()
print('\n✅ 验证完成！')
