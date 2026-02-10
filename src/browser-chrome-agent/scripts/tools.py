"""
浏览器工具实现

从 MCP 服务器移植的所有浏览器自动化工具。
每个工具接收 context 和 params，返回结果字典。
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

from utils import capture_aria_snapshot


# === 导航类工具 ===

async def navigate(context, params: dict) -> dict:
    """导航到指定 URL"""
    url = params.get("url", "")
    if not url:
        return {"success": False, "error": "缺少 url 参数"}
    await context.send_message("browser_navigate", {"url": url})
    snapshot = await capture_aria_snapshot(context)
    return {"success": True, "data": snapshot}


async def go_back(context, params: dict) -> dict:
    """浏览器后退"""
    await context.send_message("browser_go_back", {})
    snapshot = await capture_aria_snapshot(context)
    return {"success": True, "data": snapshot}


async def go_forward(context, params: dict) -> dict:
    """浏览器前进"""
    await context.send_message("browser_go_forward", {})
    snapshot = await capture_aria_snapshot(context)
    return {"success": True, "data": snapshot}


# === 页面交互工具 ===

async def click(context, params: dict) -> dict:
    """点击页面元素"""
    import asyncio
    ref = params.get("ref", "")
    if not ref:
        return {"success": False, "error": "缺少 ref 参数（使用 snapshot 中的 ref 值）"}
    try:
        await context.send_message("browser_click", {"ref": ref}, timeout_ms=5000)
    except TimeoutError:
        # 点击可能触发了页面导航，content script 被销毁导致超时
        # 等待新页面加载后继续获取快照
        await asyncio.sleep(1)
    snapshot = await capture_aria_snapshot(context, f'已点击 ref={ref}')
    return {"success": True, "data": snapshot}


async def hover(context, params: dict) -> dict:
    """悬停在页面元素上"""
    ref = params.get("ref", "")
    if not ref:
        return {"success": False, "error": "缺少 ref 参数（使用 snapshot 中的 ref 值）"}
    await context.send_message("browser_hover", {"ref": ref})
    snapshot = await capture_aria_snapshot(context, f'已悬停 ref={ref}')
    return {"success": True, "data": snapshot}


async def type_text(context, params: dict) -> dict:
    """在元素中输入文本"""
    ref = params.get("ref", "")
    text = params.get("text", "")
    submit = params.get("submit", False)
    if not ref:
        return {"success": False, "error": "缺少 ref 参数（使用 snapshot 中的 ref 值）"}
    if not text:
        return {"success": False, "error": "缺少 text 参数"}
    await context.send_message("browser_type", {"ref": ref, "text": text, "submit": submit})
    snapshot = await capture_aria_snapshot(context, f'已在 ref={ref} 中输入 "{text}"')
    return {"success": True, "data": snapshot}


async def select_option(context, params: dict) -> dict:
    """选择下拉菜单选项"""
    ref = params.get("ref", "")
    values = params.get("values", [])
    if not ref:
        return {"success": False, "error": "缺少 ref 参数（使用 snapshot 中的 ref 值）"}
    if not values:
        return {"success": False, "error": "缺少 values 参数"}
    await context.send_message("browser_select_option", {"ref": ref, "values": values})
    snapshot = await capture_aria_snapshot(context, f'已在 ref={ref} 中选择选项')
    return {"success": True, "data": snapshot}


async def drag(context, params: dict) -> dict:
    """拖拽元素"""
    start_ref = params.get("startRef", "")
    end_ref = params.get("endRef", "")
    if not start_ref or not end_ref:
        return {"success": False, "error": "缺少 startRef 或 endRef 参数"}
    await context.send_message("browser_drag", {"startRef": start_ref, "endRef": end_ref})
    snapshot = await capture_aria_snapshot(context, f'已将 ref={start_ref} 拖拽到 ref={end_ref}')
    return {"success": True, "data": snapshot}


# === 通用工具 ===

async def press_key(context, params: dict) -> dict:
    """按下键盘按键"""
    key = params.get("key", "")
    if not key:
        return {"success": False, "error": "缺少 key 参数"}
    await context.send_message("browser_press_key", {"key": key})
    return {"success": True, "data": {"type": "text", "text": f"已按下 {key}"}}


async def wait(context, params: dict) -> dict:
    """等待指定时间（秒）"""
    time_sec = params.get("time", 1)
    await context.send_message("browser_wait", {"time": time_sec})
    return {"success": True, "data": {"type": "text", "text": f"已等待 {time_sec} 秒"}}


# === 信息获取工具 ===

async def screenshot(context, params: dict) -> dict:
    """截取当前页面截图"""
    import base64
    image_data = await context.send_message("browser_screenshot", {})
    save_path = params.get("savePath", "")
    if save_path:
        from pathlib import Path
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(base64.b64decode(image_data))
        return {
            "success": True,
            "data": {"type": "text", "text": f"截图已保存到 {save_path}"},
        }
    return {
        "success": True,
        "data": {"type": "image", "data": image_data, "mimeType": "image/png"},
    }


async def snapshot(context, params: dict) -> dict:
    """获取页面 ARIA 快照"""
    result = await capture_aria_snapshot(context)
    return {"success": True, "data": result}


async def get_console_logs(context, params: dict) -> dict:
    """获取浏览器控制台日志"""
    logs = await context.send_message("browser_get_console_logs", {})
    text = "\n".join(str(log) for log in (logs or []))
    return {"success": True, "data": {"type": "text", "text": text or "（无日志）"}}


async def get_html(context, params: dict) -> dict:
    """获取页面 HTML 源码并保存到文件"""
    from pathlib import Path
    save_path = params.get("savePath", "")
    if not save_path:
        return {"success": False, "error": "缺少 savePath 参数"}
    html = await context.send_message("getPageHtml", {})
    path = Path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    size_kb = path.stat().st_size / 1024
    return {
        "success": True,
        "data": {"type": "text", "text": f"HTML 已保存到 {save_path} ({size_kb:.1f} KB)"},
    }


# === 工具注册表 ===

TOOLS = {
    "navigate": navigate,
    "go_back": go_back,
    "go_forward": go_forward,
    "click": click,
    "hover": hover,
    "type": type_text,
    "select_option": select_option,
    "drag": drag,
    "press_key": press_key,
    "wait": wait,
    "screenshot": screenshot,
    "snapshot": snapshot,
    "get_console_logs": get_console_logs,
    "get_html": get_html,
}
