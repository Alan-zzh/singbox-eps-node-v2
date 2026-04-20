#!/usr/bin/env python3
"""清理临时脚本并提交到GitHub"""
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

# 需要保留的核心文件
KEEP_FILES = {
    'scripts/', 'docs/', 'README.md', 'project_snapshot.md', 
    'install.sh', '.gitignore', 'fix_all.py'
}

# 需要删除的临时脚本模式
DELETE_PATTERNS = [
    'analyze_*.py', 'cdn_monitor_*.py', 'check_*.py', 'debug_*.py',
    'deploy_*.py', 'extract_*.py', 'final_*.py', 'find_*.py',
    'fix_*.py', 'full_*.py', 'generate_*.py', 'quick_*.py',
    'restart_*.py', 'restore_*.py', 'scrape_*.py', 'test_*.py',
    'update_*.py', 'upload_*.py', 'verify_*.py', 'wait_*.py',
    '*.sh'  # 除了install.sh
]

print('【1. 删除临时脚本】')
deleted = []
for f in os.listdir(PROJECT_DIR):
    full_path = os.path.join(PROJECT_DIR, f)
    if os.path.isfile(full_path):
        # 保留install.sh和fix_all.py
        if f in ('install.sh', 'fix_all.py'):
            continue
        # 删除所有临时脚本
        if f.endswith('.py') or f.endswith('.sh'):
            os.remove(full_path)
            deleted.append(f)
            print(f'  已删除: {f}')

print(f'\n  共删除 {len(deleted)} 个临时文件')

print('\n【2. 添加所有文件】')
out, err = run('git add -A')
print('  OK')

print('\n【3. 查看状态】')
out, err = run('git status --short')
print(f'  {out}')

print('\n【4. 提交】')
out, err = run('git commit -m "v1.0.32: clean up temp scripts + finalize project structure"')
print(f'  {out if out else err}')

print('\n【5. 推送】')
out, err = run('git push origin main', timeout=120)
print(f'  {out if out else err}')

print('\n✅ 完成')
