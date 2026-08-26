---
name: gauntlet-providers
description: Checks which optional external model providers are configured for the multi-provider Gauntlet Loop. Use when the user asks about Gauntlet providers, model routing, OpenAI, Anthropic, Gemini API, or Ollama configuration.
---

# Gauntlet Provider Status

Call the `gauntlet-router` MCP tool `provider_status`.

Report provider, configured/unconfigured, selected default model, and missing environment variable name if relevant. Never print secret values.
