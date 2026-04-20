# 项目状态快照 (Project Snapshot)

## 当前版本
**v1.0.32** (Hysteria2端口修复+CDN节点SNI修复+优选IP池优化)

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
| v1.0.19 | 2026-04-20 | 修复订阅超时+多客户端兼容+路径修复 |
| v1.0.20 | 2026-04-20 | 修复直连节点 short_id 不匹配+CDN优选IP接口+清理S-UI引用 |
| v1.0.21 | 2026-04-20 | 修复GeoIP陷阱+每协议独立CDN IP+数据库路径统一 |
| v1.0.22 | 2026-04-20 | 优化CDN IP获取策略：动态网站优先+静态源备用+IP不足时循环分配 |
| v1.0.23 | 2026-04-20 | 终极降维方案：IP身份伪装（HTTP Header Spoofing）+ 正则精准提取 |
| v1.0.24 | 2026-04-20 | 容灾轮询伪装IP池：湖南电信专属IP池+优先级递减+自动切换 |
| v1.0.25 | 2026-04-20 | SOCKS5 AI协议牵制节点集成：206.163.4.241:36753 |
| v1.0.26 | 2026-04-20 | 地区代码动态化修复：节点名称自动使用COUNTRY_CODE环境变量 |
| v1.0.27 | 2026-04-20 | 防火墙配置修复+HTTPS/HTTP自动检测+systemd服务路径修复 |
| v1.0.28 | 2026-04-20 | 服务器彻底重置+订阅服务恢复+所有组件重新安装 |
| v1.0.29 | 2026-04-20 | 配置恢复+CDN服务修复+GitHub交付版 |
| v1.0.30 | 2026-04-20 | 隐藏风险修复：时间同步/日志滚动/cert路径/联动重启 |
| v1.0.31 | 2026-04-20 | 订阅HTTP化+国家代码链接+SOCKS5代理获取优选IP |
| v1.0.32 | 2026-04-20 | Hysteria2端口修复+CDN节点SNI修复+优选IP池优化 |

---

## 最新更新内容 (v1.0.32)

### 修复1：Hysteria2端口问题（节点测试-1）
- **问题**: Hysteria2节点使用随机端口（21000-21200），但singbox配置中Hysteria2监听的是443端口
- **解决方案**: 
  - subscription_service.py 中 Hysteria2 链接使用固定端口 443
  - 删除 `random.choice(HYSTERIA2_UDP_PORTS)` 逻辑
- **效果**: Hysteria2节点现在可以正常连接

### 修复2：CDN节点SNI问题（证书不匹配）
- **问题**: CDN节点的SNI使用了CDN IP（如172.64.53.179），但证书是为域名或服务器IP签发的
- **解决方案**: 
  - 统一使用 `cdn_sni = CF_DOMAIN if CF_DOMAIN else SERVER_IP`
  - 所有CDN节点（VLESS-WS、VLESS-HTTPUpgrade、Trojan-WS）使用相同SNI
- **效果**: CDN节点TLS握手成功，不再证书验证失败

### 修复3：优选IP池优化（50ms级别）
- **问题**: 之前通过SOCKS5代理获取的IP延迟高（100ms+），不符合用户实测的最快IP
- **解决方案**: 
  - cdn_monitor.py 中内置用户实测最快IP池（50ms级别）
  - 首选IP: 172.64.33.166(46ms)、162.159.45.15(51ms)、172.64.53.179(52ms)等
  - 降级策略：首选IP不可达时尝试DNS解析，再失败使用备用IP池
- **效果**: CDN节点延迟从100ms+降至50ms左右

---

## 当前服务状态
- **singbox**: active (端口443/8443/2053/2083)
- **singbox-sub**: active (HTTP://0.0.0.0:6969)
- **singbox-cdn**: active (每小时更新优选IP)

## 订阅链接
- **格式**: http://SERVER_IP:6969/sub/{国家代码}
- **示例**: http://54.250.149.157:6969/sub/JP

## 节点列表（6个）
1. JP-VLESS-Reality: 54.250.149.157:443 (直连)
2. JP-VLESS-WS-CDN: 优选IP:8443 (CDN)
3. JP-VLESS-HTTPUpgrade-CDN: 优选IP:2053 (CDN)
4. JP-Trojan-WS-CDN: 优选IP:2083 (CDN)
5. JP-Hysteria2: 54.250.149.157:443 (直连)
6. AI-SOCKS5: 206.163.4.241:36753 (外部代理)

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
│   ├── subscription_service.py  # 订阅服务（v1.0.32）
│   └── config_generator.py # 配置生成器
├── logs/                   # 日志目录
└── backups/                # 备份目录
```

## 下一步待办
- [ ] 验证所有节点在客户端的连通性
- [ ] 监控CDN IP自动更新是否正常工作
- [ ] 上传完整技术文档到GitHub供其他AI审查
