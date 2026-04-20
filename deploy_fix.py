#!/usr/bin/env python3
"""上传修复并重启服务"""
import paramiko
import time

SERVER_IP = '54.250.149.157'
SSH_USER = 'root'
SSH_PASS = 'oroVIG38@jh.dxclouds.com'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(SERVER_IP, 22, SSH_USER, SSH_PASS, timeout=15)

def run_cmd(cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    return stdout.channel.recv_exit_status(), stdout.read().decode(), stderr.read().decode()

# 上传修复后的文件
print('【上传修复后的订阅服务代码】')
sftp = client.open_sftp()
sftp.put('d:/Documents/Syncdisk/工作用/job/S-ui/singbox-eps-node/scripts/subscription_service.py', 
         '/root/singbox-eps-node/scripts/subscription_service.py')
sftp.close()
print('上传完成')

# 重启订阅服务
print('\n【重启订阅服务】')
exit_code, out, err = run_cmd('systemctl restart singbox-sub')
print(out.strip() if out else '无输出')
if err:
    print(f'错误: {err}')

time.sleep(3)

# 检查服务状态
print('\n【服务状态】')
exit_code, out, err = run_cmd('systemctl status singbox-sub 2>&1 | head -10')
print(out.strip() if out else '无')

# 测试生成的Trojan链接
print('\n【测试生成的Trojan链接】')
exit_code, out, err = run_cmd('cd /root/singbox-eps-node && python3 -c "from scripts.subscription_service import generate_all_links; links=generate_all_links(); [print(l) for l in links if \'trojan\' in l.lower()]"')
print(out.strip() if out else '无')

# 对比用户可用链接
print('\n【用户可用链接】')
print('trojan://uG3hixuWQUJTq6_-Qiakow@104.16.124.96:2083?security=tls&sni=jp.290372913.xyz&insecure=1&allowInsecure=1&type=ws&host=jp.290372913.xyz&path=%2Ftrojan-ws#JP-Trojan-WS-CDN')

client.close()
