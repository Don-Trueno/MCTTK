#!/usr/bin/env python3
"""utils.py — 项目公共工具函数"""

import os


def load_dotenv(project_dir: str = None) -> None:
    """加载同目录下的 .env 文件到环境变量（已存在的变量不覆盖）"""
    if project_dir is None:
        project_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(project_dir, ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
