# Model Graph

A model has two graphs. The [reference graph](references.md) joins objects through the fields that
name other objects. The [HVAC topology](hvac.md) joins objects through the fluid nodes they share.
`idfkit.graph.ModelGraph` is one read-only view over both: one set of node and edge kinds, one
breadth-first walk, and one export to node-link JSON.

`ModelGraph` copies nothing. Constructing it stores the document and returns. Each walk asks the
document's reference graph and its cached `HVACTopology` for neighbours, so the view always
reflects the document as it is now. Both layers stay usable on their own.

```python
from idfkit import load_idf
from idfkit.graph import ModelGraph
from idfkit.hvac import ObjectKey

doc = load_idf("model.idf")
graph = ModelGraph(doc)

sub = graph.neighbourhood(ObjectKey("Fan:ConstantVolume", "Supply Fan"), hops=2)
for edge in sub.edges:
    print(edge.kind, edge.source, "->", edge.target)
```

## Vocabulary

Every graph node has a kind, and the kind fixes its layer.

| Node kind | Layer | Stands for | Identity |
|---|---|---|---|
| `object` | `model` | A model object | `ObjectKey` |
| `node` | `topology` | A fluid node | The node name |
| `result_fact` | `results` | A simulation result about an object | The owning `ObjectKey` |
| `message` | `results` | A simulation message | Its kind and index in the run |

Every edge is directed, and its kind fixes its layer.

| Edge kind | Layer | From → to |
|---|---|---|
| `reference` | `model` | Object → the object one of its fields names |
| `flow` | `topology` | Node → object for an inlet; object → node for an outlet |
| `control` | `topology` | Object → the node it senses, sets or actuates |
| `membership` | `topology` | Component → its loop, or zone equipment → its equipment connections |
| `result_link` | `results` | Result fact or message → the object or node it is about |

Ids are composite and upper-cased, so the same model gives the same ids every time:
`object:ZONE:SPACE1-1` for an object, `node:SUPPLY INLET NODE` for a node. A node carries the
model's spelling in `key` (objects) or `node` (fluid nodes), which can be passed back to
`HVACTopology` or the document. An edge's `key` tells apart edges between the same two nodes, such
as `reference:zone_name` and `flow:air_outlet_node_name`, and its `attrs` hold the field, connection
type, fluid and, for membership, the side, branch and position.

The sets are closed within a release. A later release may add a kind or a layer without a breaking
change, so code that reads kinds must ignore the ones it does not know.

## The results layer

The `results` layer is not available yet. `ModelGraph.layers` is `["model", "topology"]`, and
`ModelGraph.unavailable` lists `results` with the reason. A walk or an export that asks for
`result_fact`, `message` or `result_link` returns none of them and does not raise.

## Walking a neighbourhood

`neighbourhood(start, ...)` walks breadth first, in both edge directions, from an object (an
`ObjectKey`) or a fluid node (its name). It is bounded:

| Argument | Default | Bound |
|---|---|---|
| `hops` | `1` | The most edges from `start`. `0` returns `start` alone |
| `max_nodes` | `200` | The most nodes returned, `start` included |
| `node_kinds` | all | Walk only through nodes of these kinds |
| `edge_kinds` | all | Walk only along edges of these kinds |
| `categories` | all | Keep only object nodes of these component categories, plus `start` and the fluid nodes on the paths to them. Applied before `max_nodes` |

It returns a `Subgraph` with the nodes in breadth-first order and the edges between them. It also
says what it left out:

- `truncated` is true when the hop or node bound cut the walk.
- `omitted_nodes` counts nodes reached but not returned. It is a lower bound, since the walk stops
  at the cut.
- `frontier` lists the returned nodes that have neighbours not returned. Walk again from one of
  them to continue.

`coverage` reports what the view could not see: unexpanded `HVACTemplate` systems, EMS programs
and object types with no connection rule.

## Node-link export

`to_node_link()` returns the view as a dict in networkx's node-link layout. `write_node_link(graph)`
returns it as JSON text, and `save_node_link(graph, path)` writes it to a file in UTF-8. All three
take the same scope arguments: `layers`, `node_kinds`, `edge_kinds`, and `start` with `hops` for
the neighbourhood of one object or node. An export has no node bound.

```python
from idfkit.graph import save_node_link

save_node_link(graph, "model-graph.json")
save_node_link(graph, "fan.json", start=ObjectKey("Fan:ConstantVolume", "Supply Fan"), hops=2)
```

The file holds five keys:

| Key | Value |
|---|---|
| `directed` | Always `true` |
| `multigraph` | Always `true`. Edges between the same two nodes are told apart by `key` |
| `graph` | `format` (`"idfkit-model-graph"`), `format_version` (`1`), `idfkit_version`, `energyplus_version`, `layers`, `unavailable`, `coverage`, `scope` and `results_state` |
| `nodes` | One object per node: `id`, `kind`, `layer`, `label`, then `object_type`, `name` and `category` for objects, or `name` and `fluid` for fluid nodes |
| `edges` | One object per edge: `source`, `target`, `key`, `kind`, `layer`, then the edge's attributes, such as `field`, `connection_type` and `fluid` |

The edge list is under `"edges"`, not `"links"`. Every edge endpoint is a node `id`, and ids are
unique within a file. `format_version` changes only when a key is removed or renamed, or a kind
changes meaning. A new attribute, kind or layer leaves it at `1`, so a reader must skip what it
does not recognise.

### Reading the file elsewhere

networkx 3.6 and later read the file with no keyword arguments:

```python
import json

import networkx as nx

with open("model-graph.json", encoding="utf-8") as f:
    g = nx.node_link_graph(json.load(f))
```

On networkx 3.4 and 3.5, pass `edges="edges"`: `nx.node_link_graph(data, edges="edges")`.

d3-force expects the edge list under `links`. Rename the key before handing it over:

```javascript
const data = await (await fetch("model-graph.json")).json();
data.links = data.edges; delete data.edges;
```

idfkit does not depend on networkx. The export is written with the standard library's `json`.

::: idfkit.graph
