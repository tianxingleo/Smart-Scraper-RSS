"""
RSS内容聚合器启动脚本
"""

import os
import sys

# 添加src目录到Python路径
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.append(src_dir)

# 运行主程序
if __name__ == "__main__":
    from main import main
    main() 