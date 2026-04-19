# 项目状态快照 (Project Snapshot)

## 当前版本
**v1.0.10** (终极验收版)

---

## 版本历史
| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.0.0 | 2026-04-20 | 初始版本：模块化 Singbox 一键部署面板 |
| v1.0.8 | 2026-04-20 | 修复5个严重Bug：无硬编码/动态密钥/OBFS参数 |
| v1.0.9 | 2026-04-20 | 修复 Systemd 环境变量隔离盲区 |
| v1.0.10 | 2026-04-20 | 终极验收：dotenv双保险/CF证书激活 |

---

## 最新更新内容 (v1.0.10)

### 修复一：Python dotenv 双保险
- **问题**: 手动调试时 `os.getenv()` 读不到 `.env`
- **修复方案**: `subscription_service.py` 顶部新增 `from dotenv import load_dotenv; load_dotenv('/root/singbox-manager/.env')`
- **效果**: 无论手动运行还是 systemctl 启动，都能正确读取变量

### 修复二：Cloudflare 15年证书激活
- **问题**: `cert_manager.py` 已写好 CF API 证书申请，但 `install.sh` 没问用户要 Token
- **修复方案**: 
  - `generate_env_file()` 新增询问 `CF_API_TOKEN`
  - `.env` 新增 `CF_API_TOKEN` 字段
  - `generate_certificates()` 检测 Token 存在时自动调用 CF API 申请15年证书，失败自动降级自签
- **效果**: 用户可选择输入 CF Token 获得15年证书，或直接回车使用自签证书

---

## 核心目录树
```
singbox-eps-node/
├── install.sh          # 主安装脚本 (v1.0.10)
├── scripts/
│   ├── config.py       # 配置中心 (从.env读取)
│   ├── config_generator.py  # Singbox配置生成器
│   ├── subscription_service.py  # 订阅服务 (+dotenv)
│   ├── cdn_monitor.py  # CDN监控
│   ├── cert_manager.py # 证书管理 (CF API)
│   └── logger.py       # 日志模块
├── docs/
│   └── architecture.md # 架构文档
├── project_snapshot.md # 项目状态快照
└── .git/
```

---

## 依赖库版本锁定
- Python 3
- Flask (python3-flask)
- python3-dotenv
- python3-requests
- Singbox (最新版本)
- iptables-persistent

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
