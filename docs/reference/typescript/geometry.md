---
title: '@idfkit/geometry'
---

# `@idfkit/geometry`

Read-only geometry extraction: where a model's surfaces are, in one frame,
without editing the model to find out. `getScene` resolves every detailed
surface a model states, reports what it could not place and what it did not
attempt, and leaves the document byte-for-byte unchanged. It reads no files and
holds no state, so the same code runs in Node, a browser, a worker, or an edge
runtime.

Not installed by `@idfkit/idfkit` and not reachable through a subpath of the
shared name. It is added by name.

```bash
npm install @idfkit/geometry
```

For a task-shaped walkthrough, see
[How to read a model's geometry](../../geometry/reading.md).

::: @idfkit/geometry
    handler: typescript
