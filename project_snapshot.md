# 项目状态快照 (Project Snapshot)

## 当前版本
**v1.0.34** (HTTPS订阅服务+Cloudflare正式证书)

---

## 版本历史
| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.0.33 | 2026-04-20 | Hysteria2端口跳跃修复(iptables)+mport参数+文档完善 |
| v1.0.34 | 2026-04-20 | HTTPS订阅服务+Cloudflare正式证书+端口9443 |

---

## 最新更新内容 (v1.0.34)

### 新增：HTTPS订阅服务
- **证书**: Let's Encrypt正式证书，域名 `jp.290372913.xyz`
- **端口**: 9443（避免与singbox主服务443/8443冲突）
- **订阅链接**: `https://jp.290372913.xyz:9443/sub/JP`
- **证书路径**: 
  - 证书: `/root/singbox-eps-node/cert/cert.pem`
  - 私钥: `/root/singbox-eps-node/cert/key.pem`
  - 完整链: `/root/singbox-eps-node/cert/fullchain.pem`

### Cloudflare凭证配置
- **凭证类型**: API Token（43位）
- **acme.sh变量**: `CF_Token`（用于dns_cf验证）
- **自动续期**: acme.sh已配置，到期前自动续期

### 端口分配
- **443**: singbox主服务（VLESS-Reality等）
- **8443**: singbox主服务（VLESS-WS-CDN等）
- **9443**: HTTPS订阅服务（Flask+SSL）
- **2053/2083**: CDN节点端口
- **22000-22200**: Hysteria2端口跳跃（iptables转发到443）

---

## 当前服务状态
- **singbox**: active (端口443/8443/2053/2083)
- **singbox-sub**: active (HTTPS://0.0.0.0:9443)
- **singbox-cdn**: active (每小时更新优选IP)
- **iptables**: 端口跳跃 22000-22200 -> 443

## 订阅链接
- **HTTPS**: https://jp.290372913.xyz:9443/sub/{国家代码}
- **示例**: https://jp.290372913.xyz:9443/sub/JP
- **证书**: Let's Encrypt正式证书，客户端信任

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
├── .env                    # 环境变量（SUB_PORT=9443）
├── config.json             # singbox配置文件
├── cert/                   # SSL证书（Let's Encrypt）
│   ├── cert.pem
│   ├── key.pem
│   └── fullchain.pem
├── data/
│   └── singbox.db          # SQLite数据库（CDN IP等）
├── scripts/
│   ├── config.py           # 全局配置
│   ├── logger.py           # 日志管理
│   ├── cdn_monitor.py      # CDN监控脚本
│   ├── subscription_service.py  # 订阅服务（HTTPS）
│   └── config_generator.py # 配置生成器
├── logs/                   # 日志目录
└── backups/                # 备份目录
```

## 已知限制
1. **SOCKS5无自动切换**: 当前为固定配置，需要手动添加多个节点
2. **Hysteria2端口跳跃**: 使用iptables实现，sing-box本身不支持port_hopping字段

## 踩坑记录
1. **端口冲突**: 8443被singbox主服务占用，订阅服务改用9443
2. **SSL配置**: Flask的ssl_context需要fullchain.pem和key.pem
3. **acme.sh凭证**: API Token使用CF_Token变量，Global API Key使用CF_Key+CF_Email

## 下一步待办
- [ ] 验证HTTPS订阅在客户端的连通性
- [ ] 考虑添加SOCKS5自动切换逻辑
- [ ] 配置acme.sh自动续期cron任务
