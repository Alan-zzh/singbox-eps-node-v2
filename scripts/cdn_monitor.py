#!/usr/bin/env python3
"""
CDN监控脚本
Author: Alan
Version: v1.0.32
Date: 2026-04-20
功能：
  - 使用湖南电信DNS解析获取Cloudflare优选IP
  - 自动分配每个协议独立IP
  - 首选IP池：用户实测最快的IP（50ms左右）
"""

import os
import sys
import time
import sqlite3
import random
import re
import requests
import subprocess
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import (
        SERVER_IP, DATA_DIR, CF_DOMAIN,
        CDN_DB_URL, CDN_MONITOR_INTERVAL, CDN_TOP_IPS_COUNT,
        AI_SOCKS5_SERVER, AI_SOCKS5_PORT, AI_SOCKS5_USER, AI_SOCKS5_PASS
    )
    from logger import get_logger
except ImportError:
    def get_logger(name):
        import logging
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(name)

logger = get_logger('cdn_monitor')

# 湖南电信DNS服务器
HUNAN_DNS = ['222.246.129.80', '59.51.78.210', '114.114.114.114']

# 用户实测最快的Cloudflare IP池（50ms左右，按延时排序）
# 来源：用户本地通过湖南电信DNS实测
PREFERRED_IPS = [
    '172.64.33.166',    # 46.06ms - 最快
    '162.159.45.15',    # 51.39ms
    '172.64.53.179',    # 51.98ms
    '108.162.198.145',  # 52.01ms
    '172.64.52.205',    # 52.41ms
    '162.159.44.103',   # 52.51ms
    '162.159.39.190',   # 52.68ms
    '162.159.38.26',    # 53.14ms
    '162.159.7.250',    # 53.83ms
    '104.18.37.65',     # 53.78ms
]

# 备用IP池（100ms+，较慢）
BACKUP_IPS = [
    '104.26.6.15',
    '104.26.5.196',
    '104.20.18.86',
    '172.67.76.251',
    '172.67.75.190',
    '104.16.1.1',
    '104.16.132.229',
    '104.17.1.1',
]

CDN_TOP_IPS_COUNT = 5
MONITOR_INTERVAL = 3600

def init_db():
    """初始化数据库"""
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(os.path.join(DATA_DIR, 'singbox.db'))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cdn_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()
    return os.path.join(DATA_DIR, 'singbox.db')

def fetch_cdn_ips():
    """获取优选IP（优先使用用户实测最快IP池）"""
    # 策略1：直接使用用户实测最快的IP池（50ms左右）
    logger.info(f">>> 使用用户实测最快IP池（50ms级别）")
    logger.info(f">>> 首选IP: {PREFERRED_IPS[:5]}")
    
    # 验证IP是否可达（ping测试）
    valid_ips = []
    for ip in PREFERRED_IPS:
        if ping_ip(ip):
            valid_ips.append(ip)
            if len(valid_ips) >= CDN_TOP_IPS_COUNT:
                break
    
    if valid_ips:
        logger.info(f"[OK] 验证通过 {len(valid_ips)} 个最快IP: {valid_ips}")
        return valid_ips
    
    # 策略2：如果首选IP都不可达，尝试通过DNS解析获取
    logger.info(">>> 首选IP不可达，尝试DNS解析获取...")
    dns_ips = resolve_via_dns()
    if dns_ips:
        logger.info(f"[OK] DNS解析获取IP: {dns_ips}")
        return dns_ips
    
    # 策略3：使用备用IP池
    logger.warning("[WARN] DNS解析失败，使用备用IP池")
    return BACKUP_IPS[:CDN_TOP_IPS_COUNT]

def ping_ip(ip, timeout=3):
    """ping测试IP是否可达"""
    try:
        result = subprocess.run(
            ['ping', '-c', '1', '-W', str(timeout), ip],
            capture_output=True, text=True, timeout=timeout + 1
        )
        return result.returncode == 0
    except:
        return False

def resolve_via_dns():
    """通过湖南电信DNS解析CF域名获取IP"""
    cf_domains = [
        'jp.290372913.xyz',
        'cf.290372913.xyz',
        'cdn.290372913.xyz',
    ]
    
    all_ips = []
    for dns_server in HUNAN_DNS:
        for domain in cf_domains:
            try:
                result = subprocess.run(
                    ['dig', '+short', domain, f'@{dns_server}'],
                    capture_output=True, text=True, timeout=5
                )
                if result.stdout.strip():
                    for line in result.stdout.strip().split('\n'):
                        ip = line.strip()
                        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                            if ip not in all_ips:
                                all_ips.append(ip)
            except:
                continue
        
        if all_ips:
            break  # 获取到IP就停止
    
    return all_ips[:CDN_TOP_IPS_COUNT] if all_ips else []

def assign_and_save_ips(ips):
    """分配并保存优选IP（前10个随机选3个，每个协议独立IP）"""
    if not ips:
        return

    db_path = os.path.join(DATA_DIR, 'singbox.db')

    # 从前10个IP中随机选3个不同的IP
    top_10_ips = ips[:10]
    if len(top_10_ips) >= 3:
        selected_ips = random.sample(top_10_ips, 3)
    else:
        # IP不足3个时，循环使用已有的IP
        selected_ips = []
        for i in range(3):
            selected_ips.append(top_10_ips[i % len(top_10_ips)])

    vless_ws_ip = selected_ips[0]
    vless_upgrade_ip = selected_ips[1]
    trojan_ws_ip = selected_ips[2]

    logger.info(f"\n>>> CDN优选IP（前10随机选3，每个协议独立IP）:")
    logger.info(f"  候选IP: {top_10_ips}")
    logger.info(f"  VLESS-WS IP: {vless_ws_ip}")
    logger.info(f"  VLESS-HTTPUpgrade IP: {vless_upgrade_ip}")
    logger.info(f"  Trojan-WS IP: {trojan_ws_ip}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO cdn_settings (key, value) VALUES (?, ?)", ('vless_ws_cdn_ip', vless_ws_ip))
    cursor.execute("INSERT OR REPLACE INTO cdn_settings (key, value) VALUES (?, ?)", ('vless_upgrade_cdn_ip', vless_upgrade_ip))
    cursor.execute("INSERT OR REPLACE INTO cdn_settings (key, value) VALUES (?, ?)", ('trojan_ws_cdn_ip', trojan_ws_ip))
    cursor.execute("INSERT OR REPLACE INTO cdn_settings (key, value) VALUES (?, ?)", ('cdn_ips_list', ','.join(ips)))
    cursor.execute("INSERT OR REPLACE INTO cdn_settings (key, value) VALUES (?, ?)", ('cdn_updated_at', datetime.now().isoformat()))
    conn.commit()
    conn.close()
    logger.info(f"\n[OK] CDN优选IP已保存")

def run_once():
    """执行一次监控"""
    logger.info("\n" + "="*50)
    logger.info(f"CDN监控启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*50)

    ips = fetch_cdn_ips()
    if ips:
        assign_and_save_ips(ips)

def run_daemon():
    """守护进程模式"""
    logger.info("CDN监控守护进程模式")
    logger.info(f"监控间隔: {MONITOR_INTERVAL}秒")

    while True:
        try:
            run_once()
            logger.info(f"\n>>> 等待 {MONITOR_INTERVAL}秒后下次检测...")
            time.sleep(MONITOR_INTERVAL)
        except KeyboardInterrupt:
            logger.info("\n监控已停止")
            break
        except Exception as e:
            logger.error(f"\n[ERROR] 监控错误: {e}")
            time.sleep(60)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--daemon":
        run_daemon()
    else:
        run_once()
