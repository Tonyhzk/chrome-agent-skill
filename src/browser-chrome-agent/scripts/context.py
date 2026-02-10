"""
WebSocket 连接上下文管理

管理与 Chrome 扩展的 WebSocket 连接，提供请求-响应消息机制。
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

import asyncio
import json
import uuid
from typing import Any, Optional


class Context:
    """WebSocket 连接上下文，管理与 Chrome 扩展的通信"""

    def __init__(self):
        self._ws = None
        self._pending: dict[str, asyncio.Future] = {}

    @property
    def ws(self):
        if self._ws is None:
            raise ConnectionError(
                "未连接到浏览器扩展。请先点击 Browser MCP 扩展图标并点击 'Connect' 按钮。"
            )
        return self._ws

    @ws.setter
    def ws(self, websocket):
        self._ws = websocket

    def has_ws(self) -> bool:
        return self._ws is not None

    async def send_message(
        self,
        msg_type: str,
        payload: Any = None,
        timeout_ms: int = 30000,
    ) -> Any:
        """发送 WebSocket 消息并等待响应"""
        msg_id = str(uuid.uuid4())
        message = {
            "id": msg_id,
            "type": msg_type,
        }
        if payload is not None:
            message["payload"] = payload

        future: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending[msg_id] = future

        try:
            await self.ws.send(json.dumps(message))
            result = await asyncio.wait_for(future, timeout=timeout_ms / 1000)
            return result
        except asyncio.TimeoutError:
            raise TimeoutError(f"消息 '{msg_type}' 超时（{timeout_ms}ms）")
        finally:
            self._pending.pop(msg_id, None)

    def handle_response(self, data: dict):
        """处理来自扩展的响应消息"""
        # 扩展响应格式: {"id": "新UUID", "type": "messageResponse", "payload": {"requestId": "原始ID", "result": ..., "error": ...}}
        payload = data.get("payload", {})
        msg_id = payload.get("requestId") or data.get("id")
        if msg_id and msg_id in self._pending:
            future = self._pending[msg_id]
            if not future.done():
                error = payload.get("error") or data.get("error")
                if error:
                    future.set_exception(RuntimeError(error))
                else:
                    result = payload.get("result") if payload.get("result") is not None else data.get("result", data.get("data"))
                    future.set_result(result)

    async def close(self):
        if self._ws:
            await self._ws.close()
            self._ws = None
