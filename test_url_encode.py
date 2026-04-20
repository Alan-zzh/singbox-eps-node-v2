#!/usr/bin/env python3
"""测试URL编码"""
import urllib.parse

path = '/trojan-ws'
encoded = urllib.parse.quote(path)
print(f'原始: {path}')
print(f'编码后: {encoded}')
print(f'是否包含%2F: {"%2F" in encoded}')
