import subprocess
import sys
from pathlib import Path

def build():
    """构建可执行文件"""
    
    # 获取 NiceGUI 的安装路径
    import nicegui
    nicegui_path = Path(nicegui.__file__).parent
    
    cmd = [
        'pyinstaller',
        '--name=SmartScraperRSS',
        '--onefile',
        '--windowed',
        f'--add-data={nicegui_path};nicegui',
        '--hidden-import=sqlmodel',
        '--hidden-import=DrissionPage',
        '--hidden-import=feedgen',
        '--hidden-import=openai',
        'app/main.py'
    ]
    
    print("开始构建...")
    print(f"命令: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ 构建成功！")
        print("可执行文件位于: dist/SmartScraperRSS.exe")
    else:
        print("❌ 构建失败！")
        print(result.stderr)
        sys.exit(1)

if __name__ == '__main__':
    build()
