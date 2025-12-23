"""
检查 Python 环境和已安装的包
"""
import sys
import subprocess

print("=" * 60)
print("Python 环境信息:")
print("=" * 60)
print(f"Python 版本: {sys.version}")
print(f"Python 路径: {sys.executable}")
print(f"sys.path: {sys.path}")

print("\n" + "=" * 60)
print("检查 python-jenkins 是否已安装:")
print("=" * 60)

try:
    import jenkins
    print(f"✓ python-jenkins 已安装")
    print(f"  版本: {jenkins.__version__ if hasattr(jenkins, '__version__') else '未知'}")
    print(f"  路径: {jenkins.__file__}")
except ImportError as e:
    print(f"✗ python-jenkins 未安装")
    print(f"  错误: {e}")
