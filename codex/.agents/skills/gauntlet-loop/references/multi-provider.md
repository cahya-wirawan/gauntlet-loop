# Optional multi-provider routing

Native Codex subagents are sufficient to run the Gauntlet. Cross-provider calls are optional.

The bundled router supports these environment variables:

## OpenAI

```bash
export OPENAI_API_KEY=...
export GAUNTLET_OPENAI_MODEL=gpt-5.6
```

## Anthropic

```bash
export ANTHROPIC_API_KEY=...
export GAUNTLET_ANTHROPIC_MODEL=claude-sonnet-5
```

## Gemini

```bash
export GEMINI_API_KEY=...
export GAUNTLET_GEMINI_MODEL=gemini-3.1-pro-preview
```

## Ollama

```bash
export OLLAMA_BASE_URL=http://localhost:11434
export GAUNTLET_OLLAMA_MODEL=qwen3:32b
```

Run:

```bash
python .agents/skills/gauntlet-loop/scripts/provider_router.py status
```

Example request:

```bash
python .agents/skills/gauntlet-loop/scripts/provider_router.py ask anthropic \
  --system-file .agents/skills/gauntlet-loop/references/provider-critic-system.txt \
  --prompt-file /tmp/gauntlet-critic-input.txt
```

## Suggested diversity

When configured:

```text
Builder    -> native Codex
Critic     -> Gemini or Anthropic
Red Team   -> Anthropic or local
Verifier   -> native Codex + deterministic tools
Judge      -> provider different from Builder where practical
```

Do not send secrets or proprietary code to an external provider unless the user's environment
and policy permit it.

Provider routing is intentionally external to Codex custom-agent configuration. It makes
cross-provider use explicit and auditable rather than pretending that a native Codex subagent
has switched model providers.

## OpenAI base URL and API mode

The router supports a custom OpenAI-compatible endpoint:

```bash
export OPENAI_BASE_URL=https://api.openai.com/v1
```

The default API mode is the Responses API:

```bash
export OPENAI_API_MODE=responses
```

which calls `${OPENAI_BASE_URL}/responses`.

For servers that implement the traditional OpenAI-compatible Chat Completions API:

```bash
export OPENAI_BASE_URL=http://localhost:8000/v1
export OPENAI_API_MODE=chat_completions
```

which calls `${OPENAI_BASE_URL}/chat/completions`.

Do not include `/responses` or `/chat/completions` in `OPENAI_BASE_URL` itself.
Use `provider_router.py status` to inspect the resolved base URL and mode without exposing the API key.
