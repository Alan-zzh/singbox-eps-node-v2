#!/usr/bin/env python3
"""测试订阅服务生成的链接"""
import urllib.parse

SERVER_IP = '54.250.149.157'
CF_DOMAIN = 'jp.290372913.xyz'
COUNTRY_CODE = 'JP'
TROJAN_PASSWORD = 'uG3hixuWQUJTq6_-Qiakow'
TROJAN_WS_PORT = 2083
trojan_ws_addr = '104.16.124.96'

# 当前订阅服务生成的Trojan链接
params = {
    'type': 'ws',
    'security': 'tls',
    'sni': CF_DOMAIN,
    'path': '/trojan-ws',
    'host': CF_DOMAIN,
    'allowInsecure': '1'
}
param_str = '&'.join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items() if v])
link = f"trojan://{TROJAN_PASSWORD}@{trojan_ws_addr}:{TROJAN_WS_PORT}?{param_str}#{COUNTRY_CODE}-Trojan-WS-CDN"
print('当前生成的Trojan链接:')
print(link)

# 用户提供的链接
user_link = 'trojan://uG3hixuWQUJTq6_-Qiakow@104.16.124.96:2083?security=tls&sni=jp.290372913.xyz&insecure=1&allowInsecure=1&type=ws&host=jp.290372913.xyz&path=%2Ftrojan-ws#JP-Trojan-WS-CDN'
print('\n用户提供的链接:')
print(user_link)

# 解析对比
print('\n【当前链接参数解析】')
parsed = urllib.parse.urlparse(link)
query = dict(urllib.parse.parse_qsl(parsed.query))
for k, v in query.items():
    print(f'  {k}={v}')

print('\n【用户链接参数解析】')
parsed2 = urllib.parse.urlparse(user_link)
query2 = dict(urllib.parse.parse_qsl(parsed2.query))
for k, v in query2.items():
    print(f'  {k}={v}')
