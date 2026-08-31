#!/usr/bin/env python3
"""Dependency-free MCP server exposing external LLM providers to Claude Code.

Providers:
- openai      -> OpenAI Responses API
- gemini      -> Gemini Interactions API
- anthropic   -> Anthropic Messages API
- ollama      -> Ollama chat API

Only model output text is returned. API keys are read from environment variables and never emitted.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any

SERVER_INFO = {"name": "gauntlet-router", "version": "1.0.0"}

DEFAULT_MODELS = {
    "openai": os.getenv("GAUNTLET_OPENAI_MODEL", "gpt-5.6"),
    "gemini": os.getenv("GAUNTLET_GEMINI_MODEL", "gemini-3.6-flash"),
    "anthropic": os.getenv("GAUNTLET_ANTHROPIC_MODEL", "claude-opus-5"),
    "ollama": os.getenv("GAUNTLET_OLLAMA_MODEL", "qwen3:32b"),
}

ROLE_SYSTEM = {
    "critic": (
        "You are an independent Gauntlet critic. Do not repair the candidate. "
        "Find concrete correctness, requirement, architecture, maintainability, performance, "
        "and edge-case defects. Every issue needs severity, location, evidence, and proposed fix. "
        "Do not expose private chain-of-thought."
    ),
    "red-team": (
        "You are an independent Gauntlet red-team reviewer. Try to make the candidate fail using "
        "realistic functional, security, concurrency, and operational attacks. Distinguish "
        "reproducible findings from hypotheses and cite evidence. Do not expose private chain-of-thought."
    ),
    "judge": (
        "You are an independent Gauntlet judge. Do not repair the candidate. Evaluate against the "
        "given acceptance criteria and evidence. Return PASS, REVISE, or FAIL with concise scoring "
        "and blocking issues. Model consensus is not proof. Do not expose private chain-of-thought."
    ),
    "tie-breaker": (
        "Evaluate only the disputed claim from the supplied evidence. Return SUPPORTED, REFUTED, or "
        "INSUFFICIENT_EVIDENCE with a concise evidence-based explanation. Do not expose private chain-of-thought."
    ),
    "reviewer": (
        "You are an independent engineering reviewer in a multi-agent Gauntlet. Be concise, skeptical, "
        "and evidence-based. Do not expose private chain-of-thought."
    ),
}


def http_json(url: str, headers: dict[str, str], payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        raise RuntimeError(f"Provider HTTP {exc.code}: {body[:2000]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Provider connection failed: {exc}") from exc


def provider_status() -> dict[str, Any]:
    return {
        "openai": {
            "configured": bool(os.getenv("OPENAI_API_KEY")),
            "model": DEFAULT_MODELS["openai"],
            "key_env": "OPENAI_API_KEY",
            "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        },
        "gemini": {
            "configured": bool(os.getenv("GEMINI_API_KEY")),
            "model": DEFAULT_MODELS["gemini"],
            "key_env": "GEMINI_API_KEY",
        },
        "anthropic": {
            "configured": bool(os.getenv("ANTHROPIC_API_KEY")),
            "model": DEFAULT_MODELS["anthropic"],
            "key_env": "ANTHROPIC_API_KEY",
            "base_url": anthropic_url(),
        },
        "ollama": {
            "configured": bool(os.getenv("OLLAMA_BASE_URL")) or bool(os.getenv("GAUNTLET_OLLAMA_MODEL")),
            "model": DEFAULT_MODELS["ollama"],
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        },
    }


def ask_openai(system: str, prompt: str, model: str, timeout: int) -> str:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    base = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    obj = http_json(
        f"{base}/responses",
        {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        {"model": model, "instructions": system, "input": prompt},
        timeout,
    )
    if isinstance(obj.get("output_text"), str):
        return obj["output_text"]
    parts = []
    for item in obj.get("output", []):
        for content in item.get("content", []) if isinstance(item, dict) else []:
            text = content.get("text") if isinstance(content, dict) else None
            if isinstance(text, str):
                parts.append(text)
    return "\n".join(parts) or json.dumps(obj)


def ask_gemini(system: str, prompt: str, model: str, timeout: int) -> str:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not set")
    obj = http_json(
        "https://generativelanguage.googleapis.com/v1beta/interactions",
        {"x-goog-api-key": key, "Content-Type": "application/json"},
        {
            "model": model,
            "system_instruction": system,
            "input": prompt,
            "store": False
        },
        timeout,
    )
    if isinstance(obj.get("output_text"), str):
        return obj["output_text"]
    # REST response may expose text inside generated steps.
    parts = []
    for step in obj.get("steps", []):
        if not isinstance(step, dict):
            continue
        for key_name in ("text", "output_text"):
            if isinstance(step.get(key_name), str):
                parts.append(step[key_name])
        for content in step.get("content", []) if isinstance(step.get("content"), list) else []:
            if isinstance(content, dict) and isinstance(content.get("text"), str):
                parts.append(content["text"])
    return "\n".join(parts) or json.dumps(obj)


def anthropic_url() -> str:
    base = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com").rstrip("/")
    if base.endswith("/messages"):
        return base
    if base.endswith("/v1"):
        return f"{base}/messages"
    return f"{base}/v1/messages"


def ask_anthropic(system: str, prompt: str, model: str, timeout: int) -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")
    obj = http_json(
        anthropic_url(),
        {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        {
            "model": model,
            "max_tokens": 4096,
            "system": system,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout,
    )
    return "\n".join(
        block.get("text", "")
        for block in obj.get("content", [])
        if isinstance(block, dict) and block.get("type") == "text"
    )


def ask_ollama(system: str, prompt: str, model: str, timeout: int) -> str:
    base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    obj = http_json(
        f"{base}/api/chat",
        {"Content-Type": "application/json"},
        {
            "model": model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        },
        timeout,
    )
    msg = obj.get("message", {})
    return msg.get("content", "") if isinstance(msg, dict) else ""


ASKERS = {
    "openai": ask_openai,
    "gemini": ask_gemini,
    "anthropic": ask_anthropic,
    "ollama": ask_ollama,
}


def call_tool(name: str, args: dict[str, Any]) -> Any:
    if name == "provider_status":
        return provider_status()

    if name == "ask_provider":
        provider = str(args.get("provider", "")).lower()
        role = str(args.get("role", "reviewer")).lower()
        prompt = str(args.get("prompt", ""))
        if provider not in ASKERS:
            raise RuntimeError(f"Unsupported provider: {provider}")
        if not prompt.strip():
            raise RuntimeError("prompt must not be empty")

        model = str(args.get("model") or DEFAULT_MODELS[provider])
        timeout = int(args.get("timeout_seconds") or 180)
        timeout = min(max(timeout, 10), 600)
        system = str(args.get("system") or ROLE_SYSTEM.get(role, ROLE_SYSTEM["reviewer"]))

        output = ASKERS[provider](system, prompt, model, timeout)
        return {
            "provider": provider,
            "model": model,
            "role": role,
            "output": output,
        }

    raise RuntimeError(f"Unknown tool: {name}")


TOOLS = [
    {
        "name": "provider_status",
        "description": (
            "Return which external Gauntlet providers are configured (OpenAI, Gemini, Anthropic API, "
            "Ollama), their selected models, and required environment-variable names. Never returns secrets."
        ),
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "ask_provider",
        "description": (
            "Ask an external model provider for an independent Gauntlet critic, red-team, judge, "
            "tie-breaker, or generic reviewer result. Send only minimal non-secret context."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["provider", "prompt"],
            "properties": {
                "provider": {
                    "type": "string",
                    "enum": ["openai", "gemini", "anthropic", "ollama"],
                },
                "role": {
                    "type": "string",
                    "enum": ["critic", "red-team", "judge", "tie-breaker", "reviewer"],
                    "default": "reviewer",
                },
                "prompt": {"type": "string"},
                "system": {"type": "string"},
                "model": {"type": "string"},
                "timeout_seconds": {
                    "type": "integer",
                    "minimum": 10,
                    "maximum": 600,
                    "default": 180,
                },
            },
            "additionalProperties": False,
        },
    },
]


def send(obj: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(obj, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def result(req_id: Any, value: Any) -> None:
    send({"jsonrpc": "2.0", "id": req_id, "result": value})


def error(req_id: Any, code: int, message: str) -> None:
    send({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}})


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            method = req.get("method")
            req_id = req.get("id")

            if method == "initialize":
                result(req_id, {
                    "protocolVersion": req.get("params", {}).get("protocolVersion", "2025-06-18"),
                    "capabilities": {"tools": {}},
                    "serverInfo": SERVER_INFO,
                })
            elif method == "notifications/initialized":
                continue
            elif method == "ping":
                result(req_id, {})
            elif method == "tools/list":
                result(req_id, {"tools": TOOLS})
            elif method == "tools/call":
                params = req.get("params", {})
                name = params.get("name", "")
                args = params.get("arguments", {}) or {}
                try:
                    value = call_tool(name, args)
                    text = json.dumps(value, ensure_ascii=False, indent=2)
                    result(req_id, {
                        "content": [{"type": "text", "text": text}],
                        "isError": False,
                    })
                except Exception as exc:
                    result(req_id, {
                        "content": [{"type": "text", "text": f"{type(exc).__name__}: {exc}"}],
                        "isError": True,
                    })
            else:
                if req_id is not None:
                    error(req_id, -32601, f"Method not found: {method}")
        except Exception as exc:
            # Keep server alive on malformed input.
            try:
                error(None, -32603, f"Internal error: {type(exc).__name__}: {exc}")
            except Exception:
                pass


if __name__ == "__main__":
    main()
