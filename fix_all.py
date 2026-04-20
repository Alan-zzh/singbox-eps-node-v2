#!/usr/bin/env python3
"""从本地推送代码到GitHub"""
import subprocess
import os

PROJECT_DIR = r'd:\Documents\Syncdisk\工作用\job\S-ui\singbox-eps-node'
os.chdir(PROJECT_DIR)

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=PROJECT_DIR)
    return result.stdout.strip(), result.stderr.strip()

print('【1. 检查Git状态】')
out, err = run('git status --short')
print(f'  {out if out else "无变更"}')

print('\n【2. 检查远程仓库】')
out, err = run('git remote -v')
print(f'  {out if out else "无远程仓库"}')

print('\n【3. 添加所有文件】')
out, err = run('git add -A')
print(f'  {err if err else "OK"}')

print('\n【4. 查看状态】')
out, err = run('git status --short')
print(f'  待提交文件:\n{out}')

print('\n【5. 提交】')
out, err = run('git commit -m "v1.0.32: 修复Hysteria2端口+CDN节点SNI+优选IP池优化"')
print(f'  {out if out else err}')

print('\n【6. 推送】')
out, err = run('git push origin main')
print(f'  {out if out else err}')

print('\n✅ 完成')
