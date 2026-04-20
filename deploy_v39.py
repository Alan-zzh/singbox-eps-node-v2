#!/usr/bin/env python3
"""上传所有修改并重启服务"""
import paramiko
import time

SERVER_IP = '54.250.149.157'
SSH_USER = 'root'
SSH_PASS = 'oroVIG38@jh.dxclouds.com'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, 22, SSH_USER, SSH_PASS, timeout=15)

def run_cmd(client, cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    return stdout.channel.recv_exit_status(), stdout.read().decode(), stderr.read().decode()

# 上传subscription_service.py
sftp = client.open_sftp()
sftp.put(r'd:\Documents\Syncdisk\工作用\job\S-ui\singbox-eps-node\scripts\subscription_service.py', 
         '/root/singbox-eps-node/scripts/subscription_service.py')
sftp.close()
print('✅ 已上传 subscription_service.py')

print('\n【重启订阅服务】')
exit_code, out, err = run_cmd(client, 'systemctl restart singbox-sub')
time.sleep(3)

exit_code, out, err = run_cmd(client, 'systemctl is-active singbox-sub')
print(f'  状态: {out.strip()}')

print('\n【测试Trojan链接生成】')
exit_code, out, err = run_cmd(client, 'cd /root/singbox-eps-node && python3 -c "from scripts.subscription_service import generate_all_links; links = generate_all_links(); [print(l) for l in links if \'trojan\' in l.lower()]"')
print(out.strip() if out else '无')

print('\n【测试sing-box JSON路由规则】')
exit_code, out, err = run_cmd(client, 'curl -sk https://localhost:9443/singbox/JP | python3 -c "import sys,json; d=json.load(sys.stdin); rules=[r for r in d.get(\'route\',{}).get(\'rules\',[]) if r.get(\'outbound\')==\'ai-residential\']; print(json.dumps(rules, indent=2, ensure_ascii=False))"')
print(out.strip() if out else '无')

client.close()
