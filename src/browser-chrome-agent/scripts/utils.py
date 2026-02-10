"""
工具函数

端口管理、ARIA 快照捕获等通用工具。
"""

# === 依赖加载 ===
import sys
from pathlib import Path

_p = Path(__file__).resolve()
while _p != _p.parent:
    if _p.name == "skills":
        _libloader = _p / ".scripts" / "lib" / "libloader.py"
        if _libloader.exists():
            sys.path.insert(0, str(_libloader.parent))
            from libloader import setup
            setup()
        break
    _p = _p.parent
# === 依赖加载结束 ===

import socket
import subprocess
from typing import Optional


def is_port_in_use(port: int) -> bool:
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("", port))
            return False
        except OSError:
            return True


def kill_process_on_port(port: int):
    """释放指定端口上的进程"""
    try:
        if sys.platform == "win32":
            subprocess.run(
                f'FOR /F "tokens=5" %a in (\'netstat -ano ^| findstr :{port}\') do taskkill /F /PID %a',
                shell=True,
                capture_output=True,
            )
        else:
            subprocess.run(
                f"lsof -ti:{port} | xargs kill -9",
                shell=True,
                capture_output=True,
            )
    except Exception as e:
        print(f"释放端口 {port} 失败: {e}", file=sys.stderr)


async def capture_aria_snapshot(context, status: str = "") -> dict:
    """捕获页面 ARIA 快照，返回结构化结果"""
    url = await context.send_message("getUrl")
    title = await context.send_message("getTitle")
    snapshot = await context.send_message("browser_snapshot", {})

    status_line = f"{status}\n" if status else ""

    text = (
        f"{status_line}"
        f"- Page URL: {url}\n"
        f"- Page Title: {title}\n"
        f"- Page Snapshot\n"
        f"```yaml\n"
        f"{snapshot}\n"
        f"```"
    )

    return {"type": "text", "text": text}
