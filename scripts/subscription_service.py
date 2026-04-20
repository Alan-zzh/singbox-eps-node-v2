#!/usr/bin/env python3
"""
订阅服务 - Flask应用
Author: Alan
Version: v1.0.39
Date: 2026-04-20
功能：
  - 提供Base64订阅链接（包含所有节点）
  - 提供完整sing-box JSON配置（含自动路由规则）
  - CDN优选IP自动分配（每个协议独立IP）
  - HTTPS支持（Cloudflare正式证书）

订阅链接格式: 
  - Base64: https://SERVER_IP:9443/sub/{国家代码}
  - sing-box JSON: https://SERVER_IP:9443/singbox/{国家代码}

节点命名规则: {国家代码}-{协议}
- JP-VLESS-Reality (直连节点，苹果域名伪装)
- JP-VLESS-WS (CDN节点，独立优选IP)
- JP-VLESS-HTTPUpgrade (CDN节点，独立优选IP)
- JP-Trojan-WS (CDN节点，独立优选IP)
- JP-Hysteria2 (直连节点，端口跳跃)
- AI-SOCKS5 (外部代理节点)
"""

import os
import sys
import base64
import urllib.parse
import sqlite3
import random
import json
from datetime import datetime
import ssl

from dotenv import load_dotenv
load_dotenv('/root/singbox-eps-node/.env')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import (
        SERVER_IP, CF_DOMAIN, DATA_DIR, CERT_DIR, DB_FILE, SUB_PORT,
        VLESS_WS_PORT, VLESS_UPGRADE_PORT, TROJAN_WS_PORT, HYSTERIA2_PORT, SOCKS5_PORT,
        HYSTERIA2_UDP_PORTS, REALITY_SHORT_ID, REALITY_DEST, REALITY_SNI,
        AI_SOCKS5_SERVER, AI_SOCKS5_PORT, AI_SOCKS5_USER, AI_SOCKS5_PASS
    )
    from logger import get_logger
except ImportError:
    def get_logger(name):
        import logging
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(name)

logger = get_logger('subscription_service')

SERVER_IP = os.getenv('SERVER_IP', '')
CF_DOMAIN = os.getenv('CF_DOMAIN', '')
DB_PATH = DB_FILE if 'DB_FILE' in dir() else os.path.join(DATA_DIR, 'singbox.db')
SUB_PORT = int(os.getenv('SUB_PORT', '6969'))
COUNTRY_CODE = os.getenv('COUNTRY_CODE', 'JP')
USE_DOMAIN = bool(CF_DOMAIN and CF_DOMAIN.strip() != '')

VLESS_UUID = os.getenv('VLESS_UUID', '')
VLESS_WS_UUID = os.getenv('VLESS_WS_UUID', '')
VLESS_UPGRADE_PORT = int(os.getenv('VLESS_UPGRADE_PORT', '2053'))
TROJAN_PASSWORD = os.getenv('TROJAN_PASSWORD', '')
HYSTERIA2_PASSWORD = os.getenv('HYSTERIA2_PASSWORD', '')
REALITY_PUBLIC_KEY = os.getenv('REALITY_PUBLIC_KEY', '')
REALITY_SHORT_ID = os.getenv('REALITY_SHORT_ID', 'abcd1234')
REALITY_DEST = os.getenv('REALITY_DEST', 'www.apple.com:443')
REALITY_SNI = os.getenv('REALITY_SNI', 'www.apple.com')
EXTERNAL_SUBS = os.getenv('EXTERNAL_SUBS', '')

HYSTERIA2_UDP_PORTS = list(range(21000, 21201))

def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cdn_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_cdn_ip_for_protocol(protocol_key):
    """获取指定协议的CDN优选IP"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM cdn_settings WHERE key=?", (protocol_key,))
        row = cursor.fetchone()
        conn.close()
        if row and row[0] and row[0] != SERVER_IP:
            return row[0]
    except Exception:
        pass
    if CF_DOMAIN and CF_DOMAIN.strip():
        return CF_DOMAIN
    return SERVER_IP

def get_sub_address():
    """获取订阅服务地址（域名或IP）"""
    if CF_DOMAIN and CF_DOMAIN.strip():
        return CF_DOMAIN
    return SERVER_IP

def generate_all_links():
    """生成所有节点链接"""
    links = []

    vless_ws_addr = get_cdn_ip_for_protocol('vless_ws_cdn_ip')
    vless_upgrade_addr = get_cdn_ip_for_protocol('vless_upgrade_cdn_ip')
    trojan_ws_addr = get_cdn_ip_for_protocol('trojan_ws_cdn_ip')

    use_cdn = (vless_ws_addr != SERVER_IP)
    cdn_suffix = "-CDN" if use_cdn else ""

    # CDN节点的SNI：优先使用域名，没有域名则使用服务器IP
    cdn_sni = CF_DOMAIN if (CF_DOMAIN and CF_DOMAIN.strip()) else SERVER_IP

    # 1. VLESS-Reality (直连)
    params = {
        'encryption': 'none',
        'flow': 'xtls-rprx-vision',
        'type': 'tcp',
        'security': 'reality',
        'sni': REALITY_SNI,
        'fp': 'chrome',
        'pbk': REALITY_PUBLIC_KEY,
        'sid': REALITY_SHORT_ID,
        'spx': '',
        'dest': REALITY_DEST,
        'headerType': 'none'
    }
    param_str = '&'.join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items() if v])
    links.append(f"vless://{VLESS_UUID}@{SERVER_IP}:443?{param_str}#{COUNTRY_CODE}-VLESS-Reality")

    # 2. VLESS-WS (CDN)
    params = {
        'encryption': 'none',
        'type': 'ws',
        'security': 'tls',
        'sni': cdn_sni,
        'path': '/vless-ws',
        'host': cdn_sni,
        'allowInsecure': '1'
    }
    param_str = '&'.join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items() if v])
    links.append(f"vless://{VLESS_WS_UUID}@{vless_ws_addr}:{VLESS_WS_PORT}?{param_str}#{COUNTRY_CODE}-VLESS-WS{cdn_suffix}")

    # 3. VLESS-HTTPUpgrade (CDN)
    params = {
        'encryption': 'none',
        'type': 'httpupgrade',
        'security': 'tls',
        'sni': cdn_sni,
        'path': '/vless-upgrade',
        'host': cdn_sni,
        'allowInsecure': '1'
    }
    param_str = '&'.join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items() if v])
    links.append(f"vless://{VLESS_WS_UUID}@{vless_upgrade_addr}:{VLESS_UPGRADE_PORT}?{param_str}#{COUNTRY_CODE}-VLESS-HTTPUpgrade{cdn_suffix}")

    # 4. Trojan-WS (CDN)
    params = {
        'type': 'ws',
        'security': 'tls',
        'sni': cdn_sni,
        'insecure': '1',
        'allowInsecure': '1',
        'path': '/trojan-ws',
        'host': cdn_sni,
    }
    param_str = '&'.join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items() if v])
    links.append(f"trojan://{TROJAN_PASSWORD}@{trojan_ws_addr}:{TROJAN_WS_PORT}?{param_str}#{COUNTRY_CODE}-Trojan-WS{cdn_suffix}")

    # 5. Hysteria2 (直连) - 端口443，iptables端口跳跃22000-22200
    params = {
        'sni': REALITY_SNI,
        'insecure': '1',
        'obfs': 'salamander',
        'obfs-password': HYSTERIA2_PASSWORD[:8],
        'mport': '443,22000-22200'
    }
    param_str = '&'.join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items() if v])
    links.append(f"hysteria2://{HYSTERIA2_PASSWORD}@{SERVER_IP}:443?{param_str}#{COUNTRY_CODE}-Hysteria2")

    # 6. SOCKS5 (AI协议牵制节点)
    socks5_link = f"socks5://4KKsLB7F:KgEKVmVgxJ@206.163.4.241:36753#AI-SOCKS5"
    links.append(socks5_link)

    return links

def generate_singbox_config():
    """生成完整sing-box JSON配置（含自动路由规则）"""
    vless_ws_addr = get_cdn_ip_for_protocol('vless_ws_cdn_ip')
    vless_upgrade_addr = get_cdn_ip_for_protocol('vless_upgrade_cdn_ip')
    trojan_ws_addr = get_cdn_ip_for_protocol('trojan_ws_cdn_ip')

    cdn_sni = CF_DOMAIN if (CF_DOMAIN and CF_DOMAIN.strip()) else SERVER_IP

    config = {
        "log": {
            "level": "info",
            "timestamp": True
        },
        "dns": {
            "servers": [
                {
                    "tag": "dns_proxy",
                    "address": "tls://8.8.8.8",
                    "detour": "ePS-Auto"
                },
                {
                    "tag": "dns_direct",
                    "address": "h3://dns.alidns.com/dns-query",
                    "detour": "direct"
                },
                {
                    "tag": "dns_block",
                    "address": "rcode://success"
                },
                {
                    "tag": "dns_fakeip",
                    "address": "fakeip"
                }
            ],
            "rules": [
                {
                    "outbound": "any",
                    "server": "dns_direct"
                },
                {
                    "geosite": "cn",
                    "server": "dns_direct"
                },
                {
                    "geosite": "geolocation-!cn",
                    "server": "dns_proxy"
                }
            ],
            "final": "dns_proxy",
            "fakeip": {
                "enabled": True,
                "inet4_range": "198.18.0.0/15"
            }
        },
        "inbounds": [
            {
                "type": "mixed",
                "tag": "mixed-in",
                "listen": "127.0.0.1",
                "listen_port": 2080
            },
            {
                "type": "tun",
                "tag": "tun-in",
                "inet4_address": "172.19.0.1/30",
                "auto_route": True,
                "strict_route": True,
                "stack": "mixed"
            }
        ],
        "outbounds": [
            {
                "type": "selector",
                "tag": "ePS-Auto",
                "outbounds": [
                    f"{COUNTRY_CODE}-VLESS-Reality",
                    f"{COUNTRY_CODE}-VLESS-WS",
                    f"{COUNTRY_CODE}-VLESS-HTTPUpgrade",
                    f"{COUNTRY_CODE}-Trojan-WS",
                    f"{COUNTRY_CODE}-Hysteria2",
                    "AI-SOCKS5",
                    "direct"
                ],
                "default": f"{COUNTRY_CODE}-VLESS-Reality"
            },
            {
                "type": "selector",
                "tag": "ai-residential",
                "outbounds": ["AI-SOCKS5"],
                "default": "AI-SOCKS5"
            },
            {
                "type": "direct",
                "tag": "direct"
            },
            {
                "type": "block",
                "tag": "block"
            },
            {
                "type": "dns",
                "tag": "dns-out"
            },
            # VLESS-Reality
            {
                "type": "vless",
                "tag": f"{COUNTRY_CODE}-VLESS-Reality",
                "server": SERVER_IP,
                "server_port": 443,
                "uuid": VLESS_UUID,
                "flow": "xtls-rprx-vision",
                "packet_encoding": "xudp",
                "tls": {
                    "enabled": True,
                    "server_name": REALITY_SNI,
                    "utls": {
                        "enabled": True,
                        "fingerprint": "chrome"
                    },
                    "reality": {
                        "enabled": True,
                        "public_key": REALITY_PUBLIC_KEY,
                        "short_id": REALITY_SHORT_ID
                    }
                }
            },
            # VLESS-WS (CDN)
            {
                "type": "vless",
                "tag": f"{COUNTRY_CODE}-VLESS-WS",
                "server": vless_ws_addr,
                "server_port": VLESS_WS_PORT,
                "uuid": VLESS_WS_UUID,
                "packet_encoding": "xudp",
                "tls": {
                    "enabled": True,
                    "server_name": cdn_sni,
                    "insecure": True,
                    "utls": {
                        "enabled": True,
                        "fingerprint": "chrome"
                    }
                },
                "transport": {
                    "type": "ws",
                    "path": "/vless-ws",
                    "headers": {
                        "Host": cdn_sni
                    }
                }
            },
            # VLESS-HTTPUpgrade (CDN)
            {
                "type": "vless",
                "tag": f"{COUNTRY_CODE}-VLESS-HTTPUpgrade",
                "server": vless_upgrade_addr,
                "server_port": VLESS_UPGRADE_PORT,
                "uuid": VLESS_WS_UUID,
                "packet_encoding": "xudp",
                "tls": {
                    "enabled": True,
                    "server_name": cdn_sni,
                    "insecure": True,
                    "utls": {
                        "enabled": True,
                        "fingerprint": "chrome"
                    }
                },
                "transport": {
                    "type": "httpupgrade",
                    "path": "/vless-upgrade",
                    "host": cdn_sni
                }
            },
            # Trojan-WS (CDN)
            {
                "type": "trojan",
                "tag": f"{COUNTRY_CODE}-Trojan-WS",
                "server": trojan_ws_addr,
                "server_port": TROJAN_WS_PORT,
                "password": TROJAN_PASSWORD,
                "tls": {
                    "enabled": True,
                    "server_name": cdn_sni,
                    "insecure": True
                },
                "transport": {
                    "type": "ws",
                    "path": "/trojan-ws",
                    "headers": {
                        "Host": cdn_sni
                    }
                }
            },
            # Hysteria2
            {
                "type": "hysteria2",
                "tag": f"{COUNTRY_CODE}-Hysteria2",
                "server": SERVER_IP,
                "server_port": 443,
                "password": HYSTERIA2_PASSWORD,
                "tls": {
                    "enabled": True,
                    "server_name": REALITY_SNI,
                    "insecure": True
                },
                "obfs": {
                    "type": "salamander",
                    "password": HYSTERIA2_PASSWORD[:8]
                },
                "up_mbps": 100,
                "down_mbps": 100
            },
            # AI-SOCKS5
            {
                "type": "socks",
                "tag": "AI-SOCKS5",
                "server": "206.163.4.241",
                "server_port": 36753,
                "version": "5",
                "username": "4KKsLB7F",
                "password": "KgEKVmVgxJ"
            }
        ],
        "route": {
            "rules": [
                {
                    "protocol": "dns",
                    "outbound": "dns-out"
                },
                {
                    "ip_is_private": True,
                    "outbound": "direct"
                },
                {
                    "geosite": "cn",
                    "geoip": ["cn", "private"],
                    "outbound": "direct"
                },
                # AI网站自动走SOCKS5（无感路由）
                {
                    "domain_suffix": [
                        "openai.com",
                        "chatgpt.com",
                        "anthropic.com",
                        "claude.ai",
                        "gemini.google.com",
                        "bard.google.com",
                        "ai.google",
                        "aistudio.google.com",
                        "perplexity.ai",
                        "midjourney.com",
                        "stability.ai",
                        "cohere.com",
                        "replicate.com",
                        "google.com",
                        "googleapis.com",
                        "gstatic.com"
                    ],
                    "domain_keyword": [
                        "openai",
                        "anthropic",
                        "claude",
                        "gemini",
                        "perplexity",
                        "aistudio"
                    ],
                    "outbound": "ai-residential"
                },
                # 排除X/推特/groK（不走SOCKS5）
                {
                    "domain_suffix": [
                        "x.com",
                        "twitter.com",
                        "twimg.com",
                        "t.co",
                        "x.ai",
                        "grok.com"
                    ],
                    "domain_keyword": [
                        "twitter",
                        "grok"
                    ],
                    "outbound": "direct"
                }
            ],
            "auto_detect_interface": True,
            "final": "ePS-Auto"
        },
        "experimental": {
            "cache_file": {
                "enabled": True
            },
            "clash_api": {
                "external_controller": "127.0.0.1:9090",
                "external_ui": "dashboard"
            }
        }
    }

    return config

def create_app():
    """创建Flask应用"""
    from flask import Flask, Response, jsonify, request

    app = Flask(__name__)

    @app.route('/')
    def home():
        html = """
        <html>
        <head>
            <title>Singbox订阅服务</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
                h1 {{ color: #333; }}
                .sub-box {{ background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0; }}
                .sub-link {{ font-size: 18px; color: #0066cc; word-break: break-all; }}
                .info {{ color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <h1>Singbox 订阅服务</h1>
            <div class="sub-box">
                <p><strong>Base64订阅链接：</strong></p>
                <p class="sub-link">https://{server}:{port}/sub/{country}</p>
                <p class="info">（包含6个节点：{country}-VLESS-Reality、{country}-VLESS-WS、{country}-VLESS-HTTPUpgrade、{country}-Trojan-WS、{country}-Hysteria2、AI-SOCKS5）</p>
            </div>
            <div class="sub-box">
                <p><strong>sing-box JSON配置（含自动路由）：</strong></p>
                <p class="sub-link">https://{server}:{port}/singbox/{country}</p>
                <p class="info">（导入后AI流量自动走SOCKS5，无需手动选择）</p>
            </div>
            <div class="info">
                <p>服务器IP: {server}</p>
                <p>域名: {domain}</p>
                <p>使用HTTPS: 是</p>
            </div>
        </body>
        </html>
        """.format(
            server=CF_DOMAIN if (CF_DOMAIN and CF_DOMAIN.strip()) else SERVER_IP,
            port=SUB_PORT,
            country=COUNTRY_CODE,
            domain=CF_DOMAIN if CF_DOMAIN else '未配置'
        )
        return Response(html, mimetype='text/html')

    @app.route(f'/sub/{COUNTRY_CODE}')
    @app.route('/sub')
    def get_subscription():
        """Base64订阅链接（兼容旧客户端）"""
        links = generate_all_links()
        if EXTERNAL_SUBS and EXTERNAL_SUBS.strip():
            for sub_url in EXTERNAL_SUBS.split('|'):
                sub_url = sub_url.strip()
                if sub_url:
                    try:
                        req = urllib.request.Request(sub_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=5) as resp:
                            raw = resp.read().decode('utf-8').strip()
                            try:
                                padded_raw = raw + '=' * (-len(raw) % 4)
                                decoded = base64.b64decode(padded_raw).decode('utf-8')
                                links.extend([line for line in decoded.split('\n') if line.strip()])
                            except Exception:
                                links.append(raw)
                    except Exception as e:
                        logger.warning(f"Failed to fetch external sub {sub_url}: {e}")
        sub_text = '\n'.join(links)
        sub_b64 = base64.b64encode(sub_text.encode('utf-8')).decode('utf-8')
        return Response(sub_b64, mimetype='text/plain')

    @app.route(f'/singbox/{COUNTRY_CODE}')
    @app.route('/singbox')
    def get_singbox_config():
        """完整sing-box JSON配置（含自动路由规则）"""
        config = generate_singbox_config()
        return Response(
            json.dumps(config, indent=2, ensure_ascii=False),
            mimetype='application/json',
            headers={'Content-Disposition': 'attachment; filename=singbox-config.json'}
        )

    @app.route('/api/cdn', methods=['GET', 'POST'])
    def cdn_api():
        if request.method == 'POST':
            data = request.get_json()
            protocol = data.get('protocol', '').strip()
            new_ip = data.get('ip', '').strip()
            if not protocol or not new_ip:
                return jsonify({'error': 'protocol and ip required'}), 400
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO cdn_settings (key, value) VALUES (?, ?)", (protocol, new_ip))
                conn.commit()
                conn.close()
                return jsonify({'message': 'OK', 'protocol': protocol, 'ip': new_ip})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM cdn_settings")
                rows = cursor.fetchall()
                conn.close()
                result = {row[0]: row[1] for row in rows}
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    return app

if __name__ == '__main__':
    init_db()
    app = create_app()
    logger.info(f"Starting HTTPS subscription service on 0.0.0.0:{SUB_PORT}")
    logger.info(f"Base64订阅: https://SERVER_IP:{SUB_PORT}/sub/{COUNTRY_CODE}")
    logger.info(f"sing-box JSON: https://SERVER_IP:{SUB_PORT}/singbox/{COUNTRY_CODE}")
    app.run(host='0.0.0.0', port=SUB_PORT, threaded=True)
