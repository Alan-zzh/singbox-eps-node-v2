#!/usr/bin/env python3
"""检查订阅服务外部访问问题"""
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

print('【1. 检查订阅服务监听地址】')
exit_code, out, err = run_cmd(client, 'ss -tlnp | grep 6969')
print(f'  {out.strip() if out else "未监听"}')

print('\n【2. 检查防火墙6969端口】')
exit_code, out, err = run_cmd(client, 'iptables -L INPUT -n | grep 6969')
print(f'  {out.strip() if out else "无规则"}')

print('\n【3. 检查UFW状态】')
exit_code, out, err = run_cmd(client, 'ufw status 2>/dev/null || echo "UFW未启用"')
print(f'  {out}')

print('\n【4. 测试本地HTTPS订阅】')
exit_code, out, err = run_cmd(client, 'curl -sk https://127.0.0.1:6969/sub 2>/dev/null | head -c 200')
print(f'  {out if out else "无响应"}')

print('\n【5. 测试本地HTTP订阅】')
exit_code, out, err = run_cmd(client, 'curl -s http://127.0.0.1:6969/sub 2>/dev/null | head -c 200')
print(f'  {out if out else "无响应"}')

print('\n【6. 检查订阅服务日志(错误)】')
exit_code, out, err = run_cmd(client, 'journalctl -u singbox-sub --no-pager -n 20 2>&1 | grep -i "error\|warning\|fail" | tail -5')
print(f'  {out if out else "无错误日志"}')

print('\n【7. 检查订阅服务完整日志】')
exit_code, out, err = run_cmd(client, 'journalctl -u singbox-sub --no-pager -n 10 2>&1 | tail -10')
print(out)

print('\n【8. 检查Cloudflare域名代理状态】')
exit_code, out, err = run_cmd(client, 'curl -sI https://jp.290372913.xyz 2>/dev/null | grep -i "server\|cf-ray\|521"')
print(f'  {out if out else "无法访问"}')

print('\n【9. 检查订阅服务User-Agent处理】')
exit_code, out, err = run_cmd(client, 'curl -sk -H "User-Agent: Clash" https://127.0.0.1:6969/sub 2>/dev/null | head -c 100')
print(f'  Clash UA: {out if out else "无响应"}')

exit_code, out, err = run_cmd(client, 'curl -sk -H "User-Agent: v2rayN" https://127.0.0.1:6969/sub 2>/dev/null | head -c 100')
print(f'  v2rayN UA: {out if out else "无响应"}')

exit_code, out, err = run_cmd(client, 'curl -sk -H "User-Agent: Shadowrocket" https://127.0.0.1:6969/sub 2>/dev/null | head -c 100')
print(f'  Shadowrocket UA: {out if out else "无响应"}')

print('\n' + '=' * 60)
print('【正确的订阅链接】')
print('=' * 60)
print(f'HTTPS: https://{SERVER_IP}:6969/sub')
print(f'HTTP:  http://{SERVER_IP}:6969/sub')
print('\n注意：如果使用域名，需要Cloudflare关闭代理(DNS Only)')
print('或者使用80/443端口(需要配置反向代理)')

client.close()
