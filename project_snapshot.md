# 项目状态快照 (Project Snapshot)

## 当前版本
**v1.0.18** (VPS 全自动部署+VLESS uuid 修复版)

---

## 版本历史
| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.0.0 | 2026-04-20 | 初始版本：模块化 Singbox 一键部署面板 |
| v1.0.8 | 2026-04-20 | 修复5个严重Bug：无硬编码/动态密钥/OBFS参数 |
| v1.0.9 | 2026-04-20 | 修复 Systemd 环境变量隔离盲区 |
| v1.0.10 | 2026-04-20 | 终极验收：dotenv双保险/CF证书激活 |
| v1.0.11 | 2026-04-20 | 合并订阅/重装系统/非ROOT自动切换 |
| v1.0.12 | 2026-04-20 | 添加 VLESS-HTTPUpgrade 协议 (CDN节点) |
| v1.0.13 | 2026-04-20 | 修复CF证书API/Base64填充/iptables优化/域名提示 |
| v1.0.14 | 2026-04-20 | Clash自动分流订阅+TG机器人总控+CDN多源备用 |
| v1.0.15 | 2026-04-20 | 修复订阅安全漏洞+证书续签后订阅服务重启 |
| v1.0.16 | 2026-04-20 | 节点命名规则优化+CDN端口兼容Cloudflare |
| v1.0.17 | 2026-04-20 | 修复 config_generator.py 路径错误 (singbox-manager -> singbox-eps-node) |
| v1.0.18 | 2026-04-20 | 修复 VLESS 用户字段 id -> uuid (sing-box 1.10.0 兼容) |

---

## 最新更新内容 (v1.0.18)

### 重大 Bug 修复：VLESS 用户字段格式错误
- **问题**: sing-box 1.10.0 要求 VLESS 协议的 users 字段使用 `uuid` 而不是 `id`
- **表现**: `FATAL[0000] decode config: inbounds[X].users[0].id: json: unknown field "id"`
- **影响**: 所有 VLESS 节点 (Reality/WS/HTTPUpgrade) 无法启动，singbox 服务不断重启
- **修复方案**: 
  - 修改 `config_generator.py` 中所有 VLESS 节点的 users 字段：`"id"` → `"uuid"`
  - 涉及 3 个节点：vless-reality、vless-ws、vless-upgrade
- **避坑指南**: sing-box 不同版本对 VLESS 配置格式要求不同，1.9.x 用 `id`，1.10.x 用 `uuid`

### VPS 全自动部署完成
- **服务器**: 54.250.149.157 (AWS 日本)
- **域名**: jp.290372913.xyz
- **部署方式**: 全自动 SSH 脚本部署，无需手动操作
- **验证结果**: 所有服务 active，5 个节点正常，订阅链接可访问

### 当前节点列表 (5个)
| 节点名称 | 协议 | 传输 | 安全 | CDN | 端口 |
|----------|------|------|------|-----|------|
| JP-VLESS-Reality-CDN | VLESS | TCP | Reality | 是 | 443 |
| JP-VLESS-WS-CDN | VLESS | WebSocket | TLS | 是 | 8443 |
| JP-VLESS-HTTPUpgrade-CDN | VLESS | HTTPUpgrade | TLS | 是 | 2053 |
| JP-Trojan-WS-CDN | Trojan | WebSocket | TLS | 是 | 2083 |
| JP-Hysteria2 | Hysteria2 | UDP | TLS+salamander | 否 | 443 (跳跃 21000-21200) |

---

## 核心目录树
```
singbox-eps-node/
├── install.sh          # 主安装脚本 (v1.0.18)
├── scripts/
│   ├── config.py       # 配置中心 (从.env读取)
│   ├── config_generator.py  # Singbox配置生成器 (v1.0.18 uuid修复)
│   ├── subscription_service.py  # 订阅服务 (+Clash自动分流+Base64修复)
│   ├── cdn_monitor.py  # CDN监控 (+多源备用)
│   ├── cert_manager.py # 证书管理 (CF API修复)
│   ├── tg_bot.py       # TG机器人总控
│   └── logger.py       # 日志模块
├── docs/
│   └── architecture.md # 架构文档
├── project_snapshot.md # 项目状态快照
└── .git/
```

---

## 依赖库版本锁定
- Python 3
- Flask 3.0.2
- python-dotenv
- requests
- pyyaml
- Singbox 1.10.0
- iptables-persistent
- paramiko (部署脚本用)

---

## VPS 部署信息
- **服务器**: 54.250.149.157 (AWS 日本)
- **域名**: jp.290372913.xyz
- **订阅端口**: 6969
- **订阅路径**: /sub/JP
- **国家代码**: JP
- **Reality SNI**: www.apple.com
- **Hysteria2 端口跳跃**: 21000-21200 → 443

---

## 服务状态验证 (2026-04-20)
| 服务 | 状态 | 端口 |
|------|------|------|
| singbox | ✅ active | 443, 8443, 2053, 2083, 1080 |
| singbox-sub | ✅ active | 6969 |
| singbox-cdn | ✅ active | - |
| singbox-tgbot | ✅ active | - |

---

## 订阅链接
- **Base64**: `https://jp.290372913.xyz:6969/sub/JP`
- **Clash**: 使用 Clash 客户端访问同一地址（自动识别 User-Agent）

---

## 已知问题与解决方案
1. **VLESS 配置格式**: sing-box 1.10.0 使用 `uuid` 字段，不是 `id`
2. **CDN IP 文件**: 首次运行可能不存在，cdn_monitor.py 会自动生成
3. **Cloudflare 证书**: 需要域名已接入 Cloudflare 才能申请，否则使用自签证书

---

## 节点配置 (无硬编码)
| 节点 | 协议 | 说明 |
|------|------|------|
| ePS-JP-VLESS-Reality | VLESS+Reality | 殖民节点，苹果域名伪装 |
| ePS-JP-VLESS-WS | VLESS+WebSocket | CDN节点 |
| ePS-JP-Trojan-WS | Trojan+WebSocket | CDN节点 |
| ePS-JP-Hysteria2 | Hysteria2 | 直连节点，端口跳跃 21000-21200 |
| ePS-JP-SOCKS5 | SOCKS5 | 本地代理 (不出订阅) |

---

## GitHub 仓库
**仓库地址**: https://github.com/Alan-zzh/singbox-eps-node-v2

---

## 下一步待办 (Next Steps)
1. ~~修复 Reality 密钥生成~~
2. ~~修复 .env 初始化~~
3. ~~修复 PIP 安装问题~~
4. ~~移除硬编码~~
5. ~~修复 Hysteria2 obfs 参数~~
6. ~~重新上传 GitHub~~
7. ~~修复 Systemd 环境变量隔离~~
8. ~~Python dotenv 双保险~~
9. ~~激活 Cloudflare 15年证书~~
10. 服务器端完整安装测试
