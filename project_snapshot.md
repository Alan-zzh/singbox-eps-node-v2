# 项目状态快照 (Project Snapshot)

## 当前版本
**v1.0.33** (Hysteria2端口跳跃修复+iptables配置+文档完善)

---

## 版本历史
| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.0.32 | 2026-04-20 | Hysteria2端口修复+CDN节点SNI修复+优选IP池优化 |
| v1.0.33 | 2026-04-20 | Hysteria2端口跳跃修复(iptables)+mport参数+文档完善 |

---

## 最新更新内容 (v1.0.33)

### 修复1：Hysteria2端口跳跃配置
- **问题**: sing-box不支持`port_hopping`字段，直接配置会导致启动失败
- **解决方案**: 
  - 使用iptables DNAT规则实现端口跳跃：`22000-22200 UDP -> 443`
  - 订阅链接添加`mport=443,22000-22200`参数
  - 规则保存到`/etc/iptables/rules.v4`实现持久化
- **效果**: 客户端可连接22000-22200范围内任意UDP端口，避免运营商UDP QoS

### 修复2：清理旧iptables规则
- **问题**: 之前配置遗留了大量21000-21200的REDIRECT规则
- **解决方案**: 清空nat表PREROUTING链，重新添加正确的DNAT规则
- **效果**: 规则表干净，只有正确的端口跳跃规则

---

## 当前服务状态
- **singbox**: active (端口443/8443/2053/2083)
- **singbox-sub**: active (HTTP://0.0.0.0:6969)
- **singbox-cdn**: active (每小时更新优选IP)
- **iptables**: 端口跳跃 22000-22200 -> 443

## 订阅链接
- **格式**: http://SERVER_IP:6969/sub/{国家代码}
- **示例**: http://54.250.149.157:6969/sub/JP
- **协议**: 仅支持HTTP（自签证书CN不匹配，HTTPS会导致客户端拒绝）

## 节点列表（6个）
1. JP-VLESS-Reality: 54.250.149.157:443 (直连)
2. JP-VLESS-WS-CDN: 优选IP:8443 (CDN)
3. JP-VLESS-HTTPUpgrade-CDN: 优选IP:2053 (CDN)
4. JP-Trojan-WS-CDN: 优选IP:2083 (CDN)
5. JP-Hysteria2: 54.250.149.157:443 (直连，端口跳跃22000-22200)
6. AI-SOCKS5: 206.163.4.241:36753 (外部代理，固定配置)

## 核心目录
```
/root/singbox-eps-node/
├── .env                    # 环境变量（密钥、UUID等）
├── config.json             # singbox配置文件
├── cert/                   # SSL证书
│   ├── cert.pem
│   └── key.pem
├── data/
│   └── singbox.db          # SQLite数据库（CDN IP等）
├── scripts/
│   ├── config.py           # 全局配置
│   ├── logger.py           # 日志管理
│   ├── cdn_monitor.py      # CDN监控脚本（v1.0.32）
│   ├── subscription_service.py  # 订阅服务（v1.0.33）
│   └── config_generator.py # 配置生成器
├── logs/                   # 日志目录
└── backups/                # 备份目录
```

## 已知限制
1. **订阅仅支持HTTP**: 自签证书CN不匹配，HTTPS会导致客户端拒绝连接
2. **SOCKS5无自动切换**: 当前为固定配置，需要手动添加多个节点
3. **Hysteria2端口跳跃**: 使用iptables实现，sing-box本身不支持port_hopping字段

## 下一步待办
- [ ] 验证Hysteria2端口跳跃在客户端的连通性
- [ ] 考虑添加SOCKS5自动切换逻辑
- [ ] 上传完整技术文档到GitHub供其他AI审查
