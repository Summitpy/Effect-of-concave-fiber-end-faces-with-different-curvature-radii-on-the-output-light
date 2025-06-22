#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在conda环境中运行光学模拟
"""

import subprocess
import sys
import os

def main():
    env_name = "fiber_optics"
    
    print("🚀 在conda环境中运行光学模拟...")
    print(f"📦 环境名称: {env_name}")
    
    # 检查模拟文件是否存在
    if not os.path.exists("fiber_optics_simulation.py"):
        print("❌ 找不到 fiber_optics_simulation.py 文件")
        return False
    
    # 在conda环境中运行
    cmd = f"conda run -n {env_name} python fiber_optics_simulation.py"
    
    try:
        print(f"🔧 执行命令: {cmd}")
        result = subprocess.run(cmd, shell=True, check=True)
        print("✅ 模拟运行成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 运行失败: {e}")
        return False

if __name__ == "__main__":
    main()
