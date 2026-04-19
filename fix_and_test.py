#!/usr/bin/env python3
import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('54.250.149.157', port=22, username='root', password='oroVIG38@jh.dxclouds.com', timeout=10)

def run(cmd, timeout=30):
    print(f">>> {cmd[:80]}")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out.strip():
        print(out.strip()[-300:])
    if err.strip() and 'warning' not in err.lower():
        print(f"[ERR] {err.strip()[:200]}")
    return exit_code

# 1. 重新生成配置
print("[1] 重新生成 Singbox 配置...")
run("cd /root/singbox-eps-node && python3 scripts/config_generator.py")

# 2. 验证配置
print("\n[2] 验证配置...")
run("/usr/local/bin/sing-box check -c /root/singbox-eps-node/config.json 2>&1")

# 3. 重启 singbox
print("\n[3] 重启 singbox...")
run("systemctl restart singbox")
time.sleep(3)

# 4. 检查状态
print("\n[4] 检查服务状态...")
run("systemctl is-active singbox singbox-sub singbox-cdn singbox-tgbot")

# 5. 检查端口
print("\n[5] 检查端口...")
run("ss -tlnp | grep -E '443|6969|2053|2083|1080'")

# 6. 测试订阅
print("\n[6] 测试订阅链接...")
run("curl -sk https://127.0.0.1:6969/sub/JP | head -c 300")

# 7. 检查日志
print("\n[7] 检查 singbox 日志...")
run("journalctl -u singbox --no-pager -n 5")

print("\n" + "=" * 60)
print("修复完成！")
print("=" * 60)

ssh.close()
