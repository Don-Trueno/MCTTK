#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Docker 定时调度器 - 每 10 分钟运行一次 main.py"""

import time
import subprocess
import gc
import sys

INTERVAL = 600  # 10 分钟

def run_main():
    """运行 main.py 并清理内存"""
    try:
        print(f"\n{'='*60}")
        print(f"[调度器] 开始执行 - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

        result = subprocess.run(
            [sys.executable, "main.py"],
            capture_output=False,
            text=True
        )

        print(f"\n[调度器] 执行完成 (退出码: {result.returncode})")

    except Exception as e:
        print(f"[调度器] 执行失败: {e}")
    finally:
        # 强制垃圾回收
        gc.collect()

if __name__ == "__main__":
    print("[调度器] 启动 - 每 10 分钟运行一次")

    while True:
        run_main()
        print(f"[调度器] 等待 {INTERVAL} 秒...")
        time.sleep(INTERVAL)
