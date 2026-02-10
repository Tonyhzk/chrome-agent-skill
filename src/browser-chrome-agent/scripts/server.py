"""
Browser Chrome Agent - WebSocket 服务器

主入口脚本。启动 WebSocket 服务器等待 Chrome 扩展连接，
通过 stdin/stdout JSON 协议接收和返回浏览器操作命令。

用法:
  # 交互模式（从 stdin 读取 JSON 命令）
  python3 server.py [--port 3000]

  # 单次命令模式
  python3 server.py --action navigate --params '{"url": "https://example.com"}'

交互模式协议:
  输入（stdin，每行一个 JSON）:
    {"action": "navigate", "params": {"url": "https://example.com"}}
    {"action": "click", "params": {"element": "Submit button"}}

  输出（stdout，每行一个 JSON）:
    {"success": true, "data": {...}}
    {"success": false, "error": "错误信息"}

  特殊命令:
    {"action": "status"}  - 查询连接状态
    {"action": "quit"}    - 退出服务器
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

# 确保能导入同目录模块
sys.path.insert(0, str(Path(__file__).parent))

import argparse
import asyncio
import json

import websockets

from context import Context
from tools import TOOLS
from utils import is_port_in_use, kill_process_on_port

DEFAULT_PORT = 9009


def output(data: dict):
    """向 stdout 输出一行 JSON"""
    text = json.dumps(data, ensure_ascii=False) + "\n"
    # 确保 stdout 为阻塞模式，避免 BlockingIOError
    import os
    fd = sys.stdout.fileno()
    flags = os.get_blocking(fd)
    if not flags:
        os.set_blocking(fd, True)
    sys.stdout.write(text)
    sys.stdout.flush()


def log(msg: str):
    """向 stderr 输出日志（不干扰 stdout JSON 协议）"""
    print(msg, file=sys.stderr, flush=True)


async def handle_extension(websocket, context: Context):
    """处理 Chrome 扩展的 WebSocket 连接"""
    if context.has_ws():
        log("[server] 新连接到达，关闭旧连接")
        await context.close()

    context.ws = websocket
    log("[server] Chrome 扩展已连接")

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                context.handle_response(data)
            except json.JSONDecodeError:
                log(f"[server] 收到无效 JSON: {message[:100]}")
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if context._ws is websocket:
            context._ws = None
            log("[server] Chrome 扩展已断开")


async def execute_command(context: Context, action: str, params: dict) -> dict:
    """执行浏览器命令"""
    # 特殊命令
    if action == "status":
        return {
            "success": True,
            "data": {"connected": context.has_ws()},
        }
    if action == "quit":
        return {"success": True, "data": {"message": "服务器关闭中..."}}

    # 查找工具
    tool_fn = TOOLS.get(action)
    if not tool_fn:
        available = ", ".join(sorted(TOOLS.keys()))
        return {"success": False, "error": f"未知操作: {action}。可用操作: {available}"}

    # 检查连接
    if not context.has_ws():
        return {"success": False, "error": "未连接到浏览器扩展。请先点击扩展图标并连接。"}

    try:
        result = await tool_fn(context, params)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


async def stdin_reader(context: Context):
    """从 stdin 读取 JSON 命令并执行（交互模式）"""
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)

    log("[server] 交互模式就绪，等待命令...")

    while True:
        try:
            line = await reader.readline()
            if not line:
                break
            line = line.decode("utf-8").strip()
            if not line:
                continue

            try:
                cmd = json.loads(line)
            except json.JSONDecodeError:
                output({"success": False, "error": f"无效 JSON: {line[:100]}"})
                continue

            action = cmd.get("action", "")
            params = cmd.get("params", {})

            result = await execute_command(context, action, params)
            output(result)

            if action == "quit":
                break

        except Exception as e:
            output({"success": False, "error": f"内部错误: {e}"})


async def run_server(port: int, action: str = None, params: dict = None):
    """启动 WebSocket 服务器"""
    context = Context()

    # 释放端口
    if is_port_in_use(port):
        log(f"[server] 端口 {port} 被占用，尝试释放...")
        kill_process_on_port(port)
        await asyncio.sleep(0.5)

    # 启动 WebSocket 服务器
    async with websockets.serve(
        lambda ws: handle_extension(ws, context),
        "localhost",
        port,
    ) as server:
        log(f"[server] WebSocket 服务器已启动 ws://localhost:{port}")

        if action:
            # 单次命令模式：等待扩展连接后执行
            log(f"[server] 单次模式，等待扩展连接后执行: {action}")
            while not context.has_ws():
                await asyncio.sleep(0.1)
            result = await execute_command(context, action, params or {})
            output(result)
        else:
            # 交互模式：从 stdin 读取命令
            await stdin_reader(context)

    await context.close()
    log("[server] 服务器已关闭")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Browser Chrome Agent - 浏览器自动化 WebSocket 服务器"
    )
    parser.add_argument(
        "--port", type=int, default=DEFAULT_PORT,
        help=f"WebSocket 服务器端口（默认: {DEFAULT_PORT}）",
    )
    parser.add_argument(
        "--action", type=str, default=None,
        help="单次执行的操作（如 navigate, click, type 等）",
    )
    parser.add_argument(
        "--params", type=str, default="{}",
        help="操作参数（JSON 字符串）",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    params = json.loads(args.params) if args.params else {}
    try:
        asyncio.run(run_server(args.port, args.action, params))
    except KeyboardInterrupt:
        log("\n[server] 已停止")
