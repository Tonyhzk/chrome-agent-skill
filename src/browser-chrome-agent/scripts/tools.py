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

import json as _json

from utils import capture_aria_snapshot

# === 配置加载 ===
_config_path = Path(__file__).parent.parent / "config.json"
_config = {}
if _config_path.exists():
    try:
        _config = _json.loads(_config_path.read_text(encoding="utf-8"))
    except Exception:
        pass


# === 导航类工具 ===

async def navigate(context, params: dict) -> dict:
    """导航到指定 URL"""
    url = params.get("url", "")
    if not url:
        return {"success": False, "error": "缺少 url 参数"}
    await context.send_message("browser_navigate", {"url": url})
    snapshot = await capture_aria_snapshot(context, save_path=params.get("snapshot_file", ""))
    return {"success": True, "data": snapshot}


async def go_back(context, params: dict) -> dict:
    """浏览器后退"""
    await context.send_message("browser_go_back", {})
    snapshot = await capture_aria_snapshot(context, save_path=params.get("snapshot_file", ""))
    return {"success": True, "data": snapshot}


async def go_forward(context, params: dict) -> dict:
    """浏览器前进"""
    await context.send_message("browser_go_forward", {})
    snapshot = await capture_aria_snapshot(context, save_path=params.get("snapshot_file", ""))
    return {"success": True, "data": snapshot}


# === 页面交互工具 ===

async def click(context, params: dict) -> dict:
    """点击页面元素，支持 ref 或坐标"""
    import asyncio
    ref = params.get("ref", "")
    x = params.get("x")
    y = params.get("y")

    if x is not None and y is not None:
        # 坐标点击
        try:
            await context.send_message("browser_click_at", {"x": x, "y": y}, timeout_ms=5000)
        except TimeoutError:
            await asyncio.sleep(1)
        snapshot = await capture_aria_snapshot(context, f'已点击坐标 ({x}, {y})', save_path=params.get("snapshot_file", ""))
        return {"success": True, "data": snapshot}

    if not ref:
        return {"success": False, "error": "缺少 ref 参数或坐标参数 (x, y)"}
    try:
        await context.send_message("browser_click", {"ref": ref}, timeout_ms=5000)
    except TimeoutError:
        await asyncio.sleep(1)
    snapshot = await capture_aria_snapshot(context, f'已点击 ref={ref}', save_path=params.get("snapshot_file", ""))
    return {"success": True, "data": snapshot}


async def hover(context, params: dict) -> dict:
    """悬停在页面元素上"""
    ref = params.get("ref", "")
    if not ref:
        return {"success": False, "error": "缺少 ref 参数（使用 snapshot 中的 ref 值）"}
    await context.send_message("browser_hover", {"ref": ref})
    snapshot = await capture_aria_snapshot(context, f'已悬停 ref={ref}', save_path=params.get("snapshot_file", ""))
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
    snapshot = await capture_aria_snapshot(context, f'已在 ref={ref} 中输入 "{text}"', save_path=params.get("snapshot_file", ""))
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
    snapshot = await capture_aria_snapshot(context, f'已在 ref={ref} 中选择选项', save_path=params.get("snapshot_file", ""))
    return {"success": True, "data": snapshot}


async def drag(context, params: dict) -> dict:
    """拖拽元素"""
    start_ref = params.get("startRef", "")
    end_ref = params.get("endRef", "")
    if not start_ref or not end_ref:
        return {"success": False, "error": "缺少 startRef 或 endRef 参数"}
    await context.send_message("browser_drag", {"startRef": start_ref, "endRef": end_ref})
    snapshot = await capture_aria_snapshot(context, f'已将 ref={start_ref} 拖拽到 ref={end_ref}', save_path=params.get("snapshot_file", ""))
    return {"success": True, "data": snapshot}


# === 通用工具 ===

async def press_key(context, params: dict) -> dict:
    """按下键盘按键"""
    key = params.get("key", "")
    if not key:
        return {"success": False, "error": "缺少 key 参数"}
    await context.send_message("browser_press_key", {"key": key})
    return {"success": True, "data": {"type": "text", "text": f"已按下 {key}"}}


async def get_coordinates(context, params: dict) -> dict:
    """获取元素的坐标位置"""
    ref = params.get("ref", "")
    if not ref:
        return {"success": False, "error": "缺少 ref 参数"}
    try:
        coords = await context.send_message("browser_get_coordinates", {"ref": ref})
        return {"success": True, "data": {"type": "text", "text": f"ref={ref} 坐标: x={coords.get('x')}, y={coords.get('y')}"}}
    except Exception as e:
        return {"success": False, "error": str(e)}


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
    """获取页面 ARIA 快照

    参数:
        snapshot_file: 保存快照到文件路径（可选）
        inline: 为 true 时直接在响应中返回快照内容（可选）
        max_length: 快照最大字符数，0 不截断（默认从 config.json 读取，兜底 0）
    """
    max_length = params.get("max_length", _config.get("snapshot_max_length", 0))
    result = await capture_aria_snapshot(
        context,
        save_path=params.get("snapshot_file", ""),
        max_length=max_length,
        inline=params.get("inline", False),
    )
    return {"success": True, "data": result}


async def get_console_logs(context, params: dict) -> dict:
    """获取浏览器控制台日志"""
    logs = await context.send_message("browser_get_console_logs", {})
    text = "\n".join(str(log) for log in (logs or []))
    return {"success": True, "data": {"type": "text", "text": text or "（无日志）"}}


async def get_text(context, params: dict) -> dict:
    """获取页面纯文字内容

    参数:
        max_length: 最大返回字符数（默认 5000）

    从 snapshot 中提取所有文本内容，过滤掉元素标记
    """
    import re
    max_length = params.get("max_length", 5000)

    # 获取 snapshot
    snapshot_result = await context.send_message("browser_snapshot", {})
    snapshot_text = snapshot_result if isinstance(snapshot_result, str) else str(snapshot_result)

    # 提取纯文字内容
    lines = []
    for line in snapshot_text.split('\n'):
        # 跳过纯结构行（只有 - 类型 [ref=xxx] 的行）
        if re.match(r'^\s*-\s+\w+\s*\[ref=', line):
            continue
        # 提取 text: 后的内容
        text_match = re.search(r'text:\s*(.+)$', line)
        if text_match:
            text = text_match.group(1).strip().strip('"').strip("'")
            if text and text not in ['|', '-', '·']:
                lines.append(text)
            continue
        # 提取引号内的文本（如 link "文本" [ref=xxx]）
        quote_match = re.search(r'"([^"]+)"', line)
        if quote_match and '[ref=' in line:
            text = quote_match.group(1).strip()
            if text and len(text) > 1:
                lines.append(text)

    # 去重并合并
    seen = set()
    unique_lines = []
    for line in lines:
        if line not in seen:
            seen.add(line)
            unique_lines.append(line)

    result_text = '\n'.join(unique_lines)
    if len(result_text) > max_length:
        result_text = result_text[:max_length] + '\n...(已截断)'

    return {
        "success": True,
        "data": {
            "type": "text",
            "text": result_text or "（页面无文字内容）"
        }
    }


async def find_element(context, params: dict) -> dict:
    """通过关键字搜索页面元素

    参数:
        keyword: 搜索关键字（必填）
        case_sensitive: 是否区分大小写（默认 False）
        max_results: 最大返回数量（默认 20）

    返回匹配的元素列表，包含 ref、类型和文本内容
    """
    import re
    keyword = params.get("keyword", "")
    if not keyword:
        return {"success": False, "error": "缺少 keyword 参数"}

    case_sensitive = params.get("case_sensitive", False)
    max_results = params.get("max_results", 20)

    # 获取 snapshot
    snapshot_result = await context.send_message("browser_snapshot", {})
    snapshot_text = snapshot_result if isinstance(snapshot_result, str) else str(snapshot_result)

    # 解析 snapshot 找到匹配的元素
    # snapshot 格式示例:
    # - link "搜索" [ref=s1e123]:
    # - button "提交" [ref=s1e456]
    # - textbox "请输入关键词" [ref=s1e789]

    flags = 0 if case_sensitive else re.IGNORECASE
    matches = []

    # 匹配带 ref 的元素行
    # 格式: - 类型 "文本" [ref=xxx] 或 - 类型 [ref=xxx]
    pattern = r'-\s+(\w+)(?:\s+"([^"]*)")?\s*\[ref=([^\]]+)\]'

    for match in re.finditer(pattern, snapshot_text):
        elem_type = match.group(1)
        elem_text = match.group(2) or ""
        elem_ref = match.group(3)

        # 检查关键字是否匹配
        search_text = elem_text if case_sensitive else elem_text.lower()
        search_keyword = keyword if case_sensitive else keyword.lower()

        if search_keyword in search_text:
            matches.append({
                "ref": elem_ref,
                "type": elem_type,
                "text": elem_text
            })
            if len(matches) >= max_results:
                break

    if not matches:
        return {
            "success": True,
            "data": {
                "type": "text",
                "text": f"未找到包含 \"{keyword}\" 的元素"
            }
        }

    # 格式化输出
    lines = [f"找到 {len(matches)} 个匹配元素:"]
    for m in matches:
        lines.append(f"  [{m['ref']}] {m['type']}: \"{m['text']}\"")

    return {
        "success": True,
        "data": {
            "type": "text",
            "text": "\n".join(lines),
            "matches": matches  # 结构化数据供程序使用
        }
    }


async def find_and_locate(context, params: dict) -> dict:
    """搜索元素并立即获取坐标（解决 ref 过期问题）

    参数:
        keyword: 搜索关键字（必填）
        index: 匹配结果索引，默认 0（第一个匹配）
        case_sensitive: 是否区分大小写（默认 False）

    返回匹配元素的 ref、类型、文本和坐标
    """
    import re
    keyword = params.get("keyword", "")
    if not keyword:
        return {"success": False, "error": "缺少 keyword 参数"}

    index = params.get("index", 0)
    case_sensitive = params.get("case_sensitive", False)

    # 获取 snapshot
    snapshot_result = await context.send_message("browser_snapshot", {})
    snapshot_text = snapshot_result if isinstance(snapshot_result, str) else str(snapshot_result)

    # 解析 snapshot 找到匹配的元素
    pattern = r'-\s+(\w+)(?:\s+"([^"]*)")?\s*\[ref=([^\]]+)\]'
    matches = []

    for match in re.finditer(pattern, snapshot_text):
        elem_type = match.group(1)
        elem_text = match.group(2) or ""
        elem_ref = match.group(3)

        search_text = elem_text if case_sensitive else elem_text.lower()
        search_keyword = keyword if case_sensitive else keyword.lower()

        if search_keyword in search_text:
            matches.append({
                "ref": elem_ref,
                "type": elem_type,
                "text": elem_text
            })

    if not matches:
        return {
            "success": True,
            "data": {
                "type": "text",
                "text": f"未找到包含 \"{keyword}\" 的元素"
            }
        }

    if index >= len(matches):
        return {
            "success": False,
            "error": f"索引 {index} 超出范围，只找到 {len(matches)} 个匹配元素"
        }

    target = matches[index]

    # 立即获取坐标（在同一个 snapshot 周期内，ref 有效）
    try:
        coords = await context.send_message("browser_get_coordinates", {"ref": target["ref"]}, timeout_ms=10000)
        target["x"] = coords.get("x")
        target["y"] = coords.get("y")

        return {
            "success": True,
            "data": {
                "type": "text",
                "text": f"找到元素: [{target['ref']}] {target['type']}: \"{target['text']}\"\n坐标: x={target['x']}, y={target['y']}",
                "element": target
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"获取坐标失败: {str(e)}",
            "data": {
                "element": target,
                "all_matches": matches
            }
        }


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


# === 标签页管理工具 ===

async def list_tabs(context, params: dict) -> dict:
    """列出所有打开的标签页，并刷新扩展内部的活动标签页缓存"""
    tabs = await context.send_message("browser_list_tabs", {})
    # 找到当前活动标签页，用 switch_tab 刷新扩展内部缓存的 tabId
    # 解决导航后扩展缓存的旧 tabId 导致 "No tab with given id" 的问题
    active_tab = next((t for t in tabs if t.get("active")), None)
    if active_tab:
        try:
            await context.send_message("browser_switch_tab", {"tabId": active_tab["id"]})
        except Exception:
            pass  # 刷新失败不影响 list_tabs 结果
    lines = []
    for tab in tabs:
        marker = " *" if tab.get("active") else ""
        lines.append(f"[{tab['id']}]{marker} {tab.get('title', '')} - {tab.get('url', '')}")
    return {"success": True, "data": {"type": "text", "text": "\n".join(lines)}}


async def new_tab(context, params: dict) -> dict:
    """打开新标签页"""
    url = params.get("url", "about:blank")
    result = await context.send_message("browser_new_tab", {"url": url})
    return {"success": True, "data": {"type": "text", "text": f"已打开新标签页: id={result.get('id')}, url={result.get('url', url)}"}}


async def switch_tab(context, params: dict) -> dict:
    """切换到指定标签页"""
    tab_id = params.get("tabId")
    if not tab_id:
        return {"success": False, "error": "缺少 tabId 参数（先用 list_tabs 获取）"}
    result = await context.send_message("browser_switch_tab", {"tabId": tab_id})
    # 切换后获取快照，确认 debugger 已正确 attach 到新标签页
    snapshot = await capture_aria_snapshot(
        context,
        status=f"已切换到标签页: id={tab_id}, title={result.get('title', '')}, url={result.get('url', '')}",
        save_path=params.get("snapshot_file", ""),
    )
    return {"success": True, "data": snapshot}


async def close_tab(context, params: dict) -> dict:
    """关闭指定标签页"""
    tab_id = params.get("tabId")
    if not tab_id:
        return {"success": False, "error": "缺少 tabId 参数（先用 list_tabs 获取）"}
    result = await context.send_message("browser_close_tab", {"tabId": tab_id})
    switched_to = result.get("switchedTo")
    msg = f"已关闭标签页 {result.get('closed', tab_id)}"
    if switched_to:
        msg += f"，已自动切换到标签页 {switched_to}"
    return {"success": True, "data": {"type": "text", "text": msg}}


async def xpath_query(context, params: dict) -> dict:
    """通过 XPath 查询页面元素，返回匹配元素的文本或 HTML

    参数:
        xpath: XPath 表达式（必填）
        output: 输出类型（默认 "text"）
            - "text": 元素的纯文本内容
            - "inner_html": 元素的内部 HTML
            - "outer_html": 元素的完整 HTML（含自身标签）
            - "attr": 提取属性值（需配合 attr_name）
        attr_name: 当 output="attr" 时，指定要提取的属性名
        max_results: 最大返回数量（默认 20）
        max_length: 单条结果最大显示字符数（默认从 config.json 读取，兜底 500）
        save_path: 结果保存到文件的路径（可选，传入则将完整结果写入文件）

    示例 XPath:
        //h1                          → 所有 h1 标题
        //input[@type='text']         → 所有文本输入框
        //a[contains(@href,'github')] → 包含 github 的链接
        //div[@class='content']//p    → content 区域内的段落
        //meta[@name='description']/@content → meta 描述内容
    """
    from lxml import html as lxml_html
    from lxml.etree import tostring as etree_tostring

    xpath_expr = params.get("xpath", "")
    if not xpath_expr:
        return {"success": False, "error": "缺少 xpath 参数"}

    output_type = params.get("output", "text")
    attr_name = params.get("attr_name", "")
    max_results = params.get("max_results", 20)
    max_length = params.get("max_length", _config.get("xpath_max_display_length", 500))
    save_path = params.get("save_path", "")

    if output_type == "attr" and not attr_name:
        return {"success": False, "error": "output='attr' 时需要提供 attr_name 参数"}

    # 获取页面 HTML
    try:
        page_html = await context.send_message("getPageHtml", {})
    except Exception as e:
        return {"success": False, "error": f"获取页面 HTML 失败: {e}"}

    # 解析 HTML
    try:
        tree = lxml_html.fromstring(page_html)
    except Exception as e:
        return {"success": False, "error": f"解析 HTML 失败: {e}"}

    # 执行 XPath
    try:
        results = tree.xpath(xpath_expr)
    except Exception as e:
        return {"success": False, "error": f"XPath 表达式错误: {e}"}

    if not results:
        return {"success": True, "data": {"type": "text", "text": f"XPath \"{xpath_expr}\" 未匹配到任何元素", "count": 0}}

    # 格式化结果
    items = []
    for i, node in enumerate(results[:max_results]):
        if isinstance(node, str):
            items.append(node.strip())
        elif hasattr(node, 'tag'):
            if output_type == "text":
                items.append(node.text_content().strip())
            elif output_type == "inner_html":
                inner = (node.text or "") + "".join(
                    etree_tostring(child, encoding="unicode", method="html")
                    for child in node
                )
                items.append(inner.strip())
            elif output_type == "outer_html":
                items.append(etree_tostring(node, encoding="unicode", method="html").strip())
            elif output_type == "attr":
                items.append(node.get(attr_name, ""))
            else:
                items.append(node.text_content().strip())
        else:
            items.append(str(node).strip())

    # 过滤空结果
    items = [item for item in items if item]
    total = len(results)
    shown = len(items)

    # 保存到文件（完整内容，不截断）
    if save_path:
        try:
            file_lines = [f"XPath: {xpath_expr}", f"匹配 {total} 个结果（显示 {shown} 个）:", ""]
            for i, item in enumerate(items):
                file_lines.append(f"[{i+1}] {item}")
                file_lines.append("")
            Path(save_path).write_text("\n".join(file_lines), encoding="utf-8")
        except Exception as e:
            return {"success": False, "error": f"保存文件失败: {e}"}

    # 构建显示文本（截断）
    lines = [f"匹配 {total} 个结果（显示 {shown} 个）:"]
    for i, item in enumerate(items):
        display = item if len(item) <= max_length else item[:max_length] + "..."
        lines.append(f"  [{i+1}] {display}")

    if save_path:
        lines.append(f"\n完整结果已保存到: {save_path}")

    return {
        "success": True,
        "data": {
            "type": "text",
            "text": "\n".join(lines),
            "count": total,
            "items": items
        }
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
    "get_coordinates": get_coordinates,
    "find_element": find_element,
    "find_and_locate": find_and_locate,
    "get_text": get_text,
    "wait": wait,
    "screenshot": screenshot,
    "snapshot": snapshot,
    "get_console_logs": get_console_logs,
    "get_html": get_html,
    "list_tabs": list_tabs,
    "new_tab": new_tab,
    "switch_tab": switch_tab,
    "close_tab": close_tab,
    "xpath_query": xpath_query,
}
