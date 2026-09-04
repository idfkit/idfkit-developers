# Developing with an AI assistant

idfkit ships a reference set written for **AI coding assistants** writing Python against it,
bundled inside the wheel as the `developing-with-idfkit` skill. Sixteen topics, each
self-contained and task-oriented: a "when to use" summary, a quick start, a core API table,
then the details.

## Why they are not on this page

They used to be published here, one page per topic. They are not any more, and the reason is
the same one that makes the skill worth having.

The skill resolves the idfkit **installed in your project** and loads the references baked
into that exact version. A page on this site can only ever show one version, the one the site
is built against, which is stated in the footer. So a published copy is the one artifact in
the arrangement that can be wrong for a given reader: right for whoever happens to be on the
pinned version, quietly stale for everyone else. That is precisely the drift the skill exists
to prevent, and publishing a second copy to reintroduce it would be an odd thing to do.

The references are generated, not written twice. Their prose lives in
`agent_references/templates/` in the library, their code in `agent_references/snippets/`,
which is linted with ruff and type-checked with pyright under a strict configuration, so the
examples run as written. A build step inlines the code into the bundle.

## Why a skill and not just docs

An assistant that guesses at an API invents methods that don't exist. The skill
solves that by resolving the idfkit **installed in your project** and loading the
reference set baked into that exact version. Pin idfkit 0.13 and you get 0.13's
guidance; upgrade and the guidance upgrades with it. No version drift, and no
copy-pasted API summary in your `CLAUDE.md` going stale behind your back.

The bundle lives in the pip package at
`idfkit/.agents/skills/developing-with-idfkit/`, not in the plugin repo. Install
idfkit once and every project gets the matching docs.

## Installing the skill

The skill ships in the
[idfkit plugin](https://github.com/idfkit/idfkit-plugin). It requires **idfkit
0.13 or newer** installed in the project you're working on.

=== "Claude Code"

    Installs the skill alongside the MCP server, workflow skills, agents, and
    hooks:

    ```
    /plugin marketplace add idfkit/idfkit-plugin
    /plugin install idfkit@idfkit
    ```

=== "Any agent"

    [`skills`](https://github.com/vercel-labs/skills) is a cross-agent
    installer covering Claude Code, Cursor, Copilot, Gemini CLI, and Codex:

    ```bash
    npx skills add idfkit/idfkit-plugin -s developing-with-idfkit -g
    ```

    `-s` picks this one skill; `-g` installs it for every project. Drop `-g` to
    install into the current project's `.<agent>/skills/` instead.

=== "Copilot / Cursor"

    ```bash
    gh skill install idfkit/idfkit-plugin developing-with-idfkit --scope user
    ```

    Add `--agent cursor` for Cursor.

=== "Gemini CLI"

    ```bash
    gemini skills install https://github.com/idfkit/idfkit-plugin.git
    ```

=== "Codex"

    Run `$skill-installer` inside a Codex session and point it at
    `idfkit/idfkit-plugin`. The repo ships a `.codex-plugin/` manifest.

Once installed, the skill locates your project's interpreter (respecting
`VIRTUAL_ENV`, a local `.venv`, conda, pipenv, poetry, pdm, or uv) and reads the
bundle from there. To reach the same files directly, without the plugin:

```python
from importlib.resources import files

skill = files("idfkit") / ".agents" / "skills" / "developing-with-idfkit"
print((skill / "SKILL.md").read_text())
```

## What the sixteen references cover

The file name in the bundle is the second column, under
`idfkit/.agents/skills/developing-with-idfkit/references/`. They are not linked, because they
are not pages: they are files inside the wheel you already have installed.

| Task | File |
| ---- | ---- |
| Build, load, query, or modify a model | `document-and-objects.md` |
| Parse `.idf` / `.epJSON` files | `parsing-idf-epjson.md` |
| Write `.idf` / `.epJSON` files | `writing-output.md` |
| Validate a model against the schema | `schema-and-validation.md` |
| Find or update cross-references between objects | `reference-tracking.md` |
| Compute surface area, zone volume, azimuth, WWR | `geometry-and-surfaces.md` |
| Build a building footprint and zone it | `geometry-builders-and-zoning.md` |
| Stand up an HVAC system quickly with `HVACTemplate:*` | `hvac-templates.md` |
| Hand-author `AirLoopHVAC` / `PlantLoop` / `CondenserLoop` | `hvac-loops.md` |
| Run EnergyPlus simulations (sync, async, batch) | `simulation-execution.md` |
| Parse SQL / CSV / ESO / MTR / ERR simulation output | `result-parsing.md` |
| Find a weather station, download EPW/DDY, inject design days | `weather-data.md` |
| Evaluate `Schedule:*` objects to time series | `schedule-evaluation.md` |
| Compute R-value, U-value, SHGC, gas mixture properties | `thermal-properties.md` |
| Render building geometry to 3D or SVG | `visualization.md` |
| Migrate a model forward across EnergyPlus versions | `version-migration.md` |

## Conventions used in every reference

- **Imports come from `idfkit` directly** unless the symbol lives in a
  sub-package (`idfkit.simulation`, `idfkit.weather`, `idfkit.schedules`,
  `idfkit.thermal`, `idfkit.visualization`).
- **Python 3.10+** syntax: `tuple[int, int, int]`, and
  `from __future__ import annotations` in real code.
- **Strict mode is the default**: unknown field names raise `InvalidFieldError`.
  Pass `strict=False` only as a tolerant migration fallback.
- **The EnergyPlus version is part of every document**: `doc.version` is a
  `tuple[int, int, int]`, and the newest supported version is
  `idfkit.LATEST_VERSION`.

## A different surface: the MCP server

Writing Python that imports idfkit is what this skill is for. Driving a model
*through* an assistant, where the agent calls `load_model` and `run_simulation`
as tools rather than writing code, is the job of the separate
[idfkit-mcp](https://github.com/idfkit/idfkit-mcp) server, which the plugin also
installs.

## See also

- [Build your first model](../tutorials/first-model.md) for the human-facing
  walkthrough of the same API.
- [Reference](../reference/index.md) for the generated API documentation.
