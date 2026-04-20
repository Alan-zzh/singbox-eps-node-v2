#!/usr/bin/env python3
"""检查订阅服务状态"""
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

print('【1. 检查订阅服务状态】')
exit_code, out, err = run_cmd(client, 'systemctl is-active singbox-sub')
print(f'  singbox-sub: {out.strip()}')

print('\n【2. 检查订阅服务端口监听】')
exit_code, out, err = run_cmd(client, 'ss -tlnp | grep 6969')
print(f'  {out.strip() if out else "端口6969未监听"}')

print('\n【3. 检查订阅服务日志(最近10条)】')
exit_code, out, err = run_cmd(client, 'journalctl -u singbox-sub --no-pager -n 10 2>&1 | tail -10')
print(out)

print('\n【4. 本地测试订阅链接(HTTP)】')
exit_code, out, err = run_cmd(client, 'curl -s -o /dev/null -w "HTTP状态码: %{http_code}\\n响应大小: %{size_download}字节\\n" http://127.0.0.1:6969/sub 2>&1')
print(f'  {out}')

print('\n【5. 本地测试订阅链接(HTTPS)】')
exit_code, out, err = run_cmd(client, 'curl -sk -o /dev/null -w "HTTP状态码: %{http_code}\\n响应大小: %{size_download}字节\\n" https://127.0.0.1:6969/sub 2>&1')
print(f'  {out}')

print('\n【6. 检查防火墙规则】')
exit_code, out, err = run_cmd(client, 'iptables -L INPUT -n | grep 6969')
print(f'  {out.strip() if out else "无6969端口规则"}')

print('\n【7. 检查订阅服务进程】')
exit_code, out, err = run_cmd(client, 'ps aux | grep subscription_service | grep -v grep')
print(f'  {out.strip() if out else "订阅服务进程未运行"}')

print('\n【8. 检查证书文件】')
exit_code, out, err = run_cmd(client, 'ls -la /root/singbox-eps-node/cert/ 2>/dev/null || echo "cert目录不存在"')
print(f'  {out}')

client.close()
