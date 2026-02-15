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


async def capture_aria_snapshot(context, status: str = "", save_path: str = "", max_length: int = 0, inline: bool = False) -> dict:
    """捕获页面信息，可选保存 ARIA 快照到文件或直接返回

    Args:
        context: 浏览器上下文
        status: 操作状态描述（如 "已点击 ref=s1e5"）
        save_path: 快照保存路径。传入路径则获取快照并写入文件
        max_length: 快照最大字符数。0 表示不截断，>0 则截断快照内容
        inline: 为 True 时直接在响应中返回快照内容（受 max_length 截断）
    """
    url = await context.send_message("getUrl")
    title = await context.send_message("getTitle")
    status_line = f"{status}\n" if status else ""

    need_snapshot = save_path or inline
    snapshot = ""
    if need_snapshot:
        snapshot = await context.send_message("browser_snapshot", {})
        if max_length > 0 and len(snapshot) > max_length:
            snapshot = snapshot[:max_length] + f"\n... (truncated, total {len(snapshot)} chars)"

    if save_path:
        full_text = (
            f"{status_line}"
            f"- Page URL: {url}\n"
            f"- Page Title: {title}\n"
            f"- Page Snapshot\n"
            f"```yaml\n"
            f"{snapshot}\n"
            f"```"
        )
        path = Path(save_path)
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(full_text, encoding="utf-8")
        return {"type": "text", "text": f"{status_line}- Page URL: {url}\n- Page Title: {title}\n- Snapshot saved to: {save_path}"}

    if inline:
        return {"type": "text", "text": f"{status_line}- Page URL: {url}\n- Page Title: {title}\n- Page Snapshot\n```yaml\n{snapshot}\n```"}

    return {"type": "text", "text": f"{status_line}- Page URL: {url}\n- Page Title: {title}"}
