#!/usr/bin/env python3
"""提交最终版本到GitHub"""
import subprocess
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
PROJECT_DIR = r'd:\Documents\Syncdisk\工作用\job\S-ui\singbox-eps-node'
os.chdir(PROJECT_DIR)

def run(cmd, timeout=60):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=PROJECT_DIR, 
                          encoding='utf-8', errors='replace', timeout=timeout)
    return result.stdout.strip(), result.stderr.strip()

print('【1. 添加所有文件】')
out, err = run('git add -A')
print('  OK')

print('\n【2. 查看状态】')
out, err = run('git status --short')
print(f'  {out if out else "无变更"}')

print('\n【3. 提交】')
out, err = run('git commit -m "v1.0.32: finalize - sync server files + update docs"')
print(f'  {out if out else "无新提交"}')

print('\n【4. 推送】')
out, err = run('git push origin main', timeout=120)
print(f'  {out if out else err}')

print('\n【5. 最终仓库结构】')
out, err = run('git ls-files')
print(f'  仓库文件:\n{out}')

print('\n✅ 完成')
