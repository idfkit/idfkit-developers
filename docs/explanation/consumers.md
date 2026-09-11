# Who consumes the libraries

idfkit is two libraries, and around them sits a workspace of projects that use them: a model
server for AI tools, a language server for editors, a web editor, a browser tool, the EnergyPlus
documentation project, this site, a hosted deployment, an editor plugin, and a marketing page that
tells strangers what to install. When a library releases, every one of those has to move, in an
order that cannot be wrong, and some of them may deliberately not move at all.

This page is the roster those moves are governed by. It explains the register rather than
documenting a procedure: what it records, what it refuses to record, and why.

## A roster, not a table of versions

The register records who the consumers are, which door each comes through in JavaScript, how each
resolves a library, which consumer each depends on, and **where each one's level is written**. It
never records the level itself.

That refusal is the design. The register is read at an immutable governance tag, and a consumer's
level moves every time it adopts a release. Writing the levels here would mean cutting a tag per
bump, and it would make two facts out of one, which is a failure this project has already had: a
page claimed one governance tag while the release pinned the next, because only one copy moved. So
the register points, and a reader follows the pointer to the consumer's own file. The scheduled
sweep in the conformance repository is what reads every level and says who is behind.

## Behind is allowed; behind without a reason is not

A consumer may sit on an older level. What the register forbids is the silence about it. A lag has
one of the two kinds the parity ledger already uses for an absence: **not yet**, which names the
tracked item that will close it, or **deliberate**, which states a policy. A lag never names a
version, because a version in a reason is stale the moment anything moves.

## Two doors, both open

JavaScript can be installed under the shared name or as the scoped packages, and both are supported.
A consumer on the scoped packages is not behind anything and carries no lag on that account. Nothing
in the register may present a door as work outstanding, and nothing is satisfied by moving a
consumer from one door to the other.

## Where it lives, and who may change it

`governance/consumers.toml` sits beside the naming register and the parity ledger in the
conformance repository, which belongs to neither language. Every consumer's CI checks itself
against its own entry at a pinned tag, and a change to the register takes review from a maintainer
of the other language. For the parity side of the same governance, see
[the parity ledger](parity.md); for the vocabulary, [the naming map](naming-map.md).

<!-- BEGIN GENERATED FROM consumers.toml. Edit the register, not this page. -->

Generated from [`governance/consumers.toml`](https://github.com/idfkit/idfkit-conformance/blob/governance-2026.18/governance/consumers.toml) at `governance-2026.18`, the governance tag this
release pins. Correct the register and regenerate; a correction made on this page would be
overwritten, and it would never reach a consumer's self-check.

## Every consumer { #every-consumer }

| Consumer | Repository | Role | Depends on |
| --- | --- | --- | --- |
| `idfkit-mcp` | [idfkit/idfkit-mcp](https://github.com/idfkit/idfkit-mcp) | builds against it | nothing |
| `idfkit-lsp` | [idfkit/idfkit-lsp](https://github.com/idfkit/idfkit-lsp) | builds against it | nothing |
| `idfkit-docs` | [idfkit/idfkit-docs](https://github.com/idfkit/idfkit-docs) | builds against it | nothing |
| `idfkit-developers` | [idfkit/idfkit-developers](https://github.com/idfkit/idfkit-developers) | builds against it | nothing |
| `envelop` | [idfkit/idfkit-app](https://github.com/idfkit/idfkit-app) | builds against it | nothing |
| `idfkit-shoebox` | [idfkit/idfkit-shoebox](https://github.com/idfkit/idfkit-shoebox) | builds against it | nothing |
| `idfkit-mcp-deployment` | [idfkit/idfkit-mcp-deployment](https://github.com/idfkit/idfkit-mcp-deployment) | delivers it to a person | `idfkit-mcp` |
| `idfkit-plugin` | [idfkit/idfkit-plugin](https://github.com/idfkit/idfkit-plugin) | delivers it to a person | `idfkit-mcp`, `idfkit-lsp` |
| `idfkit-com` | [idfkit/idfkit.com](https://github.com/idfkit/idfkit.com) | teaches a reader to install it | nothing |

## Where each level is written { #where-each-level-is-written }

One row per consumer per library. Follow the place to read the level; the register never
states it. A lag of "none" means nothing is wrong: it is the normal state.

| Consumer | Library | Door | How | Where the level is written | Lag |
| --- | --- | --- | --- | --- | --- |
| `idfkit-mcp` | Python | `idfkit` | declared directly | `pyproject.toml` at `project.dependencies[idfkit]` | not yet, [tracked](https://github.com/idfkit/idfkit-mcp/pull/75) |
| `idfkit-lsp` | Python | `idfkit` | declared directly | `server/pyproject.toml` at `project.dependencies[idfkit]`<br>`levels.json` at `libraries[name=idfkit].level` | not yet, [tracked](https://github.com/idfkit/idfkit-lsp/issues/17) |
| `idfkit-lsp` | JavaScript | the scoped packages | declared directly | `model-server/package.json` at `dependencies["@idfkit/core"]`<br>`model-server/package.json` at `dependencies["@idfkit/language"]`<br>`levels.json` at `libraries[name=@idfkit/core].level` | not yet, [tracked](https://github.com/idfkit/idfkit-lsp/issues/17) |
| `idfkit-docs` | Python | `idfkit` | declared directly | `pyproject.toml` at `project.dependencies[idfkit]` | not yet, [tracked](https://github.com/idfkit/idfkit-docs/pull/30) |
| `idfkit-developers` | Python | `idfkit` | declared directly | `pyproject.toml` at `project.dependencies[idfkit]`<br>`pyproject.toml` at `tool.idfkit.library.level` | none |
| `envelop` | JavaScript | the scoped packages | declared directly | `package.json` at `dependencies["@idfkit/core"]`<br>`package.json` at `dependencies["@idfkit/schemas"]`<br>`package.json` at `dependencies["@idfkit/language"]`<br>`package.json` at `dependencies["@idfkit/weather"]` | not yet, [tracked](https://github.com/idfkit/idfkit-app/issues/226) |
| `idfkit-shoebox` | JavaScript | the scoped packages | declared directly | `package.json` at `dependencies["@idfkit/core"]`<br>`package.json` at `dependencies["@idfkit/schemas"]`<br>`package.json` at `dependencies["@idfkit/weather"]` | none |
| `idfkit-mcp-deployment` | Python | `idfkit` | in a container image | `cdk.json` at `context.idfkit_mcp_ref` (idfkit-mcp via `idfkit-mcp`) | none |
| `idfkit-plugin` | Python | `idfkit` | fetched when an editor starts | `.mcp.json` at `mcpServers.idfkit.args[0]` (idfkit-mcp via `idfkit-mcp`)<br>`.lsp.json` at `idfkit.args[1]` (idfkit-lsp via `idfkit-lsp`), range | not yet, [tracked](https://github.com/idfkit/idfkit-plugin/issues/17) |

## Recorded, and governed by nothing here { #ungoverned }

Dependencies the constitution places outside the unification. They are listed so that a
coordinated bump can see them, and no check in the register acts on them.

| Consumer | Package | Note |
| --- | --- | --- |
| `envelop` | `@idfkit/engine` | EnergyPlus compiled to WebAssembly, run in the browser. Outside the unification by the constitution. |
| `idfkit-shoebox` | `@idfkit/engine` | EnergyPlus compiled to WebAssembly. Declared as a caret range; the lockfile holds what is installed. |
| `idfkit-shoebox` | `@idfkit/engine-assets` | The engine's binary assets, staged into public/ by predev and prebuild. Outside the unification. |

## Does a save keep the user's formatting? { #formatting }

What each consumer does today when it writes a model to disk, not what it should do or
plans to. The register carries the reason beside each answer.

| Consumer | Preserves formatting |
| --- | --- |
| `idfkit-mcp` | no |
| `idfkit-lsp` | not-applicable |
| `envelop` | yes |
| `idfkit-shoebox` | not-applicable |
| `idfkit-mcp-deployment` | inherited |
| `idfkit-plugin` | not-applicable |

## Documentation surfaces { #surfaces }

| Host | Status | Published by | Must |
| --- | --- | --- | --- |
| `developers.idfkit.com` | serving | `idfkit-developers` | state the level it describes |
| `py.idfkit.com` | retired | `idfkit/idfkit` | redirect permanently to `developers.idfkit.com` |
| `js.idfkit.com` | retired | `idfkit/idfkit-js` | redirect permanently to `developers.idfkit.com` |

<!-- END GENERATED FROM consumers.toml. -->
