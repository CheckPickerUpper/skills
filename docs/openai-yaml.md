# Codex metadata

`SKILL.md` frontmatter is the only authored source for a published skill. Run `python3 scripts/generate-skill-artifacts.py` to emit `agents/openai.yaml`; never edit that generated file directly.

The picker name is always derived from the lowercase kebab-case `name`:

```yaml
name: to-tickets
```

becomes `To Tickets`. `display_name` is forbidden in authored metadata, so the name cannot drift between the picker, catalog, docs, and descriptor.

## Supported source fields

```yaml
short_description: "Break a spec into vertical tickets."
openai:
  interface:
    default_prompt: "Use $to-tickets to break this spec into vertical tickets."
    icon_small: "./assets/icon-small.svg"
    icon_large: "./assets/icon-large.svg"
    brand_color: "#0891B2"
  dependencies:
    tools:
      - type: "mcp"
        value: "github"
        description: "Publish approved tickets to GitHub."
        transport: "streamable_http"
  policy:
    products:
      - "codex"
```

The generator validates icon paths, hex colors, tool dependency fields, product lists, prompt length, and the required `$skill-name` in `default_prompt`. It derives `policy.allow_implicit_invocation` from the explicit frontmatter flag, Matt's `disable-model-invocation`, or the Codex default.

Use `python3 scripts/generate-skill-artifacts.py --check` in CI to fail on missing or stale descriptors, docs, catalogs, router references, or plugin entries.
