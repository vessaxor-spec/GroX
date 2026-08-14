from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import subprocess
from typing import Any


class MCPError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class MCPAdapterSpec:
    argv: tuple[str, ...]
    allowed_tools: frozenset[str]
    mutating_tools: frozenset[str] = field(default_factory=frozenset)
    cwd: str | None = None


class StdioMCPClient:
    def __init__(self, registry: dict[str, MCPAdapterSpec] | None = None):
        self.registry = dict(registry or {})

    def call(self, adapter: str, tool: str, arguments: dict[str, Any], *, allow_mutation: bool, timeout: int = 10) -> dict:
        if adapter not in self.registry:
            raise MCPError(f"MCP adapter is not pre-registered: {adapter}")
        spec = self.registry[adapter]
        if tool not in spec.allowed_tools:
            raise MCPError(f"MCP tool is not allowed for adapter {adapter}: {tool}")
        mutating = tool in spec.mutating_tools
        if mutating and not allow_mutation:
            raise MCPError(f"MCP tool requires explicit mutation authority: {adapter}/{tool}")
        messages = [
            {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"GroX","version":"A5"}}},
            {"jsonrpc":"2.0","method":"notifications/initialized","params":{}},
            {"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}},
            {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":tool,"arguments":arguments}},
        ]
        payload = "".join(json.dumps(m, separators=(",", ":")) + "\n" for m in messages)
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG":"C", "LC_ALL":"C"}
        kwargs: dict[str, Any] = {}
        if os.geteuid() == 0:
            kwargs["user"] = "nobody"
        try:
            cp = subprocess.run(
                list(spec.argv), input=payload, text=True, capture_output=True, timeout=timeout,
                cwd=spec.cwd or None, env=env, **kwargs,
            )
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError(f"MCP adapter {adapter} exceeded {timeout}s") from exc
        if cp.returncode != 0:
            raise MCPError(f"MCP adapter failed: {adapter}: {cp.stderr[-1000:]}")
        responses: dict[int, dict] = {}
        for line in cp.stdout.splitlines():
            if not line.strip():
                continue
            try:
                message = json.loads(line)
            except json.JSONDecodeError as exc:
                raise MCPError(f"MCP adapter emitted invalid JSON: {adapter}") from exc
            if isinstance(message.get("id"), int):
                responses[message["id"]] = message
        for required in (1, 2, 3):
            if required not in responses:
                raise MCPError(f"MCP adapter omitted response id {required}: {adapter}")
            if "error" in responses[required]:
                raise MCPError(f"MCP adapter returned error for id {required}: {responses[required]['error']}")
        init = responses[1].get("result") or {}
        listed = responses[2].get("result") or {}
        names = {x.get("name") for x in listed.get("tools", []) if isinstance(x, dict)}
        if tool not in names:
            raise MCPError(f"MCP adapter did not advertise requested tool: {tool}")
        return {
            "adapter": adapter,
            "tool": tool,
            "mutating": mutating,
            "protocol_version": init.get("protocolVersion"),
            "result": responses[3].get("result"),
        }
