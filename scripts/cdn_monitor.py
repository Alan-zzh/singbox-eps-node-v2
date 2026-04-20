#!/usr/bin/env python3
"""
CDN监控脚本
Author: Alan
Version: v1.0.37
Date: 2026-04-20
功能：
  - 使用固定优选IP池（中国用户实测延迟低）
  - 每小时随机轮换IP，避免IP失效
  - 自动分配每个协议独立IP
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

# 中国用户实测最快的Cloudflare IP池（50ms左右，按延时排序）
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
    '172.67.178.214',   # 备用
    '104.21.35.190',    # 备用
    '104.16.123.96',    # 备用
    '104.16.124.96',    # 备用
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
    """获取优选IP（从固定IP池随机选择并验证）"""
    logger.info(f">>> 从固定优选IP池随机选择（中国用户实测最快）")
    
    # 随机打乱IP池
    shuffled_ips = PREFERRED_IPS.copy()
    random.shuffle(shuffled_ips)
    
    # 验证IP是否可达
    valid_ips = []
    for ip in shuffled_ips:
        if ping_ip(ip):
            valid_ips.append(ip)
            if len(valid_ips) >= CDN_TOP_IPS_COUNT:
                break
    
    if valid_ips:
        logger.info(f"[OK] 验证通过 {len(valid_ips)} 个IP: {valid_ips}")
        return valid_ips
    else:
        logger.warning("[WARN] 所有IP ping失败，返回前5个IP")
        return PREFERRED_IPS[:CDN_TOP_IPS_COUNT]

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
