#!/usr/bin/env python3
"""更新文档并提交"""
import os

LOCAL_DIR = r'd:\Documents\Syncdisk\工作用\job\S-ui\singbox-eps-node'
os.chdir(LOCAL_DIR)

snapshot = """# 项目状态快照 (Project Snapshot)

## 当前版本
**v1.0.36** (CDN优选IP改为实时DNS解析+每小时自动更新)

---

## 版本历史
| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.0.34 | 2026-04-20 | HTTPS订阅服务+Cloudflare正式证书+端口9443 |
| v1.0.35 | 2026-04-20 | 文档完善+CDN/SOCKS5状态确认+证书申请流程记录 |
| v1.0.36 | 2026-04-20 | CDN优选IP改为实时DNS解析+每小时自动更新 |

---

## 最新更新内容 (v1.0.36)

### CDN优选IP改为实时DNS解析
**之前的问题**: 写死了10个固定IP池，IP可能失效
**现在的方案**: 每小时通过湖南电信DNS实时解析获取最新Cloudflare IP

**工作流程**:
1. 使用湖南电信DNS（222.246.129.80, 59.51.78.210, 114.114.114.114）解析域名
2. 获取Cloudflare返回的IP列表
3. ping测试验证IP可达性
4. 分配给不同协议（每个协议独立IP）
5. 保存到数据库，订阅服务自动读取
6. 每小时重复一次

**当前优选IP** (2026-04-20 14:18):
- VLESS-WS: 104.21.35.190:8443
- VLESS-HTTPUpgrade: 172.67.178.214:2053
- Trojan-WS: 104.21.35.190:2083

### Cloudflare正式证书申请流程
**证书类型**: Let's Encrypt正式证书（通过acme.sh + Cloudflare DNS API）

**申请步骤**:
1. 安装acme.sh: `curl https://get.acme.sh | sh`
2. 配置Cloudflare API Token: `export CF_Token="你的Token"`
3. 申请证书: `~/.acme.sh/acme.sh --issue --dns dns_cf -d jp.290372913.xyz --server letsencrypt`
4. 安装证书到项目: 
```bash
~/.acme.sh/acme.sh --install-cert -d jp.290372913.xyz \\
    --cert-file /root/singbox-eps-node/cert/cert.pem \\
    --key-file /root/singbox-eps-node/cert/key.pem \\
    --fullchain-file /root/singbox-eps-node/cert/fullchain.pem
```

**Cloudflare凭证说明**:
- **类型**: API Token（43位字符串）
- **变量名**: `CF_Token`（acme.sh使用）
- **权限要求**: Zone.DNS编辑权限
- **获取方式**: Cloudflare控制台 → 个人资料 → API Tokens → 创建Token

**自动续期**: 
- cron任务: `48 8 * * *` (每天8:48自动检查续期)
- 证书有效期: 90天，到期前30天自动续期

---

## 当前服务状态
- **singbox**: active (端口443/8443/2053/2083)
- **singbox-sub**: active (HTTPS://0.0.0.0:9443)
- **singbox-cdn**: active (每小时DNS解析更新优选IP)
- **iptables**: 端口跳跃 22000-22200 -> 443
- **acme.sh**: 自动续期已配置 (每天8:48)

## 订阅链接
- **HTTPS**: https://jp.290372913.xyz:9443/sub/{国家代码}
- **示例**: https://jp.290372913.xyz:9443/sub/JP
- **证书**: Let's Encrypt正式证书，客户端信任

## 节点列表（6个）
1. JP-VLESS-Reality: 54.250.149.157:443 (直连)
2. JP-VLESS-WS-CDN: 优选IP:8443 (CDN，每小时更新)
3. JP-VLESS-HTTPUpgrade-CDN: 优选IP:2053 (CDN，每小时更新)
4. JP-Trojan-WS-CDN: 优选IP:2083 (CDN，每小时更新)
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
│   ├── cdn_monitor.py      # CDN监控脚本（每小时DNS解析）
│   ├── subscription_service.py  # 订阅服务（HTTPS）
│   └── config_generator.py # 配置生成器
├── logs/                   # 日志目录
└── backups/                # 备份目录
```

## 已知限制
1. **SOCKS5无自动切换**: 当前为固定配置，需要手动添加多个节点
2. **Hysteria2端口跳跃**: 使用iptables实现，sing-box本身不支持port_hopping字段
3. **cron任务重复**: CDN监控有8条重复cron任务，需清理

## 踩坑记录
1. **端口冲突**: 8443被singbox主服务占用，订阅服务改用9443
2. **SSL配置**: Flask的ssl_context需要fullchain.pem和key.pem
3. **acme.sh凭证**: API Token使用CF_Token变量，Global API Key使用CF_Key+CF_Email
4. **CDN IP写死**: 之前写死10个固定IP，改为每小时DNS实时解析

## 下一步待办
- [ ] 清理重复的cron任务
- [ ] 开发SOCKS5自动切换功能（需要更多节点）
- [ ] 验证HTTPS订阅在客户端的连通性
"""

with open(os.path.join(LOCAL_DIR, 'project_snapshot.md'), 'w', encoding='utf-8') as f:
    f.write(snapshot)
print('✅ project_snapshot.md已更新')

# 删除临时脚本
for f in ['check_socks5.py', 'check_cdn_method.py', 'check_db_ips.py', 'deploy_cdn.py', 'check_cdn_log.py', 'check_cdn_log2.py', 'update_docs.py']:
    path = os.path.join(LOCAL_DIR, f)
    if os.path.exists(path):
        os.remove(path)
        print(f'✅ 已删除: {f}')

print('\n✅ 完成')
