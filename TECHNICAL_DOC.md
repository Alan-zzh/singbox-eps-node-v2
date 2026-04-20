# 技术文档 - 供其他AI审查

## 项目概述
- **项目名称**: Singbox EPS Node (代理节点订阅系统)
- **服务器**: 54.250.149.157 (日本AWS)
- **域名**: jp.290372913.xyz (Cloudflare DNS)
- **当前版本**: v1.0.34

---

## 当前架构

### 服务列表
| 服务 | 端口 | 协议 | 状态 |
|------|------|------|------|
| singbox主服务 | 443, 8443, 2053, 2083 | TCP/UDP | ✅ active |
| singbox-sub订阅 | 9443 | HTTPS | ✅ active |
| singbox-cdn监控 | - | 定时任务 | ✅ active |

### 节点列表（6个）
1. **JP-VLESS-Reality**: 54.250.149.157:443 (直连，Reality协议)
2. **JP-VLESS-WS-CDN**: Cloudflare优选IP:8443 (CDN)
3. **JP-VLESS-HTTPUpgrade-CDN**: Cloudflare优选IP:2053 (CDN)
4. **JP-Trojan-WS-CDN**: Cloudflare优选IP:2083 (CDN)
5. **JP-Hysteria2**: 54.250.149.157:443 (直连，iptables端口跳跃22000-22200)
6. **AI-SOCKS5**: 206.163.4.241:36753 (外部代理，固定配置)

---

## 已完成功能

### 1. HTTPS订阅服务 ✅
- **订阅链接**: `https://jp.290372913.xyz:9443/sub/JP`
- **证书**: Let's Encrypt正式证书（acme.sh + Cloudflare DNS API）
- **端口**: 9443（避免与singbox主服务冲突）
- **自动续期**: acme.sh已配置

### 2. Hysteria2端口跳跃 ✅
- **实现方式**: iptables DNAT规则
- **规则**: `iptables -t nat -A PREROUTING -p udp --dport 22000:22200 -j DNAT --to-destination :443`
- **订阅参数**: `mport=443,22000-22200`
- **持久化**: `/etc/iptables/rules.v4`

### 3. CDN优选IP ✅
- **机制**: 每小时测试Cloudflare IP延迟，自动更新最低延迟IP
- **存储**: SQLite数据库 (`/root/singbox-eps-node/data/singbox.db`)
- **分配**: 每个CDN协议独立优选IP

---

## 待解决问题（需要其他AI帮助）

### 问题1: SOCKS5自动切换 ❌
**现状**: 
- 当前SOCKS5节点是固定配置在订阅中的
- 只有一个节点: `socks5://4KKsLB7F:KgEKVmVgxJ@206.163.4.241:36753#AI-SOCKS5`

**需求**:
- 实现SOCKS5节点自动切换功能
- 当当前节点不可用时，自动切换到备用节点
- 需要维护一个SOCKS5节点池

**可能方案**:
1. 在订阅服务中添加多个SOCKS5节点
2. 实现健康检查机制，定期测试节点可用性
3. 根据延迟自动排序，优先返回最快节点

### 问题2: acme.sh自动续期验证 ⚠️
**现状**:
- acme.sh已安装并申请证书
- 证书有效期至2026-07-19
- 需要确认cron自动续期任务是否配置

**需要验证**:
```bash
crontab -l | grep acme
```

### 问题3: 订阅服务HTTPS证书CN匹配 ✅ 已解决
**原问题**: 自签证书CN为`www.apple.com`，导致HTTPS订阅时客户端拒绝
**解决方案**: 使用Cloudflare DNS API + acme.sh申请Let's Encrypt正式证书

---

## 技术细节

### Cloudflare凭证
- **类型**: API Token
- **变量**: `CF_Token`（acme.sh使用）
- **权限**: 需要Zone.DNS编辑权限

### 端口分配
```
443    - singbox VLESS-Reality入站
8443   - singbox VLESS-WS-CDN入站
2053   - singbox VLESS-HTTPUpgrade-CDN入站
2083   - singbox Trojan-WS-CDN入站
9443   - Flask订阅服务（HTTPS）
22000-22200 - Hysteria2端口跳跃（iptables转发到443）
```

### 文件路径
```
/root/singbox-eps-node/
├── .env                           # 环境变量
├── config.json                    # singbox配置
├── cert/                          # SSL证书
│   ├── cert.pem                   # Let's Encrypt证书
│   ├── key.pem                    # 私钥
│   └── fullchain.pem              # 完整证书链
├── data/singbox.db                # SQLite数据库
├── scripts/
│   ├── config.py                  # 全局配置
│   ├── logger.py                  # 日志管理
│   ├── cdn_monitor.py             # CDN监控
│   ├── subscription_service.py    # 订阅服务（HTTPS）
│   └── config_generator.py        # 配置生成器
└── logs/                          # 日志目录
```

---

## 订阅服务代码关键部分

### SSL配置 (subscription_service.py)
```python
app.run(host='0.0.0.0', port=SUB_PORT, threaded=True, 
        ssl_context=('/root/singbox-eps-node/cert/fullchain.pem', 
                     '/root/singbox-eps-node/cert/key.pem'))
```

### Hysteria2节点生成
```python
params = {
    'sni': REALITY_SNI,
    'insecure': '1',
    'obfs': 'salamander',
    'obfs-password': HYSTERIA2_PASSWORD[:8],
    'mport': '443,22000-22200'  # 端口跳跃
}
links.append(f"hysteria2://{HYSTERIA2_PASSWORD}@{SERVER_IP}:443?{param_str}#{COUNTRY_CODE}-Hysteria2")
```

---

## 给其他AI的建议

1. **修改代码前**: 先查阅 `project_snapshot.md` 了解当前状态
2. **端口冲突**: 避免使用443/8443/2053/2083/9443
3. **证书路径**: 使用 `/root/singbox-eps-node/cert/` 下的证书文件
4. **环境变量**: 从 `/root/singbox-eps-node/.env` 读取配置
5. **测试方法**: 修改后重启服务 `systemctl restart singbox-sub`

---

## 联系方式
- **GitHub**: https://github.com/Alan-zzh/singbox-eps-node-v2
- **服务器**: 54.250.149.157 (SSH root)
