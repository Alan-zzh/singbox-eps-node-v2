#!/usr/bin/env python3
"""测试sing-box JSON路由规则"""
import paramiko
import json

SERVER_IP = '54.250.149.157'
SSH_USER = 'root'
SSH_PASS = 'oroVIG38@jh.dxclouds.com'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, 22, SSH_USER, SSH_PASS, timeout=15)

def run_cmd(client, cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    return stdout.channel.recv_exit_status(), stdout.read().decode(), stderr.read().decode()

print('【测试sing-box JSON路由规则】')
exit_code, out, err = run_cmd(client, 'curl -sk https://localhost:9443/singbox/JP')
if out:
    try:
        d = json.loads(out)
        rules = [r for r in d.get('route',{}).get('rules',[]) if r.get('outbound')=='ai-residential']
        print(json.dumps(rules, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f'解析错误: {e}')
        print(out[:500])
else:
    print('无输出')
    print(f'err: {err[:500] if err else "无"}')

client.close()
