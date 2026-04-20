#!/usr/bin/env python3
"""上传订阅服务并重启"""
import paramiko
import time

SERVER_IP = '54.250.149.157'
SSH_USER = 'root'
SSH_PASS = 'oroVIG38@jh.dxclouds.com'

LOCAL_FILE = r'd:\Documents\Syncdisk\工作用\job\S-ui\singbox-eps-node\scripts\subscription_service.py'
REMOTE_FILE = '/root/singbox-eps-node/scripts/subscription_service.py'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, 22, SSH_USER, SSH_PASS, timeout=15)

sftp = client.open_sftp()
sftp.put(LOCAL_FILE, REMOTE_FILE)
sftp.close()
print('✅ 已上传 subscription_service.py')

def run_cmd(client, cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    return stdout.channel.recv_exit_status(), stdout.read().decode(), stderr.read().decode()

print('\n【重启订阅服务】')
exit_code, out, err = run_cmd(client, 'systemctl restart singbox-sub')
print(f'  重启: {out.strip() if out else "完成"}')

time.sleep(5)

exit_code, out, err = run_cmd(client, 'systemctl is-active singbox-sub')
print(f'  状态: {out.strip()}')

print('\n【测试sing-box JSON配置】')
exit_code, out, err = run_cmd(client, 'curl -sk https://localhost:9443/singbox/JP | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\'路由规则数: {len(d.get(\\\"route\\\",{}).get(\\\"rules\\\",[]))}\'); print(f\'出站数: {len(d.get(\\\"outbounds\\\",[]))}\'); ai_rules=[r for r in d.get(\\\"route\\\",{}).get(\\\"rules\\\",[]) if r.get(\\\"outbound\\\")==\\\"ai-residential\\\"]; print(f\'AI路由规则: {ai_rules}\')"')
print(out.strip() if out else '无')

client.close()
