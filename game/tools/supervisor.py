# -*- coding: utf-8 -*-
"""项目监督者：守护游戏服务器 + 周期性健康检查 + 自动回归测试。

被 cron 自动化定期调用；也可手动运行：python3 tools/supervisor.py [--once]
逻辑：
  1. 健康探测 /api/health，失败 → 等 60 秒重试，连续失败 → 自动拉起服务器
  2. 服务器存活但测试失败 → 记录日志（不改动代码，留给人修）
  3. 全部通过 → 记录心跳
"""
import json
import os
import subprocess
import sys
import time
import urllib.request

# 绕过系统代理：localhost 健康探测被代理拦截会误判服务器宕机
urllib.request.install_opener(
    urllib.request.build_opener(urllib.request.ProxyHandler({})))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # 本脚本在 tools/，游戏根目录是上一层
LOG_DIR = os.path.join(ROOT, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG = os.path.join(LOG_DIR, 'supervisor.log')
PORT = 8300
BASE = 'http://127.0.0.1:%d' % PORT


def log(msg):
    line = '[%s] %s' % (time.strftime('%Y-%m-%d %H:%M:%S'), msg)
    print(line)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def health(tries=1):
    for i in range(tries):
        try:
            with urllib.request.urlopen(BASE + '/api/health', timeout=5) as r:
                return json.loads(r.read().decode()).get('ok') is True
        except Exception:
            if i + 1 < tries:
                time.sleep(60)
    return False


def start_server():
    log('服务器无响应，尝试重新拉起…')
    subprocess.run(['pkill', '-f', 'uvicorn server.app'], capture_output=True)
    time.sleep(1)
    p = subprocess.Popen(
        [sys.executable, '-m', 'uvicorn', 'server.app:app',
         '--host', '127.0.0.1', '--port', str(PORT), '--log-level', 'warning'],
        cwd=ROOT, stdout=open(os.path.join(LOG_DIR, 'server.log'), 'a'),
        stderr=subprocess.STDOUT,
        start_new_session=True)
    time.sleep(4)
    ok = health()
    log('拉起结果: %s (pid=%s)' % ('成功' if ok else '失败', p.pid))
    return ok


def run_tests():
    env = dict(os.environ)
    # 回归清单：既有基线 + 论文补充批次（C1~C8）的新测试，全部离线确定性
    cases = [
        ('engine', 'tests/test_consistency.py'),
        ('branching', 'tests/test_branching.py'),
        ('guardrails_C3', 'tests/test_stage_guardrails.py'),
        ('memory_C1C2', 'tests/test_memory.py'),
        ('canon_guide_gossip_C4C7C8', 'tests/test_canon_guide_gossip.py'),
        ('mystery_attack_C6', 'tests/mystery_attack.py --offline'),
        ('adversary_C6', 'tests/adversary.py --offline'),
        ('interview_C5', 'tests/interview_eval.py --offline'),
    ]
    outs, fails = [], []
    for name, cmd in cases:
        r = subprocess.run([sys.executable] + cmd.split() + [],
                           cwd=ROOT, capture_output=True, text=True, env=env)
        outs.append('[%s] rc=%d\n%s' % (name, r.returncode, (r.stdout + r.stderr)[-1500:]))
        if r.returncode != 0:
            fails.append(name)
    if health():
        r = subprocess.run([sys.executable, 'tests/e2e_playthrough.py'],
                           cwd=ROOT, capture_output=True, text=True, env=env)
        outs.append('[e2e] rc=%d\n%s' % (r.returncode, (r.stdout + r.stderr)[-1500:]))
        if r.returncode != 0:
            fails.append('e2e')
    return not fails, fails, '\n'.join(outs)


def supervise_once():
    if not health(tries=2):          # 两轮探测（含 60s 等待重试）
        start_server()
        if not health(tries=2):      # 拉起后再探测，仍失败则隔一分钟再试一次
            time.sleep(60)
            start_server()
    if health():
        ok, fails, out = run_tests()
        status = 'HEARTBEAT-OK' if ok else ('TEST-FAIL %s' % ','.join(fails))
        log(status)
        if not ok:
            with open(os.path.join(LOG_DIR, 'last_fail.log'), 'w', encoding='utf-8') as f:
                f.write(out[-8000:])
    else:
        log('SERVER-DOWN 无法恢复，将在下个周期重试')


if __name__ == '__main__':
    if '--daemon' in sys.argv:
        while True:
            supervise_once()
            time.sleep(1800)
    else:
        supervise_once()
