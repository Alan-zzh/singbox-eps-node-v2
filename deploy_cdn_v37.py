#!/usr/bin/env python3
"""上传CDN监控脚本并重启服务"""
import paramiko

SERVER_IP = '54.250.149.157'
SSH_USER = 'root'
SSH_PASS = 'oroVIG38@jh.dxclouds.com'

LOCAL_FILE = r'd:\Documents\Syncdisk\工作用\job\S-ui\singbox-eps-node\scripts\cdn_monitor.py'
REMOTE_FILE = '/root/singbox-eps-node/scripts/cdn_monitor.py'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, 22, SSH_USER, SSH_PASS, timeout=15)

sftp = client.open_sftp()
sftp.put(LOCAL_FILE, REMOTE_FILE)
sftp.close()
print('✅ 已上传 cdn_monitor.py')

def run_cmd(client, cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    return stdout.channel.recv_exit_status(), stdout.read().decode(), stderr.read().decode()

print('\n【重启CDN监控服务】')
exit_code, out, err = run_cmd(client, 'systemctl restart singbox-cdn')
print(f'  重启: {out.strip() if out else "完成"}')

exit_code, out, err = run_cmd(client, 'systemctl is-active singbox-cdn')
print(f'  状态: {out.strip()}')

print('\n【等待15秒后查看日志】')
import time
time.sleep(15)

exit_code, out, err = run_cmd(client, 'journalctl -u singbox-cdn --no-pager -n 20')
print(out.strip()[-1000:] if out else '无日志')

print('\n【数据库中的优选IP】')
exit_code, out, err = run_cmd(client, 'sqlite3 /root/singbox-eps-node/data/singbox.db "SELECT * FROM cdn_settings;"')
print(out.strip() if out else '无数据')

client.close()
