#!/usr/bin/env python3
"""
CDN监控脚本
Author: Alan
Version: v1.0.36
Date: 2026-04-20
功能：
  - 使用湖南电信DNS解析获取Cloudflare优选IP
  - 自动分配每个协议独立IP
  - 每小时自动更新，保证IP最新
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
            break
    
    return all_ips

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

def fetch_cdn_ips():
    """获取优选IP（通过湖南电信DNS实时解析）"""
    logger.info(f">>> 使用湖南电信DNS实时解析获取优选IP")
    
    dns_ips = resolve_via_dns()
    if dns_ips:
        logger.info(f"[OK] DNS解析获取 {len(dns_ips)} 个IP: {dns_ips}")
        
        valid_ips = []
        for ip in dns_ips:
            if ping_ip(ip):
                valid_ips.append(ip)
                if len(valid_ips) >= CDN_TOP_IPS_COUNT:
                    break
        
        if valid_ips:
            logger.info(f"[OK] 验证通过 {len(valid_ips)} 个IP: {valid_ips}")
            return valid_ips
        else:
            logger.warning("[WARN] 所有IP ping失败，返回原始DNS解析结果")
            return dns_ips[:CDN_TOP_IPS_COUNT]
    
    logger.error("[ERROR] DNS解析失败，无可用IP")
    return []

def assign_and_save_ips(ips):
    """分配并保存优选IP（每个协议独立IP）"""
    if not ips:
        return

    db_path = os.path.join(DATA_DIR, 'singbox.db')

    selected_ips = ips[:3] if len(ips) >= 3 else ips + [ips[0]] * (3 - len(ips))

    vless_ws_ip = selected_ips[0]
    vless_upgrade_ip = selected_ips[1]
    trojan_ws_ip = selected_ips[2]

    logger.info(f"\n>>> CDN优选IP（每个协议独立IP）:")
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
    else:
        logger.error("[ERROR] 未获取到任何IP，跳过本次更新")
    
    logger.info(f"\n>>> 等待 {MONITOR_INTERVAL}秒后下次检测...")

if __name__ == '__main__':
    init_db()
    while True:
        try:
            run_once()
            time.sleep(MONITOR_INTERVAL)
        except KeyboardInterrupt:
            logger.info("CDN监控已停止")
            break
        except Exception as e:
            logger.error(f"[ERROR] {e}")
            time.sleep(60)
