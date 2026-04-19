#!/usr/bin/env python3
import paramiko
import time
import json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('54.250.149.157', port=22, username='root', password='oroVIG38@jh.dxclouds.com', timeout=10)

def run(cmd, timeout=30):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out.strip():
        print(out.strip()[-200:])
    if err.strip() and 'warning' not in err.lower():
        print(f"[ERR] {err.strip()[:200]}")
    return exit_code

# 1. 读取当前 config.json
print("[1] 读取当前配置...")
stdin, stdout, stderr = ssh.exec_command('cat /root/singbox-eps-node/config.json')
config_json = stdout.read().decode()
config = json.loads(config_json)

# 2. 修复所有 VLESS 节点的 users 字段 (id -> uuid)
print("[2] 修复所有 VLESS 节点配置...")
for i, inbound in enumerate(config['inbounds']):
    if inbound.get('type') == 'vless':
        for user in inbound.get('users', []):
            if 'id' in user:
                user['uuid'] = user.pop('id')
                print(f"  修复 inbounds[{i}] ({inbound.get('tag')}): id -> uuid")

# 3. 写回修复后的配置
print("[3] 保存修复后的配置...")
fixed_json = json.dumps(config, indent=2, ensure_ascii=False)
stdin, stdout, stderr = ssh.exec_command(f"cat > /root/singbox-eps-node/config.json << 'JSONEOF'\n{fixed_json}\nJSONEOF")
print("  配置已保存")

# 4. 验证配置
print("\n[4] 验证配置...")
run("/usr/local/bin/sing-box check -c /root/singbox-eps-node/config.json 2>&1")

# 5. 重启 singbox
print("\n[5] 重启 singbox...")
run("systemctl restart singbox")
time.sleep(3)

# 6. 检查状态
print("\n[6] 检查服务状态...")
run("systemctl is-active singbox singbox-sub singbox-cdn singbox-tgbot")

# 7. 检查端口
print("\n[7] 检查端口...")
run("ss -tlnp | grep -E '443|6969|2053|2083|1080'")

# 8. 检查日志
print("\n[8] 检查 singbox 日志...")
run("journalctl -u singbox --no-pager -n 5")

# 9. 测试订阅
print("\n[9] 测试订阅链接...")
run("curl -sk https://127.0.0.1:6969/sub/JP | head -c 200")

print("\n" + "=" * 60)
print("修复完成！")
print("=" * 60)

ssh.close()
