#!/usr/bin/env python3
from __future__ import annotations
import json, os, sys, urllib.request, urllib.error
from typing import Any

SERVER = {"name": "gauntlet-router", "version": "1.1.0"}
DEFAULT_MODELS = {
    "openai": os.getenv("GAUNTLET_OPENAI_MODEL", "gpt-5.6"),
    "anthropic": os.getenv("GAUNTLET_ANTHROPIC_MODEL", "claude-opus-5"),
    "gemini": os.getenv("GAUNTLET_GEMINI_MODEL", "gemini-3.6-flash"),
    "ollama": os.getenv("GAUNTLET_OLLAMA_MODEL", "qwen3:32b")
}
ROLE = {
    "critic": "You are an independent Gauntlet critic. Do not repair the candidate. Find concrete correctness, requirements, architecture, maintainability, performance, and edge-case defects. Give severity, location, evidence, and proposed fix. Do not expose private chain-of-thought.",
    "red-team": "You are an independent Gauntlet red-team reviewer. Try to make the candidate fail using realistic functional, security, concurrency, and operational attacks. Distinguish reproducible findings from hypotheses and cite evidence. Do not expose private chain-of-thought.",
    "judge": "You are an independent Gauntlet judge. Do not repair the candidate. Evaluate against acceptance criteria and evidence. Return concise scores, blockers, and exactly PASS, REVISE, or FAIL. Model consensus is not proof. Do not expose private chain-of-thought.",
    "tie-breaker": "Evaluate only the disputed claim. Return SUPPORTED, REFUTED, or INSUFFICIENT_EVIDENCE with concise evidence. Do not expose private chain-of-thought.",
    "reviewer": "You are an independent engineering reviewer in a multi-agent Gauntlet. Be skeptical, concise, and evidence-based. Do not expose private chain-of-thought."
}

def post(url, headers, payload, timeout):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        raise RuntimeError(f"Provider HTTP {e.code}: {body[:2000]}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Provider connection failed: {e}") from e

def provider_status():
    status = {
        "openai": {"configured": bool(os.getenv("OPENAI_API_KEY")), "model": DEFAULT_MODELS["openai"], "required_env": "OPENAI_API_KEY"},
        "anthropic": {"configured": bool(os.getenv("ANTHROPIC_API_KEY")), "model": DEFAULT_MODELS["anthropic"], "required_env": "ANTHROPIC_API_KEY"},
        "gemini": {"configured": bool(os.getenv("GEMINI_API_KEY")), "model": DEFAULT_MODELS["gemini"], "required_env": "GEMINI_API_KEY"},
        "ollama": {"configured": bool(os.getenv("OLLAMA_BASE_URL")) or bool(os.getenv("GAUNTLET_OLLAMA_MODEL")), "model": DEFAULT_MODELS["ollama"], "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")}
    }
    if os.getenv("OPENAI_BASE_URL"):
        status["openai"]["base_url"] = os.getenv("OPENAI_BASE_URL")
    if os.getenv("ANTHROPIC_BASE_URL"):
        status["anthropic"]["base_url"] = os.getenv("ANTHROPIC_BASE_URL")
    return status

def ask_openai(system, prompt, model, timeout):
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    base = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    url = base if base.endswith("/responses") else f"{base}/responses"
    o = post(url, {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, {"model": model, "instructions": system, "input": prompt}, timeout)
    if isinstance(o.get("output_text"), str):
        return o["output_text"]
    chunks = []
    for item in o.get("output", []):
        if isinstance(item, dict):
            for c in item.get("content", []) or []:
                if isinstance(c, dict) and isinstance(c.get("text"), str):
                    chunks.append(c["text"])
    return chr(10).join(chunks) or json.dumps(o)

def ask_anthropic(system, prompt, model, timeout):
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")
    base = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com").rstrip("/")
    if base.endswith("/messages"):
        url = base
    elif base.endswith("/v1"):
        url = f"{base}/messages"
    else:
        url = f"{base}/v1/messages"
    o = post(url, {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"}, {"model": model, "max_tokens": 4096, "system": system, "messages": [{"role": "user", "content": prompt}]}, timeout)
    return chr(10).join(b.get("text", "") for b in o.get("content", []) if isinstance(b, dict) and b.get("type") == "text")

def ask_gemini(system, prompt, model, timeout):
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not set")
    base = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com").rstrip("/")
    url = f"{base}/v1beta/models/{model}:generateContent?key={key}"
    o = post(url, {"Content-Type": "application/json"}, {"system_instruction": {"parts": [{"text": system}]}, "contents": [{"role": "user", "parts": [{"text": prompt}]}]}, timeout)
    cs = o.get("candidates", [])
    if not cs:
        return json.dumps(o)
    return chr(10).join(p.get("text", "") for p in cs[0].get("content", {}).get("parts", []) if isinstance(p, dict) and p.get("text"))

def ask_ollama(system, prompt, model, timeout):
    base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    o = post(base + "/api/chat", {"Content-Type": "application/json"}, {"model": model, "stream": False, "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}]}, timeout)
    return o.get("message", {}).get("content", "")

ASK = {"openai": ask_openai, "anthropic": ask_anthropic, "gemini": ask_gemini, "ollama": ask_ollama}
TOOLS = [
    {"name": "provider_status", "description": "Show configured external Gauntlet providers and selected models without secrets.", "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "ask_provider", "description": "Ask OpenAI, Anthropic, Gemini, or Ollama for an independent Gauntlet review.", "inputSchema": {"type": "object", "required": ["provider", "prompt"], "properties": {"provider": {"type": "string", "enum": ["openai", "anthropic", "gemini", "ollama"]}, "role": {"type": "string", "enum": ["critic", "red-team", "judge", "tie-breaker", "reviewer"], "default": "reviewer"}, "prompt": {"type": "string"}, "system": {"type": "string"}, "model": {"type": "string"}, "timeout_seconds": {"type": "integer", "minimum": 10, "maximum": 600, "default": 180}}, "additionalProperties": False}}
]

def call(name, args):
    if name == "provider_status":
        return provider_status()
    if name != "ask_provider":
        raise RuntimeError(f"Unknown tool: {name}")
    p = str(args.get("provider", "")).lower()
    prompt = str(args.get("prompt", ""))
    role = str(args.get("role", "reviewer")).lower()
    if p not in ASK:
        raise RuntimeError(f"Unsupported provider: {p}")
    if not prompt.strip():
        raise RuntimeError("prompt must not be empty")
    system = str(args.get("system") or ROLE.get(role, ROLE["reviewer"]))
    model = str(args.get("model") or DEFAULT_MODELS[p])
    timeout = max(10, min(int(args.get("timeout_seconds", 180)), 600))
    return {"provider": p, "model": model, "role": role, "output": ASK[p](system, prompt, model, timeout)}

def send(o):
    sys.stdout.write(json.dumps(o, separators=(",", ":")) + chr(10))
    sys.stdout.flush()

def ok(i, r):
    send({"jsonrpc": "2.0", "id": i, "result": r})

def err(i, c, m):
    send({"jsonrpc": "2.0", "id": i, "error": {"code": c, "message": m}})

def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            q = json.loads(line)
            i = q.get("id")
            m = q.get("method")
            if m == "initialize":
                ok(i, {"protocolVersion": q.get("params", {}).get("protocolVersion", "2025-06-18"), "capabilities": {"tools": {}}, "serverInfo": SERVER})
            elif m == "notifications/initialized":
                continue
            elif m == "ping":
                ok(i, {})
            elif m == "tools/list":
                ok(i, {"tools": TOOLS})
            elif m == "tools/call":
                p = q.get("params", {}) or {}
                try:
                    ok(i, {"content": [{"type": "text", "text": json.dumps(call(p.get("name", ""), p.get("arguments", {}) or {}), ensure_ascii=False, indent=2)}], "isError": False})
                except Exception as e:
                    ok(i, {"content": [{"type": "text", "text": f"{type(e).__name__}: {e}"}], "isError": True})
            elif i is not None:
                err(i, -32601, f"Method not found: {m}")
        except Exception as e:
            err(None, -32603, f"Internal error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    main()
