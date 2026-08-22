---
name: gauntlet-providers
description: Show which external providers are configured for the Gauntlet Loop and how roles can be routed. Use when the user asks about Gauntlet provider configuration.
disable-model-invocation: true
---

Use the bundled `gauntlet-router` MCP provider-status tool.

Report only:
- configured/unconfigured providers;
- current default model for configured providers;
- relevant environment variable names that are missing.

Never print API-key values.
