# Results API

Simulation result container and output file access.

## SimulationResult

::: idfkit.simulation.result.SimulationResult
    options:
      show_root_heading: true
      show_source: true

## ErrorReport

::: idfkit.simulation.parsers.err.ErrorReport
    options:
      show_root_heading: true
      show_source: true

## ErrorMessage

::: idfkit.simulation.parsers.err.ErrorMessage
    options:
      show_root_heading: true
      show_source: true

## HTMLResult

::: idfkit.simulation.parsers.html.HTMLResult
    options:
      show_root_heading: true
      show_source: true

## HTMLTable

::: idfkit.simulation.parsers.html.HTMLTable
    options:
      show_root_heading: true
      show_source: true

## Linking results to the model

`ResultIndex.build(doc, result, run_revision=..., run_model_hash=...)` links what a run wrote to
its SQLite output to the objects and nodes of the document that was simulated: component sizing
rows, timeseries output keys (the values in `ReportData` are never read), the object rows of
tabular reports, and every warning, severe and fatal message. Each key goes through an ordered
chain of rules, and the first that answers wins: `exact`, `typed`, `zonelist_composite`,
`space_to_zone`, `mirrored_shading`, `aggregate`, `ideal_loads_suffix`, `ems_key` and
`substring`. Every link is a `Resolution` that records its rule and a confidence. Items no rule
answers are listed in `unresolved` and counted in `coverage`, never dropped. Zone facts carry the
zone multiplier, so a total built from zone rows can apply it.

`for_object()` returns everything the run reported about one object or node; `objects_with()`
ranks objects by one metric; `is_fresh()` says whether the document still matches the run.

::: idfkit.simulation.linking
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      filters:
        - "!^_"

## Message catalogue

`classify_message()` recognises the most common EnergyPlus warnings and errors. Each of the 21
`MessageKind` entries in `MESSAGE_KINDS` has a stable dotted id, a hint at the likely causes, the
neighbouring object types worth inspecting and the result symptoms it can explain. `ResultIndex`
uses it to give every `LinkedMessage` its `kind`.

::: idfkit.simulation.parsers.err_catalog
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      filters:
        - "!^_"
