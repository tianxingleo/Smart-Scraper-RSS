import os
import json
from typing import Set

def load_processed_bvids() -> Set[str]:
    """加载已处理的bvid集合"""
    if os.path.exists('processed_bvids.txt'):
        with open('processed_bvids.txt', 'r') as f:
            return set(line.strip() for line in f)
    return set()

def add_processed_bvid(bvid: str):
    """添加已处理的bvid"""
    processed_bvids = load_processed_bvids()
    processed_bvids.add(bvid)
    with open('processed_bvids.txt', 'w') as f:
        for bvid in sorted(processed_bvids):
            f.write(f"{bvid}\n")

def clear_processed_bvids():
    """清空已处理的bvid集合"""
    with open('processed_bvids.txt', 'w') as f:
        f.write("")