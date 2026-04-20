#!/usr/bin/env python3
"""检查服务器配置文件"""
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

print('【1. 查找所有singbox配置文件】')
exit_code, out, err = run_cmd(client, 'find /root -name "*.json" -path "*singbox*" 2>/dev/null')
print(out if out else '未找到')

print('\n【2. 查看/root/singbox-eps-node/目录结构】')
exit_code, out, err = run_cmd(client, 'ls -la /root/singbox-eps-node/ 2>&1')
print(out)

print('\n【3. 查看/root/singbox-eps-node/config/目录】')
exit_code, out, err = run_cmd(client, 'ls -la /root/singbox-eps-node/config/ 2>&1')
print(out)

print('\n【4. 查看/root/singbox-eps-node/scripts/目录】')
exit_code, out, err = run_cmd(client, 'ls -la /root/singbox-eps-node/scripts/ 2>&1')
print(out)

print('\n【5. 查看systemd服务文件】')
exit_code, out, err = run_cmd(client, 'ls -la /etc/systemd/system/singbox* 2>&1')
print(out)

print('\n【6. 查看singbox二进制位置】')
exit_code, out, err = run_cmd(client, 'which sing-box 2>&1')
print(out.strip())

print('\n【7. 查看singbox版本】')
exit_code, out, err = run_cmd(client, 'sing-box version 2>&1')
print(out)

print('\n【8. 查看config_generator.py生成的配置】')
exit_code, out, err = run_cmd(client, 'cat /root/singbox-eps-node/scripts/config_generator.py 2>&1 | head -5')
print(out[:500] if out else '无')

client.close()
print('\n✅ 检查完成')
