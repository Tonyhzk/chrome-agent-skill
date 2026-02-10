#!/usr/bin/env python3
"""
符号链接管理工具
创建/移除 .claude 目录的符号链接，实现多项目共享配置
"""

import os
import sys
import platform
import shutil
import subprocess
from pathlib import Path

# 各系统默认外部 .claude 目录路径
DEFAULT_EXTERNAL_DIR_MAC = "/Users/hzk/Documents/GitHub/HZK-Daily/.claude"
DEFAULT_EXTERNAL_DIR_WIN = r"C:\Users\jjp\Documents\GIthub\.claude"
DEFAULT_EXTERNAL_DIR_LINUX = "/home/hzk/Documents/GitHub/HZK-Daily/.claude"

# 根据当前系统选择默认路径
SYSTEM = platform.system()
if SYSTEM == "Darwin":
    DEFAULT_EXTERNAL_DIR = DEFAULT_EXTERNAL_DIR_MAC
elif SYSTEM == "Windows":
    DEFAULT_EXTERNAL_DIR = DEFAULT_EXTERNAL_DIR_WIN
elif SYSTEM == "Linux":
    DEFAULT_EXTERNAL_DIR = DEFAULT_EXTERNAL_DIR_LINUX
else:
    DEFAULT_EXTERNAL_DIR = DEFAULT_EXTERNAL_DIR_MAC


def get_external_dir():
    """获取外部 .claude 目录路径"""
    default_exists = Path(DEFAULT_EXTERNAL_DIR).exists()

    if default_exists:
        print(f"默认目标目录: {DEFAULT_EXTERNAL_DIR}")
        print()
        print("选项:")
        print("  1. 使用默认路径")
        print("  2. 输入其他路径")
        print()
        choice = input("请选择 [1/2]: ").strip()

        if choice == "2":
            user_input = input("输入新路径: ").strip()
            if user_input:
                return Path(user_input)
        return Path(DEFAULT_EXTERNAL_DIR)
    else:
        print(f"默认路径不存在: {DEFAULT_EXTERNAL_DIR}")
        user_input = input("请输入有效路径: ").strip()
        if user_input:
            return Path(user_input)
        return None


def is_network_path(path: Path) -> bool:
    """检查路径是否是网络路径（UNC 或映射的网络驱动器）"""
    path_str = str(path)
    # UNC 路径
    if path_str.startswith('\\\\'):
        return True
    # 检查映射的网络驱动器
    try:
        resolved = str(path.resolve())
        if resolved.startswith('\\\\'):
            return True
    except:
        pass
    return False


def create_symlink_windows(target: Path, link: Path) -> bool:
    """
    Windows 专用：创建目录符号链接或 junction
    - 对于本地路径：优先尝试符号链接，失败则使用 junction
    - 对于网络路径：只能使用符号链接（mklink /D）
    """
    # 使用原始路径字符串，避免 resolve() 将映射驱动器转换为 UNC 路径
    target_str = str(target)
    link_str = str(link)
    
    # 检查是否是网络路径
    is_network = is_network_path(target)
    
    # 方法1：优先使用 mklink /D 创建目录符号链接（通过 cmd，保持原始路径）
    print("尝试使用 mklink /D 创建符号链接...")
    try:
        result = subprocess.run(
            ['cmd', '/c', 'mklink', '/D', link_str, target_str],
            capture_output=True,
            text=True,
            shell=False
        )
        if result.returncode == 0:
            print(f"创建目录符号链接: {link} -> {target}")
            return True
        else:
            stderr = result.stderr.strip()
            print(f"mklink /D 失败: {stderr}")
            # 检查是否是权限问题
            if "没有足够的权限" in stderr or "privilege" in stderr.lower():
                print("需要管理员权限或开发者模式")
    except Exception as e:
        print(f"mklink /D 异常: {e}")
    
    # 方法2：对于本地路径，尝试使用 junction（不需要特殊权限，但不支持网络路径）
    if not is_network:
        print("尝试使用 junction 作为备选方案...")
        try:
            # junction 需要使用解析后的绝对路径
            resolved_target = str(target.resolve())
            result = subprocess.run(
                ['cmd', '/c', 'mklink', '/J', link_str, resolved_target],
                capture_output=True,
                text=True,
                shell=False
            )
            if result.returncode == 0:
                print(f"创建目录连接 (junction): {link} -> {target}")
                return True
            else:
                print(f"Junction 创建失败: {result.stderr.strip()}")
        except Exception as e:
            print(f"Junction 创建异常: {e}")
    
    # 方法3：尝试使用 os.symlink（可能会解析路径）
    try:
        os.symlink(target_str, link_str, target_is_directory=True)
        print(f"创建符号链接: {link} -> {target}")
        return True
    except OSError as e:
        error_code = getattr(e, 'winerror', None)
        print(f"os.symlink 失败 (错误: {error_code}): {e}")
    
    # 所有方法都失败
    print()
    print("=" * 50)
    print("无法创建符号链接！可能的解决方案：")
    print("=" * 50)
    print()
    print("方案1：启用 Windows 开发者模式")
    print("  设置 -> 更新和安全 -> 开发者选项 -> 开发人员模式")
    print()
    print("方案2：以管理员身份运行此脚本")
    print("  右键点击 PowerShell/CMD -> 以管理员身份运行")
    print()
    if is_network:
        print("注意：目标路径是网络路径（映射的网络驱动器），只能使用符号链接")
        print("      Junction 不支持网络路径")
        print(f"  目标: {target}")
    print()
    return False


def create_symlink(external_dir: Path):
    """创建符号链接"""
    project_dir = Path.cwd()
    local_claude = project_dir / ".claude"
    backup_claude = project_dir / ".claude.bak"

    # 检查外部目录是否存在
    if not external_dir.exists():
        print(f"错误：外部 .claude 目录不存在: {external_dir}")
        return False

    # 已经是正确的符号链接或 junction
    if local_claude.is_symlink() or (SYSTEM == "Windows" and local_claude.is_dir()):
        try:
            # 检查是否是 junction（Windows 特有）
            if SYSTEM == "Windows" and local_claude.is_dir() and not local_claude.is_symlink():
                # 使用 fsutil 检查是否是 reparse point (junction)
                result = subprocess.run(
                    ['fsutil', 'reparsepoint', 'query', str(local_claude)],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    # 不是 junction，是普通目录
                    shutil.move(local_claude, backup_claude)
                    print(f"备份现有目录: {local_claude} -> {backup_claude}")
                else:
                    # 是 junction，检查目标
                    target = local_claude.resolve()
                    if target == external_dir.resolve():
                        print(f"目录连接已存在: {local_claude} -> {target}")
                        return True
                    else:
                        # 移除旧的 junction
                        os.rmdir(local_claude)
                        print(f"移除旧目录连接: {local_claude}")
            elif local_claude.is_symlink():
                target = os.readlink(local_claude)
                if Path(target).resolve() == external_dir.resolve():
                    print(f"符号链接已存在: {local_claude} -> {target}")
                    return True
                else:
                    os.unlink(local_claude)
                    print(f"移除旧符号链接: {local_claude} -> {target}")
        except Exception as e:
            print(f"检查现有链接时出错: {e}")
            # 尝试移除
            try:
                if local_claude.is_symlink():
                    os.unlink(local_claude)
                else:
                    os.rmdir(local_claude)
            except:
                pass

    # 备份现有目录（非符号链接/junction）
    elif local_claude.exists():
        shutil.move(local_claude, backup_claude)
        print(f"备份现有目录: {local_claude} -> {backup_claude}")

    # 创建符号链接
    if SYSTEM == "Windows":
        return create_symlink_windows(external_dir, local_claude)
    else:
        os.symlink(external_dir, local_claude)
        print(f"创建符号链接: {local_claude} -> {external_dir}")
        return True


def is_junction(path: Path) -> bool:
    """检查路径是否是 Windows junction"""
    if SYSTEM != "Windows" or not path.exists():
        return False
    try:
        result = subprocess.run(
            ['fsutil', 'reparsepoint', 'query', str(path)],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False


def remove_symlink():
    """移除符号链接或 junction 并恢复原目录"""
    project_dir = Path.cwd()
    local_claude = project_dir / ".claude"
    backup_claude = project_dir / ".claude.bak"

    is_symlink = local_claude.is_symlink()
    is_junc = is_junction(local_claude)
    
    if not is_symlink and not is_junc:
        print(f"当前不是符号链接或目录连接: {local_claude}")
        return

    if is_symlink:
        target = os.readlink(local_claude)
        os.unlink(local_claude)
        print(f"移除符号链接: {local_claude} -> {target}")
    elif is_junc:
        target = local_claude.resolve()
        os.rmdir(local_claude)  # junction 使用 rmdir 移除
        print(f"移除目录连接 (junction): {local_claude} -> {target}")

    # 恢复备份
    if backup_claude.exists():
        shutil.move(backup_claude, local_claude)
        print(f"恢复备份目录: {backup_claude} -> {local_claude}")


def show_status():
    """显示当前状态"""
    project_dir = Path.cwd()
    local_claude = project_dir / ".claude"
    backup_claude = project_dir / ".claude.bak"

    print(f"项目目录: {project_dir}")
    print(f"默认目标: {DEFAULT_EXTERNAL_DIR}")
    print()

    if local_claude.is_symlink():
        target = os.readlink(local_claude)
        print(f".claude 状态: 符号链接 -> {target}")
    elif is_junction(local_claude):
        target = local_claude.resolve()
        print(f".claude 状态: 目录连接 (junction) -> {target}")
    elif local_claude.exists():
        print(f".claude 状态: 普通目录")
    else:
        print(f".claude 状态: 不存在")

    if backup_claude.exists():
        print(f".claude.bak: 存在（有备份）")


def interactive_menu():
    """交互式菜单"""
    while True:
        print("\n" + "=" * 40)
        print("符号链接管理工具")
        print("=" * 40)
        show_status()
        print()
        print("操作选项:")
        print("  1. 创建符号链接 (link)")
        print("  2. 移除符号链接 (unlink)")
        print("  3. 刷新状态 (status)")
        print("  q. 退出")
        print()

        choice = input("请选择 [1/2/3/q]: ").strip().lower()

        if choice in ("1", "link"):
            external_dir = get_external_dir()
            if external_dir:
                create_symlink(external_dir)
        elif choice in ("2", "unlink"):
            remove_symlink()
        elif choice in ("3", "status"):
            continue
        elif choice in ("q", "quit", "exit"):
            print("退出")
            break
        else:
            print("无效选项")


def main():
    usage = """
符号链接管理工具

用法:
    python3 run_claude.py           交互式菜单
    python3 run_claude.py link      创建符号链接（使用默认路径）
    python3 run_claude.py unlink    移除符号链接并恢复
    python3 run_claude.py status    显示当前状态
"""

    # 检查当前目录是否是源目录本身
    cwd = Path.cwd().resolve()
    source_dir = Path(DEFAULT_EXTERNAL_DIR).resolve().parent  # HZK-Daily 目录
    if cwd == source_dir or cwd == Path(DEFAULT_EXTERNAL_DIR).resolve():
        print("错误：当前目录是配置源目录，不能在此创建符号链接")
        print(f"当前目录: {cwd}")
        print("请在其他项目目录中运行此脚本")
        input("\n按回车键退出...")
        sys.exit(1)

    if len(sys.argv) < 2:
        interactive_menu()
    else:
        cmd = sys.argv[1]
        if cmd == "link":
            create_symlink(Path(DEFAULT_EXTERNAL_DIR))
        elif cmd == "unlink":
            remove_symlink()
        elif cmd == "status":
            show_status()
        else:
            print(usage)
            sys.exit(1)


if __name__ == "__main__":
    main()