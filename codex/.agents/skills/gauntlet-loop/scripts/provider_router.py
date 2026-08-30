#!/usr/bin/env python3
"""Optional cross-provider router for the Codex Gauntlet skill.

OpenAI configuration:
  OPENAI_BASE_URL=https://api.openai.com/v1
  OPENAI_API_MODE=responses            # default
  OPENAI_API_MODE=chat_completions     # OpenAI-compatible chat API

The base URL must not include /responses or /chat/completions; the router appends
that endpoint automatically.
"""
from __future__ import annotations
import argparse, json, os, sys, urllib.request, urllib.error


def post_json(url, headers, payload, timeout=180):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        raise RuntimeError(f"HTTP {e.code}: {body}") from e


def openai_config():
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    mode = os.getenv("OPENAI_API_MODE", "responses").strip().lower()
    aliases = {
        "response": "responses",
        "responses_api": "responses",
        "chat": "chat_completions",
        "chat-completions": "chat_completions",
        "chat_completion": "chat_completions",
    }
    mode = aliases.get(mode, mode)
    if mode not in {"responses", "chat_completions"}:
        raise RuntimeError("OPENAI_API_MODE must be 'responses' or 'chat_completions'")
    return base_url, mode


def extract_responses_text(obj):
    if isinstance(obj.get("output_text"), str):
        return obj["output_text"]
    chunks = []
    for out in obj.get("output", []):
        if not isinstance(out, dict):
            continue
        for c in out.get("content", []) or []:
            if isinstance(c, dict) and isinstance(c.get("text"), str):
                chunks.append(c["text"])
    return "\n".join(chunks) or json.dumps(obj)


def extract_chat_text(obj):
    choices = obj.get("choices") or []
    if not choices or not isinstance(choices[0], dict):
        return json.dumps(obj)
    msg = choices[0].get("message") or {}
    content = msg.get("content") if isinstance(msg, dict) else None
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        chunks = [p.get("text") for p in content if isinstance(p, dict) and isinstance(p.get("text"), str)]
        if chunks:
            return "\n".join(chunks)
    return json.dumps(obj)


def ask_openai(system, prompt):
    key = os.environ["OPENAI_API_KEY"]
    model = os.getenv("GAUNTLET_OPENAI_MODEL", "gpt-5.6")
    base_url, mode = openai_config()
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    if mode == "responses":
        obj = post_json(
            f"{base_url}/responses", headers,
            {"model": model, "instructions": system, "input": prompt},
        )
        return extract_responses_text(obj)
    obj = post_json(
        f"{base_url}/chat/completions", headers,
        {"model": model, "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ]},
    )
    return extract_chat_text(obj)


def ask_anthropic(system, prompt):
    key = os.environ["ANTHROPIC_API_KEY"]
    model = os.getenv("GAUNTLET_ANTHROPIC_MODEL", "claude-sonnet-5")
    obj = post_json(
        "https://api.anthropic.com/v1/messages",
        {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
        {"model": model, "max_tokens": 4096, "system": system,
         "messages": [{"role": "user", "content": prompt}]},
    )
    return "\n".join(x.get("text", "") for x in obj.get("content", []) if x.get("type") == "text")


def ask_gemini(system, prompt):
    key = os.environ["GEMINI_API_KEY"]
    model = os.getenv("GAUNTLET_GEMINI_MODEL", "gemini-3.1-pro-preview")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    obj = post_json(url, {"Content-Type": "application/json"}, {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
    })
    parts = obj.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    return "\n".join(p.get("text", "") for p in parts if p.get("text"))


def ask_ollama(system, prompt):
    base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    model = os.getenv("GAUNTLET_OLLAMA_MODEL", "qwen3:32b")
    obj = post_json(f"{base}/api/chat", {"Content-Type": "application/json"}, {
        "model": model, "stream": False,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
    })
    return obj.get("message", {}).get("content", "")


PROVIDERS = {
    "openai": ("OPENAI_API_KEY", ask_openai),
    "anthropic": ("ANTHROPIC_API_KEY", ask_anthropic),
    "gemini": ("GEMINI_API_KEY", ask_gemini),
    "ollama": (None, ask_ollama),
}


def read_text(path):
    if path == "-": return sys.stdin.read()
    return open(path, "r", encoding="utf-8").read()


def get_status():
    result = {}
    for name, (env_name, _) in PROVIDERS.items():
        if name == "openai":
            try:
                base_url, mode = openai_config(); config_error = None
            except Exception as exc:
                base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
                mode = os.getenv("OPENAI_API_MODE", "responses")
                config_error = str(exc)
            result[name] = {
                "configured": bool(os.getenv("OPENAI_API_KEY")),
                "env": "OPENAI_API_KEY",
                "model": os.getenv("GAUNTLET_OPENAI_MODEL", "gpt-5.6"),
                "base_url": base_url,
                "api_mode": mode,
            }
            if config_error: result[name]["config_error"] = config_error
        elif name == "ollama":
            result[name] = {
                "configured": bool(os.getenv("OLLAMA_BASE_URL")) or bool(os.getenv("GAUNTLET_OLLAMA_MODEL")),
                "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                "model": os.getenv("GAUNTLET_OLLAMA_MODEL", "qwen3:32b"),
            }
        else:
            result[name] = {"configured": bool(os.getenv(env_name)), "env": env_name}
    return result


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    ask = sub.add_parser("ask")
    ask.add_argument("provider", choices=PROVIDERS)
    ask.add_argument("--system", default="")
    ask.add_argument("--system-file")
    ask.add_argument("--prompt")
    ask.add_argument("--prompt-file")
    args = ap.parse_args()
    if args.cmd == "status":
        print(json.dumps(get_status(), indent=2)); return
    system = read_text(args.system_file) if args.system_file else args.system
    prompt = args.prompt if args.prompt is not None else (read_text(args.prompt_file) if args.prompt_file else sys.stdin.read())
    env_name, fn = PROVIDERS[args.provider]
    if env_name and not os.getenv(env_name): raise SystemExit(f"{env_name} is not set")
    print(fn(system, prompt))


if __name__ == "__main__":
    main()
