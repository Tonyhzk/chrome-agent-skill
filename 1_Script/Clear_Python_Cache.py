#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
clean_project_cache.py - 清理项目缓存文件和目录

支持清理:
- Python 缓存: __pycache__、*.pyc、*.pyo
- Claude 临时文件: tmpclaude-*
- 其他临时文件和缓存目录

注意: *.pyd 是 Python 动态链接库（编译后的扩展模块），不是缓存，不应删除！
"""

import os
import shutil
from pathlib import Path
import fnmatch

# ==================== 配置区 ====================

# 要清理的目录（支持通配符）
DIRS_TO_CLEAN = [
    "__pycache__",
    ".pycache",
    ".pytest_cache",    # pytest 缓存
    ".mypy_cache",      # mypy 类型检查缓存
    ".ruff_cache",      # ruff 缓存
    "node_modules",     # Node.js 依赖（如果不需要可取消注释）
    ".venv_backup",     # 备份的虚拟环境
]

# 要清理的文件（支持通配符）
FILES_TO_CLEAN = [
    "*.pyc",           # Python 字节码缓存
    "*.pyo",           # Python 优化字节码
    ".DS_Store",       # macOS 系统文件
    "Thumbs.db",       # Windows 缩略图缓存
    "desktop.ini",     # Windows 文件夹配置
    "*.tmp",           # 临时文件
    "*.log",           # 日志文件（可选，根据需要取消注释）
    "tmpclaude-*",     # Claude 生成的临时文件
]

# 要保护的目录（不进入扫描，避免误删）
PROTECTED_DIRS = [
    ".git",            # Git 仓库
    ".venv",           # 虚拟环境
    "venv",            # 虚拟环境
    "node_modules",    # Node.js 依赖（如果需要保留）
    "backup",          # 备份目录
]

# ==================== 功能函数 ====================

def match_pattern(name, patterns):
    """检查名称是否匹配任一模式"""
    for pattern in patterns:
        if fnmatch.fnmatch(name, pattern):
            return True
    return False


def get_dir_size(path):
    """计算目录大小（字节）"""
    total_size = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file():
                total_size += entry.stat().st_size
            elif entry.is_dir():
                total_size += get_dir_size(entry.path)
    except Exception:
        pass
    return total_size


def format_size(size_bytes):
    """格式化显示文件大小"""
    if size_bytes == 0:
        return "0 B"
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def collect_cache_items():
    """收集所有要清理的缓存项目"""
    target_dirs = []
    target_files = []
    total_size = 0

    print(f"正在扫描项目缓存...")
    print(f"起点: {os.path.abspath('.')}\n")

    # 扫描所有文件和目录
    for root, dirs, files in os.walk('.'):
        # 过滤掉保护目录，不进入扫描
        dirs[:] = [d for d in dirs if not match_pattern(d, PROTECTED_DIRS)]

        # 查找匹配的目录
        for dir_name in dirs[:]:  # 使用副本遍历，因为可能修改原列表
            if match_pattern(dir_name, DIRS_TO_CLEAN):
                dir_path = os.path.join(root, dir_name)
                size = get_dir_size(dir_path)
                target_dirs.append((dir_path, size))
                total_size += size
                # 从遍历列表中移除（已标记删除，无需深入）
                dirs.remove(dir_name)

        # 查找匹配的文件
        for file_name in files:
            if match_pattern(file_name, FILES_TO_CLEAN):
                file_path = os.path.join(root, file_name)
                # 跳过已标记删除目录中的文件（避免重复计算）
                parent_dir = os.path.basename(root)
                if not match_pattern(parent_dir, DIRS_TO_CLEAN):
                    try:
                        size = os.path.getsize(file_path)
                        target_files.append((file_path, size))
                        total_size += size
                    except Exception:
                        pass

    return target_dirs, target_files, total_size


def display_items(target_dirs, target_files, total_size):
    """显示要清理的项目"""
    print("=" * 80)
    print("项目缓存清理工具")
    print("=" * 80)

    if not target_dirs and not target_files:
        print("\n未发现任何缓存内容。")
        return False

    print(f"\n[发现的缓存内容] (总计: {format_size(total_size)})")
    print("-" * 80)

    # 显示目录
    if target_dirs:
        print(f"\n📁 目录 ({len(target_dirs)} 个):")
        for dir_path, size in target_dirs[:50]:  # 最多显示50个
            print(f"  {dir_path} ({format_size(size)})")
        if len(target_dirs) > 50:
            print(f"  ... 还有 {len(target_dirs) - 50} 个目录")

    # 显示文件
    if target_files:
        print(f"\n📄 文件 ({len(target_files)} 个):")
        for file_path, size in target_files[:50]:  # 最多显示50个
            print(f"  {file_path} ({format_size(size)})")
        if len(target_files) > 50:
            print(f"  ... 还有 {len(target_files) - 50} 个文件")

    print("-" * 80)
    print(f"总计: {len(target_dirs)} 个目录, {len(target_files)} 个文件")
    print(f"预计释放空间: {format_size(total_size)}")

    return True


def clean_items(target_dirs, target_files, total_size):
    """执行清理操作"""
    # 用户确认
    print("\n是否确认删除以上内容? (y/n): ", end="")
    confirm = input().strip().lower()

    if confirm not in ['y', 'yes', '是']:
        print("已取消清理")
        return False

    # 执行删除
    print("\n[开始清理...]")
    print("-" * 80)

    count_dirs = 0
    count_files = 0
    failed_items = []

    # 删除目录
    for dir_path, size in target_dirs:
        try:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                print(f"  ✓ [目录] {dir_path} ({format_size(size)})")
                count_dirs += 1
        except Exception as e:
            print(f"  ✗ [错误] {dir_path}: {e}")
            failed_items.append((dir_path, str(e)))

    # 删除文件
    for file_path, size in target_files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"  ✓ [文件] {file_path} ({format_size(size)})")
                count_files += 1
        except Exception as e:
            print(f"  ✗ [错误] {file_path}: {e}")
            failed_items.append((file_path, str(e)))

    # 显示结果
    print("-" * 80)
    print("\n" + "=" * 80)
    print("清理完成!")
    print("=" * 80)
    print(f"  ✓ 删除了 {count_dirs} 个目录")
    print(f"  ✓ 删除了 {count_files} 个文件")
    print(f"  ✓ 释放空间: {format_size(total_size)}")

    if failed_items:
        print(f"\n  ⚠ 有 {len(failed_items)} 个项目清理失败:")
        for item, error in failed_items[:10]:
            print(f"    - {item}")
        if len(failed_items) > 10:
            print(f"    ... 还有 {len(failed_items) - 10} 个失败项目")

    print("=" * 80)

    return True


def clean_cache():
    """清理项目缓存（主函数）"""
    # 第一步：收集缓存项目
    target_dirs, target_files, total_size = collect_cache_items()

    # 第二步：显示要清理的内容
    has_items = display_items(target_dirs, target_files, total_size)

    if not has_items:
        return

    # 第三步：执行清理
    clean_items(target_dirs, target_files, total_size)


if __name__ == "__main__":
    clean_cache()
